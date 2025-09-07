# -------------------------------------------------------------------
#                    VIEWS.BOOKS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# # https://console.cloud.google.com/welcome?project=knihy-div
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------

import base64
import datetime
import io
import json
import math
import os
import qrcode
import requests
import smtplib
import unicodedata

from datetime import datetime
from decimal import Decimal

from django.conf import settings

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from django.core.mail import EmailMessage
from django.core.paginator import Paginator

from django.db import models
from django.db.models import Avg, Count, Case, When, Value, IntegerField

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import now

from django.views.decorators.http import require_POST

from dotenv import load_dotenv

from div_content.forms.books import BookAddForm, BookDivRatingForm, BookCharacterForm, BookListingForm, Bookquoteform, CommentFormBook, ManualBookForm, SearchFormBooks
from div_content.forms.divkvariat import BookListingForm
from div_content.models import (
    Book, Bookauthor, Bookcharacter, Bookcomments, Bookcover, Bookgenre, Bookisbn, Booklisting, 
    Bookpublisher, Bookpurchase, Bookquotes, Bookrating, Booksource, Bookwriters, Charactermeta, Metagenre, Metaindex, Metastats, Metauniversum, Userlist, Userlistbook, Userlisttype, FavoriteSum, Userbookgoal, Userlistitem
)

from div_content.utils.books import get_market_listings
from div_content.utils.metaindex import add_to_metaindex
#from div_content.utils.books import fetch_book_from_google_by_id, fetch_books_from_google
from div_content.utils.payments import prepare_qr_codes_for_book, qr_code_ebook
from div_content.utils.palmknihy import get_catalog_product

load_dotenv()
from div_content.views.login import custom_login_view
from div_content.views.palmknihy import get_palmknihy_ebooks
from div_content.views.payments import get_ebook_purchase_status

from email.message import EmailMessage


from io import BytesIO

from star_ratings.models import Rating, UserRating






# Konstanty
USERLISTTYPE_FAVORITE_BOOK_ID = 4 # Oblíbená kniha
USERLISTTYPE_READLIST_ID = 5 # Chci číst
USERLISTTYPE_READ_BOOKS_ID = 6 # Přečteno
USERLISTTYPE_BOOK_LIBRARY_ID = 10 # Knihovna

#CONTENT_TYPE_BOOK_ID = 9
book_content_type = ContentType.objects.get_for_model(Book)
CONTENT_TYPE_BOOK_ID = book_content_type.id

def is_staff(user):
    return user.is_staff or user.is_superuser




class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)

def order_listings(qs):
    status_order = Case(
        When(status='ACTIVE',    then=Value(0)),
        When(status='RESERVED',  then=Value(1)),
        When(status='PAID',      then=Value(2)),
        When(status='SHIPPED',   then=Value(3)),   # pokud používáš
        When(status='COMPLETED', then=Value(99)),  # „Prodáno“ až na konec
        When(status='CANCELLED', then=Value(100)),
        When(status='DELETED',   then=Value(101)),
        default=Value(200),
        output_field=IntegerField(),
    )
    return qs.annotate(status_order=status_order).order_by('status_order', '-createdat')

def normalize(text):
    return (text or "").lower().strip().replace("á", "a").replace("č", "c").replace("ď", "d")\
           .replace("é", "e").replace("ě", "e").replace("í", "i").replace("ň", "n")\
           .replace("ó", "o").replace("ř", "r").replace("š", "s").replace("ť", "t")\
           .replace("ú", "u").replace("ů", "u").replace("ý", "y").replace("ž", "z")


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
            booksread=0,
            lastupdated=timezone.now()
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
        
    return redirect('books_index') 

# === === === === ===
# === DIV KVARIÁT ===
# === === === === ===
def book_listings(request, book_url):
    #Zobrazení všech nabídek pro konkrétní knihu.
    book = get_object_or_404(Book, url=book_url)
    listings = Booklisting.objects.filter(book=book, active=True).order_by('-createdat')
    
    # Rozdělení na prodej a poptávku
    sell_listings = listings.filter(listingtype__in=['SELL', 'GIVE'])
    buy_listings = listings.filter(listingtype='BUY')
    
    return render(request, 'books/listings.html', {
        'book': book,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings
    })


