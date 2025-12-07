# -------------------------------------------------------------------
#                    UTILS.DIVKVARIAT.PY
# -------------------------------------------------------------------

# ------------------------------------------------------
# DIVKVARIAT – image tools (path + compression)
# ------------------------------------------------------

import time
from PIL import Image
from django.core.files.base import ContentFile
from io import BytesIO
import time



# ------------------------------------------------------
# DIVKVARIAT – IMAGE UPLOAD + COMPRESSION
# ------------------------------------------------------

import time
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile


def listing_image_path(instance, filename):
    """
    Výsledná cesta:
    divkvariat/YYYY/MM/listing-123-user-55-1700000000.jpg
    """
    ext = filename.split('.')[-1].lower()
    ts = int(time.time())
    return (
        f"divkvariat/{time.strftime('%Y/%m')}/"
        f"listing-{instance.listing.booklistingid}-user-{instance.listing.user.id}-{ts}.{ext}"
    )


def compress_image(image_file, max_kb=400, max_width=1600):
    """Komprese do JPEG, max 400 KB / max_width 1600px."""
    img = Image.open(image_file)
    img = img.convert("RGB")

    # Resize
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    buffer = BytesIO()
    quality = 85
    img.save(buffer, format="JPEG", quality=quality, optimize=True)

    # Komprese dokud nepodlezeme max_kb
    while buffer.tell() > max_kb * 1024 and quality > 40:
        buffer = BytesIO()
        quality -= 5
        img.save(buffer, format="JPEG", quality=quality, optimize=True)

    return ContentFile(buffer.getvalue())



