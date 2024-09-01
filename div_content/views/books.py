# VIEWS.BOOKS.PY

# https://console.cloud.google.com/welcome?project=knihy-div
import os
import requests

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required

from div_content.forms.books import BookAddForm, Bookquoteform, SearchFormBooks, CommentFormBook
from div_content.models import (
    Book, Bookauthor, Bookcharacter, Bookcomments, Bookcover, Bookgenre, Bookisbn, 
    Bookpublisher, Bookquotes, Bookrating, Bookwriters, Charactermeta, Metagenre, Metaindex, Metastats,
    Userlisttype, Userlist, Userlistbook
                                )

from div_content.utils.books import fetch_books_from_google, fetch_book_from_google_by_id 
from dotenv import load_dotenv

load_dotenv()

def books(request):
    #api_key = os.getenv('GOOGLE_API_KEY')
    #api_test_message = "API klíč není nastaven" if not api_key else "API klíč je nastaven"

    #try:
        #books_from_api = fetch_books_from_google(api_key, "Harry Potter")  # Můžete změnit dotaz podle potřeby
        #if not books_from_api:
            #api_test_message += " | Nebyly získány žádné knihy z API"
        #else:
            #api_test_message += " | API funguje správně"
        #top_20_books = Book.objects.order_by('-bookrating').all()[:20]
        #top_20_books = Book.objects.order_by('-bookrating').values('bookid', 'img', 'url')[:20]

    top_books = Metaindex.objects.filter(section='Book').order_by('-popularity')[:20]
        #all_books = books_from_api + list(top_20_books)
    #except Exception as e:
        #all_books = []
        #api_test_message += " | Chyba při získávání dat z API: " + str(e)
    
    book_list_15 = Book.objects.filter(year__gt=2022)[:15]

    # Knihy podle popularity
    # book_list_15 = Metaindex.objects.filter(year__gt=2018).order_by("-popularity").values('title', 'url', 'img', 'description')[:15]

    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()

    return render(request, 'books/books_list.html', {
        'top_books': top_books,
        "book_list_15": book_list_15,
        'stats_book': stats_book,
        'stats_writters': stats_writters
        })
#'top_20_books': top_20_books, 'all_books': all_books, 'api_test_message': api_test_message




