# -------------------------------------------------------------------
#                    VIEWS.PAYMENTS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### variabilni symbol (metodika)
# ### funkce
# 
# bank_transactions            |
# generate_qr                  |
# get_mimetype_from_format     |
# check_payments_from_fio      |
# check_purchase_status        |
# get_ebook_purchase_status    |
# posledni_pending_purchaseid  |
# strip_diacritics             |
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# Vše co souvisí s platbami za eKnihy
# 
#
#
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------
import datetime
import io
import os
import qrcode
import re
import requests
import unicodedata

from decimal import Decimal

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from div_content.models import Book, Bookisbn, Booklisting, Bookpurchase
#from div_content.views.ebooks import 

from div_content.utils.palmknihy import get_catalog_product, get_palmknihy_download_url, get_token

# IMPORT VE FUNKCI GENERATE_QR
#from div_content.utils.palmknihy_sync import fetch_and_update_bookisbn 

from div_content.utils.payments import generate_qr_for_bookpurchase

from div_content.views.divkvariat import send_listing_payment_confirmation_email, send_listing_payment_email
from div_content.views.ebooks import generate_div_epub

from io import BytesIO


# -------------------------------------------------------------------
#                    KONSTANTY
# -------------------------------------------------------------------
FIO_API_URL = "https://fioapi.fio.cz/v1/rest/periods/"


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
# 0103859999  - Projekt DIV.cz (010), knihy (38), burza koupě (5), objednávka č. 9999 / poptávka
# 0103869999  - Projekt DIV.cz (010), knihy (38), burza prodej(6), objednávka č. 9999
#
# Každý projekt má svůj trojciferný kód (PPP), každý typ (TT) a formát (F) je určen tabulkou.
# NNNN je unikátní pro každou objednávku v daném projektu a typu.
#
# F: 0 = print, 1 = audio, 2 = epub, 3 = mobi, 4 = pdf, 5 = burza koupě, 6 = burza prodej
#
# Více informací o struktuře VS viz interní dokumentace nebo konzultuj s Martinem.
# =========================================================


