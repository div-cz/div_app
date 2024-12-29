# VIEWS.BOOKS.PY TEST

# https://console.cloud.google.com/welcome?project=knihy-div
import datetime
import os
import requests

from django.contrib.auth.decorators import login_required

from django.contrib.contenttypes.models import ContentType


from django.db.models import Avg

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from dotenv import load_dotenv

from div_content.forms.books import BookAddForm, BookDivRatingForm, BookCharacterForm, Bookquoteform, CommentFormBook, SearchFormBooks
from div_content.models import (
    Book, Bookauthor, Bookcharacter, Bookcomments, Bookcover, Bookgenre, Bookisbn, 
    Bookpublisher, Bookquotes, Bookrating, Bookwriters, Charactermeta, Metagenre, Metaindex, Metastats,
    Userlist, Userlistbook, Userlisttype, FavoriteSum, Userbookgoal, Userlistitem
)
#from div_content.utils.books import fetch_book_from_google_by_id, fetch_books_from_google


load_dotenv()
from div_content.views.login import custom_login_view

from star_ratings.models import Rating, UserRating

from django.db.models import Avg, Count
import math
from django.contrib import messages
from datetime import datetime


# Konstanty
USERLISTTYPE_FAVORITE_BOOK_ID = 4 # Oblíbená kniha
USERLISTTYPE_READLIST_ID = 5 # Chci číst
USERLISTTYPE_READ_BOOKS_ID = 6 # Přečteno
USERLISTTYPE_BOOK_LIBRARY_ID = 10 # Knihovna

CONTENT_TYPE_BOOK_ID = 9



def get_reading_goal(request):
    current_year = datetime.now().year
    user_goal = Userbookgoal.objects.filter(
        user=request.user,
        goalyear=current_year
    ).first()
    
    if not user_goal:
        # Vytvoříme nový cíl pokud neexistuje
        user_goal = Userbookgoal.objects.create(
            user=request.user,
            goalyear=current_year,
            goal=0,
            booksread=0
        )
    
    # Spočítáme skutečný počet přečtených knih
    read_list = Userlist.objects.filter(
        user=request.user,
        listtype_id=6,  # ID pro "přečtené" knihy
        createdat__year=current_year
    ).first()
    
    if read_list:
        books_read = Userlistitem.objects.filter(
            userlist=read_list,
            addedat__year=current_year
        ).count()
        
        # Aktualizujeme počet přečtených knih
        user_goal.booksread = books_read
        user_goal.save()
        if user_goal.goal > 0:
            user_goal.progress = round((user_goal.booksread * 100) / user_goal.goal, 1)
        else:
            user_goal.progress = 0
    
     # Zajistíme správný formát s tečkou
        user_goal.progress = f"{user_goal.progress:.1f}".replace(",", ".")

    return user_goal

