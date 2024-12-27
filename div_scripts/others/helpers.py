import django
import os
import requests
from django.http import JsonResponse,HttpRequest
from django.conf import settings
from asgiref.sync import async_to_sync
from typing import Optional
from div_content.models import Bookisbn,Book
from .updated.db_pool import create_db_pool
from .unique_url_v3 import get_uniqueurl_v2,clean_character_name as clean



os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'div_config.settings')
django.setup()

db_config = {
    'user': settings.DATABASES['default']['USER'],
    'password': settings.DATABASES['default']['PASSWORD'],
    'host': settings.DATABASES['default']['HOST'],
    'database': settings.DATABASES['default']['NAME'],
    'port': int(settings.DATABASES['default']['PORT']),
 }
def check_isbn_exists(request: HttpRequest) -> JsonResponse:
    """
    check for existence of isbn
    """
    isbn = request.GET.get('isbn', None)
    if isbn:
        exists = Bookisbn.objects.filter(isbn=isbn).exists()
        return JsonResponse({'exists': exists})
    return JsonResponse({'exists': False})

def check_book_exists(request: HttpRequest) -> JsonResponse:
    """
    check for existence of pair title amd author, exclude authors already added for another book authors
    """
    title = request.GET.get('title')
    authorid = request.GET.get('authorid')
    exclude_book_id = request.GET.get('exclude_book_id')

    # Přidej základní kontrolu na vstupy
    if not title or not authorid:
        return JsonResponse({'error': 'Missing title or authorid'}, status=400)

    try:
        books = Book.objects.filter(title=title, authorid=authorid)
        if exclude_book_id:
            books = books.exclude(bookid=exclude_book_id)

        if books.exists():
            return JsonResponse({'exists': True})

        return JsonResponse({'exists': False})

    except Exception as e:
        print(f"Error in check_book_exists: {e}")
        return JsonResponse({'error': 'Something went wrong'}, status=500)

async def get_unique_url(title:str, table_name:str, column_name:str, year:Optional[int]=None) -> str:
    """
    fuction creaters database pool and returns  unique url for title with table and column name. year is optional if added
    """
    db_pool = await create_db_pool(db_config)
    async with db_pool.acquire() as conn:
        unique_url = await get_uniqueurl_v2(conn,title, table_name, column_name, year)
    return unique_url

def clean_character_name_sync(character_name: str) -> str:
    """
    Call the asynchronous clean_character_name function in a synchronous environment.

    Args:
        character_name (str): The character name to clean.

    Returns:
        str: The cleaned character name.
    """
    return async_to_sync(clean)(character_name)