# views.payments.py 

import datetime
import io
import os
import smtplib
from decimal import Decimal

import qrcode
import requests

from email.message import EmailMessage

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.timezone import now
from django.views.decorators.http import require_POST

from div_content.models import Book, Bookisbn, Bookpurchase
from div_content.utils.palmknihy import get_catalog_product
from div_content.utils.palmknihy_sync import fetch_and_update_bookisbn





FIO_API_URL = "https://www.fio.cz/ib_api/rest/"


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





# QR kod pro zaplaceni konkretni e-knihy ve formatu SPD (FIO)
def generate_qr(request, book_id, format):
    book = get_object_or_404(Book, pk=book_id)
    fetch_and_update_bookisbn(book)  # vzdy kontroluj aktualni cenu

    bookisbn = Bookisbn.objects.filter(book=book).first()
    if not bookisbn or not bookisbn.price:
        raise Http404("E-kniha není dostupná nebo nemá cenu.")

    # vytvor zaznam o zamyslene koupi
    purchase = Bookpurchase.objects.create(
        book=book,
        user=request.user if request.user.is_authenticated else None,
        format=format,
        price=bookisbn.price,
        status="PENDING",
        createdat=now(),
    )

    vs = str(purchase.purchaseid)
    msg = f"ebook-{book.bookid}-{format}"

    # SPD format pro FIO
    amount = f"{Decimal(bookisbn.price):.2f}"
    qr_text = f"SPD*1.0*ACC:CZ1234567890123456789012*AM:{amount}*CC:CZK*MSG:{msg}*X-VS:{vs}"

    img = qrcode.make(qr_text)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")



def check_payments():
    """FIO API"""
    token = "FIO_TOKEN"  # Uloženo v .env
    response = requests.get(f"{FIO_API_URL}last/{token}/transactions.json")
    
    if response.status_code == 200:
        transactions = response.json().get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
        
        for tx in transactions:
            vs = tx.get("variableSymbol")
            amount = tx.get("amount")
            
            # Platbu podle VS
            purchase = Bookpurchase.objects.filter(purchaseid=vs, status="PENDING").first()
            if purchase and float(purchase.price) == float(amount):
                purchase.status = "PAID"
                purchase.paymentdate = now()
                purchase.expirationdate = now().replace(year=now().year + 3)  # Platnost 3 roky
                purchase.save()

                print(f"Platba potvrzena pro ID {vs}")

    return "Kontrola dokončena"




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





# Stáhnout e-knihu – zdarma nebo po zaplacení
@login_required
def download_ebook(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    # kontrola: zdarma nebo uživatel zaplatil
    if bookisbn.price == 0:
        allowed = True
    else:
        allowed = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            status="PAID"
        ).exists()

    if not allowed:
        raise Http404("Nemáte oprávnění k této e-knize.")

    # cesta k souboru – předpokládá se název podle URL knihy
    filename = f"{book.url}.{format.lower()}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)

    if not os.path.exists(filepath):
        raise Http404("Soubor nebyl nalezen.")

    with open(filepath, "rb") as f:
        response = HttpResponse(f.read(), content_type="application/pdf")
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response




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
    return redirect("book_detail", book_url=book.url)




@login_required
def send_to_reader(request, isbn, format):
    bookisbn = get_object_or_404(Bookisbn, isbn=isbn)
    book = bookisbn.book

    if request.method == "POST":
        kindlemail = request.POST.get("kindlemail") or request.user.email
        # Ulož do bookpurchase!
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
            },
        )
        # Pokud už existuje, případně aktualizuj e-mail (volitelné)
        if not created and not purchase.kindlemail:
            purchase.kindlemail = kindlemail
            purchase.save()
    else:
        # Pokud GET, zobraz formulář!
        # Ideálně renderuj modal (nebo přesměruj) s formulářem
        return render(request, "books/send_to_reader_email.html", {"isbn": isbn, "format": format, "user": request.user})

    # --- Teprve pak pokračuj odesláním e-mailu ---
    #recipient = purchase.kindlemail or request.user.email

    # >>> or request.user.email <<<
    recipient = purchase.kindlemail 

    mimetype, ext = get_mimetype_from_format(format)
    filename = f"{book.url}.{ext}"
    filepath = os.path.join(os.getenv("FREE_EBOOKS_PATH"), filename)
    if not os.path.exists(filepath):
        raise Http404("Soubor nenalezen.")

    msg = EmailMessage()
    msg['Subject'] = f"E-kniha z DIV.cz: {book.title}"
    msg['From'] = os.getenv("EBOOK_SENDER_ADDRESS")
    msg['To'] = recipient
    msg.set_content("Vaše e-kniha je v příloze. Užij si čtení a nezapomeň ohodnotit na DIV.cz.\n\n Tým DIV.cz")

    with open(filepath, 'rb') as f:
        maintype, subtype = get_mimetype_from_format(format)
        msg.add_attachment(f.read(), maintype=mimetype.split('/')[0], subtype=mimetype.split('/')[1], filename=filename)

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("EBOOK_SENDER_ADDRESS"), os.getenv("EBOOK_SENDER_PASSWORD"))
        smtp.send_message(msg)

    messages.success(request, f"E-kniha <strong>{book.title}</strong> byla odeslána do vaší čtečky na e-mail <strong>{recipient}</strong>.")
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