@login_required
def set_reading_goal(request):
    if request.method == 'POST':
        goal = request.POST.get('goal')
        if goal and goal.isdigit():
            current_year = datetime.now().year
            user_goal, created = Userbookgoal.objects.get_or_create(
                user=request.user,
                goalyear=current_year,
                defaults={'goal': int(goal)}
            )
            if not created:
                user_goal.goal = int(goal)
                user_goal.save()
            messages.success(request, f'Čtenářský cíl pro rok {current_year} byl nastaven na {goal} knih!')
        
    return redirect('books_index')  # Ujistěte se, že 'books' je správný name v urls.py



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

    top_books = Book.objects.order_by('-divrating')[:10]
        #all_books = books_from_api + list(top_20_books)
    #except Exception as e:
        #all_books = []
        #api_test_message += " | Chyba při získávání dat z API: " + str(e)
    

    book_list_15 = Book.objects.filter(year__gt=2022).order_by('-divrating')[10:35]


    # Knihy podle popularity
    # book_list_15 = Metaindex.objects.filter(year__gt=2018).order_by("-popularity").values('title', 'url', 'img', 'description')[:15]

    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()



    reading_goal = None
    if request.user.is_authenticated:
        reading_goal = get_reading_goal(request)
    


    return render(request, 'books/books_list.html', {
        'top_books': top_books,
        "book_list_15": book_list_15,
        'stats_book': stats_book,

        'stats_writters': stats_writters,
        'reading_goal': reading_goal

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

            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_BOOK_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=book.bookid, userlist=favourites_list).exists()

        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel knihu v seznamu Chci číst
    if user.is_authenticated:
        try:

            readlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READLIST_ID)
            readlist_list = Userlist.objects.get(user=user, listtype=readlist_type)
            is_in_readlist = Userlistitem.objects.filter(object_id=book.bookid, userlist=readlist_list).exists()

        except Exception as e:
            is_in_readlist = False
    else:
        is_in_readlist = False

    # Zjistí, jestli má uživatel knihu v seznamu Přečteno
    if user.is_authenticated:
        try:

            read_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READ_BOOKS_ID)
            read_list = Userlist.objects.get(user=user, listtype=read_type)
            is_in_read_books = Userlistitem.objects.filter(object_id=book.bookid, userlist=read_list).exists()

        except Exception as e:
            is_in_read_books = False
    else:
        is_in_read_books = False
    
    # Zjistí, jestli má uživatel knihu v seznamu Knihovna
    if user.is_authenticated:
        try:

            library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_BOOK_LIBRARY_ID)
            library_list = Userlist.objects.get(user=user, listtype=library_type)
            is_in_book_library = Userlistitem.objects.filter(object_id=book.bookid, userlist=library_list).exists()

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




    # Fetch book ratings
    book_content_type = ContentType.objects.get_for_model(Book)
    ratings = UserRating.objects.filter(rating__content_type=book_content_type, rating__object_id=book.bookid)

    # Calculate average rating
    average_rating_result = ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result.get('average')

    if average_rating is not None:
        average_rating = math.ceil(average_rating)
    else:
        average_rating = 0

    # Fetch user's rating for the book
    user_rating = None
    if user.is_authenticated:
        user_rating = UserRating.objects.filter(user=user, rating__object_id=book.bookid).first()


    # Formulář pro úpravu DIV Ratingu u Book
    book_div_rating_form = None
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_divrating' in request.POST:
            book_div_rating_form = BookDivRatingForm(request.POST, instance=book)
            if book_div_rating_form.is_valid():
                book_div_rating_form.save()
                return redirect('book_detail', book_url=book_url)
        else:
            book_div_rating_form = BookDivRatingForm(instance=book)



    # POSTAVA
    character_form = BookCharacterForm()
    characters = Bookcharacter.objects.filter(bookid=book).select_related('characterid')

    # Zpracování formuláře pro přidání postavy
    if request.method == "POST" and "add_character" in request.POST:
        character_form = BookCharacterForm(request.POST)
        if character_form.is_valid():
            new_character = character_form.save(commit=False)
            new_character.bookid = book
            new_character.save()
            messages.success(request, f"Postava {new_character.characterid.charactername} byla přidána ke knize {book.title}.")
            return redirect('book_detail', book_url=book.url)
        else:
            messages.error(request, "Chyba při přidávání postavy. Zkontrolujte formulář.")

    # AJAX načítání postav
    if request.method == "GET" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        matching_characters = Charactermeta.objects.filter(charactername__icontains=query).order_by('charactername').values('characterid', 'charactername')[:20]
        return JsonResponse({'results': list(matching_characters)}, safe=False)



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

        "is_in_book_library": is_in_book_library,
        'ratings': ratings,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'book_div_rating_form': book_div_rating_form,

        })
#    top_20_books = Book.objects.order_by('-bookrating').all()[:20]  # Define top_20_books here
    #'top_20_books': top_20_books




