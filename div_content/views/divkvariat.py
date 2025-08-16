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
# listing_detail                    |
# send_listing_cancel_email         |
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
import unicodedata

from div_content.models import Book, Booklisting, Userprofile

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import EmailMessage 
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.template.loader import render_to_string

from django.utils.timezone import now
from django.utils import timezone



from dotenv import load_dotenv
from email.message import EmailMessage
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
    from div_content.models import Booklisting

    count_sell = Booklisting.objects.filter(listingtype__in=["SELL", "GIVE"], active=True).count()
    count_buy = Booklisting.objects.filter(listingtype="BUY", active=True).count()

    all_listings = list(Booklisting.objects.filter(active=True, status="ACTIVE")[:100])
    random_listings = sample(all_listings, min(len(all_listings), 4))  # max 4

    return render(request, "books/antikvariat_home.html", {
        "count_sell": count_sell,
        "count_buy": count_buy,
        "random_listings": random_listings,
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
        .filter(listingtype__in=['SELL', 'GIVE'], active=True, status='ACTIVE')
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
            return redirect('index') 
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
            listing_to_cancel.delete()
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
#                    LISTING DETAIL
# -------------------------------------------------------------------
def listing_detail(request, book_url, listing_id):
    book = get_object_or_404(Book, url=book_url)
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, book=book)

    if request.method == 'POST' and request.user.is_authenticated:
        # REZERVACE
        if 'reserve_listing' in request.POST and request.user != listing.user:
            if listing.status != 'ACTIVE':
                messages.error(request, 'Nabídka již není aktivní.')
            else:
                commission_input = request.POST.get("commission", "").strip()
                try:
                    commission = int(commission_input)
                    if commission < 0:
                        commission = 0
                except:
                    commission = 10  # výchozí hodnota
    
                listing.commission = commission
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


        # Poslánjí knihy
        elif 'shipping_listing' in request.POST and request.user == listing.user: 
            if listing.status != 'PAID':
                messages.error(request, 'Nabídka není ve stavu pro potvrzení odeslání knihy.')
            else:
                listing.status = 'SHIPPED'
                listing.save()
                messages.success(request, 'Odeslání knihy bylo potvrzení')
                send_listing_shipped_email(listing)
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)


        # DOKONČENÍ (pro prodávajícího)
        elif 'complete_listing' in request.POST and request.user == listing.buyer:
            if listing.status not in ['SHIPPED', 'PAID']:
                messages.error(request, 'Nabídka není ve stavu pro dokončení.')
            else:
                listing.status = 'COMPLETED'
                listing.save()
                send_listing_completed_email_buyer(listing)
                send_listing_completed_email_seller(listing)
                messages.success(request, 'Transakce byla dokončena.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)


        # DOKONČENÍ (pro prodávajícího)
        elif 'complete_listing' in request.POST and request.user == listing.user:
            if listing.status != 'RESERVED':
                messages.error(request, 'Nabídka není ve stavu pro dokončení.')
            else:
                listing.status = 'COMPLETED'
                listing.completedat = timezone.now()
                listing.save()
                send_listing_completed_email_buyer(listing)
                send_listing_completed_email_seller(listing)
                messages.success(request, 'Transakce byla dokončena.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)


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
        qr_message = f"{book_title}|{listing.user.username}"
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


    return render(request, 'books/listing_detail.html', {
        'book': book,
        'listing': listing,
        'payment_info': payment_info,
        'can_rate_seller': can_rate_seller,
        'can_rate_buyer': can_rate_buyer,
        'can_cancel_reservation': can_cancel_reservation,
        'can_cancel_offer': can_cancel_offer,
        'can_confirm_shipping': can_confirm_shipping,    
        'can_complete_transaction': can_complete_transaction,
        'debug_post': debug_post,
        'recent_sell_listings': recent_sell_listings,
        'recent_buy_listings': recent_buy_listings,
    })


# -------------------------------------------------------------------
#                    SEND LISTING CANCEL EMAIL
# -------------------------------------------------------------------

def send_listing_cancel_email(request_or_user, listing):
    if hasattr(request_or_user, "user"):
        user = request_or_user.user
    else:
        user = request_or_user

    book = listing.book
    context = {
        'buyer_name': user.first_name or user.username,
        'book_title': book.titlecz,
    }
    recipient = user.email
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



# -------------------------------------------------------------------
#                    SEND LISTING PAYMENT EMAIL
# -------------------------------------------------------------------

def send_listing_payment_confirmation_email(listing):
    book = listing.book
    user = listing.buyer
    if not user or not user.email:
        return
    context = {
        'book_title': book.titlecz,
        'buyer_name': user.first_name or user.username,
        'shippingaddress': listing.shippingaddress,
    }
    recipient = user.email
    html_email = render_to_string('emails/listing_paid_confirmation_buyer.html', context)

    msg = EmailMessage()
    msg['Subject'] = os.getenv("EMAIL_SUBJECT_PAID").format(title=book.titlecz)
    msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
    msg['To'] = recipient
    msg.set_content(html_email, subtype='html')

    with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
        smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
        smtp.send_message(msg)

# -------------------------------------------------------------------
#                    SEND LISTING PAYMENT EMAIL
# -------------------------------------------------------------------

def send_listing_payment_email(listing):
    book = listing.book
    buyer = listing.buyer
    seller = listing.user
    recipient = seller.email if seller else None
    if not recipient:
        print("[✖] Kupující nemá e-mail – e-mail neodeslán.")
        return

    qr_message = f"Žádost o zaslání knihy '{book.titlecz}' - ID: {book.bookid}"

    context = {
        'buyer_name': buyer.first_name or buyer.username,
        'book_title': book.titlecz,
        'total': float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0),
        'shipping': listing.shipping,
        'shippingaddress': listing.shippingaddress,
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
        print(f"[✔] E-mail o zaplacení odeslán kupujícímu na {recipient}")
    except Exception as e:
        print(f"[✖] Chyba při odesílání e-mailu: {e}")


# -------------------------------------------------------------------
#                    SEND LISTING RESERVATION EMAIL
# -------------------------------------------------------------------
@login_required
def send_listing_reservation_email(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    if listing.status in ['RESERVED', 'PENDING']:
        book = listing.book
        total_amount = int(float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0))
        qr_message = f"Platba za knihu {book.titlecz} na DIV.cz - ID: {book.bookid}"
  

        payment_info = {
            'amount': total_amount,
            'qr_code': qr_code_market(total_amount, listing, qr_message)[0],
            'variable_symbol': qr_code_market(total_amount, listing, qr_message)[1],
            'note': qr_message, 
        }


        context = {
            'buyer_name': request.user.first_name or request.user.username, 
            'book_title': book.titlecz, 
            'amount': int(float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0)),
            'payment_info': payment_info,
            'shippingaddress': listing.shippingaddress,
        }

        recipient = request.user.email

        html_email =  render_to_string('emails/listing_send_reservation_buyer.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_RESERVED").format(title=book.titlecz)
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            messages.success(request, f"Potvrzeni rezervace bylo poslano na vas  e-mail: <strong>{recipient}</strong>. Zaplatte prosím pomocí QR kodu na této stránce nebo v emailu. Zkontrolujte radši i spam. :)")
        except Exception as e:
            messages.error(request, f"Chyba pri odeslani e-mailu: {e}")

    else:
        messages.warning(request, f"Nabidka neni ve stavu pro rezervaci (status: {listing.status}).")


# -------------------------------------------------------------------
#                    SEND LISTING SHIPPED EMAIL - BUYER
# -------------------------------------------------------------------
def send_listing_shipped_email(listing):
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
        print(f"[✔] E-mail o odeslání knihy poslán kupujícímu na {buyer.email}")
    except Exception as e:
        print(f"[✖] Chyba při odesílání e-mailu kupujícímu: {e}")


# -------------------------------------------------------------------
#                    SEND LISTING COMPLETED EMAIL - BUYER
# -------------------------------------------------------------------
def send_listing_completed_email_buyer(listing):
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


# -------------------------------------------------------------------
#                    SEND LISTING COMPLETED EMAIL - SELLER
# -------------------------------------------------------------------
def send_listing_completed_email_seller(listing):
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