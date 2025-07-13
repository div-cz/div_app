# VIEWS.DIVKVARIAT.PY

import base64
import smtplib
import os
import qrcode
import unicodedata

from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from div_content.models import Book, Booklisting
from io import BytesIO

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



# e-mail pro kupujícího REZERVACE
@login_required
def send_listing_reservation_email(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    if listing.status in ['RESERVED', 'PENDING']:
        book = listing.book
        total_amount = listing.price 
        qr_message = f"Platba za rezervaci knihy '{book.titlecz}' - ID: {book.bookid}"
  

        payment_info = {
            'total': total_amount,
            'qr_code': qr_code_market(total_amount, book.bookid, qr_message),
            'variable_symbol': book.bookid,
            'note': qr_message, 
        }


        context = {
            'buyer_name': request.user.first_name or request.user.username, 
            'book_title': book.titlecz, 
            'amount': listing.price,
            'payment_info': payment_info,
        }

        recipient = request.user.email

        html_email =  render_to_string('emails/reservation_message.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_RESERVED")
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            messages.success(request, f"Potvrzeni rezervace bylo poslano na vas  e-mail: <strong>{recipient}</strong>.")
        except Exception as e:
            messages.error(request, f"Chyba pri odeslani e-mailu: {e}")

    else:
        messages.warning(request, f"Nabidka neni ve stavu pro rezervaci (status: {listing.status}).")


# e-mail RESERVED - Zrušení rezervace
@login_required
def send_listing_cancel_email(request, listing_id):
 listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)
 book = listing.book 
 context = {
        'buyer_name': request.user.first_name or request.user.username, 
        'book_title': book.title,
        }
 recipient = request.user.email 
 html_email =  render_to_string('emails/cancel_reservation_message.html', context)

 msg = EmailMessage()
 msg['Subject'] = os.getenv("EMAIL_SUBJECT_CANCELLATION").format(title=book.title)
 msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
 msg['To'] = recipient
 msg.set_content(html_email, subtype='html')

 try:
     with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
          smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
          smtp.send_message(msg)
     messages.success(request, f"Informace o zruseni rezervace bylo poslano na email: <strong>{recipient}</strong>.")
 except Exception as e:
            messages.error(request, f"Chyba pri odeslani  e-mailu: {e}")
 
 
# e-mail PAID - výzva k zaslání knihy
@login_required
def send_listing_payment_email(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    if listing.status in ['PAID']:
        book = listing.book
        total_amount = listing.price 
        qr_message = f"Žádost o zaslání knihy '{book.titlecz}' - ID: {book.bookid}" 
        shipping = listing.shipping
        buyer_adress = UserProfile.adress

        context = {
            'buyer_name': request.user.first_name or request.user.username, 
            'book_title': book.titlecz, 
            'amount': listing.price,
            'shipping': shipping,
            'buyer_adress': buyer-adress

        }

        recipient = request.user.email

        html_email =  render_to_string('emails/payment_message.html', context)

        msg = EmailMessage()
        msg['Subject'] = os.getenv("EMAIL_SUBJECT_PAID")
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(html_email, subtype='html')

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            messages.success(request, f"Zadost o zaslani knihy byla zaslana na email : <strong>{recipient}</strong>.")
        except Exception as e:
            messages.error(request, f"Chyba v odeslani emailu {e}")



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

    if request.method == 'POST' and request.user.is_authenticated:
        # REZERVACE
        if 'reserve_listing' in request.POST and request.user != listing.user:
            if listing.status != 'ACTIVE':
                messages.error(request, 'Nabídka již není aktivní.')
            else:
                listing.status = 'RESERVED'
                listing.buyer = request.user
                listing.save()
                messages.success(request, 'Nabídka byla rezervována.')
                send_listing_reservation_email(request, listing.booklistingid)
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)


        # DOKONČENÍ (pro prodávajícího)
        elif 'complete_listing' in request.POST and request.user == listing.user:
            if listing.status != 'RESERVED':
                messages.error(request, 'Nabídka není ve stavu pro dokončení.')
            else:
                listing.status = 'COMPLETED'
                listing.completedat = timezone.now()
                listing.save()
                messages.success(request, 'Transakce byla dokončena.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)

        # ZRUŠENÍ REZERVACE (pro kupujícího)
        elif 'cancel_reservation' in request.POST and request.user == listing.buyer:
            if listing.status == 'RESERVED':
                listing.status = 'ACTIVE'
                listing.buyer = None
                listing.save()
                messages.success(request, 'Rezervace byla zrušena a nabídka vrácena do aktivního stavu.')
                return redirect('listing_detail_sell', book_url=book_url, listing_id=listing_id)
            else:
                messages.error(request, 'Tuto rezervaci nelze zrušit.')

        # Hodnocení prodávající/kupující
        elif 'sellerrating' in request.POST and request.user == listing.user:
            if listing.buyerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.buyerrating = request.POST.get('rating')
                listing.buyercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení kupujícího bylo přidáno.')

        elif 'buyerrating' in request.POST and request.user == listing.buyer:
            if listing.sellerrating:
                messages.error(request, 'Hodnocení již bylo přidáno.')
            else:
                listing.sellerrating = request.POST.get('rating')
                listing.sellercomment = request.POST.get('comment')
                listing.save()
                messages.success(request, 'Hodnocení prodejce bylo přidáno.')

    # QR platba 
    payment_info = None
    if listing.status == 'RESERVED' and listing.buyer == request.user:
        total_amount = float(listing.price or 0) + float(listing.shipping or 0) + float(listing.commission or 0)
        qr_message = f"{book.title}|{listing.user.username}"
        # Prodej/koupě: zjisti, zda je typ 5 nebo 6 (můžeš to mít v listing.listingtype apod.)
        format_code = "5" if listing.listingtype == "BUY" else "6"  # uprav dle své logiky
        qr_code, vs = qr_code_market(total_amount, listing, qr_message, format_code)
        payment_info = {
            'total': total_amount,
            'qr_code': qr_code,
            'variable_symbol': vs,
            'note': qr_message
        }


    elif 'cancel_offer' in request.POST and request.user == listing.user:
            if listing.status == 'ACTIVE' or listing.status == 'RESERVED':
                listing.delete()
                messages.success(request, 'Nabídka byla úspěšně zrušena.')
                return redirect('book_listings', book_url=book_url)
            else:
                messages.error(request, 'Tuto nabídku nelze zrušit v aktuálním stavu.')      

    # Možnost hodnocení/zrušení pro správného uživatele
    can_rate_seller = (listing.status == 'COMPLETED' and request.user == listing.buyer and not listing.sellerrating)
    can_rate_buyer = (listing.status == 'COMPLETED' and request.user == listing.user and not listing.buyerrating)
    can_cancel_reservation = (listing.status == 'RESERVED' and request.user == listing.buyer)

    can_cancel_offer = (request.user == listing.user and listing.status in ['ACTIVE', 'RESERVED'])


    return render(request, 'books/listing_detail.html', {
        'book': book,
        'listing': listing,
        'payment_info': payment_info,
        'can_rate_seller': can_rate_seller,
        'can_rate_buyer': can_rate_buyer,
        'can_cancel_reservation': can_cancel_reservation,
        'can_cancel_offer': can_cancel_offer,
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
def cancel_sell(request, listing_id):
    listing_to_cancel = get_object_or_404(Booklisting, booklistingid=listing_id, user=request.user)

    if request.method == "POST":
        if listing_to_cancel.status == 'ACTIVE' or listing_to_cancel.status == 'RESERVED':
            old_status = listing_to_cancel.status

            listing_to_cancel.status = "CANCELLED"
            listing_to_cancel.active = False
            
            if old_status == 'RESERVED':
                listing_to_cancel.buyer = None
                messages.info(request, "Přiřazený kupující byl odstraněn.")

            listing_to_cancel.save()

            messages.success(request, f'Vaše nabídka knihy "{listing_to_cancel.book.titlecz}" byla úspěšně zrušena.')
            
            return redirect('index')
        else:
            messages.error(request, f'Nabídku knihy nelze zrušit".')
            return redirect('index')

    return render(request, "books/market_cancel_offer.html", {"listing_offer": listing_to_cancel})   




@login_required
def confirm_sale(request, purchase_id):
    purchase = get_object_or_404(Bookpurchase, id=purchase_id, seller=request.user)
    if request.method == "POST":
        purchase.status = "completed"
        purchase.completedat = timezone.now()
        purchase.save()
        return redirect("index")
    return render(request, "books/market_confirm_sale.html", {"purchase": purchase})
