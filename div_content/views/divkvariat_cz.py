# -------------------------------------------------------------------
#                    VIEWS.DIVKVARIAT.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### variabilní symboly
# ### e-maily
# ### funkce
# 
# books_listings                    | popis
# books_market_offers               |
# books_market_wants                |
# cancel_listing_reservation        |
# confirm_sale                      |
# cancel_sell                       |
# get_book_price                    |
# get_market_listings               |
# listing_add_book                  |
# listing_detail                    |
# listing_search_book               |
# send_listing_cancel_email         |
# send_listing_expired_email_buyer  |
# send_listing_paid_expired_email_buyer
# send_listing_paid_expired_email_seller
# send_listing_payment_confirmation_email
# send_listing_payment_email        |
# send_listing_reservation_email    |
# qr_code_market                    |
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# Vše co souvisí s divkvaritáme
# Tři varianty: 
# 1) PRODEJ
# 2) POPTÁVKA 
# 3) DARUJI
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
import json
import os
import qrcode
import requests
import smtplib
import threading
import unicodedata

from allauth.account.views import LoginView, SignupView, LogoutView

from datetime import timedelta

from div_content.forms.divkvariat import BookListingForm
from div_content.models import Article, Book, Bookauthor, Bookgenre, Bookwriters, Booklisting, Metagenre, Userprofile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User



from django.contrib import messages
from django.core.mail import EmailMessage 
from django.core.paginator import Paginator

from django.db.models import Avg, Count, Sum, F, Q
from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from django.urls import reverse

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.timezone import now

from django.views.decorators.csrf import csrf_exempt

from dotenv import load_dotenv
from email.message import EmailMessage
from io import BytesIO

# -------------------------------------------------------------------
#                    KONSTANTY
# -------------------------------------------------------------------

ANTHROPIC_API_KEY = os.getenv("DIVKVARIAT_CHATBOT")

SYSTEM_PROMPT = """
Jsi AI asistent DIVkvariátu. Odpovídej česky, stručně a přátelsky.
VŽDY formátuj výstup pomocí čistého HTML (pouze <p>, <ul>, <li>, <strong>, <em>, <br>).
Nikdy nepoužívej <div>, <span>, <style>, <script> ani žádné nebezpečné tagy.
"""



# =========================================================
# Variabilní symbol pro platby – metodika DIV.cz / eKultura
# ---------------------------------------------------------
# VS je vždy 10 číslic, skládá se takto:
#
# PPP TT F NNNN
#  |   |  |  |
#  |   |  |  +--- Pořadové číslo objednávky (poslední 4 čísla)
#  |   |  +------ Formát  (5 - poptávka, 6 - prodej)
#  |   +--------- Typ produktu/služby (38 = kniha)
#  +------------- Projekt (010 = div.cz)
#
# Příklady:
# 0103821234  – Projekt DIV.cz (010), knihy (38), formát epub (2), objednávka č. 1234
# 0103831235  – Projekt DIV.cz (010), knihy (38), formát mobi (3), objednávka č. 1235
# 0103859999  - Projekt DIV.cz (010), knihy (38), burza koupě (5), objednávka č. 9999 / poptávka
# 0103869999  - Projekt DIV.cz (010), knihy (38), burza prodej(6), objednávka č. 9999
#
# Každý projekt má svůj trojciferný kód (PPP), každý typ (TT) a formát (F) je určen tabulkou.
# NNNN je unikátní pro každou objednávku v daném projektu a typu.
#
# F: 0 = print, 1 = audio, 2 = epub, 3 = mobi, 4 = pdf, 5 = burza koupě, 6 = burza prodej
#
# Více informací o struktuře VS viz interní dokumentace nebo konzultuj s Martinem.
# =========================================================
#
#
# Booklisting = Divkvariat (Bookpurchase = eknihy)
#

# QR kody pro makret = nic jiného není třeba



# =========================================================
# Přehled odesílaných e-mailů v DIVkvariátu (Booklisting)
# ---------------------------------------------------------
# E-maily se odesílají v těchto situacích:

# 1) Potvrzení REZERVACE knihy
#    -------------------------------------------
#    - Odesílá se kupujícímu (listing.buyer)
#    - Kdy: Jakmile uživatel rezervuje knihu (listing.status přechod na 'RESERVED')
#    - Kdo: Funkce send_listing_reservation_email(request, listing_id)
#    - Obsah: Potvrzení rezervace, QR platba, info o dalším postupu

# 2) Zrušení rezervace
#    -------------------------------------------
#    - Odesílá se kupujícímu (listing.buyer)
#    - Kdy: Jakmile kupující zruší rezervaci (listing.status zpět na 'ACTIVE')
#    - Kdo: Funkce send_listing_cancel_email(request, listing)
#    - Obsah: Info o zrušení rezervace

# 3) Výzva k zaslání knihy (po zaplacení)
#    -------------------------------------------
#    - Odesílá se prodávajícímu (listing.user)
#    - Kdy: Jakmile kupující zaplatí a status se změní na 'PAID'
#    - Kdo: Funkce send_listing_payment_email(request, listing_id)
#    - Obsah: Výzva k odeslání knihy, údaje o kupujícím

# 4) (Nepovinné: notifikace o dokončení/kompletním prodeji)
#    -------------------------------------------
#    - Můžeš přidat další, například po změně na 'COMPLETED' apod.
#
# 5) (Nepovinné: upomínky, upozornění, změny ceny, apod.)
#    -------------------------------------------
#    - Stejný princip: najít místo změny statusu a volat e-mailovou funkci.
#
# ---------------------------------------------------------
# Shrnutí:
# - E-maily posíláš vždy po změně určitého stavu v Booklisting.
# - Každá funkce na odesílání e-mailu je jasně oddělena, volá se **po změně statusu** nebo události.
# - Všechny e-maily směřují na správného uživatele (buyer/user).
# - Obsahy e-mailů a šablony najdeš v `templates/emails/`.
# =========================================================


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    user_message = data.get("message", "")

    # NEPŘIHLÁŠENÝ
    if not request.user.is_authenticated:
        return JsonResponse({
            "reply": "📚 Ahoj! Pro plnou podporu se prosím přihlas. Můžu ti poradit s nákupem nebo hledáním knih."
        })

    # PŘIHLÁŠENÝ → voláme API Claude
    payload = {
        "model": "claude-sonnet-4-20250514",
        "system": SYSTEM_PROMPT,
        "max_tokens": 400,
        "messages": [
            {"role": "user", "content": user_message}
        ]
    }

    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    try:
        r = requests.post("https://api.anthropic.com/v1/messages",
                          headers=headers, json=payload)
        reply = r.json()["content"][0]["text"]
        return JsonResponse({"reply": reply})
    except Exception:
        return JsonResponse({"reply": "❗ Omlouvám se, ale došlo k chybě při spojení."})


