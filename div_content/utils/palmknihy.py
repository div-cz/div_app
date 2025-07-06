# utils/palmknihy.py

import datetime
import json
import os
import re
import requests
import unicodedata

from div_content.models import Book, Bookisbn
from div_content.utils.functions import normalize_isbn, format_isbn

from dotenv import load_dotenv, find_dotenv
print("Načítám .env ze souboru:", find_dotenv())
load_dotenv()


API_BASE_URL = os.getenv("PALMKNIHY_API_URL")
CLIENT_ID = os.getenv("PALMKNIHY_CLIENT_ID")
CLIENT_SECRET = os.getenv("PALMKNIHY_CLIENT_SECRET")


AUTH_URL = f"{API_BASE_URL}/auth"

def normalize(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^a-zA-Z0-9]+', '', text).lower()
    return text


def get_token():
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(AUTH_URL, data=data)
    result = response.json()

    print("&#128274; Odpověď z token endpointu:", result)

    # Token
    if "data" not in result or "token" not in result["data"]:
        raise Exception("&#10060; Token se nepodařilo načíst – chybí pole 'data.token'.")

    return result["data"]["token"]





def get_product_by_isbn(isbn):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{API_BASE_URL}/catalog/product/{isbn}"
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_product_by_id(product_id):
    token = get_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }
    url = f"{API_BASE_URL}/catalog/product/{product_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()


def get_catalog_product(limit=100, page=1, available=True, product_type="ebook"):
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "limit": limit,
        "page": page,
        "available": str(available).lower(),
        "type": product_type
    }
    response = requests.get(f"{API_BASE_URL}/catalog/product", headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("data", [])


def get_all_palmknihy_products():
    page = 1
    all_books = []
    while True:
        books = get_catalog_product(limit=100, page=page)
        if not books:
            break
        all_books.extend(books)
        page += 1
    return all_books




def get_palmknihy_download_url(palmknihyid, purchaseid, user_id, email, format, delivery_type="ebook"):
    token = get_token() 
    endpoint = os.getenv("PALMKNIHY_API_URL") + "/partner/provision"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-AM-Consumer-Key": os.getenv("PALMKNIHY_CLIENT_ID")
    }
    data = {
        "product_id": palmknihyid,
        "order_id": str(purchaseid),
        "purchase_date": datetime.datetime.now().isoformat(),  # doplň aktuální datum
        "delivery_type": delivery_type,
        "delivery_email": email,
        "format": format.lower()  # zkusit, jestli provision API podporuje tento parametr
    }
    print("PALMKNIHY PROVISION REQ:", json.dumps(data, indent=2))
    response = requests.post(endpoint, json=data, headers=headers, timeout=10)
    print("PALMKNIHY PROVISION RESPONSE:", response.status_code, response.text)
    if response.status_code == 200:
        return response.json().get("download_url") or response.json().get("link")
    return None






def match_and_store_ebooks():
    palmknihy_books = get_all_palmknihy_products()
    unknown_book = Book.objects.get(pk=1)  # fallback kniha

    for pbook in palmknihy_books:
        title = pbook.get("title", "")
        authors = pbook.get("authors", [])
        author_name = authors[0]["name"] if authors else "Neznámý autor"
        isbn = normalize_isbn(pbook.get("isbn"))
        format_type = pbook.get("spec_ebook-type", "").lower()
        price = pbook.get("current_valid_price", {}).get("price")

        if not isbn or not format_type:
            continue

        # Normalizuj pro porovnání
        norm_title = normalize(title)
        norm_author = normalize(author_name)

        # Najdi odpovídající Book
        match = Book.objects.filter(
            titlecz__isnull=False,
        ).annotate(
            norm_title=models.Func(models.F("titlecz"), function='LOWER')
        ).filter(
            norm_title__icontains=norm_title[:10]  # fuzzy match
        ).first()

        book = match if match else unknown_book

        # Ulož nebo aktualizuj BookISBN
        Bookisbn.objects.update_or_create(
            isbn=isbn,
            defaults={
                "book": book,
                "format": format_type,
                "price": price or None,
                "language": pbook.get("language", "cs"),
                "description": pbook.get("description", "")[:500],  # safe truncation
            }
        )