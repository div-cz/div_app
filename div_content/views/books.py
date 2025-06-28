# VIEWS.BOOKS.PY TEST

# https://console.cloud.google.com/welcome?project=knihy-div

import base64
import datetime
import io
import json
import math
import os
import qrcode
import requests
import unicodedata

from datetime import datetime
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

from django.core.paginator import Paginator

from django.db import models
from django.db.models import Avg, Count
from django.db.models import Avg

from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import now

from django.views.decorators.http import require_POST

from dotenv import load_dotenv

from div_content.forms.books import BookAddForm, BookDivRatingForm, BookCharacterForm, BookListingForm, Bookquoteform, CommentFormBook, SearchFormBooks
from div_content.models import (
    Book, Bookauthor, Bookcharacter, Bookcomments, Bookcover, Bookgenre, Bookisbn, Booklisting, 
    Bookpublisher, Bookpurchase, Bookquotes, Bookrating, Bookwriters, Charactermeta, Metagenre, Metaindex, Metastats, Metauniversum, Userlist, Userlistbook, Userlisttype, FavoriteSum, Userbookgoal, Userlistitem
)
#from div_content.utils.books import fetch_book_from_google_by_id, fetch_books_from_google
from div_content.utils.payments import generate_qr, prepare_qr_codes_for_book, qr_code_ebook, qr_code_market
from div_content.utils.palmknihy import get_catalog_product

load_dotenv()
from div_content.views.login import custom_login_view
from div_content.views.palmknihy import get_palmknihy_ebooks
from div_content.views.payments import get_ebook_purchase_status

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



class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)



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



def get_book_price(book_id, format):
    """ Vrátí cenu e-knihy podle jejího formátu """
    book_isbn = Bookisbn.objects.filter(book_id=book_id, format=format).first()
    return book_isbn.price if book_isbn and book_isbn.price else None




    
def listing_detail(request, book_url, listing_id):
    book = get_object_or_404(Book, url=book_url)
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, book=book)
    
    user_purchase = None 
    if request.user.is_authenticated:
        try:
            user_purchase = Bookpurchase.objects.get(
                user=request.user,
                book=book,
                status='RESERVED' 
            )
        except Bookpurchase.DoesNotExist:
            user_purchase = None
        except Bookpurchase.MultipleObjectsReturned:
            user_purchase = Bookpurchase.objects.filter(
                user=request.user,
                book=book,
                status='RESERVED'
            ).order_by('-orderdate').first()

    if request.method == 'POST' and request.user.is_authenticated:
        if 'reserve_listing' in request.POST and request.user != listing.user:
            print("\n--- Pokus o rezervaci nabídky ---")
            print(f"Aktuální listing.status: {listing.status}")
            print(f"Uživatel: {request.user.username} (ID: {request.user.id})")
            print(f"Kniha: {book.titlecz} (ID: {book.bookid})")
            
            if listing.status != 'ACTIVE':
                messages.error(request, 'Nabídka již není aktivní.')
                print("Chyba: Nabídka není aktivní.")
            elif user_purchase:
                messages.warning(request, 'Tuto knihu jste již rezervoval(a).')
                print(f"Chyba: Uživatel již má existující purchase (ID: {user_purchase.purchaseid}, status: {user_purchase.status}).")
            else:      
                try:
                    new_purchase = Bookpurchase.objects.create(
                        user=request.user,
                        book=book,
                        price=listing.price,
                        format='pdf', 
                        status='RESERVED', 
                        orderdate=timezone.now()
                    )
                    messages.success(request, 'Kniha byla úspěšně rezervována. Čeká na platbu.')
                    user_purchase = new_purchase
                    print(f"Úspěšně vytvořen nový Bookpurchase! ID: {new_purchase.purchaseid}, User: {new_purchase.user.username}, Book ID: {new_purchase.book.bookid}, Status: {new_purchase.status}")

                except Exception as e:
                    messages.error(request, f'Chyba při vytváření rezervace: {e}')
                    print(f"CHYBA PŘI VYTVÁŘENÍ PURCHASE: {e}")
                    return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

                listing.status = 'RESERVED' 
                listing.buyer = request.user
                listing.save()
                messages.success(request, 'Nabídka byla rezervována.')
                print(f"Listing aktualizován: Status={listing.status}, Kupující={listing.buyer.username}")
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)    
   # --- Dokončení transakce (pro prodejce) ---
        elif 'complete_listing' in request.POST and request.user == listing.user:
            if listing.status != 'RESERVED':
                messages.error(request, 'Nabídka není ve stavu pro dokončení.')

            elif not user_purchase or user_purchase.status != 'RESERVED': 
                messages.error(request, 'Nelze dokončit, chybí odpovídající rezervace.')
            else:
                listing.status = 'COMPLETED'
                listing.completed_at = timezone.now()
                listing.save()
                
                user_purchase.status = 'PAID'  
                user_purchase.paymentdate = timezone.now()
                user_purchase.save()

                messages.success(request, 'Transakce byla dokončena.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

        elif 'cancel_reservation' in request.POST and user_purchase: 
            if (user_purchase.user == request.user and 
                listing.status == 'RESERVED' and 
                user_purchase.status == 'RESERVED'): 
                
                user_purchase.status = 'CANCELLED' 
                user_purchase.cancelreason = request.POST.get("cancel_reason", "Bez udání důvodu")
                user_purchase.save()

                listing.status = 'ACTIVE' 
                listing.buyer = None 
                listing.save()

                messages.success(request, 'Rezervace byla zrušena a nabídka vrácena do aktivního stavu.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
            else:
                messages.error(request, 'Tuto rezervaci nelze zrušit. Nesplňuje podmínky pro zrušení.')        
        
        # Přidání hodnocení prodejcem
        elif 'sellerrating' in request.POST and request.user == listing.user:
            if listing.buyerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.buyerrating = request.POST.get('rating')
                listing.buyercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení kupujícího bylo přidáno.')
            
        # Přidání hodnocení kupujícím
        elif 'buyerrating' in request.POST and request.user == listing.buyer:
            if listing.sellerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.sellerrating = request.POST.get('rating')
                listing.sellercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení prodejce bylo přidáno.')

 
    # QR kód a platební údaje
    payment_info = None
    if listing.status == 'RESERVED' and listing.buyer == request.user:
        total_amount = float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0)
        qr_message = f"{book.title}|{listing.user.username}"
        payment_info = {
            'total': total_amount,
            'qr_code': get_qr_code(total_amount, book.bookid, qr_message),
            'variable_symbol': book.bookid,
            'note': qr_message
        }
    
 # Zjištění, zda může uživatel přidat hodnocení
    can_rate_seller = (listing.status == 'COMPLETED' and 
                      request.user == listing.buyer and 
                      not listing.sellerrating)
    can_rate_buyer = (listing.status == 'COMPLETED' and 
                     request.user == listing.user and 
                     not listing.buyerrating)
    can_cancel_reservation = False # Inicializace

    if request.user.is_authenticated:
        # Podmínka pro ZRUŠENÍ REZERVACE (kupující)
        if (listing.status  == 'RESERVED' and 
            user_purchase and 
            user_purchase.user == request.user and 
            user_purchase.status == 'PENDING'):
            can_cancel_reservation = True

    return render(request, 'books/listing_detail.html', {
        'book': book,
        'listing': listing,
        'payment_info': payment_info,
        'can_rate_seller': can_rate_seller,
        'can_rate_buyer': can_rate_buyer,
        'purchase': user_purchase,
        'can_cancel_reservation': can_cancel_reservation,
    })    
     


def get_market_listings(limit=5):
    #Pomocná funkce pro hlavní stranu a výpis
    #recent_listings = get_market_listings()
    sell_listings = (Booklisting.objects.filter(
        listingtype__in=['SELL', 'GIVE'], 
        active=True,
        status='ACTIVE'
    ).select_related('book', 'user')
     .order_by('-createdat')[:limit])
    
    return sell_listings


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
    book_list_15 = Book.objects.all().annotate(
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
    )[:30]
    # Zaokrouhlíme hodnoty na celá čísla a převedeme na procenta
    for book in book_list_15:
        if book['average_rating'] is not None:
            book['average_rating'] = round(float(book['average_rating']) * 20)  # převod z 5 na 100%
        else:
            book['average_rating'] = 0
    #větší než 2022
    #book_list_15 = Book.objects.filter(year__gt=2022).order_by('-divrating')[20:35]

    # Knihy podle popularity
    # book_list_15 = Metaindex.objects.filter(year__gt=2018).order_by("-popularity").values('title', 'url', 'img', 'description')[:15]

    top_books = Book.objects.order_by('-divrating')[:10]

    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()


    reading_goal = None
    if request.user.is_authenticated:
        reading_goal = get_reading_goal(request)
    
    recent_listings = get_market_listings()
    
    ebooks2 = get_palmknihy_ebooks(limit=6)
    
    last_comment = Bookcomments.objects.select_related('user', 'bookid').order_by('-commentid').first()
    latest_comments = Bookcomments.objects.order_by('-dateadded')[:3]

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
        })