def book_detail(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    user = request.user
    comment_form = None

    genres = book.bookgenre_set.all()[:3]
    
    # Fetch authors associated with the book
    authors = Bookauthor.objects.filter(
        authorid__in=Bookwriters.objects.filter(book_id=book.bookid).values_list('author_id', flat=True)
    )
     #Fetch characters associated with the book
    characters_with_roles = Bookcharacter.objects.filter(bookid=book.bookid).select_related('characterid')

    # Fetch quotes associated with the book
    quotes = Bookquotes.objects.filter(bookid=book)

    # Initialize the quote form
    if user.is_authenticated:
        if request.method == 'POST' and 'quote' in request.POST:
            quote_form = Bookquoteform(request.POST, bookid=book.bookid)
            if quote_form.is_valid():
                new_quote = quote_form.save(commit=False)
                new_quote.bookid = book
                new_quote.user = request.user
                new_quote.authorid = book.authorid 
                new_quote.save()
                return redirect('book_detail', book_url=book_url)
        else:
            quote_form = Bookquoteform(bookid=book.bookid)
    else:
        quote_form = None

    # Zjistí, jestli má uživatel knihu v seznamu Oblíbené
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=4)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistbook.objects.filter(book__bookid=book.bookid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel knihu v seznamu Chci číst
    if user.is_authenticated:
        try:
            readlist_type = Userlisttype.objects.get(userlisttypeid=5)
            readlist_list = Userlist.objects.get(user=user, listtype=readlist_type)
            is_in_readlist = Userlistbook.objects.filter(book__bookid=book.bookid, userlist=readlist_list).exists()
        except Exception as e:
            is_in_readlist = False
    else:
        is_in_readlist = False

    # Zjistí, jestli má uživatel knihu v seznamu Přečteno
    if user.is_authenticated:
        try:
            read_type = Userlisttype.objects.get(userlisttypeid=6)
            read_list = Userlist.objects.get(user=user, listtype=read_type)
            is_in_read_books = Userlistbook.objects.filter(book__bookid=book.bookid, userlist=read_list).exists()
        except Exception as e:
            is_in_read_books = False
    else:
        is_in_read_books = False
    
    # Zjistí, jestli má uživatel knihu v seznamu Knihovna
    if user.is_authenticated:
        try:
            library_type = Userlisttype.objects.get(userlisttypeid=10)
            library_list = Userlist.objects.get(user=user, listtype=library_type)
            is_in_book_library = Userlistbook.objects.filter(book__bookid=book.bookid, userlist=library_list).exists()
        except Exception as e:
            is_in_book_library = False
    else:
        is_in_book_library = False
    
    if user.is_authenticated:
        if 'comment' in request.POST:
                comment_form = CommentFormBook(request.POST)
                if comment_form.is_valid():
                    comment = comment_form.cleaned_data['comment']
                    Bookcomments.objects.create(comment=comment, bookid=book, user=request.user)
                    return redirect('book_detail', book_url=book_url)
                else:
                    print(comment_form.errors)
        else:
            comment_form = CommentFormBook(request=request)

    comments = Bookcomments.objects.filter(bookid=book).order_by('-commentid')

    return render(request, 'books/book_detail.html', {
        'book': book,
        'authors': authors, 
        'genres': genres, 
        "comment_form": comment_form,
        "comments": comments,
        'characters_with_roles': characters_with_roles,
        'quotes': quotes,
        'quote_form': quote_form,
        "is_in_favourites": is_in_favourites,
        "is_in_readlist": is_in_readlist,
        "is_in_read_books": is_in_read_books,
        "is_in_book_library": is_in_book_library
        })
#    top_20_books = Book.objects.order_by('-bookrating').all()[:20]  # Define top_20_books here
    #'top_20_books': top_20_books



def books_search(request):
    books = None
    if 'q' in request.GET:
        form = SearchFormBooks(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            books = (Book.objects.filter(title__icontains=query)
                .values('title', 'url', 'year', 'googleid', 'pages', 'author')[:50])
    else:
        form = SearchFormBooks()

    return render(request, 'books/books_search.html', {'form': form, 'books': books})





#def books_search(request):
#    query = request.GET.get('query', '')  # Přečte parametr 'query' z GET požadavku
#    q = forms.CharField(label='Search', max_length=100)
#    return render(request, 'books/books_search.html', {'books': books})


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


# Přidat do sezanmu: Oblíbené knihy
@login_required
def add_to_favourite_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=4)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistbook.objects.filter(userlist=favourites_list, book=book).exists():
        print("already in favourites")
    else:
        Userlistbook.objects.create(userlist=favourites_list, book=book)
        print("new list created")
    
    return redirect("book_detail", book_url=book.url)

# # Přidat do seznamu: Chci číst
@login_required
def add_to_readlist(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    readlist_type = Userlisttype.objects.get(userlisttypeid=5)
    readlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=readlist_type)

    if Userlistbook.objects.filter(userlist=readlist_list, book=book).exists():
        print("already in favourites")
    else:
        Userlistbook.objects.create(userlist=readlist_list, book=book)
        print("new list created")
    
    return redirect("book_detail", book_url=book.url)   

# Přidat do seznamu: Přečteno
@login_required
def add_to_read_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    read_type = Userlisttype.objects.get(userlisttypeid=6)
    read_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=read_type)

    if Userlistbook.objects.filter(userlist=read_list, book=book).exists():
        print("already in favourites")
    else:
        Userlistbook.objects.create(userlist=read_list, book=book)
        print("new list created")
    
    return redirect("book_detail", book_url=book.url)   

# Přidat do seznamu: Knihovna
@login_required
def add_to_book_library(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    library_type = Userlisttype.objects.get(userlisttypeid=10)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)

    if Userlistbook.objects.filter(userlist=library_list, book=book).exists():
        print("already in favourites")
    else:
        Userlistbook.objects.create(userlist=library_list, book=book)
        print("new list created")
    
    return redirect("book_detail", book_url=book.url) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourites_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=4)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlistbook = Userlistbook.objects.get(book=book, userlist=favourites_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)

# Smazat ze seznamu: Chci číst
@login_required
def remove_from_readlist(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    readlist_type = Userlisttype.objects.get(userlisttypeid=5)
    readlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=readlist_type)
    userlistbook = Userlistbook.objects.get(book=book, userlist=readlist_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# Smazat ze seznamu: Přečteno
@login_required
def remove_from_read_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    read_type = Userlisttype.objects.get(userlisttypeid=6)
    read_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=read_type)
    userlistbook = Userlistbook.objects.get(book=book, userlist=read_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# Smazat ze seznamu: Knihovna
@login_required
def remove_from_book_library(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    library_type = Userlisttype.objects.get(userlisttypeid=10)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)
    userlistbook = Userlistbook.objects.get(book=book, userlist=library_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)
