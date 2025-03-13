import qrcode
import base64
from io import BytesIO

def generate_qr_code(book_id, format, amount, user):
    message = f"{format} - {book_id} - {user.username}"
    qr_string = f"SPD*1.0*ACC:CZ5620100000002602912559*AM:{amount}*CC:CZK*MSG:{message}*X-VS:{book_id}"
    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer)
    return base64.b64encode(buffer.getvalue()).decode()