def books_market_offers(request):
    #View for sell/give offers
    sell_listings = (Booklisting.objects
        .filter(listingtype__in=['SELL', 'GIVE'], active=True, status='ACTIVE')
        .select_related('book', 'user')
        .order_by('-createdat'))
    
    paginator = Paginator(sell_listings, 12)
    page = request.GET.get('page')
    listings = paginator.get_page(page)

    return render(request, 'books/books_market_offers.html', {
        'listings': listings
    })

def books_market_wants(request):
    #View for buy requests
    buy_listings = (Booklisting.objects
        .filter(listingtype='BUY', active=True, status='ACTIVE')
        .select_related('book', 'user')
        .order_by('-createdat'))
    
    paginator = Paginator(buy_listings, 12)
    page = request.GET.get('page')
    listings = paginator.get_page(page)

    return render(request, 'books/books_market_wants.html', {
        'listings': listings
    })








@login_required
def cancel_purchase(request, purchase_id):
    purchase = get_object_or_404(Bookpurchase, purchaseid=purchase_id, user=request.user) 
    
    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "Bez udání důvodu") 
        
        if purchase.book and purchase.book.status == 'RESERVED' and purchase.status == 'PENDING':
            book_obj = purchase.book 
            
            book_obj.status = "ACTIVE" 
            book_obj.save() 
            
            purchase.status = "CANCELLED" 
            purchase.cancelreason = reason
            purchase.save()
            
            messages.success(request, f'Rezervace knihy "{book_obj.titlecz}" byla zrušena.')
            if hasattr(purchase, 'listing') and purchase.listing: # Check if 'listing' attribute exists and is not None
                send_listing_cancel_email(request, purchase.listing.booklistingid)
            return redirect('index') 
        else:
            messages.error(request, 'Rezervaci nelze zrušit, protože kniha/rezervace již není ve stavu "RESERVED"/"PENDING".')
            return redirect('index') 



@login_required
def cancel_purchase(request, purchase_id):
    purchase = get_object_or_404(Bookpurchase, purchaseid=purchase_id, user=request.user) 
    
    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "Bez udání důvodu") 
        
        if purchase.book and purchase.book.status == 'RESERVED' and purchase.status == 'PENDING':
            book_obj = purchase.book 
            
            book_obj.status = "ACTIVE" 
            book_obj.save() 
            
            purchase.status = "CANCELLED" 
            purchase.cancelreason = reason
            purchase.save()
            
            messages.success(request, f'Rezervace knihy "{book_obj.titlecz}" byla zrušena.')
            return redirect('index') 
        else:
            messages.error(request, 'Rezervaci nelze zrušit, protože kniha/rezervace již není ve stavu "RESERVED"/"PENDING".')
            return redirect('index') 

    return render(request, "books/market_cancel_purchase.html", {"purchase": purchase})

