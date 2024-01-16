# VIEWS.BOOKS.PY

# https://console.cloud.google.com/welcome?project=knihy-div
import os
import requests

from django.shortcuts import get_object_or_404, render, redirect

from div_content.forms.books import BookAddForm
from div_content.models import Book, Bookauthor, Bookcomments, Bookcover, Bookisbn, Bookpublisher, Bookrating

from div_content.utils.books import fetch_books_from_google, fetch_book_from_google_by_id 
from dotenv import load_dotenv

load_dotenv()

def books(request):
    api_key = os.getenv('GOOGLE_API_KEY')
    api_test_message = "API klíč není nastaven" if not api_key else "API klíč je nastaven"

    try:
        books_from_api = fetch_books_from_google(api_key, "Harry Potter")  # Můžete změnit dotaz podle potřeby
        if not books_from_api:
            api_test_message += " | Nebyly získány žádné knihy z API"
        else:
            api_test_message += " | API funguje správně"
        top_20_books = Book.objects.order_by('-bookrating').all()[:20]
        all_books = books_from_api + list(top_20_books)
    except Exception as e:
        all_books = []
        api_test_message += " | Chyba při získávání dat z API: " + str(e)

    return render(request, 'books/books_list.html', {'all_books': all_books, 'api_test_message': api_test_message})





def book_detail(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    top_20_books = Book.objects.order_by('-bookrating').all()[:20]  # Define top_20_books here
    return render(request, 'books/book_detail.html', {'book': book, 'top_20_books': top_20_books})






def books_search(request):
    query = request.GET.get('query', '')  # Přečte parametr 'query' z GET požadavku
    if query:
        fetch_books_from_google(query)  # Načte knihy z Google Books
        books = Book.objects.filter(title__icontains=query)  # Filtruje knihy podle názvu
    else:
        books = []
    return render(request, 'books/books_search.html', {'books': books})


def book_add(request):
    form = BookAddForm(request.POST or None)
    book_data = None
    status_code = None
    api_response = None

    if request.method == 'POST' and form.is_valid():
        api_key = os.getenv('GOOGLE_API_KEY')
        identifier = form.cleaned_data['identifier']
        book_data, status_code, api_response = fetch_book_from_google_by_id(api_key, identifier)

    return render(request, 'books/book_add.html', {
        'form': form,
        'book_data': book_data,
        'status_code': status_code,
        'api_response': api_response
    })