# -------------------------------------------------------------------
#                    BOOK DETAIL
# -------------------------------------------------------------------
def book_detail_cz(request, book_url):

    book = get_object_or_404(Book, url=book_url)

    # --- Aktivní nabídky a poptávky ---
    listings = Booklisting.objects.filter(book=book, active=True)

    sell_listings = listings.filter(
        listingtype__in=['SELL', 'GIVE'], status='ACTIVE'
    ).order_by('-createdat')

    buy_listings = listings.filter(
        listingtype='BUY', status='ACTIVE'
    ).order_by('-createdat')

    # --- Statistika ---
    sold_count = Booklisting.objects.filter(
        book=book,
        listingtype__in=['SELL', 'GIVE'],
        status='COMPLETED'
    ).count()

    total_active_offers = sell_listings.count()
    total_active_wants = buy_listings.count()

    context = {
        "book": book,
        "sell_listings": sell_listings,
        "buy_listings": buy_listings,
        "sold_count": sold_count,
        "total_active_offers": total_active_offers,
        "total_active_wants": total_active_wants,
    }

    return render(request, "divkvariat/book_detail.html", context)


# -------------------------------------------------------------------
#                    AUTHOR DETAIL
# -------------------------------------------------------------------
def author_detail_cz(request, author_url):

    author = get_object_or_404(Bookauthor, url=author_url)

    # ID knih od autora
    book_ids = Bookwriters.objects.filter(author=author).values_list('book', flat=True)

    # Seznam knih autora
    books = Book.objects.filter(bookid__in=book_ids).order_by("-year")

    # Nabídky a poptávky – pro KAŽDOU knihu
    book_data = []
    for book in books:

        listings = Booklisting.objects.filter(book=book, active=True)

        active_sells = listings.filter(
            listingtype__in=['SELL', 'GIVE'],
            status='ACTIVE'
        )

        active_buys = listings.filter(
            listingtype='BUY',
            status='ACTIVE'
        )

        sold_count = Booklisting.objects.filter(
            book=book,
            listingtype__in=['SELL', 'GIVE'],
            status='COMPLETED'
        ).count()

        book_data.append({
            "book": book,
            "active_sells": active_sells,
            "active_buys": active_buys,
            "sold_count": sold_count,
        })

    return render(request, "divkvariat/author_detail.html", {
        "author": author,
        "book_data": book_data,
    })

# -------------------------------------------------------------------
#                    ANTIKVARIAT HOME
# -------------------------------------------------------------------
def antikvariat_home(request):
    from random import sample

    if request.method == 'POST' and request.user.is_authenticated:
        if 'request_payout' in request.POST:
            user = request.user
            listings_to_update = Booklisting.objects.filter(
                user=user,
                status='COMPLETED',
                paidtoseller=False,
                requestpayout=False,
            )

            if listings_to_update.exists():
                total_user_payment_update = listings_to_update.aggregate(total_price=Sum(F('price') + F('shipping')))['total_price']

                for listing in listings_to_update:
                    listing.requestpayout = True
                    listing.save()
                    send_listing_request_seller_payment(listing, total_user_payment_update)

                messages.success(request, f'Žádost o vyplacení částky {total_user_payment_update} Kč byla odeslána. Počkejte prosím na zpracování.')
                return redirect('antikvariat_home')
            else:
                messages.error(request, 'Neexistují žádné nevyplacené transakce.')

    count_sell = Booklisting.objects.filter(listingtype__in=["SELL", "GIVE"], active=True, status="ACTIVE").count()
    count_buy = Booklisting.objects.filter(listingtype="BUY", active=True, status="ACTIVE").count()
    all_listings = list(Booklisting.objects.filter(active=True, status="ACTIVE")[:100])
    #random_listings = sample(all_listings, min(len(all_listings), 4))
    # Nabídky
    sell_listings = Booklisting.objects.filter(
        listingtype__in=["SELL", "GIVE"], active=True, status="ACTIVE"
    ).order_by("-createdat")

    # Poptávky
    buy_listings = Booklisting.objects.filter(
        listingtype="BUY", active=True, status="ACTIVE"
    ).order_by("-createdat")

    # Stránkování ( 24 na stránku)
    paginator_sell = Paginator(sell_listings, 24)
    paginator_buy = Paginator(buy_listings, 24)

    page_sell = request.GET.get("page_sell")
    page_buy = request.GET.get("page_buy")

    listings_sell = paginator_sell.get_page(page_sell)
    listings_buy = paginator_buy.get_page(page_buy)

    if request.user.is_authenticated:
        user = request.user
        amount_to_pay = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            paidtoseller=False,
        )
        
        pay_to_user = amount_to_pay.aggregate(
             total_price=Sum(F('price') + F('shipping'))
         )

        total_user_payment = pay_to_user['total_price'] or 0
        button_appear = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            paidtoseller=False,
            requestpayout=False,
        ).exists()
        user_sold_books = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            listingtype__in=['SELL', 'GIVE'],
        ).count()
        user_buyed_books = Booklisting.objects.filter(
            buyer=user,
            status='COMPLETED',
            listingtype__in=['SELL', 'GIVE'],
        ).count()
        user_pending_books = Booklisting.objects.filter(
            user=user,
            status__in=['ACTIVE', 'RESERVED'],
            listingtype__in=['SELL', 'GIVE'],
        ).count()
        user_pending_amount = Booklisting.objects.filter(
            user=user,
            status__in=['ACTIVE', 'RESERVED'],
            listingtype__in=['SELL', 'GIVE'],
        )
        pending_to_user = user_pending_amount.aggregate(pending_price=Sum(F('price')))
        total_user_pending = pending_to_user['pending_price'] or 0
        user_paid_amount = Booklisting.objects.filter(
            user=user,
            status='completed',
            paidtoseller= True,
        )
        paid_to_user= user_paid_amount.aggregate(total_price=Sum(F('price') + F('shipping')))
        total_user_paid_amount = paid_to_user['total_price'] or 0
        context_data = {
            "total_user_payment": total_user_payment,
            "button_appear": button_appear,
            "user_sold_books": user_sold_books,
            "user_buyed_books": user_buyed_books,
            "user_pending_books": user_pending_books,
            "total_user_pending": total_user_pending,
            "total_user_paid_amount": total_user_paid_amount,
        }
    else:
        context_data = {}



    final_context = {
        "count_sell": count_sell,
        "count_buy": count_buy,
        "listings_sell": listings_sell,
        "listings_buy": listings_buy,
        #"random_listings": random_listings,
        **context_data, 
    }

#    template = "books/antikvariat_home.html"
#    # Pokud jsme na divkvariat.cz / magic / test
#    if getattr(request, "site", None) == "divkvariat":
#        template = "books/divkvariat/antikvariat_home.html"
#    return render(request, template, final_context)
    return render(request, "divkvariat/antikvariat_home.html", final_context)


# ----------------------------------------------------
# BLOG — LIST
# ----------------------------------------------------
def blog_list(request):
    articles = Article.objects.filter(
        typ="Divkvariat"
    ).order_by("-created")

    paginator = Paginator(articles, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "divkvariat/blog_list.html", {
        "articles": page_obj,
    })



# ----------------------------------------------------
# BLOG — DETAIL
# ----------------------------------------------------
def blog_detail(request, url):
    article = get_object_or_404(
        Article,
        url=url,
        typ="Divkvariat"   # jen články DIVkvariát
    )

    return render(request, "divkvariat/blog_detail.html", {
        "article": article,
    })


