# VIEWS.DIVKVARIAT.PY


from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
import smtplib
import os

from div_content.models import Booklisting







@login_required
def send_listing_reservation_email(request, listing_id):
    listing = get_object_or_404(Booklisting, booklistingid=listing_id, buyer=request.user)

    if listing.status in ['RESERVED', 'PENDING']:
        book = listing.book
        recipient = request.user.email

        msg = EmailMessage()
        msg['Subject'] = f"Rezervace knihy z DIVkvariátu: {book.title}"
        msg['From'] = os.getenv("ANTIKVARIAT_ADDRESS")
        msg['To'] = recipient
        msg.set_content(
            f"Zarezervovali jste si knihu {book.title}. Prosíme, zaplaťte cenu dle platebních údajů v detailu nabídky.\n\nDěkujeme,\nTým DIV.cz"
        )

        try:
            with smtplib.SMTP_SSL("smtp.seznam.cz", 465) as smtp:
                smtp.login(os.getenv("ANTIKVARIAT_ADDRESS"), os.getenv("ANTIKVARIAT_PASSWORD"))
                smtp.send_message(msg)
            messages.success(request, f"Potvrzení rezervace bylo posláno na váš e-mail: <strong>{recipient}</strong>.")
        except Exception as e:
            messages.error(request, f"Chyba při odesílání e-mailu: {e}")

    else:
        messages.warning(request, f"Nabídka není ve stavu pro rezervaci (status: {listing.status}).")

    return redirect("listing_detail_sell", book_url=listing.book.url, listing_id=listing.booklistingid)

    



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

    # QR platba atd – pouze pokud chceš
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


    # Možnost hodnocení/zrušení pro správného uživatele
    can_rate_seller = (listing.status == 'COMPLETED' and request.user == listing.buyer and not listing.sellerrating)
    can_rate_buyer = (listing.status == 'COMPLETED' and request.user == listing.user and not listing.buyerrating)
    can_cancel_reservation = (listing.status == 'RESERVED' and request.user == listing.buyer)

    return render(request, 'books/listing_detail.html', {
        'book': book,
        'listing': listing,
        'payment_info': payment_info,
        'can_rate_seller': can_rate_seller,
        'can_rate_buyer': can_rate_buyer,
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