def character_list_ajax(request):
    query = request.GET.get('q', '').strip()
    characters = Charactermeta.objects.filter(charactername__icontains=query).order_by('charactername').values('characterid', 'charactername')[:20]
    return JsonResponse({'results': list(characters)}, safe=False)


@login_required
def rate_book(request, book_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        user = request.user
        book = get_object_or_404(Book, id=book_id)
        
        BookRating.objects.create(Rating=rating, Book=book, User=user)
        return redirect('book_detail', book_id=book_id)
    else:
        # Zobrazte formulář pro hodnocení
        return render(request, 'book/book_detail.html', {'book_id': book_id})




@require_POST
def ratequote(request, quote_id):
    quote = get_object_or_404(Bookquotes, pk=quote_id)
    action = request.POST.get('action')

    # Zkontroluje cookies
    cookie_name = f'voted_{quote_id}'
    if request.COOKIES.get(cookie_name):
        return JsonResponse({'error': 'Již jste hlasoval/a.'})

    # Pokud uživatel nehlasoval, zvýšíme hlas a nastavíme cookie
    if action == 'thumbsup':
        quote.thumbsup += 1
    elif action == 'thumbsdown':
        quote.thumbsdown += 1

    quote.save()

    response = JsonResponse({'thumbsup': quote.thumbsup, 'thumbsdown': quote.thumbsdown})
    
    # Nastaví cookie na týden
    expires = timezone.now() + datetime.timedelta(days=7)
    response.set_cookie(cookie_name, 'voted', expires=expires)
    
    return response



def books_search(request):
    books = None
    if 'q' in request.GET:
        form = SearchFormBooks(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            # Použití select_related pro připojení autora k výsledkům
            books = (Book.objects.filter(title__icontains=query)
                .select_related('authorid')  # Připojení modelu Bookauthor
                .values('title', 'url', 'year', 'googleid', 'pages', 'author', 'authorid__url', 'authorid__firstname', 'authorid__lastname')[:50])
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

    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_BOOK_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=bookid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOK_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=bookid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=bookid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()

    
    return redirect("book_detail", book_url=book.url)

# # Přidat do seznamu: Chci číst
@login_required
def add_to_readlist(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    readlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READLIST_ID)
    readlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=readlist_type)

    if Userlistitem.objects.filter(userlist=readlist_list, object_id=bookid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOK_ID)
        Userlistitem.objects.create(
            userlist=readlist_list, 
            content_type=content_type,
            object_id=bookid
            )

        print("new list created")
    
    return redirect("book_detail", book_url=book.url)   

# Přidat do seznamu: Přečteno
@login_required
def add_to_read_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    read_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READ_BOOKS_ID)
    read_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=read_type)

    if Userlistitem.objects.filter(userlist=read_list, object_id=bookid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOK_ID)
        Userlistitem.objects.create(
            userlist=read_list, 
            content_type=content_type,
            object_id=bookid
            )

    
    return redirect("book_detail", book_url=book.url)   

# Přidat do seznamu: Knihovna
@login_required
def add_to_book_library(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_BOOK_LIBRARY_ID)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)

    if Userlistitem.objects.filter(userlist=library_list, object_id=bookid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOK_ID)
        Userlistitem.objects.create(
            userlist=library_list, 
            content_type=content_type,
            object_id=bookid)

    
    return redirect("book_detail", book_url=book.url) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourites_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_BOOK_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=favourites_list)
    userlistbook.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOK_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=bookid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()

    
    return redirect("book_detail", book_url=book.url)

# Smazat ze seznamu: Chci číst
@login_required
def remove_from_readlist(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    readlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READLIST_ID)
    readlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=readlist_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=readlist_list)

    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# Smazat ze seznamu: Přečteno
@login_required
def remove_from_read_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    read_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READ_BOOKS_ID)
    read_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=read_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=read_list)

    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# Smazat ze seznamu: Knihovna
@login_required
def remove_from_book_library(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)

    library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_BOOK_LIBRARY_ID)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=library_list)

    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)