# -------------------------------------------------------------------
#                    BOOK LISTINGS
# -------------------------------------------------------------------
def book_listings(request, book_url):
    #Zobrazení všech nabídek pro konkrétní knihu.
    book = get_object_or_404(Book, url=book_url)
    listings = Booklisting.objects.filter(book=book, active=True).order_by('-createdat')
    
    # Rozdělení na prodej a poptávku
    sell_listings = listings.filter(listingtype__in=['SELL', 'GIVE'])
    buy_listings = listings.filter(listingtype='BUY')
    
    return render(request, 'divkvariat/listings.html', {
        'book': book,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings
    })


# -------------------------------------------------------------------
#                    BOOKS MARKET OFFERS
# -------------------------------------------------------------------
def books_market_offers(request):

    # Základní queryset
    listings = Booklisting.objects.filter(
        listingtype__in=['SELL', 'GIVE'],
        active=True,
        status='ACTIVE'
    ).select_related("book", "user").order_by("-createdat")

    # FILTRACE DLE ŽÁNRŮ
    selected_genre = request.GET.get("zanr")

    if selected_genre:
        listings = listings.filter(
            book__bookgenre__genreid__url=selected_genre
        )

    # ZÍSKÁNÍ REÁLNĚ POUŽITÝCH ŽÁNRŮ
    genre_ids = Bookgenre.objects.filter(
        bookid__in=listings.values_list("book", flat=True)
    ).values_list("genreid", flat=True).distinct()

    categories = Metagenre.objects.filter(
        genreid__in=genre_ids
    ).order_by("genrenamecz")[:25]

    # TOP PRODEJCI
    top_sellers = (
        User.objects.annotate(
            total_sales=Count(
                "booklisting",
                filter=Q(booklisting__listingtype__in=['SELL', 'GIVE'])
            )
        ).filter(total_sales__gt=0)
         .order_by("-total_sales")[:6]
    )

    # PAGINACE
    paginator = Paginator(listings, 18)
    page = request.GET.get("page")
    listings_page = paginator.get_page(page)

    return render(request, "divkvariat/books_market_offers.html", {
        "listings": listings_page,
        "categories": categories,
        "selected_genre": selected_genre,
        "top_sellers": top_sellers,
    })


# -------------------------------------------------------------------
#                    BOOK MARKET WANTS
# -------------------------------------------------------------------
def books_market_wants(request):

    # --- KATALOG POPTÁVEK ---
    listings = Booklisting.objects.filter(
        listingtype='BUY',
        active=True
    ).select_related("book", "user").order_by("-createdat")

    # --- FILTRACE DLE ŽÁNRŮ ---
    selected_genre = request.GET.get("zanr")

    if selected_genre:
        listings = listings.filter(
            book__bookgenre__genreid__url=selected_genre
        )

    # --- ZÍSKÁNÍ KATEGORIÍ (pouze ty, které se reálně vyskytují v poptávkách) ---
    genre_ids = Bookgenre.objects.filter(
        bookid__in=listings.values_list("book", flat=True)
    ).values_list("genreid", flat=True).distinct()

    categories = Metagenre.objects.filter(
        genreid__in=genre_ids
    ).order_by("genrenamecz")[:25]  # limit aby to nebylo 1200 žánrů

    # --- TOP KUPUJÍCÍ ---
    top_buyers = (
        User.objects.annotate(
            total_buys=Count("booklisting", filter=Q(booklisting__listingtype="BUY"))
        )
        .filter(total_buys__gt=0)
        .order_by("-total_buys")[:6]
    )

    # --- PAGINACE ---
    from django.core.paginator import Paginator
    paginator = Paginator(listings, 18)
    page = request.GET.get("page")
    listings_page = paginator.get_page(page)

    return render(request, "divkvariat/books_market_wants.html", {
        "listings": listings_page,
        "categories": categories,
        "selected_genre": selected_genre,
        "top_buyers": top_buyers,
    })