#'top_20_books': top_20_books, 'all_books': all_books, 'api_test_message': api_test_message


def books_alphabetical(request):
    return render(request, "books/books_alphabetical.html")


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


    booklisting_form = None
    if user.is_authenticated:
        if request.method == 'POST' and request.POST.get('form_type') == 'booklisting':
            booklisting_form = BookListingForm(request.POST)
            if booklisting_form.is_valid():
                listing = booklisting_form.save(commit=False)
                listing.user = request.user
                listing.book = book
                listing.save()
                messages.success(request, 'Nabídka byla úspěšně vytvořena.')
                return redirect('book_detail', book_url=book_url)
        else:
            booklisting_form = BookListingForm()

    # Načtení nabídek
    listings = Booklisting.objects.filter(book_id=book.bookid, active=True).order_by('-createdat')
    sell_listings = listings.filter(listingtype__in=['SELL', 'GIVE'])
    buy_listings = listings.filter(listingtype='BUY')


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

    ALLOWED_EBOOK_FORMATS = ["EPUB", "MOBI", "PDF", "AUDIO"]
    bookisbns = Bookisbn.objects.filter(book=book, format__in=ALLOWED_EBOOK_FORMATS)
    ebook_formats = {
        b.format.lower(): {
            "isbn": b.isbn,
            "price": b.price,
            "free": b.price == 0,
            "available": b.price is not None,
            "type": b.ISBNtype,
        }
        for b in bookisbns if b.isbn and b.format
    }
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
        'palmknihy_data': matched,
        'ebook_info': ebook_info,
        'has_ebook': has_ebook,
        'has_audio': has_audio,
        'prices': prices,
        'cena_od': cena_od,
        'existing_paid_email': existing_paid_email,
        'ebook_formats': ebook_formats,  
        'ebook_formats_json': json.dumps(ebook_formats, cls=DecimalEncoder),
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
            books = (Book.objects.filter(title__icontains=query)
                .select_related('authorid')  # Připojení modelu Bookauthor
                .values('title', 'titlecz', 'url', 'year', 'googleid', 'pages', 'img', 'author', 'authorid__url', 'authorid__firstname', 'authorid__lastname')[:50])
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


