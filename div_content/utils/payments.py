# -------------------------------------------------------------------
#                    UTILS.PAYMENTS.PY
# -------------------------------------------------------------------


import base64
import qrcode
import unicodedata

from io import BytesIO

from django.http import HttpResponse

# -------------------------------------------------------------------
#                    OBSAH
# generate_qr_for_bookpurchase
# get_mimetype_from_format
# prepare_qr_codes_for_book
# qr_code_ebook
# qr_code_market
# 
# -------------------------------------------------------------------

# Generuje finalní kod views.payments.py
def generate_qr_for_bookpurchase(purchase, book, user):
    format_code = {"epub": "2", "mobi": "3", "pdf": "4"}.get(purchase.format.lower(), "9")
    vs = f"01038{format_code}{str(purchase.purchaseid).zfill(4)}"
    username = user.username if user and hasattr(user, "username") else "anon"
    msg = f"{book.titlecz or book.title}-{purchase.format}-{username}-DIVcz"
    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii').replace(" ", "")
    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(purchase.price):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg.replace('=', ':')}"
        f"*X-VS:{vs}"
    )
    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return HttpResponse(buffer.getvalue(), content_type="image/png")



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



def prepare_qr_codes_for_book(user, book, ebook_formats):
    from div_content.models import Bookpurchase

    qr_codes = {}

    if not user.is_authenticated:
        return qr_codes

    pending_purchases = {
        p.format.lower(): p
        for p in Bookpurchase.objects.filter(user=user, book=book, status="PENDING")
    }

    for fmt, data in ebook_formats.items():
        if data["available"] and data["price"]:
            if fmt not in pending_purchases:
                purchase, _ = Bookpurchase.objects.get_or_create(
                    user=user,
                    book=book,
                    format=fmt.upper(),
                    status="PENDING",
                    defaults={"price": data["price"]}
                )
                pending_purchases[fmt] = purchase
            qr_codes[fmt] = qr_code_ebook(pending_purchases[fmt])

    return qr_codes


"""
def generate_qr(request, book_id, format):
    FORMAT_MAPPING = {
        'epub': '2',
        'mobi': '3',
        'pdf': '4',
        'print': '0',
        'audio': '1',
        'burza_koupe': '5',
        'burza_prodej': '6'
    }

    book_isbn = Bookisbn.objects.select_related('book').filter(book=book_id, format=format).first()
    if not book_isbn or not book_isbn.price:
        return HttpResponse(status=404)

    user = request.user if request.user.is_authenticated else None

    purchase = Bookpurchase.objects.filter(
        book=book_isbn.book,
        user=user,
        format=format,
        status="PENDING"
    ).first()

    if not purchase:
        purchase = Bookpurchase.objects.create(
            book=book_isbn.book,
            user=user,
            format=format,
            price=book_isbn.price,
            status="PENDING",
        )
    # --- TVŮJ VS --- #
    form_num = FORMAT_MAPPING.get(format, '0')   # fallback je '0'
    vs = f"01038{form_num}{str(purchase.purchaseid).zfill(4)[-4:]}"  # vždy poslední 4 čísla

    username = purchase.user.username if purchase.user and hasattr(purchase.user, "username") else "anon"
    msg = f"{purchase.book.titlecz or purchase.book.title}-{purchase.format}-{username}-DIVcz"
    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii').replace(" ", "")


    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(book_isbn.price):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg}"
        f"*X-VS:{vs}"
    )

    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")
"""





# používáme v views.books.py ?? asi se používá views.payments generace_qr na radku 99
# QR
def qr_code_ebook(purchase):

    username = purchase.user.username if purchase.user and hasattr(purchase.user, "username") else "anon"
    msg = f"{purchase.book.titlecz or purchase.book.title}-{purchase.format}-{username}-DIVcz-2"
    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii').replace(" ", "")


    format_code = {
        "epub": "2",
        "mobi": "3",
        "pdf": "4",
    }.get(purchase.format.lower(), "9")
    vs = f"01038{format_code}{str(purchase.purchaseid).zfill(4)}"

    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(purchase.price):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg}"
        f"*X-VS:{vs}"
    )
    # VS = 10138 - další číslo je  1 = audio, 2 = epub, 3 = mobi, 4 = pdf, 5 = burza koupě, 6 = burza prodej
    # poslední čtyří čísla jsou poslední čtyří id z bookpurchase/booklisting
    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()



def qr_code_market(amount, listing, message=None, format_code="5"):
    username = listing.user.username if hasattr(listing.user, "username") else "anon"
    
    msg = message or f"{listing.book.titlecz or listing.book.title}-{listing.listingtype}-{username}-DIVcz-{format_code}"
    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii').replace(" ", "")
    
    vs = f"01038{format_code}{str(listing.booklistingid).zfill(4)[-4:]}"  

    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(amount):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg}"
        f"*X-VS:{vs}"
    )

    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_code_base64, vs