# -------------------------------------------------------------------
#                    CANCEL LISTING RESERVATION
# -------------------------------------------------------------------
def cancel_listing_reservation(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    if request.method == "POST":
        reason = request.POST.get("cancel_reason", "Bez udání důvodu")

        if listing.status == 'RESERVED':
            book_obj = listing.book

            book_obj.status = "ACTIVE"
            book_obj.save()

            listing.status = "ACTIVE"
            listing.cancelreason = reason 
            listing.buyer = None 
            listing.save()

            messages.success(request, f'Rezervace knihy "{book_obj.titlecz}" byla zrušena.')

            send_listing_cancel_email(request, listing)
            return redirect('antikvariat_home') 
        else:
            messages.error(request, 'Rezervaci této knihy nelze zrušit, protože není ve stavu "REZERVACE".')
            return redirect('antikvariat_home')


# -------------------------------------------------------------------
#                    CONFIRM SALE
# -------------------------------------------------------------------
@login_required
def confirm_sale(request, purchase_id):
    purchase = get_object_or_404(Bookpurchase, id=purchase_id, seller=request.user)
    if request.method == "POST":
        purchase.status = "completed"
        purchase.completedat = timezone.now()
        purchase.save()
        return redirect("antikvariat_home")
    return render(request, "divkvariat/market_confirm_sale.html", {"purchase": purchase})


# -------------------------------------------------------------------
#                    CANCEL SELL
# -------------------------------------------------------------------
@login_required
def cancel_sell(request, listing_id):
    listing_to_cancel = get_object_or_404(Booklisting, booklistingid=listing_id, user=request.user)

    if request.method == "POST":
        if listing_to_cancel.status == 'ACTIVE' or listing_to_cancel.status == 'RESERVED':
            #listing_to_cancel.delete()
            listing_to_cancel.status = 'CANCELLED'
            listing_to_cancel.save()
            messages.success(request, f'Vaše nabídka knihy "{listing_to_cancel.book.titlecz}" byla úspěšně smazána.')
            return redirect('antikvariat_home')
        else:
            messages.error(request, 'Tuto nabídku nelze smazat v aktuálním stavu.')
            return redirect('antikvariat_home')

    return render(request, "divkvariat/market_cancel_offer.html", {"listing_offer": listing_to_cancel})


# -------------------------------------------------------------------
#                    GET BOOK PRICE
# -------------------------------------------------------------------
def get_book_price(book_id, format):
    """ Vrátí cenu e-knihy podle jejího formátu """
    book_isbn = Bookisbn.objects.filter(book_id=book_id, format=format).first()
    return book_isbn.price if book_isbn and book_isbn.price else None


# -------------------------------------------------------------------
#                    GET MARKET LISTINGS
# -------------------------------------------------------------------
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

# -------------------------------------------------------------------
#                    REQUEST PAYMENT EMAIL
# -------------------------------------------------------------------
def send_listing_request_seller_payment(listing,total_user_payment):
    user=listing.user
    amounttoseller = total_user_payment
    bankaccount = user.userprofile.bankaccount 
    recipient = ['finance@div.cz'] #lilien-rose@seznam.cz / 
    if not recipient:
        print("[✖] Superuser nemá e-mail – automatický e-mail neodeslán.")
        return

    context = {
        'seller_name': user.first_name or user.username,
        'total_user_payment': total_user_payment,
        'bank_account': bankaccount,
    }

    html_email = render_to_string('emails/listing_request_payment_seller.html', context)

    msg = EmailMessage()
    msg['Subject'] = os.getenv("EMAIL_SUBJECT_REQUEST")
    msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
    msg['To'] = recipient
    msg.set_content(html_email, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
            smtp.send_message(msg)
        print(f"[✔] Superuser dostal e-mail ohledně žádosti o vyplácení odeslán na {recipient}")
    except Exception as e:
        print(f"[✖] Chyba při odesílání automatického e-mailu pro superuser: {e}")


# -------------------------------------------------------------------
#                    LISTING ADD_BOOK
# -------------------------------------------------------------------
def listing_add_book(request):
    """Stránka pro přidání inzerátu - nejdřív vybereš knihu"""
    user = request.user
    
    if not user.is_authenticated:
        messages.warning(request, 'Pro vytvoření nabídky se musíte přihlásit.')
        return redirect('account_login')
    
    booklisting_form = None
    selected_book = None
    
    # Pokud už má book_id v GET (po výběru knihy)
    book_id = request.GET.get('book_id')
    if book_id:
        try:
            selected_book = Book.objects.get(bookid=book_id)
        except Book.DoesNotExist:
            messages.error(request, 'Kniha nebyla nalezena.')
    
    # POST - odesílání formuláře
    if request.method == 'POST' and request.POST.get('form_type') == 'booklisting':
        book_id = request.POST.get('book_id')
        if not book_id:
            messages.error(request, 'Musíte vybrat knihu.')
        else:
            try:
                book = Book.objects.get(bookid=book_id)
                booklisting_form = BookListingForm(request.POST, user=request.user)
                
                if booklisting_form.is_valid():
                    listing = booklisting_form.save(commit=False)
                    listing.user = request.user
                    listing.book = book
                    listing.paidtoseller = False
                    listing.requestpayout = False
                    listing.save()
                    
                    title = book.title or book.titlecz
                    messages.success(request, f'Nabídka pro knihu "{title}" byla úspěšně vytvořena - <a href=\"https://magic.div.cz/antikvariat/pridat-knihu/\">Vytvořit novou</a>.')
                    return redirect('book_detail_cz', book_url=book.url)
            except Book.DoesNotExist:
                messages.error(request, 'Kniha nebyla nalezena.')
    else:
        if selected_book:
            booklisting_form = BookListingForm(user=request.user)
    
    return render(request, 'divkvariat/listing_add_book.html', {
        'booklisting_form': booklisting_form,
        'selected_book': selected_book,
    })

# -------------------------------------------------------------------
#                    LISTING DETAIL
# -------------------------------------------------------------------
def listing_detail(request, book_url, listing_id):
    book = get_object_or_404(Book, url=book_url)
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, book=book)
    user = request.user

    # defaulty pro nepřihlášeného
    total_user_payment = 0
    button_appear = False
    user_sold_books = 0
    user_buyed_books = 0
    user_pending_books = 0
    total_user_pending = 0
    total_user_paid_amount = 0
    deadline_date = None
    shipped_deadline = None

    # Výpočet deadlinů podle stavu
    if listing.status == "RESERVED":
        deadline_date = listing.updatedat + timedelta(days=7)
    elif listing.status == "PAID":
        deadline_date = listing.updatedat + timedelta(days=10)
    elif listing.status == "SHIPPED":
        shipped_deadline = listing.updatedat + timedelta(days=10)

    if request.user.is_authenticated:
        amount_to_pay = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            paidtoseller=False,
        )
        pay_to_user = amount_to_pay.aggregate(
            total_price=Sum(F('price') + F('shipping'))
        )
        total_user_payment = pay_to_user['total_price'] or 0

        button_appear = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            paidtoseller=False,
            requestpayout=False,
        ).exists()

        user_sold_books = Booklisting.objects.filter(
            user=user,
            status='COMPLETED',
            listingtype__in=['SELL', 'GIVE'],
        ).count()

        user_buyed_books = Booklisting.objects.filter(
            buyer=user,
            status='COMPLETED',
            listingtype__in=['SELL', 'GIVE'],
        ).count()

        user_pending_books = Booklisting.objects.filter(
            user=user,
            status__in=['ACTIVE', 'RESERVED'],
            listingtype__in=['SELL', 'GIVE'],
        ).count()

        user_pending_amount = Booklisting.objects.filter(
            user=user,
            status__in=['ACTIVE', 'RESERVED'],
            listingtype__in=['SELL', 'GIVE'],
        )
        pending_to_user = user_pending_amount.aggregate(pending_price=Sum(F('price')))
        total_user_pending = pending_to_user['pending_price'] or 0

        user_paid_amount = Booklisting.objects.filter(
            user=user,
            status='completed',
            paidtoseller=True,
        )
        paid_to_user = user_paid_amount.aggregate(
            total_price=Sum(F('price') + F('shipping'))
        )
        total_user_paid_amount = paid_to_user['total_price'] or 0


    if request.method == 'POST' and request.user.is_authenticated:
        if 'request_payout' in request.POST:
            amount_to_pay_for_update = Booklisting.objects.filter(
                user=user,
                status='COMPLETED',
                paidtoseller=False,
                requestpayout=False,
            )
            pay_to_user_update = amount_to_pay_for_update.aggregate(total_price=Sum(F('price')))
            total_user_payment_update = pay_to_user_update['total_price']

            if total_user_payment_update is not None and total_user_payment_update > 0:
                amount_to_pay_for_update.update(
                    requestpayout=True,
                )
                send_listing_request_seller_payment(listing, total_user_payment)
                messages.success(request, f'Žádost o vyplacení částky {total_user_payment_update} Kč byla odeslána. Počkejte prosím na zpracování.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
            else:
                messages.error(request, 'Neexistují žádné nevyplacené transakce.')
        
        # REZERVACE
        elif 'reserve_listing' in request.POST and request.user != listing.user:
            if listing.status != 'ACTIVE':
                messages.error(request, 'Nabídka již není aktivní.')
            else:
                commission_input = request.POST.get("commission", "").strip()
                try:
                    commission = int(commission_input)
                    if commission < 0:
                        commission = 0
                except:
                    commission = 10 


                listing.commission = commission
                shipping_price = request.POST.get("shipping")
                listing.shipping = int(float(shipping_price)) if shipping_price else 0
                shippingaddress = request.POST.get("shippingaddress", "").strip()
    
                listing.status = 'RESERVED'
                listing.buyer = request.user
                listing.shippingaddress = shippingaddress
                listing.save()
    
                try:
                    profile = request.user.userprofile
                except Userprofile.DoesNotExist:
                    profile = None
                if profile and not profile.shippingaddress:
                    profile.shippingaddress = shippingaddress
                    profile.save()
    
                messages.success(request, 'Nabídka byla rezervována.')
                send_listing_reservation_email(request, listing.booklistingid)
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
        
        # Poslání knihy
        elif 'shipping_listing' in request.POST and request.user == listing.user: 
            if listing.status != 'PAID':
                messages.error(request, 'Nabídka není ve stavu pro potvrzení odeslání knihy.')
            else:
                listing.status = 'SHIPPED'
                listing.save()
                messages.success(request, 'Odeslání knihy bylo potvrzeno')
                send_listing_shipped_email(listing)
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

        # DOKONČENÍ (pro kupujícího)
        elif 'complete_listing' in request.POST and request.user == listing.buyer:
            if listing.status not in ['SHIPPED', 'PAID']:
                messages.error(request, 'Nabídka není ve stavu pro dokončení.')
            else:
                listing.status = 'COMPLETED'
                listing.completedat = timezone.now()
                listing.save()
                send_listing_completed_email_buyer(listing)
                send_listing_completed_email_seller(listing)
                messages.success(request, 'Transakce byla dokončena.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

        # DOKONČENÍ (pro prodávajícího)
       # elif 'complete_listing' in request.POST and request.user == listing.user:
          #  if listing.status != 'RESERVED':
              #  messages.error(request, 'Nabídka není ve stavu pro dokončení.')
          #  else:
          #      listing.status = 'COMPLETED'
           #     listing.completedat = timezone.now()
         #      listing.save()
         #       send_listing_completed_email_buyer(listing)
         #       send_listing_completed_email_seller(listing)
        #       messages.success(request, 'Transakce byla dokončena.')
        #        return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

        # Hodnocení prodávající/kupující
        elif 'sellerrating' in request.POST and request.user == listing.buyer:
            if listing.sellerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.sellerrating = request.POST.get('rating')
                listing.sellercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení kupujícího bylo přidáno.')
        
        elif 'buyerrating' in request.POST and request.user == listing.user:
            if listing.buyerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.buyerrating = request.POST.get('rating')
                listing.buyercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení prodejce bylo přidáno.')

    # QR platba 
    payment_info = None
    if listing.status == 'RESERVED' and listing.buyer == request.user:
        total_amount = float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0)
        book_title = book.titlecz or book.title or ""
        qr_message = f"DIV.cz | {book_title} | {listing.user.username}"
        # Prodej/koupě: zjisti, zda je typ 5 nebo 6 (můžeš to mít v listing.listingtype apod.)
        format_code = "5" if listing.listingtype == "BUY" else "6"  
        qr_code, vs = qr_code_market(total_amount, listing, qr_message, format_code)
        payment_info = {
            'total': total_amount,
            'qr_code': qr_code,
            'variable_symbol': vs,
            'note': qr_message
        }
    
    # Možnost hodnocení/zrušení pro správného uživatele
    can_rate_seller = (listing.status == 'COMPLETED' and request.user == listing.buyer and not listing.sellerrating)
    can_rate_buyer = (listing.status == 'COMPLETED' and request.user == listing.user and not listing.buyerrating)
    can_cancel_reservation = (listing.status == 'RESERVED' and request.user == listing.buyer)

    can_cancel_offer = (request.user == listing.user and listing.status in ['ACTIVE', 'RESERVED'])
    can_confirm_shipping = (listing.status == 'PAID' and request.user == listing.user)
    can_complete_transaction = (listing.status == 'SHIPPED' and request.user == listing.buyer)

    recent_sell_listings = Booklisting.objects.filter(
        listingtype__in=["SELL", "GIVE"], status="ACTIVE"
    ).order_by("-createdat")[:5]
    
    recent_buy_listings = Booklisting.objects.filter(
        listingtype="BUY", status="ACTIVE"
    ).order_by("-createdat")[:5]

    debug_post = None
    if request.method == 'POST':
        debug_post = dict(request.POST)

    print("==== RECENT ====")
    print(recent_sell_listings)
    print(recent_buy_listings)

    buyer_email = None
    buyer_phone = None

    if listing.buyer:
        buyer_email = listing.buyer.email
        try:
            profile = listing.buyer.userprofile
            buyer_phone = profile.phone
        except Userprofile.DoesNotExist:
            buyer_phone = None
        
    return render(request, 'divkvariat/listing_detail.html', {
        'book': book,
        'listing': listing,
        'payment_info': payment_info,
        'deadline_date': deadline_date,
        'shipped_deadline': shipped_deadline, 
        'can_rate_seller': can_rate_seller,
        'can_rate_buyer': can_rate_buyer,
        'can_cancel_reservation': can_cancel_reservation,
        'can_cancel_offer': can_cancel_offer,
        'can_confirm_shipping': can_confirm_shipping,    
        'can_complete_transaction': can_complete_transaction,
        'debug_post': debug_post,
        'recent_sell_listings': recent_sell_listings,
        'recent_buy_listings': recent_buy_listings,
        'total_user_payment': total_user_payment,
        'user_sold_books': user_sold_books,
        'user_buyed_books': user_buyed_books,
        'user_pending_books': user_pending_books,
        'total_user_pending': total_user_pending,
        'total_user_paid_amount': total_user_paid_amount,
        'button_appear': button_appear,
        'buyer_email': buyer_email,
        'buyer_phone': buyer_phone,
    })



# -------------------------------------------------------------------
#                    LISTING DETAIL EDIT
# -------------------------------------------------------------------
@login_required
def listing_detail_edit(request, book_url, listing_id):
    """Editace existující nabídky - samostatná stránka"""
    book = get_object_or_404(Book, url=book_url)
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, book=book, user=request.user)

    # DEBUG - PŘIDEJ TOHLE
    print("=" * 50)
    print(f"DEBUG EDIT FORM:")
    print(f"listing.price = {listing.price}")
    print(f"type(listing.price) = {type(listing.price)}")
    print(f"listing.price repr = {repr(listing.price)}")
    print("=" * 50)
    # KONEC DEBUG
    
    # Pouze ACTIVE nabídky lze editovat
    if listing.status != 'ACTIVE':
        messages.error(request, 'Tuto nabídku už nelze upravovat.')
        return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
    
    if request.method == 'POST':
        try:
            new_price = int(request.POST.get('new_price', 0))
        except (ValueError, TypeError):
            new_price = listing.price or 0
            
        new_description = request.POST.get('new_description', '')
        new_personal_pickup = 'new_personal_pickup' in request.POST
        new_location = request.POST.get('new_location', '')
        new_condition = request.POST.get('new_condition', '')
        
        # Zpracování shipping options
        zasilkovna = request.POST.get('shipping_zasilkovna', '')
        balikovna = request.POST.get('shipping_balikovna', '')
        osobni = request.POST.get('shipping_osobni', '')
        
        # Vytvoření shippingoptions stringu
        shipping_options = []
        if zasilkovna:
            shipping_options.append(f"zasilkovna:{zasilkovna}")
        if balikovna:
            shipping_options.append(f"balikovna:{balikovna}")
        if osobni is not None and osobni != '':
            shipping_options.append(f"osobni:{osobni}")
        
        listing.price = new_price
        listing.shippingoptions = ",".join(shipping_options) if shipping_options else listing.shippingoptions
        listing.personal_pickup = new_personal_pickup
        listing.description = new_description
        listing.location = new_location
        listing.condition = new_condition
        
        listing.save()
        
        messages.success(request, 'Nabídka byla úspěšně aktualizována!')
        return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
    
    # Parsování současných shipping options pro předvyplnění formuláře
    current_shipping = {'zasilkovna': '49', 'balikovna': '69', 'osobni': '0'}
    if listing.shippingoptions:
        for opt in listing.shippingoptions.split(','):
            parts = opt.split(':')
            if len(parts) == 2:
                current_shipping[parts[0]] = parts[1]
    
    # Debug - vypsat hodnoty
    print(f"DEBUG: listing.price = {listing.price}, type = {type(listing.price)}")
    
    # Zajistit, že price je číslo nebo prázdný string
    display_price = listing.price if listing.price is not None else ''
    
    return render(request, 'divkvariat/listing_edit.html', {
        'book': book,
        'listing': listing,
        'current_shipping': current_shipping,
        'display_price': display_price,  # Přidáno
    })


