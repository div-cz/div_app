# views.payments.py 

import datetime
import io
import os
import qrcode
import re
import requests
import smtplib
import unicodedata

from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from div_content.models import Book, Bookisbn, Booklisting, Bookpurchase
from div_content.utils.palmknihy import get_catalog_product, get_palmknihy_download_url, get_token

# IMPORT VE FUNKCI GENERATE_QR
#from div_content.utils.palmknihy_sync import fetch_and_update_bookisbn 

from div_content.utils.payments import generate_qr_for_bookpurchase

from email.message import EmailMessage
from io import BytesIO



# =========================================================
# Variabilní symbol pro platby – metodika DIV.cz / eKultura
# ---------------------------------------------------------
# VS je vždy 10 číslic, skládá se takto:
#
# PPP TT F NNNN
#  |   |  |  |
#  |   |  |  +--- Pořadové číslo objednávky (poslední 4 čísla)
#  |   |  +------ Formát  (0–9, podle TT)
#  |   +--------- Typ produktu/služby (01–99, v rámci projektu)
#  +------------- Projekt (001–999, podle tabulky projektů)
#
# Příklady:
# 0103821234  – Projekt DIV.cz (010), knihy (38), formát epub (2), objednávka č. 1234
# 0103831235  – Projekt DIV.cz (010), knihy (38), formát mobi (3), objednávka č. 1235
#
# Každý projekt má svůj trojciferný kód (PPP), každý typ (TT) a formát (F) je určen tabulkou.
# NNNN je unikátní pro každou objednávku v daném projektu a typu.
#
# F: 0 = print, 1 = audio, 2 = epub, 3 = mobi, 4 = pdf, 5 = burza koupě, 6 = burza prodej
#
# Více informací o struktuře VS viz interní dokumentace nebo konzultuj s Martinem.
# =========================================================


FIO_API_URL = "https://fioapi.fio.cz/v1/rest/periods/"


def get_mimetype_from_format(fmt):
    fmt = fmt.lower()
    if fmt == "pdf":
        return ("application/pdf", "pdf")
    elif fmt == "mobi":
        return ("application/x-mobipocket-ebook", "mobi")
    elif fmt == "epub":
        return ("application/epub+zip", "epub")
    else:
        return ("application/octet-stream", fmt)