@login_required
def confirm_sale(request, purchase_id):
    purchase = get_object_or_404(Bookpurchase, id=purchase_id, seller=request.user)
    if request.method == "POST":
        purchase.status = "completed"
        purchase.completedat = timezone.now()
        purchase.save()
        return redirect("index")
    return render(request, "books/market_confirm_sale.html", {"purchase": purchase})



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


        #all_books = books_from_api + list(top_20_books)
    #except Exception as e:
        #all_books = []
        #api_test_message += " | Chyba při získávání dat z API: " + str(e)
    
    #book_list_15 = Book.objects.all().order_by('-divrating')[:30]
    # Získáme knihy včetně jejich hodnocení
    book_content_type = ContentType.objects.get_for_model(Book)
    """book_list_15 = Book.objects.all().annotate(
        average_rating=models.Subquery(
            Rating.objects.filter(
                content_type=book_content_type,
                object_id=models.OuterRef('bookid')
            ).values('average')[:1]
        )
    ).order_by('-divrating').values(
        'title', 
        'titlecz', 
        'description', 
        'url', 
        'img',
        'author',
        'authorid',
        'googleid',
        'average_rating'
    )[:30]"""

    book_list_15 = (
        Book.objects
        .select_related("authorid")  # JOIN na autora
        .annotate(
            average_rating=models.Subquery(
                Rating.objects.filter(
                    content_type=book_content_type,
                    object_id=models.OuterRef('bookid')
                ).values('average')[:1]
            )
        )
        .order_by('-divrating')[:10]
    )

    # Zaokrouhlíme hodnoty na celá čísla a převedeme na procenta
    for book in book_list_15:
        if book.average_rating is not None:
            book.average_rating = round(float(book.average_rating) * 20)
        else:
            book.average_rating = 0
    #větší než 2022
    #book_list_15 = Book.objects.filter(year__gt=2022).order_by('-divrating')[20:35]

    # Knihy podle popularity
    # book_list_15 = Metaindex.objects.filter(year__gt=2018).order_by("-popularity").values('title', 'url', 'img', 'description')[:15]

    top_books = Book.objects.select_related("authorid").order_by('-divrating')[:10]

    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()


    reading_goal = None
    if request.user.is_authenticated:
        reading_goal = get_reading_goal(request)
    
    recent_listings = get_market_listings()
    
    ebooks2 = get_palmknihy_ebooks(limit=6)
    
    last_comment = Bookcomments.objects.select_related('user', 'bookid').order_by('-commentid').first()
    latest_comments = Bookcomments.objects.order_by('-dateadded')[:3]
    
    recent_sell_listings, recent_buy_listings = get_market_listings()

    return render(request, 'books/books_list.html', {
        'top_books': top_books,
        'book_list_15': book_list_15,
        'stats_book': stats_book,
        'stats_writters': stats_writters,
        'reading_goal': reading_goal,
        'category_key': 'knihy',
        'recent_listings': recent_listings,
        'ebooks2': ebooks2,
        'last_comment': last_comment,
        'latest_comments': latest_comments,
        'recent_sell_listings': recent_sell_listings,
        'recent_buy_listings': recent_buy_listings,
        })
#'top_20_books': top_20_books, 'all_books': all_books, 'api_test_message': api_test_message


def books_alphabetical(request):
    return render(request, "books/books_alphabetical.html")


def get_book_price(book_id, format):
    """ Vrátí cenu e-knihy podle jejího formátu """
    book_isbn = Bookisbn.objects.filter(book_id=book_id, format=format).first()
    return book_isbn.price if book_isbn and book_isbn.price else None
    
    