# -------------------------------------------------------------------
# F:                 BANK TRANSACTIONS
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 GENERATE QR
# -------------------------------------------------------------------
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
    if getattr(bookisbn, "isbntype", "").upper() == "PALM":
        fetch_and_update_bookisbn(book)
    
    amount = bookisbn.price

    # 1. Vytvoř záznam o zamýšlené koupi
    user = request.user if request.user.is_authenticated else None

    palmknihy_id = bookisbn.sourceid if bookisbn.sourcetype == "PALM" else None
    
    purchase = Bookpurchase.objects.create(
        book=book,
        user=user,
        format=format,
        price=bookisbn.price,
        status="PENDING",
        sourcetype="PALM",
        sourceid=palmknihy_id,
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


# -------------------------------------------------------------------
# F:                 GET MIMETYPE FROM FORMAT
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 CHECK PAYMENTS FROM FIO
# -------------------------------------------------------------------
def check_payments_from_fio():
    token = os.getenv("FIO_TOKEN")
    if not token:
        print("Chybí FIO_TOKEN v env.")
        return

    today = datetime.date.today()
    ninety_days_ago = today - datetime.timedelta(days=1)
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
        # F: 0 = print, 1 = audio, 2 = epub, 3 = mobi, 4 = pdf, 5 = burza koupě, 6 = burza prodej
        # --- Booklisting (DIVkvariát) ---
        if fmt_num in ["5", "6"]:
            listing = Booklisting.objects.filter(booklistingid=int(suffix), status="RESERVED").first()
            if listing:
                listing.status = "PAID"
                listing.paymentdate = now()
                listing.paid_to_seller = False
                
                #listing.amount_to_seller = listing.price + listing.shipping - listing.commission
                price = listing.price or Decimal("0.00")
                shipping = listing.shipping or Decimal("0.00")
                commission = listing.commission or Decimal("0.00")

                listing.amount_to_seller = price + shipping - commission

                listing.request_payout = False
                listing.paymentdate = now()
                listing.save()
                print(f"✅ Platba spárována pro Booklisting {listing.booklistingid}")
                send_listing_payment_confirmation_email(listing)
                send_listing_payment_email(listing) 
                continue
            listing_paid = Booklisting.objects.filter(booklistingid=int(suffix), status="PAID").first()
            if listing_paid:
                print(f"VS {vs} (BooklistingID {suffix}) už je ve stavu PAID (dříve spárováno).")
            else:
                print(f"❌ Nenalezen Booklisting pro VS {vs}")
            continue

        # === Bookpurchase (eKniha) ===
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
                    purchase_paid = Bookpurchase.objects.filter(
                        purchaseid=int(suffix),
                        status="PAID"
                    ).first()
                    if purchase_paid:
                        print(f"VS {vs} (PurchaseID {suffix}) už je spárován a má status PAID.")
                    else:
                        print(f"❌ Nenalezen Bookpurchase pro VS {vs}")
                    continue

            if not purchase:
                print(f"❌ Nenalezen Bookpurchase pro VS {vs}")
                continue
            if float(purchase.price) == float(amount):
                purchase.status = "PAID"
                purchase.paymentdate = now()
                purchase.expirationdate = now().replace(year=now().year + 3)
                purchase.save()
                print(f"✅ Platba spárována a potvrzena pro VS {vs} (PurchaseID {purchase.purchaseid})")
                #---------
                # Pokud je formát EPUB a typ DIV, vygeneruj personalizovaný EPUB na druhém serveru:
                #---------
                if purchase.format.lower() == "epub":
                    bookisbn = Bookisbn.objects.filter(book=purchase.book, format=purchase.format).first()
                    if bookisbn and (bookisbn.ISBNtype or "").upper() == "DIV":
            
                        api_secret = os.getenv("EKULTURA_API_EPUB_SECRET")
						payload = {
							"token": api_secret,
							"book_slug": purchase.book.url,   # slug knihy
							"user_email": purchase.user.email if purchase.user else "",
							"order_id": str(purchase.purchaseid),
							"user_id": str(purchase.user.id if purchase.user else "000"),
							"with_watermark": True,
						}
						
						try:
							r = requests.post(
								"https://nakladatelstvi.ekultura.eu/api/epub2/api_generate.php",
								json=payload,
								timeout=60
							)
							if r.status_code == 200:
								print("✅ EPUB vygenerováno přes nové API!")
							else:
								print("❌ Chyba generování EPUB:", r.status_code, r.text)
						except Exception as e:
							print("❌ Výjimka při volání API generování EPUB:", e)
						
						# Hned poslat email (volání funkce z ebooks.py)
						from div_content.views.ebooks import send_ebook_paid_email
						send_ebook_paid_email(purchase)
			else:
                print(f"❌ Částka nesouhlasí pro VS {vs}: očekáváno {purchase.price}, přišlo {amount}")


# -------------------------------------------------------------------
# F:                 CHECK PURCHASE STATUS
# -------------------------------------------------------------------
@login_required
def check_purchase_status(request, purchase_id):
    try:
        purchase = Bookpurchase.objects.get(pk=purchase_id, user=request.user)
        return JsonResponse({"status": purchase.status})
    except Bookpurchase.DoesNotExist:
        return JsonResponse({"status": "NOT_FOUND"}, status=404)


# -------------------------------------------------------------------
# F:                 GET EBOOK PURCHASE STATUS
# -------------------------------------------------------------------
def get_ebook_purchase_status(user, book, ebook_formats):
    """
    Přidá ke každému formátu (epub/pdf/mobi...) hodnoty:
    - is_paid: True/False
    - show_qr: True/False
    - is_free_div: True/False
    - is_external_free: True/False
    """
    if not user.is_authenticated:
        for fmt, data in ebook_formats.items():
            sourcetype = (data.get("sourcetype") or "").upper()
            data['is_external_free'] = False
            if sourcetype in ["MLP", "PALM", "GUTENBERG"]:
                data['is_external_free'] = True
                continue  # externí zdroje necháváme jak jsou

            data['is_paid'] = False
            data['show_qr'] = data.get('price', 0) > 0
            data['is_free_div'] = sourcetype == 'DIV' and (data.get('price') == 0 or not data.get('price'))
        return ebook_formats

    paid_purchases = Bookpurchase.objects.filter(user=user, book=book, status="PAID")
    paid_formats = {p.format.lower() for p in paid_purchases}

    for fmt, data in ebook_formats.items():
        sourcetype = (data.get("sourcetype") or "").upper()
        data['is_external_free'] = False
        if sourcetype in ["MLP", "PALM", "GUTENBERG"]:
            data['is_external_free'] = True
            continue

        data['is_paid'] = fmt in paid_formats
        data['show_qr'] = data.get('price', 0) > 0 and not data['is_paid']
        data['is_free_div'] = sourcetype == 'DIV' and (data.get('price') == 0 or not data.get('price'))
    return ebook_formats




# -------------------------------------------------------------------
# F:                 POSLEDNI PENDING PURCHASEID
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 STRIP DIACRITICS
# -------------------------------------------------------------------
def strip_diacritics(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode('ascii')


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

# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------