def strip_diacritics(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')


# QR kod pro zaplaceni konkretni e-knihy ve formatu SPD (FIO)
def generate_qr(request, book_id, format):
    if not format:
        return HttpResponse("Chybí formát.", status=400)
    book = get_object_or_404(Book, pk=book_id)
    from div_content.utils.palmknihy_sync import fetch_and_update_bookisbn
    
    #fetch_and_update_bookisbn(book)  # vždy ověř aktuální cenu
    # jen PALM
    bookisbn = Bookisbn.objects.filter(book=book, format__iexact=format).first()
    if not bookisbn or not bookisbn.price:
        raise Http404("E-kniha není dostupná nebo nemá cenu.")

    # sync only for PALM
    if getattr(bookisbn, "ISBNtype", "").upper() == "PALM":
        fetch_and_update_bookisbn(book)
    
    amount = bookisbn.price

    # 1. Vytvoř záznam o zamýšlené koupi
    user = request.user if request.user.is_authenticated else None

    palmknihy_id = bookisbn.palmknihyid
    
    purchase = Bookpurchase.objects.create(
        book=book,
        user=user,
        format=format,
        price=bookisbn.price,
        status="PENDING",
        palmknihyid=palmknihy_id,
        #createdat=now(),
    )


    # 2. Použij purchase.purchaseid jako X-VS
    format_code = {"epub": "2", "mobi": "3", "pdf": "4"}.get(purchase.format.lower(), "9")
    vs = f"01038{format_code}{str(purchase.purchaseid).zfill(4)}"
    # Odstraň diakritiku pro MSG 

    username = user.username if user and hasattr(user, "username") else "anon"
    msg = unicodedata.normalize(
        'NFKD',
        f"{book.title}-{format}-{username}-DIVcz"
    ).encode('ascii', 'ignore').decode('ascii').replace(" ", "")

    #používá se funkce v views.books.py = update, tak asi už ne
    qr_string = f"SPD*1.0*ACC:CZ2620100000002602912559*AM:{amount}*CC:CZK*MSG:{msg.replace('=', ':')}*X-VS:{vs}"


    # 3. Vytvoř QR obrázek
    img = qrcode.make(qr_string)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    # 4. Vrať QR obrázek jako response
    return HttpResponse(buffer.getvalue(), content_type="image/png")


  

  

"""
def check_payments():
    ###FIO API###
    token = "FIO_TOKEN"  # Uloženo v .env
    response = requests.get(f"{FIO_API_URL}last/{token}/transactions.json")
    
    if response.status_code == 200:
        transactions = response.json().get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
        
        for tx in transactions:
            vs = str(tx.get("column5", {}).get("value", ""))
            try:
                amount = float(str(tx.get("column1", {}).get("value", "0")).replace(",", "."))
            except Exception:
                amount = 0.0

            if amount <= 0:
                continue  # zajímají nás jen příchozí platby

            print(f"Kontroluji VS: {vs} částka: {amount}")

            m = re.match(r"01038([23456])(\d{4})$", vs)
            if not m:
                print(f"❌ VS {vs} neodpovídá očekávanému tvaru.")
                continue

            fmt_num = m.group(1)
            suffix = m.group(2)
            print(f"➡️  Formát VS: {fmt_num}, Suffix: {suffix}")

            if fmt_num in ["2", "3", "4"]:
                purchase = Bookpurchase.objects.filter(
                    purchaseid=int(suffix),  # nebo purchaseid__endswith=suffix
                    status="PENDING"
                ).first()
                print(f"Našel jsem purchase: {purchase}")
                if purchase:
                    print(f"Purchase price: {purchase.price}, Expected amount: {amount}")
                    if float(purchase.price) == float(amount):
                        purchase.status = "PAID"
                        purchase.paymentdate = now()
                        purchase.expirationdate = now().replace(year=now().year + 3)
                        purchase.save()
                        print(f"✅ Platba spárována a potvrzena pro VS {vs} (PurchaseID {purchase.purchaseid}), stav změněn na PAID")
                    else:
                        print(f"❌ Částka nesouhlasí pro VS {vs}: očekáváno {purchase.price}, přišlo {amount}")
                else:
                    print(f"❌ Nenalezen žádný PENDING purchase pro suffix {suffix} (VS {vs})")

    return "Kontrola dokončena"
"""



def check_payments_from_fio():
    token = os.getenv("FIO_TOKEN")
    if not token:
        print("Chybí FIO_TOKEN v env.")
        return

    today = datetime.date.today()
    ninety_days_ago = today - datetime.timedelta(days=90)
    from_date = ninety_days_ago.strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    url = f"{FIO_API_URL}{token}/{from_date}/{to_date}/transactions.json"

    response = requests.get(url, timeout=10)
    if response.status_code != 200:
        print(f"FIO API chyba: {response.status_code}")
        print(f"Odpověď: {response.text}")
        return
        
    if response.status_code == 409:
        print("FIO API říká: příliš rychlé dotazy, vyčkej minutu a zkus znovu.")
        return


    try:
        data = response.json()
    except Exception as e:
        print("Chyba při parsování JSON:", e)
        print("Odpověď:", response.text[:1000])
        return

    transactions = data.get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
    for tx in transactions:
        vs = str(tx.get("variableSymbol", "")) or str(tx.get("column5", {}).get("value", ""))
        # Amount parsing
        try:
            amount = float(str(tx.get("column1", {}).get("value", "0")).replace(",", "."))
        except Exception:
            amount = 0.0
        if amount <= 0:
            continue  # zajímají nás jen příchozí platby            
        print("Kontroluji VS:", vs, "částka:", amount)
        m = re.match(r"01038([23456])(\d{4})$", vs)
        if not m:
            continue
        fmt_num = m.group(1)
        suffix = m.group(2)

        # Páruj Booklisting (burza)
        if fmt_num in ["5", "6"]:
            listing = Booklisting.objects.filter(booklistingid__endswith=suffix, status="RESERVED").first()
            if listing:
                listing.status = "PAID"
                listing.paymentdate = now()
                listing.save()
                print(f"✅ Platba spárována pro Booklisting {listing.booklistingid}")
                continue

        # Páruj Bookpurchase (ekniha)
        if fmt_num in ["2", "3", "4"]:
            m = re.match(r"01038([23456])(\d{4})$", vs)
            if not m:
                print(f"❌ VS {vs} neodpovídá očekávanému tvaru.")
                continue
            
            fmt_num = m.group(1)
            suffix = m.group(2)
            
            if fmt_num in ["2", "3", "4"]:
                purchase = Bookpurchase.objects.filter(
                    purchaseid=int(suffix),          #purchaseid__endswith=suffix,
                    status="PENDING"
                ).first()

            if not purchase:
                print(f"❌ Nenalezen Bookpurchase pro VS {vs}")
                continue
            if float(purchase.price) == float(amount):
                purchase.status = "PAID"
                purchase.paymentdate = now()
                purchase.expirationdate = now().replace(year=now().year + 3)
                purchase.save()
                print(f"✅ Platba spárována a potvrzena pro VS {vs} (PurchaseID {purchase.purchaseid})")
            else:
                print(f"❌ Částka nesouhlasí pro VS {vs}: očekáváno {purchase.price}, přišlo {amount}")




@login_required
def check_purchase_status(request, purchase_id):
    try:
        purchase = Bookpurchase.objects.get(pk=purchase_id, user=request.user)
        return JsonResponse({"status": purchase.status})
    except Bookpurchase.DoesNotExist:
        return JsonResponse({"status": "NOT_FOUND"}, status=404)

@login_required
def posledni_pending_purchaseid(request):
    bookid = request.GET.get('bookid')
    fmt = request.GET.get('format')
    purchase = Bookpurchase.objects.filter(
        book_id=bookid,
        user=request.user,
        format=fmt,
        status="PENDING"
    ).order_by('-purchaseid').first()
    if purchase:
        return JsonResponse({"purchase_id": purchase.purchaseid})
    return JsonResponse({"purchase_id": None})


def bank_transactions(request):
    if not request.user.is_superuser:
        raise Http404("Nepovolený přístup.")

    token = os.getenv("FIO_TOKEN")  # nebo použij os.getenv("FIO_TOKEN") když budeš chtít zpátky z env
    today = datetime.date.today()
    from_date = (today - datetime.timedelta(days=90)).strftime("%Y-%m-%d")
    to_date = today.strftime("%Y-%m-%d")
    url = f"https://fioapi.fio.cz/v1/rest/periods/{token}/{from_date}/{to_date}/transactions.json"

    response = requests.get(url, timeout=10)
    fio_status = response.status_code
    fio_text = response.text[:1000]

    try:
        data = response.json()
    except Exception:
        data = None

    fio_raw = repr(data) if data else ""
    transactions = []
    if data:
        transactions = data.get("accountStatement", {}).get("transactionList", {}).get("transaction", []) if data else []


    return render(request, "admin/banka.html", {
        "transactions": transactions,
        "fio_url": url,
        "fio_status": fio_status,
        "fio_text": fio_text,
        "fio_token": token,
        "fio_raw": fio_raw,
    })




def get_ebook_purchase_status(user, book, ebook_formats):
    """
    Přidá ke každému formátu (epub/pdf/mobi...) hodnoty:
    - is_paid: True/False
    - show_qr: True/False
    - is_free_div: True/False
    """
    if not user.is_authenticated:
        for fmt, data in ebook_formats.items():
            data['is_paid'] = False
            data['show_qr'] = data.get('price', 0) > 0
            data['is_free_div'] = data.get('type') == 'DIV' and (data.get('price') == 0 or not data.get('price'))
        return ebook_formats

    paid_purchases = Bookpurchase.objects.filter(user=user, book=book, status="PAID")
    paid_formats = {p.format.lower() for p in paid_purchases}
    for fmt, data in ebook_formats.items():
        data['is_paid'] = fmt in paid_formats
        data['show_qr'] = data.get('price', 0) > 0 and not data['is_paid']
        data['is_free_div'] = data.get('type') == 'DIV' and (data.get('price') == 0 or not data.get('price'))
    return ebook_formats









# Stáhnout e-knihu – zdarma nebo po zaplacení
@login_required
def download_ebook(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn, format=format)
    book = bookisbn.book

    # Poznáš zdroj
    isbntype = (bookisbn.ISBNtype or "").upper()

    # 1. PALM - stahování řešit přes Palmknihy API, přesměruj/poskytni link nebo stáhni jejich API
    if bookisbn.ISBNtype == "PALM":
        # Najdi nebo vytvoř purchase (objednávku), musíš mít purchaseid!
        purchase = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            format=format,
            status="PAID"
        ).first()
        if not purchase:
            raise Http404("Nemáte zaplaceno nebo objednáno.")
    
        # Připrav JSON data dle příručky
        palmknihy_link = get_palmknihy_download_url(
            palmknihyid=bookisbn.palmknihyid,
            purchaseid=purchase.purchaseid,
            user_id=request.user.id,
            email=request.user.email,
            format=format,
            delivery_type="ebook" if format.lower() in ["epub", "pdf", "mobi"] else "audiobook"
        )
        if not palmknihy_link:
            return HttpResponse("Palmknihy - link není dostupný.", status=404)
        return redirect(palmknihy_link)


    # 2. DIV (nebo prázdný/ostatní) – tvůj původní kód:
    if bookisbn.price == 0 or bookisbn.price is None:
        allowed = True
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            format=format,
            defaults={
                "status": "PAID",
                "price": 0,
                "paymentdate": now(),
                "expirationdate": now().replace(year=now().year + 3),
                "source": isbntype,
            },
        )
        if not created and purchase.status != "PAID":
            purchase.status = "PAID"
            purchase.price = 0
            purchase.paymentdate = now()
            purchase.expirationdate = now().replace(year=now().year + 3)
            purchase.save()
    else:
        allowed = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            status="PAID"
        ).exists()

    if not allowed:
        raise Http404("Nemáte oprávnění k této e-knize.")

    filename = f"{book.url}.{format.lower()}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)

    if not os.path.exists(filepath):
        messages.error(
            request,
            "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
        )
        return redirect("book_detail", book_url=book.url)

    with open(filepath, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


"""
@require_POST
@login_required
def send_to_reader_modal(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    purchase = Bookpurchase.objects.filter(book=book, user=request.user, format=format, status="PAID").order_by('purchaseid').first()
    if purchase and purchase.kindlemail:
        # Pokud už byla objednávka zaplacena a máme email, POUŽIJEME VŽDY JEN TEN
        kindlemail = purchase.kindlemail
    else:
        # Nová objednávka, vezmeme z POST nebo user.email
        kindlemail = request.POST.get("kindlemail") or request.user.email
        # Nezapomeň ho i uložit do purchase při prvním stažení/zaplacení

    if not kindlemail or "@" not in kindlemail:
        # Nebudeme vůbec pokračovat, zobrazíme chybovou hlášku
        messages.error(request, "Neplatný e-mail pro odeslání do čtečky!")
        return redirect("book_detail", book_url=book.url)


    user = request.user

    # Placené knihy: kontrola zaplacení a e-mail už neměnit
    paid_purchase = Bookpurchase.objects.filter(
        book=book,
        user=user,
        format=format,
        status="PAID"
    ).order_by('purchaseid').first()

    if bookisbn.price > 0:
        if not paid_purchase:
            raise Http404("Nemáte zaplaceno.")
        # Pokud už byl e-mail uložen, NEPŘEPISUJEME ho (pole bude readonly)
        if not paid_purchase.kindlemail:
            paid_purchase.kindlemail = kindlemail
            paid_purchase.save()
        kindlemail = paid_purchase.kindlemail
    else:
        # Zdarma: povolíme vždy zadat nový e-mail, nebo použijeme existující
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=user,
            format=format,
            defaults={
                "status": "PAID",
                "price": 0,
                "paymentdate": now(),
                "expirationdate": now().replace(year=now().year + 3),
                "kindlemail": kindlemail,
                "readonly": True,
            },
        )
        # Pokud existoval, případně updatni email (u zdarma je to OK)
        if not created and purchase.kindlemail != kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
        kindlemail = purchase.kindlemail

    # Odeslání do čtečky:
    recipient = kindlemail
    mimetype, ext = get_mimetype_from_format(format)
    filename = f"{book.url}.{ext}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
    if not os.path.exists(filepath):
        raise Http404("Soubor nenalezen.")

    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užijte si čtení.\n\n Tým DIV.cz")

    with open(filepath, 'rb') as f:
        maintype, subtype = mimetype.split('/')
        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)

    messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
    messages.error(
    request,
    "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
)
    return redirect("book_detail", book_url=book.url)
"""



@login_required
def send_to_reader_modal(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    # Najdi první PAID objednávku
    purchase = Bookpurchase.objects.filter(
        book=book,
        user=request.user,
        format=format,
        status="PAID"
    ).order_by('purchaseid').first()

    # Pokud není, najdi PENDING (u placené knihy), nebo vytvoř novou (jen pokud žádná není)
    if not purchase:
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            format=format,
            status="PENDING" if bookisbn.price > 0 else "PAID",   # free hned paid
            defaults={
                "price": bookisbn.price or 0,
                "paymentdate": now() if bookisbn.price == 0 else None,
                "expirationdate": now().replace(year=now().year + 3) if bookisbn.price == 0 else None,
                "source": (bookisbn.ISBNtype or "").upper(),
            }
        )

    # Už je uložen kindle mail? (readonly)
    kindlemail = purchase.kindlemail if purchase and purchase.kindlemail else request.user.email  # Pokud už v purchase je, použij, jinak předvyplň uživatelovým
    readonly = bool(purchase and purchase.kindlemail)  # Pokud už je v DB, už nikdy neměnit


    if request.method == "POST":
        kindlemail = request.POST.get("kindlemail")
        if not kindlemail or "@" not in kindlemail:
            messages.error(request, "Neplatný e-mail.")
            return redirect("book_detail", book_url=book.url)
        if not purchase.kindlemail:
            # První zápis je povolený
            purchase.kindlemail = kindlemail
            purchase.save()
        # Další pokusy už mail nemění!
        recipient = purchase.kindlemail

        # ---- ODESLÁNÍ E-MAILU --------
        mimetype, ext = get_mimetype_from_format(format)
        filename = f"{book.url}.{ext}"
        filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
        if not os.path.exists(filepath):
            messages.error(
                request,
                "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            return redirect("book_detail", book_url=book.url)

        msg = EmailMessage()
        msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
        msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
        msg['To'] = recipient
        msg.set_content("Vaše e-kniha je v příloze. Užijte si čtení.\n\n Tým DIV.cz")

        with open(filepath, 'rb') as f:
            maintype, subtype = mimetype.split('/')
            msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=filename)

        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
            smtp.send_message(msg)

        messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
        return redirect("book_detail", book_url=book.url)

    # ---- GET požadavek – jen zobrazení formuláře ----------
    return render(request, "books/send_to_reader_email.html", {
        "isbn": isbn,
        "format": format,
        "user": request.user,
        "kindlemail": purchase.kindlemail or request.user.email,
        "readonly": bool(purchase.kindlemail),
    })




@login_required
def send_to_reader(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    if request.method == "POST":
        kindlemail = request.POST.get("kindlemail") or request.user.email
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            format=format,
            defaults={
                "status": "PAID" if bookisbn.price == 0 else "PENDING",
                "price": bookisbn.price or 0,
                "paymentdate": now() if bookisbn.price == 0 else None,
                "expirationdate": now().replace(year=now().year + 3) if bookisbn.price == 0 else None,
                "kindlemail": kindlemail
            }
        )
        if not created and not purchase.kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
    else:
        return render(request, "books/send_to_reader_email.html", {"isbn": isbn, "format": format, "user": request.user})

    recipient = purchase.kindlemail

    # PALMKNIHY: stáhni přes API, přilož do mailu
    if bookisbn.ISBNtype == "PALM":
        palmknihy_link = get_palmknihy_download_url(
            palmknihyid=bookisbn.palmknihyid,
            purchaseid=purchase.purchaseid,
            user_id=request.user.id,
            email=request.user.email,
            format=format,
            delivery_type="ebook"
        )
        if not palmknihy_link:
            messages.error(
                request,
                "Link není dostupný. Pokud je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a> nebo zkontrolujte svou objednávku v DIV.cz."
            )
            return redirect("book_detail", book_url=book.url)
        import tempfile, requests, os
        resp = requests.get(palmknihy_link)
        if resp.status_code != 200:
            messages.error(
                request,
                "Palmknihy - soubor není dostupný. Pokud je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            return redirect("book_detail", book_url=book.url)
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{format}") as tmp:
            tmp.write(resp.content)
            tmp_path = tmp.name
        file_to_attach = tmp_path
    else:
        filename = f"{book.url}.{format.lower()}"
        filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
        if not os.path.exists(filepath):
            messages.error(
                request,
                "Soubor s e-knihou není aktuálně dostupný. Pokud myslíte, že je to chyba, napište na <a href='mailto:info@div.cz'>info@div.cz</a>."
            )
            return redirect("book_detail", book_url=book.url)
        file_to_attach = filepath

    # Odeslání e-mailem (společné pro oba případy)
    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užij si čtení a nezapomeň ohodnotit na DIV.cz.\n\n Tým DIV.cz")

    with open(file_to_attach, 'rb') as f:
        mimetype, ext = get_mimetype_from_format(format)
        maintype, subtype = mimetype.split('/')
        msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(file_to_attach))

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)

    # Smaž temp soubor, pokud byl PALM
    if bookisbn.ISBNtype == "PALM" and file_to_attach:
        os.unlink(file_to_attach)

    # Úspěšná hláška vždy
    messages.success(
        request,
        f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>."
    )
    return redirect("book_detail", book_url=book.url)


'''
@login_required
def send_to_reader(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book


    if bookisbn.price == 0:
        purchase, created = Bookpurchase.objects.get_or_create(
            book=book,
            user=request.user,
            defaults={
                "status": "PAID",
                "price": 0,
                "format": bookisbn.format,
                "paymentdate": now(),
                "expirationdate": now().replace(year=now().year + 3),
            },
        )

    # povolení: pokud zdarma nebo uživatel zaplatil
    if bookisbn.price > 0:
        paid = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            status="PAID"
        ).exists()
        if not paid:
            raise Http404("Nemáte přístup k této e-knize.")

    mimetype, ext = get_mimetype_from_format(format)
    filename = f"{book.url}.{ext}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
    if not os.path.exists(filepath):
        raise Http404("Soubor nenalezen.")

    recipient = request.user.email

    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užijte si čtení.\n\n Tým DIV.cz")

    with open(filepath, 'rb') as f:
        maintype, subtype = get_mimetype_from_format(format)
        msg.add_attachment(f.read(), maintype=mimetype.split('/')[0], subtype=mimetype.split('/')[1], filename=filename)


    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)


    messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
    return redirect("book_detail", book_url=book.url)

'''