def book_detail(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    user = request.user
    comment_form = None
    series = None
    series_books = []

    genres = book.bookgenre_set.all()[:3]
    
    # Fetch authors associated with the book
    authors = Bookauthor.objects.filter(
        authorid__in=Bookwriters.objects.filter(book_id=book.bookid).values_list('author_id', flat=True)
    )
     #Fetch characters associated with the book
    characters_with_roles = Bookcharacter.objects.filter(bookid=book.bookid).select_related('characterid')

    # Fetch quotes associated with the book
    quotes = Bookquotes.objects.filter(bookid=book).order_by('-divrating')

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
    # Calculate average rating
    book_content_type = ContentType.objects.get_for_model(Book)
    ratings = UserRating.objects.filter(rating__content_type=book_content_type, rating__object_id=book.bookid)
    
    average_rating_result = ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result["average"]
    
    if average_rating is not None:
        average_rating = math.ceil(float(average_rating) * 20)  # převod na %
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


    booklisting_form = None
    if user.is_authenticated:
        if request.method == 'POST' and request.POST.get('form_type') == 'booklisting':
            booklisting_form = BookListingForm(request.POST)
            if booklisting_form.is_valid():
                listing = booklisting_form.save(commit=False)
                listing.user = request.user
                listing.book = book
                listing.paidtoseller = False
                listing.requestpayout = False
                listing.save()
                messages.success(request, 'Nabídka byla úspěšně vytvořena.')
                return redirect('book_detail', book_url=book_url)
        else:
            booklisting_form = BookListingForm(user=request.user)

    # Načtení nabídek
    listings = order_listings(
        Booklisting.objects.filter(book_id=book.bookid, active=True)
    )
    sell_listings = listings.filter(listingtype__in=['SELL', 'GIVE'], status='ACTIVE')
    buy_listings  = listings.filter(listingtype='BUY', status='ACTIVE')


    if book.universumid:
        series = book.universumid
        series_books = Book.objects.filter(universumid=book.universumid).exclude(bookid=book.bookid)[:10]
    
    # Načtení QR kódu pro eKnihu, pokud ji uživatel koupil a čeká na platbu
    user_ebook_purchases = []
    if user.is_authenticated:  # ✅ Zkontrolujeme, zda je uživatel přihlášený
        user_ebook_purchases = Bookpurchase.objects.filter(user=user, book=book, status="PENDING").order_by('-purchaseid')


    # TEST API EKNIHY
    try:
        ebooks = get_catalog_product(limit=300)
    except Exception as e:
        ebooks = []
        print(f"Chyba při načítání e-knih z Palmknihy: {e}")


    matched = None
    
    for ebook in ebooks:
        # Porovnáme název knihy
        if not isinstance(ebook, dict):
            continue
    
        # Porovnáme autora – API vrací list autorů (dicty), např. [{"name": "Václav"}]
        authors_api = [normalize(a.get("name", "")) if isinstance(a, dict) else normalize(a) for a in ebook.get("authors", [])]
        if normalize(book.author) not in authors_api:
            continue
    
        # Shoda nalezena
        matched = ebook
        break

    bookisbns = Bookisbn.objects.filter(book=book)

    ALLOWED_EBOOK_FORMATS = ["EPUB", "MOBI", "PDF", "DIV-AUDIO"]
    bookisbns = Bookisbn.objects.filter(book=book, format__in=ALLOWED_EBOOK_FORMATS)
    primary_source = None
    primary_source_url = None
    primary_source_id = None

    if bookisbns.exists():
        main_isbn = bookisbns.first()
        primary_source = (main_isbn.sourcetype or "").upper()
        if primary_source == "MLP":
            primary_source_url = main_isbn.url
        elif primary_source == "PALM":
            primary_source_id = main_isbn.sourceid

    ebook_formats = {}
    for b in bookisbns:
        if not b.isbn or not b.format:
            continue

        sourcetype = (b.sourcetype or "").upper()
        fmt = b.format.lower()

        data = {
            "isbn": b.isbn,
            "price": b.price,
            "free": b.price is not None and b.price == 0,
            "available": b.price is not None,
            "type": b.ISBNtype,
            "sourcetype": sourcetype,
        }

        # ✅ externí zdroje – vždy považuj za dostupné, pokud mají URL
        if sourcetype in ["MLP", "PALM", "GUTENBERG", "NDB"]:
            if b.url or b.sourceid:  # nějaký externí identifikátor
                data["available"] = True

        ebook_formats[fmt] = data



    ebook_formats = get_ebook_purchase_status(request.user, book, ebook_formats)
    ebook_info = next(iter(ebook_formats.values()), None)
    has_ebook = any(data.get("available") for data in ebook_formats.values())
    has_audio = any(fmt == "audio" and data.get("available") for fmt, data in ebook_formats.items())


    # Urči minimální dostupnou cenu (od)
    cena_od = min(
        [data["price"] for data in ebook_formats.values() if data.get("price") is not None and data.get("price") > 0],
        default=None
    )

    if request.user.is_authenticated:
        existing_paid_email = Bookpurchase.objects.filter(
            book=book,
            user=request.user,
            status="PAID"
        ).order_by('purchaseid').first()
        existing_paid_email = existing_paid_email.kindlemail if existing_paid_email else ""
    else:
        existing_paid_email = ""


    qr_codes = {}
    if user.is_authenticated:
        pending_purchases = {p.format.lower(): p for p in Bookpurchase.objects.filter(
            user=user, book=book, status="PENDING"
        )}
        for fmt, data in ebook_formats.items():
            if data["available"] and data["price"]:
                if fmt not in pending_purchases:
                    purchase, _ = Bookpurchase.objects.get_or_create(
                        user=user,
                        book=book,
                        format=fmt.upper(),
                        status="PENDING",
                        defaults={"price": data["price"]}
                    )
                    pending_purchases[fmt] = purchase
                qr_codes = prepare_qr_codes_for_book(user, book, ebook_formats)

    prepared = prepare_qr_codes_for_book(user, book, ebook_formats)
    if prepared:
        qr_codes = prepared

    print("QR codes", prepare_qr_codes_for_book(user, book, ebook_formats))




    qr_code_base64 = ""
    if user_ebook_purchases:
        qr_code_base64 = qr_code_ebook(user_ebook_purchases.first())


    prices = {
        'mobi': get_book_price(book.bookid, 'MOBI'),
        'epub': get_book_price(book.bookid, 'EPUB'),
        'pdf': get_book_price(book.bookid, 'PDF'),
    }

    ebook_formats = get_ebook_purchase_status(request.user, book, ebook_formats)

    format_kindlemails = {}
    if user.is_authenticated:
        for fmt in ebook_formats:
            purchase = Bookpurchase.objects.filter(
                book=book, user=user, format=fmt.upper(), status="PAID"
            ).order_by('-purchaseid').first()
            format_kindlemails[fmt] = {
                "kindlemail": purchase.kindlemail if purchase and purchase.kindlemail else user.email,
                "readonly": bool(purchase and purchase.kindlemail)
            }

    if request.method == "POST" and request.user.is_superuser and 'add_to_metaindex' in request.POST:
        result = add_to_metaindex(book, 'Book')
        if result == "added":
            messages.success(request, "Záznam byl přidán na hlavní stránku.")
        elif result == "exists":
            messages.info(request, "Záznam už existuje.")
        else:
            messages.error(request, "Nepodařilo se přidat.")
        return redirect('book_detail', book_url=book.url)


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
        'booklisting_form': booklisting_form,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings,
        'series': series,
        'series_books': series_books,
        'user_ebook_purchases': user_ebook_purchases,
        'qr_codes': qr_codes,
        'qr_code_base64': qr_code_base64,
        'prices': prices,
        'primary_source': primary_source,
        'primary_source_url': primary_source_url,
        'primary_source_id': primary_source_id,
        'palmknihy_data': matched,
        'ebook_info': ebook_info,
        'has_ebook': has_ebook,
        'has_audio': has_audio,
        'prices': prices,
        'cena_od': cena_od,
        'existing_paid_email': existing_paid_email,
        'ebook_formats': ebook_formats,  
        'ebook_formats_json': json.dumps(ebook_formats, cls=DecimalEncoder),
        "format_kindlemails": format_kindlemails,
        #'books_with_series': books_with_series,
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
@login_required
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
        quote.divrating = (quote.divrating or 0) + 1 
    elif action == 'thumbsdown':
        quote.thumbsdown += 1
        quote.divrating = (quote.divrating or 0) - 1

    quote.save()

    response = JsonResponse({'thumbsup': quote.thumbsup, 'thumbsdown': quote.thumbsdown, 'divrating': quote.divrating})
    
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
            books = (Book.objects.filter(titlecz__icontains=query)
                .select_related('authorid')  # Připojení modelu Bookauthor
                .values('title', 'titlecz', 'url', 'year', 'googleid', 'pages', 'img', 'author', 'authorid__url', 'authorid__firstname', 'authorid__lastname')[:50])
    else:
        form = SearchFormBooks()

    return render(request, 'books/books_search.html', {'form': form, 'books': books})






#def books_search(request):
#    query = request.GET.get('query', '')  # Přečte parametr 'query' z GET požadavku
#    q = forms.CharField(label='Search', max_length=100)
#    return render(request, 'books/books_search.html', {'books': books})


#def book_add(request):
#    return render(request, "books/book_add.html")

@login_required
@user_passes_test(is_staff)
def book_add(request):
    if request.method == "POST":
        form = ManualBookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            
            # Vygeneruj URL slug
            from div_management.shared.universal_url_cleaner import clean_url
            if not book.url:
                base_url = clean_url(book.title)
                if not base_url:
                    base_url = "kniha"
                
                # Zajisti unikátnost
                counter = 1
                unique_url = base_url
                while Book.objects.filter(url=unique_url).exists():
                    unique_url = f"{base_url}-{counter}"
                    counter += 1
                
                book.url = unique_url
            
            # Nastav výchozí hodnoty
            if not book.titlecz:
                book.titlecz = book.title
            book.img = 'noimg.png'
            book.divrating = 0
            
            book.save()
            
            # Zpracuj autor -> BookWriters
            if book.authorid:
                Bookwriters.objects.get_or_create(book=book, author=book.authorid)
                if not book.author:
                    book.author = f"{book.authorid.firstname} {book.authorid.lastname}".strip()
                    book.save()
            
            # Zpracuj žánry
            genres = form.cleaned_data.get("genres", [])
            for genre in genres:
                Bookgenre.objects.get_or_create(bookid=book, genreid=genre)
            
            # Zpracuj obrázek
            cover_image = form.cleaned_data.get('cover_image')
            if cover_image:
                image_path = save_book_cover(book, cover_image)
                if image_path:
                    book.img = image_path
                    book.save()
            
            # Vytvoř záznam zdroje
            Booksource.objects.create(
                bookid=book,
                sourcetype="MANUAL",
                externalid=f"manual-{book.bookid}",
                externaltitle=book.title,
                externalauthors=book.author or "",
                externalurl=f"/knihy/{book.url}/"
            )
            
            messages.success(request, f"Kniha '{book.title}' byla úspěšně přidána.")
            return redirect("book_detail", book_url=book.url)
            
        else:
            messages.error(request, "Formulář obsahuje chyby. Zkontrolujte zadané údaje.")
    
    else:
        form = ManualBookForm()
    
    return render(request, "books/book_add.html", {
        "form": form,
        "page_title": "Přidat knihu ručně"
    })

def save_book_cover(book, image_file):
    """Uloží obrázek obálky knihy"""
    try:
        # Validace velikosti
        if image_file.size > 10 * 1024 * 1024:  # 10MB
            return None
        
        # Vytvoř cestu
        year = datetime.now().year
        media_path = f"/var/www/media.div.cz/knihy/{year}/"
        os.makedirs(media_path, exist_ok=True)
        
        # Název souboru
        filename = f"{book.bookid}-{book.url}.jpg"
        full_path = os.path.join(media_path, filename)
        
        # Ulož soubor
        with open(full_path, 'wb+') as destination:
            for chunk in image_file.chunks():
                destination.write(chunk)
        
        # Vrať relativní cestu
        return f"knihy/{year}/{filename}"
        
    except Exception as e:
        print(f"Chyba při ukládání obrázku: {e}")
        return None



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


# -------------------------------------------------------------------
# F:                 ADD TO READ BOOKS
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 ADD TO BOOK LIBRARY
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 REMOVE FROM FAVOURITES BOOKS
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 REMOVE FROM READLIST
# -------------------------------------------------------------------
@login_required
def remove_from_readlist(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    readlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READLIST_ID)
    readlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=readlist_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=readlist_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# -------------------------------------------------------------------
# F:                 REMOVE FROM READ BOOKS
# -------------------------------------------------------------------
@login_required
def remove_from_read_books(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    read_type = get_object_or_404(Userlisttype, userlisttypeid=USERLISTTYPE_READ_BOOKS_ID)
    read_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=read_type)
    
    book_content_type = ContentType.objects.get_for_model(Book)
    
    userlistbook = get_object_or_404(
        Userlistitem,
        object_id=bookid,
        content_type=book_content_type,
        userlist=read_list
    )
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# -------------------------------------------------------------------
# F:                 REMOVE FROM BOOK LIBRARY
# -------------------------------------------------------------------
@login_required
def remove_from_book_library(request, bookid):
    book = get_object_or_404(Book, bookid=bookid)
    library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_BOOK_LIBRARY_ID)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)
    userlistbook = Userlistitem.objects.get(object_id=bookid, userlist=library_list)
    userlistbook.delete()
    
    return redirect("book_detail", book_url=book.url)


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------