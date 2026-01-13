# -------------------------------------------------------------------
#                    UTILS.DIVKVARIAT.PY
# -------------------------------------------------------------------

# ------------------------------------------------------
# DIVKVARIAT – image tools (path + compression)
# ------------------------------------------------------

import time
from io import BytesIO

from PIL import Image, ExifTags
from django.core.files.base import ContentFile

#nepoužíva se
from django.shortcuts import render




# ------------------------------------------------------
# DIVKVARIAT – IMAGE UPLOAD + COMPRESSION
# ------------------------------------------------------


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
    img = Image.open(image_file)

    # --- AUTO ROTATE PODLE EXIF ---
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = img._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation)

            if orientation_value == 3:
                img = img.rotate(180, expand=True)
            elif orientation_value == 6:
                img = img.rotate(270, expand=True)
            elif orientation_value == 8:
                img = img.rotate(90, expand=True)
    except Exception:
        pass
    # -----------------------------

    img = img.convert("RGB")

    # Resize
    if img.width > max_width:
        ratio = max_width / img.width
        height = int(img.height * ratio)
        img = img.resize((max_width, height), Image.LANCZOS)

    # Save to buffer
    buffer = BytesIO()
    quality = 85
    img.save(buffer, format="JPEG", optimize=True, quality=quality)

    # Reduce quality until small enough
    while buffer.tell() > max_kb * 1024 and quality > 40:
        buffer = BytesIO()
        quality -= 5
        img.save(buffer, format="JPEG", optimize=True, quality=quality)

    return ContentFile(buffer.getvalue(), name=image_file.name)


# ------------------------------------------------------
# DIVKVARIAT – PLATFORM
# ------------------------------------------------------

PLATFORM_MAP = {
    "DIV": {
        "name": "DIV.cz",
        "domain": "https://div.cz",
        "antikvariat": "https://div.cz/antikvariat",
    },
    "DIVKVARIAT": {
        "name": "DIVkvariat.cz",
        "domain": "https://divkvariat.cz",
        "antikvariat": "https://divkvariat.cz",
    },
}

DEFAULT_PLATFORM = "DIVKVARIAT"


def get_platform(platform_code: str | None):
    code = (platform_code or DEFAULT_PLATFORM).upper()
    return PLATFORM_MAP.get(code, PLATFORM_MAP[DEFAULT_PLATFORM])


def get_antikvariat_url(platform_code: str | None):
    return get_platform(platform_code)["antikvariat"]


def get_domain(platform_code: str | None):
    return get_platform(platform_code)["domain"]

def get_listing_path(platform_code: str | None, book_url: str, listing_id: int, listing_type: str = "SELL") -> str:
    listing_type = (listing_type or "SELL").upper()
    book_url = (book_url or "").strip("/")
    action = "poptavka" if listing_type == "BUY" else "prodej"
    return f"/{book_url}/{action}/{listing_id}/"



# Nepoužíváme 
def get_listing_url(platform_code: str | None, book_url: str, listing_id: int, listing_type: str = "SELL") -> str:
    base = get_antikvariat_url(platform_code).rstrip("/")
    return f"{base}{get_listing_path(platform_code, book_url, listing_id, listing_type)}"


def get_book_url(platform_code: str | None, book_url: str) -> str:
    base = get_antikvariat_url(platform_code).rstrip("/")
    book_url = (book_url or "").strip("/")
    return f"{base}/{book_url}/"



