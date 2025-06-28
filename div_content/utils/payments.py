#utils.payments

import qrcode
import base64
import unicodedata
from io import BytesIO






def generate_qr(request, book_id, format):
    # Ovìøení, zda existuje kniha a formát v databázi Bookisbn
    book_isbn = Bookisbn.objects.select_related('book').filter(book=book_id, format=format).first()
    if not book_isbn or not book_isbn.price:
        return HttpResponse(status=404)

    # Získání uživatele
    user = request.user if request.user.is_authenticated else None

    # Získání nebo vytvoøení PENDING purchase
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

    # Normalizovaná zpráva
    msg = unicodedata.normalize(
        'NFKD',
        f"{book_isbn.book.titlecz or book_isbn.book.title}-{book_isbn.book.pk}-{format}"
    ).encode('ascii', 'ignore').decode('ascii').replace(" ", "")

    # QR kód jako platba
    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(book_isbn.price):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg}"
        f"*X-VS:{purchase.purchaseid}"
    )

    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return HttpResponse(buffer.getvalue(), content_type="image/png")






# používáme v views.books.py
# QR
def qr_code_ebook(purchase):
    msg = unicodedata.normalize(
        'NFKD',
        f"{purchase.book.titlecz or purchase.book.title}-{purchase.book.pk}-{purchase.format}"
    ).encode('ascii', 'ignore').decode('ascii').replace(" ", "")
    qr_string = (
        f"SPD*1.0*ACC:CZ5620100000002602912559"
        f"*AM:{float(purchase.price):.2f}"
        f"*CC:CZK"
        f"*MSG:{msg}"
        f"*X-VS:{purchase.purchaseid}"
    )
    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode()



def qr_code_market(amount, vs, message):
    qr_string = f"SPD*1.0*ACC:CZ5620100000002602912559*AM:{amount}*CC:CZK*MSG:{message}*X-VS:{vs}"
    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()




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