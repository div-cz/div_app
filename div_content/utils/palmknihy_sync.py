# utils/palmknihy_sync.py

import datetime
import unidecode
from div_content.models import Book, Bookisbn
from div_content.utils.palmknihy import get_catalog_product

def clean(text):
    return unidecode.unidecode(text.lower().strip()) if text else ""

def fetch_and_update_bookisbn(book):
    now = datetime.datetime.now()

    # Volat jen pokud je book.lastupdated starsi nez 7 dni nebo None
    if book.lastupdated and (now - book.lastupdated).days < 7:
        return None  # Není třeba kontrolovat

    # Existuje záznam v BookISBN?
    isbn_obj = Bookisbn.objects.filter(book=book).first()

    # Stáhni z Palmknihy
    ebooks = get_catalog_product(limit=300, available=True)

    for ebook in ebooks:
        title_match = clean(ebook.get("title")) == clean(book.title)
        authors_api = [clean(a.get("name")) for a in ebook.get("authors", [])]
        author_match = clean(book.author) in authors_api

        if title_match and author_match:
            price_from_api = ebook.get("current_valid_price", {}).get("price")
            isbn = ebook.get("isbn")

            if not isbn:
                break

            if isbn_obj:
                if isbn_obj.price != price_from_api:
                    isbn_obj.price = price_from_api
                isbn_obj.lastupdated = now
                isbn_obj.save()
            else:
                Bookisbn.objects.create(
                    isbn=isbn,
                    book=book,
                    format="epub",
                    language=ebook.get("language", "cs"),
                    description=ebook.get("summary", ""),
                    price=price_from_api,
                    lastupdated=now
                )
            break  # Úspěšně napárováno

    # I když nenajdeme nic, nastavíme lastupdated
    book.lastupdated = now
    book.save()

    return None
