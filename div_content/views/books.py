from django.shortcuts import get_object_or_404, render
from div_content.models import Game



def books(request):
    books = Book.objects.all()
    return render(request, 'books/books_list.html', {'books': books})

def book_detail(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    return render(request, 'books/book_detail.html', {'book': book})