# -------------------------------------------------------------------
# LISTING SEARCH BOOKS
# -------------------------------------------------------------------
def listing_search_books(request):
    """Ajax endpoint pro vyhledávání knih"""
    if request.method == 'GET' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({'results': []})
        
        # Hledání podle názvu nebo autora
        books = Book.objects.filter(
            Q(title__icontains=query) | 
            Q(titlecz__icontains=query) |
            Q(author__icontains=query)
        ).order_by('-divrating')[:20]
        
        results = []
        for book in books:
            results.append({
                'bookid': book.bookid,
                'title': book.titlecz or book.title,
                'author': book.author,
                'year': book.year,
                'img': book.img,
                'googleid': book.googleid,
                'url': book.url,
            })
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

# -------------------------------------------------------------------
# SEND LISTING AUTO-COMPLETED EMAIL - BUYER
# -------------------------------------------------------------------
def send_listing_auto_completed_email_buyer(listing):
    def _send(listing):
        book = listing.book
        buyer = listing.buyer
        recipient = buyer.email if buyer else None
        if not recipient:
            print("[✖] Kupující nemá e-mail – automatický e-mail neodeslán.")
            return

        context = {
            'buyer_name': buyer.first_name or buyer.username,
            'book_title': book.titlecz,
            'book_url': book.url,
            'listing_id': listing.booklistingid,
        }

        html_email = render_to_string('emails/listing_auto_completed_buyer.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_AUTO_COMPLETED_BUYER").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] Automatický e-mail o dokončení (kupující) odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání automatického e-mailu kupujícímu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
# SEND LISTING AUTO-COMPLETED EMAIL - SELLER
# -------------------------------------------------------------------
def send_listing_auto_completed_email_seller(listing):
    def _send(listing):
        book = listing.book
        seller = listing.user
        recipient = seller.email if seller else None
        if not recipient:
            print("[✖] Prodávající nemá e-mail – automatický e-mail neodeslán.")
            return

        context = {
            'seller_name': seller.first_name or seller.username,
            'book_title': book.titlecz,
            'book_url': book.url,
            'listing_id': listing.booklistingid,
        }

        html_email = render_to_string('emails/listing_auto_completed_seller.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_AUTO_COMPLETED_SELLER").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] Automatický e-mail o dokončení (prodávající) odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání automatického e-mailu prodávajícímu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
#                    SEND LISTING CANCEL EMAIL
# -------------------------------------------------------------------
def send_listing_cancel_email(request_or_user, listing):
    def _send(user, listing):
        book = listing.book
        context = {
            'buyer_name': user.first_name or user.username,
            'book_title': book.titlecz,
        }
        recipient = user.email
        if not recipient:
            print("[✖] Kupující nemá e-mail – e-mail neodeslán.")
            return

        html_email = render_to_string('emails/listing_cancel_reservation_buyer.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_ACTIVE").format(title=book.title)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] E-mail o zrušení rezervace odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání e-mailu: {e}")

    # zjistíme správného uživatele
    if hasattr(request_or_user, "user"):
        user = request_or_user.user
    else:
        user = request_or_user

    threading.Thread(target=_send, args=(user, listing)).start()


# -------------------------------------------------------------------
#                    SEND LISTING EXPIRED EMAIL BUYER
# -------------------------------------------------------------------
def send_listing_expired_email_buyer(listing):
    """Pošle e-mail kupujícímu o vypršení zaplacené transakce (PAID -> EXPIRED)."""
    buyer = listing.buyer
    if not buyer or not buyer.email:
        return

    book = listing.book
    book_title = book.titlecz or book.title

    context = {
        'buyer_name': buyer.first_name or buyer.username,
        'book_title': book_title,
        'listing': listing,
    }

    html_email = render_to_string('emails/listing_expired_buyer.html', context)

    msg = EmailMessage()
    msg['Subject'] = f"Rezervace knihy {book_title} vypršela"
    msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
    msg['To'] = buyer.email
    msg.set_content(html_email, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
            smtp.send_message(msg)
        print(f"[✔] Automatický e-mail o vypršení rezervace odeslán na {buyer.email}")
    except Exception as e:
        print(f"[✖] Chyba při odesílání e-mailu (EXPIRED): {e}")


# -------------------------------------------------------------------
#                    SEND LISTING PAID EXPIRED EMAIL BUYER
# -------------------------------------------------------------------
def send_listing_paid_expired_email_buyer(listing):
    """Pošle e-mail kupujícímu, že jeho zaplacená objednávka byla zrušena (prodejce nepotvrdil odeslání)."""
    book = listing.book
    buyer = listing.buyer

    context = {
        'buyer_name': buyer.first_name or buyer.username,
        'book_title': book.titlecz or book.title,
    }

    recipient = buyer.email
    html_email = render_to_string('emails/listing_paid_expired_buyer.html', context)

    msg = EmailMessage()
    msg['Subject'] = f"Objednávka knihy {book.titlecz or book.title} – zrušena"
    msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
    msg['To'] = recipient
    msg.set_content(html_email, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
            smtp.send_message(msg)
        print(f"[✔] E-mail kupujícímu {recipient} o expirované objednávce byl odeslán.")
    except Exception as e:
        print(f"[✖] Chyba při odesílání e-mailu kupujícímu: {e}")


# -------------------------------------------------------------------
#                    SEND LISTING PAID EXPIRED EMAIL SELLER
# -------------------------------------------------------------------
def send_listing_paid_expired_email_seller(listing):
    """Pošle e-mail prodejci, že jeho nabídka byla zrušena (nepotvrdil odeslání)."""
    book = listing.book
    seller = listing.user

    context = {
        'seller_name': seller.first_name or seller.username,
        'book_title': book.titlecz or book.title,
    }

    recipient = seller.email
    html_email = render_to_string('emails/listing_paid_expired_seller.html', context)

    msg = EmailMessage()
    msg['Subject'] = f"Nabídka knihy {book.titlecz or book.title} – zrušena"
    msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
    msg['To'] = recipient
    msg.set_content(html_email, subtype='html')

    try:
        with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
            smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
            smtp.send_message(msg)
        print(f"[✔] E-mail prodejci {recipient} o expirované nabídce byl odeslán.")
    except Exception as e:
        print(f"[✖] Chyba při odesílání e-mailu prodejci: {e}")


# -------------------------------------------------------------------
#                    SEND LISTING PAYMENT EMAIL
# -------------------------------------------------------------------
def send_listing_payment_confirmation_email(listing):
    def _send(listing):
        book = listing.book
        user = listing.buyer
        if not user or not user.email:
            print("[✖] Kupující nemá e-mail – e-mail neodeslán.")
            return

        amount = int(float(listing.price or 0) + float(listing.commission or 0))
        shipping = int(float(listing.shipping or 0))
        context = {
            'book_title': book.titlecz,
            'buyer_name': user.first_name or user.username,
            'shippingaddress': listing.shippingaddress,
            'amount': amount,
            'shipping': shipping,
            'seller_name': listing.user.first_name or listing.user.username if listing.user else "",
        }

        recipient = user.email
        html_email = render_to_string('emails/listing_paid_confirmation_buyer.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_PAID").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] Potvrzení platby odesláno kupujícímu na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání potvrzení platby: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
#                    SEND LISTING PAYMENT EMAIL
# -------------------------------------------------------------------
def send_listing_payment_email(listing):
    def _send(listing):
        book = listing.book
        buyer = listing.buyer
        seller = listing.user
        recipient = seller.email if seller else None
        if not recipient:
            print("[✖] Prodávající nemá e-mail – e-mail neodeslán.")
            return

        amount = int(float(listing.price or 0) + float(listing.commission or 0))
        shipping = int(float(listing.shipping or 0))

        qr_message = f"Žádost o zaslání knihy '{book.titlecz}' - ID: {book.bookid}"

        context = {
            'buyer_name': buyer.first_name or buyer.username,
            'buyer_id': buyer.id if buyer else "",
            'buyer_phone': buyer.userprofile.phone if hasattr(buyer, "userprofile") else "",
            'buyer_email': buyer.email if buyer else "",
            'book_title': book.titlecz,
            'amount': amount,
            'shipping': shipping,
            'shippingaddress': listing.shippingaddress,
            'user_name': seller.first_name or seller.username if seller else "",
        }

        html_email = render_to_string('emails/listing_paid_confirmation_seller.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_PAID").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] E-mail o zaplacení odeslán prodávajícímu na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání e-mailu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
#                    SEND LISTING PAYMENT REQUEST CONFIRMED
# -------------------------------------------------------------------
# Email po vyplacení
def send_listing_payment_request_confirmed(listing, amount_to_seller):
    def _send(listing, amount_to_seller):
        seller = listing.user
        bankaccount = seller.userprofile.bankaccount if hasattr(seller, "userprofile") else None
        recipient = seller.email if seller else None

        if not recipient:
            print("[✖] Uživatel nemá e-mail – automatický e-mail neodeslán.")
            return

        context = {
            'amount_to_seller': amount_to_seller,
            'bank_account': bankaccount,
        }

        html_email = render_to_string('emails/listing_payment_request_confirmed.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_REQUEST_CONFIRMED")
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] Uživatel dostal e-mail ohledně potvrzení o vyplácení odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání automatického e-mailu pro uživatele: {e}")

    threading.Thread(target=_send, args=(listing, amount_to_seller)).start()


# -------------------------------------------------------------------
#                    SEND LISTING RESERVATION EMAIL
# -------------------------------------------------------------------
@login_required
def send_listing_reservation_email(request, listing_id):
    def _send(listing, request):
        if listing.status in ['RESERVED', 'PENDING']:
            book = listing.book
            buyer = request.user
            book_title = book.titlecz or book.title or ""
            
            total_amount = int(float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0))
            qr_message = f"DIV.cz | {book_title} | {listing.user.username}"
      
            format_code = "5" if listing.listingtype == "BUY" else "6"
            qr_code, vs = qr_code_market(total_amount, listing, qr_message, format_code)

            payment_info = {
                'amount': total_amount,
                'qr_code': qr_code,
                'variable_symbol': vs,
                'note': qr_message, 
            }

            context = {
                'buyer_name': buyer.first_name or buyer.username, 
                'book_title': book.titlecz, 
                'book': book,
                'listing': listing,
                'amount': total_amount,
                'payment_info': payment_info,
                'shippingaddress': listing.shippingaddress,
            }

            recipient = buyer.email
            html_email = render_to_string('emails/listing_send_reservation_buyer.html', context)

            msg = EmailMessage()
            msg['Subject'] = os.getenv("EMAIL_SUBJECT_RESERVED").format(title=book.titlecz)
            msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
            msg['To'] = recipient
            msg.set_content(html_email, subtype='html')

            try:
                with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                    smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                    smtp.send_message(msg)
                print(f"[✔] Rezervační e-mail odeslán na {recipient}")
            except Exception as e:
                print(f"[✖] Chyba při odesílání e-mailu: {e}")
        else:
            print(f"[!] Nabídka není ve stavu pro rezervaci (status: {listing.status}).")

    # získání listing jen jednou na začátku
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    # spuštění v threadu
    threading.Thread(target=_send, args=(listing, request)).start()


# -------------------------------------------------------------------
#                    SEND LISTING SHIPPED EMAIL - BUYER
# -------------------------------------------------------------------
def send_listing_shipped_email(listing):
    def _send(listing):
        buyer = listing.buyer
        book = listing.book
        if not buyer or not buyer.email:
            return
        context = {
            'buyer_name': buyer.first_name or buyer.username,
            'book_title': book.titlecz,
            'listing_id': listing.booklistingid,
            'book_url': book.url,
        }
        html_email = render_to_string('emails/listing_shipped_information_buyer.html', context)
        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_SHIPPED").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = buyer.email
        msg.set_content(html_email, subtype='html')
        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
        except Exception as e:
            print(f"[✖] Chyba při odesílání e-mailu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
#                   SEND LISTING COMPLETED EMAIL - BUYER
# -------------------------------------------------------------------
def send_listing_completed_email_buyer(listing):
    def _send(listing):
        book = listing.book
        buyer = listing.buyer
        recipient = buyer.email if buyer else None
        if not recipient:
            print("[✖] Kupující nemá e-mail – e-mail neodeslán.")
            return

        context = {
            'buyer_name': buyer.first_name or buyer.username,
            'book_title': book.titlecz,
            'book_url': book.url,
            'listing_id': listing.booklistingid,
        }

        html_email = render_to_string('emails/listing_completed_confirmation_buyer.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_COMPLETED_BUYER").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] E-mail o dokončení obchodu (kupující) odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání e-mailu kupujícímu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()


# -------------------------------------------------------------------
#                    SEND LISTING COMPLETED EMAIL - SELLER
# -------------------------------------------------------------------
def send_listing_completed_email_seller(listing):
    def _send(listing):
        book = listing.book
        seller = listing.user
        recipient = seller.email if seller else None
        if not recipient:
            print("[✖] Prodávající nemá e-mail – e-mail neodeslán.")
            return

        context = {
            'seller_name': seller.first_name or seller.username,
            'book_title': book.titlecz,
            'book_url': book.url,
            'listing_id': listing.booklistingid,
        }

        html_email = render_to_string('emails/listing_completed_confirmation_seller.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_COMPLETED_SELLER").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            print(f"[✔] E-mail o dokončení obchodu (prodávající) odeslán na {recipient}")
        except Exception as e:
            print(f"[✖] Chyba při odesílání e-mailu prodávajícímu: {e}")

    threading.Thread(target=_send, args=(listing,)).start()



# -------------------------------------------------------------------
#                    QR CODE MARKET
# -------------------------------------------------------------------
def qr_code_market(amount, listing, message=None, format_code="5"):
    username = listing.user.username if hasattr(listing.user, "username") else "anon"
    
    msg = message or f"{listing.book.titlecz or listing.book.title}-{listing.listingtype}-{username}-DIVcz-{format_code}"
    msg = unicodedata.normalize('NFKD', msg).encode('ascii', 'ignore').decode('ascii').replace(" ", "")
    
    vs = f"01038{format_code}{str(listing.booklistingid).zfill(4)[-4:]}"  # např. 010385012

    qr_string = (
        f"SPD*1.0*ACC:CZ2620100000002602912559"
        f"*AM:{float(amount):.2f}"
        f"*CC:CZK"
        f"*X-VS:{vs}"
        f"*MSG:{msg}"
    )

    img = qrcode.make(qr_string)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return qr_code_base64, vs


# -------------------------------------------------------------------
# F:                 CustomLoginView
# -------------------------------------------------------------------

class CustomLoginView(LoginView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['signup_url'] = reverse('account_signup')  
        return context

class CustomSignupView(SignupView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = reverse('account_login')  
        return context

class CustomLogoutView(LogoutView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['login_url'] = reverse('account_login')  
        return context

# -------------------------------------------------------------------
# F:                 USER PROFILE
# -------------------------------------------------------------------
def user_profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    # Aktivní nabídky (SELL a GIVE)
    active_sell = Booklisting.objects.filter(
        user=profile_user,
        listingtype__in=["SELL", "GIVE"],
        status="ACTIVE"
    ).order_by("-createdat")

    # Aktivní poptávky (BUY)
    active_buy = Booklisting.objects.filter(
        user=profile_user,
        listingtype="BUY",
        status="ACTIVE"
    ).order_by("-createdat")

    # Historie — prodeje, které už skončily
    sold_history = Booklisting.objects.filter(
        user=profile_user,
        status="COMPLETED"
    ).order_by("-completedat")

    # Historie — nákupy
    bought_history = Booklisting.objects.filter(
        buyer=profile_user,
        status="COMPLETED"
    ).order_by("-completedat")

    return render(request, "divkvariat/user_profile.html", {
        "profile_user": profile_user,
        "active_sell": active_sell,
        "active_buy": active_buy,
        "sold_history": sold_history,
        "bought_history": bought_history,
    })
# -------------------------------------------------------------------
# F:                 USER EDIT
# -------------------------------------------------------------------
@login_required
def account_edit(request):
    profile = Userprofile.objects.get_or_create(user=request.user)[0]

    if request.method == "POST":
        # User model
        request.user.email = request.POST.get("email", "").strip()
        request.user.first_name = request.POST.get("first_name", "").strip()
        request.user.last_name = request.POST.get("last_name", "").strip()
        request.user.save()

        # Userprofile (telefon, adresa, účet)
        profile.phone = request.POST.get("phone", "").strip()
        profile.shippingaddress = request.POST.get("shippingaddress", "").strip()
        profile.bankaccount = request.POST.get("bankaccount", "").strip()
        profile.save()

        messages.success(request, "Údaje byly úspěšně uloženy.")
        return redirect("account_edit")

    return render(request, "divkvariat/account/account_edit.html", {
        "profile": profile,
    })


# -------------------------------------------------------------------
# F:                 ACCOUNT VIEW
# -------------------------------------------------------------------
@login_required
def account_view(request):
    return render(request, "divkvariat/account/account_edit.html", {
        "user": request.user,
        "profile": request.user.userprofile,
    })


# -------------------------------------------------------------------
# F:                 USER BOOK LISTINGS
# -------------------------------------------------------------------
# A N T I K V A R I Á T
def user_book_listings(request, user_id):
    """Přehledová stránka všech nabídek uživatele."""
    user = get_object_or_404(User, id=user_id)
    
    # Získání prodejních nabídek
    sell_listings = Booklisting.objects.filter(
        user=user,
        listingtype__in=['SELL', 'GIVE'],
        active=True
    ).order_by('-createdat')[:5]
    
    # Získání poptávek
    buy_listings = Booklisting.objects.filter(
        user=user,
        listingtype='BUY',
        active=True
    ).order_by('-createdat')[:5]
    
    # Získání hodnocení jako prodejce
    seller_ratings = Booklisting.objects.filter(
        user=user,
        status='COMPLETED',
        sellerrating__isnull=False
    )
    avg_seller_rating = seller_ratings.aggregate(Avg('sellerrating'))['sellerrating__avg']
    seller_ratings_count = seller_ratings.count()
    
    # Získání hodnocení jako kupující
    buyer_ratings = Booklisting.objects.filter(
        buyer=user,
        status='COMPLETED',
        buyerrating__isnull=False
    )
    avg_buyer_rating = buyer_ratings.aggregate(Avg('buyerrating'))['buyerrating__avg']
    buyer_ratings_count = buyer_ratings.count()
    
    return render(request, 'divkvariat/user_book_listings.html', {  # změněna cesta k šabloně
        'profile_user': user,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings,
        'seller_rating': avg_seller_rating,
        'seller_ratings_count': seller_ratings_count,
        'buyer_rating': avg_buyer_rating,
        'buyer_ratings_count': buyer_ratings_count
    })


# -------------------------------------------------------------------
# F:                 USER_SELL_LISTINGS
# -------------------------------------------------------------------
def user_sell_listings(request, user_id):
    """Seznam všech prodejních nabídek uživatele."""
    user = get_object_or_404(User, id=user_id)
    listings = (
        Booklisting.objects
        .filter(user=user, listingtype__in=['SELL', 'GIVE'], status='ACTIVE')
        .order_by('-createdat')
    )

    
    # Získání průměrného hodnocení jako prodejce
    sellerratings = Booklisting.objects.filter(
        user=user,
        status='COMPLETED',
        sellerrating__isnull=False
    )
    avg_rating = sellerratings.aggregate(Avg('sellerrating'))['sellerrating__avg']
    
    return render(request, 'divkvariat/user_book_sell.html', {
        'profile_user': user,
        'listings': listings,
        'avg_rating': avg_rating,
        'total_ratings': sellerratings.count()
    })


# -------------------------------------------------------------------
# F:                 USER BUY LISTINGS
# -------------------------------------------------------------------
def user_buy_listings(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    listings = (Booklisting.objects.filter(
        user=profile_user,
        listingtype='BUY',
        status='ACTIVE'
    ).order_by('-createdat')
    )
   
    buyer_ratings = Booklisting.objects.filter(
        buyer=profile_user,
        status='COMPLETED',
        buyerrating__isnull=False
    )
    avg_rating = buyer_ratings.aggregate(Avg('buyerrating'))['buyerrating__avg']
   
    return render(request, 'divkvariat/user_book_buy.html', {
       'profile_user': profile_user,
        'listings': listings,
        'avg_rating': avg_rating, 
        'total_ratings': buyer_ratings.count()
    })


# -------------------------------------------------------------------
# F:                 SEARCH VIEW
# -------------------------------------------------------------------
def search_view(request):
    query = request.GET.get("q", "").strip()
    books = []
    listings = []

    if query:
        # Vyhledávání knih
        books = Book.objects.filter(
            Q(title__icontains=query) |
            Q(titlecz__icontains=query) |
            Q(author__icontains=query)
        ).order_by("title")[:30]

        # Vyhledávání v nabídce i poptávce
        listings = Booklisting.objects.filter(
            Q(book__title__icontains=query) |
            Q(book__titlecz__icontains=query) |
            Q(book__author__icontains=query),
            active=True
        ).select_related("book", "user").order_by("-createdat")

    # Stránkování
    paginator = Paginator(listings, 18)
    page = request.GET.get("page")
    listings_page = paginator.get_page(page)

    return render(request, "divkvariat/search.html", {
        "query": query,
        "books": books,
        "listings": listings_page,
    })

# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------