# UTILS.BOOKS


import requests
import logging

from div_content.models import Book, Booklisting

logger = logging.getLogger(__name__)



def get_market_listings(limit=5):
    sell_listings = Booklisting.objects.filter(
        listingtype__in=['SELL', 'GIVE'], 
        active=True,
        status='ACTIVE'
    ).select_related('book', 'user').order_by('-createdat')[:limit]
    
    buy_listings = Booklisting.objects.filter(
        listingtype='BUY', 
        active=True,
        status='ACTIVE'
    ).select_related('book', 'user').order_by('-createdat')[:limit]
    
    return sell_listings, buy_listings





def fetch_books_from_google(api_key, query):
    if not api_key:
        logger.error("Google API key is missing or not loaded correctly.")
        return []

    books = []
    url = f'https://www.googleapis.com/books/v1/volumes?q={query}&key={api_key}'
    response = requests.get(url)

    if response.status_code != 200:
        logger.error(f"Failed to fetch from Google Books API: Status Code {response.status_code}")
        return []

    try:
        data = response.json()
        for book in data.get('items', []):
            books.append({
                'title': book['volumeInfo'].get('title', 'Unknown Title'),
                'author': book['volumeInfo'].get('authors', ['Unknown Author'])[0],
                'pub_year': book['volumeInfo'].get('publishedDate', 'Unknown Year'),
                'genre': book['volumeInfo'].get('categories', ['Unknown Genre'])[0],
            })
    except Exception as e:
        logger.error(f"Error processing the API response: {e}")

    return books



def fetch_book_from_google_by_id(api_key, identifier):
    query_param = 'isbn:' + identifier if identifier.replace('-', '').isdigit() else identifier
    query_url = f'https://www.googleapis.com/books/v1/volumes?q={query_param}&key={api_key}'

    response = requests.get(query_url)
    status_code = response.status_code
    api_response = response.json()

    if status_code != 200 or 'items' not in api_response:
        return None, status_code, api_response  # Vrací None pro data knihy, stavový kód a odpověď API

    book_data = api_response['items'][0]['volumeInfo']
    return book_data, status_code, api_response  
