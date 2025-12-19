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
import smtplib
import os
import qrcode
import threading
import unicodedata

from datetime import timedelta

from div_content.forms.divkvariat import BookListingForm
from div_content.utils.divkvariat import compress_image
from div_content.models import Book, Booklisting, Booklistingimage, Userprofile

from django.contrib.auth.decorators import login_required
from django.contrib import messages
#from django.core.mail import EmailMessage 
from django.core.paginator import Paginator

from django.db.models import Sum, F, Q
from django.http import JsonResponse

from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from django.views.decorators.http import require_POST


from django.utils import timezone
from django.utils.timezone import now


from dotenv import load_dotenv
from email.message import EmailMessage as PyEmailMessage

from io import BytesIO

# -------------------------------------------------------------------
#                    KONSTANTY
# -------------------------------------------------------------------



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
    return render(request, "books/antikvariat_home.html", final_context)


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
    
    return render(request, 'books/listings.html', {
        'book': book,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings
    })


# -------------------------------------------------------------------
#                    BOOKS MARKET OFFERS
# -------------------------------------------------------------------
def books_market_offers(request):
    #View for sell/give offers
    sell_listings = (Booklisting.objects
        .filter(listingtype__in=['SELL'], active=True, status='ACTIVE')
        .select_related('book', 'user')
        .order_by('-createdat'))
    
    paginator = Paginator(sell_listings, 12)
    page = request.GET.get('page')
    listings = paginator.get_page(page)

    return render(request, 'books/books_market_offers.html', {
        'listings': listings
    })


# -------------------------------------------------------------------
#                    BOOK MARKET WANTS
# -------------------------------------------------------------------
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
            return redirect('index')


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
        return redirect("index")
    return render(request, "books/market_confirm_sale.html", {"purchase": purchase})


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
            return redirect('index')
        else:
            messages.error(request, 'Tuto nabídku nelze smazat v aktuálním stavu.')
            return redirect('index')

    return render(request, "books/market_cancel_offer.html", {"listing_offer": listing_to_cancel})


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

    msg = PyEmailMessage()
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
        return redirect('login')
    
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
                    return redirect('book_detail', book_url=book.url)
            except Book.DoesNotExist:
                messages.error(request, 'Kniha nebyla nalezena.')
    else:
        if selected_book:
            booklisting_form = BookListingForm(user=request.user)
    
    return render(request, 'books/listing_add_book.html', {
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

    # seřadit možnosti poštovného, aby osobní nebyl první
    if listing.shippingoptions:
        options = listing.shippingoptions.split(",")
        paid_options = [o for o in options if not o.startswith("OSOBNI")]
        personal_options = [o for o in options if o.startswith("OSOBNI")]
        sorted_options = paid_options + personal_options
        listing.shippingoptions = ",".join(sorted_options)


    return render(request, 'books/listing_detail.html', {
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
    book = get_object_or_404(Book, url=book_url)
    listing = get_object_or_404(
        Booklisting,
        booklistingid=listing_id,
        book=book,
        user=request.user,
        status='ACTIVE'
    )

    # Parsování aktuálních shipping options
    current_shipping = {}
    if listing.shippingoptions:
        for opt in listing.shippingoptions.split(","):
            parts = opt.split(":")
            if len(parts) == 2:
                current_shipping[parts[0]] = parts[1]

    if request.method == "POST":
        # Manuální zpracování POST dat
        listing.price = request.POST.get("new_price", listing.price)
        listing.description = request.POST.get("new_description", "")
        listing.condition = request.POST.get("condition") or request.POST.get("new_condition")
        listing.location = request.POST.get("new_location", "")

        listing.editionyear = request.POST.get("editionyear") or None
        listing.firstedition = bool(request.POST.get("firstedition"))
        listing.edition_note = request.POST.get("edition_note", "")
    
        # Zpracování shipping options
        options = []
        if request.POST.get("personal_pickup"):
            options.append("OSOBNI:0")
        
        # Pro div.cz (shipping_zasilkovna + shipping_zasilkovna_price)
        if request.POST.get("shipping_zasilkovna"):
            price = request.POST.get("shipping_zasilkovna_price", "89")
            options.append(f"ZASILKOVNA:{price}")
        
        # Pro divkvariat.cz (enable_zasilkovna + shipping_zasilkovna jako cena)
        if request.POST.get("enable_zasilkovna"):
            price = request.POST.get("shipping_zasilkovna", "89")
            options.append(f"ZASILKOVNA:{price}")
        
        # Balíkovna
        if request.POST.get("shipping_balikovna") or request.POST.get("enable_balikovna"):
            price = request.POST.get("shipping_balikovna_price") or request.POST.get("shipping_balikovna", "99")
            options.append(f"BALIKOVNA:{price}")
        
        # Pošta
        if request.POST.get("shipping_posta") or request.POST.get("enable_posta"):
            price = request.POST.get("shipping_posta_price") or request.POST.get("shipping_posta", "109")
            options.append(f"POSTA:{price}")
        
        listing.shippingoptions = ",".join(options)
        listing.save()
        
        messages.success(request, "Nabídka byla aktualizována.")
        return redirect("listing_detail_sell", book_url=book.url, listing_id=listing.booklistingid)
    
    return render(request, "books/listing_edit.html", {
        "book": book,
        "listing": listing,
        "current_shipping": current_shipping,
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

        msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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

    msg = PyEmailMessage()
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

    msg = PyEmailMessage()
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

    msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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


@login_required
def listing_upload_image(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, user=request.user)

    files = request.FILES.getlist("images") or request.FILES.getlist("image")
    if request.method == "POST" and files:
        for img in request.FILES.getlist("images"):
            compressed = compress_image(img)
            Booklistingimage.objects.create(listing=listing, image=compressed)

        messages.success(request, "Fotografie byly nahrány.")
        return redirect("listing_detail_sell", book_url=listing.book.url, listing_id=listing.booklistingid)

    return JsonResponse({"error": "No image uploaded"}, status=400)


@login_required
def listing_delete_image(request, image_id):
    image = get_object_or_404(Booklistingimage, id=image_id, listing__user=request.user)

    listing = image.listing
    image.image.delete(save=False)
    image.delete()

    messages.success(request, "Fotografie byla smazána.")
    return redirect("listing_detail_sell", book_url=listing.book.url, listing_id=listing.booklistingid)


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

        msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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

            msg = PyEmailMessage()
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
        msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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

        msg = PyEmailMessage()
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
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------