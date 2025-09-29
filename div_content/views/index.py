# VIEWS.INDEX.PY TEST


import math
import qrcode

from datetime import date
from io import BytesIO
from django.contrib import messages

from div_content.forms.admins import TaskCommentForm, TaskForm
from div_content.forms.index import ArticleForm, ArticlenewsForm
from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (

    AATask, Article, Articlenews, Book, Bookcomments, Booklisting, Bookpurchase, Creator, Creatorbiography, Game, Gamecomments, 
    Metacharts, Metagenre, Metaindex, Metalocation,  Metastats, Movie, Moviecinema, Moviedistributor, Moviecomments, Moviecrew, Moviegenre, Movierating, 
    Tvgenre, Tvshow, User, Userprofile

)
from div_content.utils.books import get_market_listings

from div_content.views.divkvariat import qr_code_market, send_listing_payment_request_confirmed
from div_content.views.login import custom_login_view

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.contenttypes.models import ContentType

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

#importy pro zasílání e-mailu
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from dotenv import load_dotenv
import os
import smtplib

# for index
from django.db import models
from django.db.models import Avg, Count, Q
from django.db.models.functions import ExtractYear
from django.db.models import F, Sum, Count
from django.utils import timezone
from itertools import chain
from operator import attrgetter

from star_ratings.models import Rating, UserRating


#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')
def redirect_view(request):

    return redirect('https://div.cz')


# TASK MANAGEMENT 
def get_sorted_tasks(user):
    # Získáme všechny hlavní úkoly (bez parentid)
    main_tasks = AATask.objects.filter(
        parentid__isnull=True,
        status__in=['Ke zpracování', 'Probíhá']
    ).order_by('-created')[:10]
    
    # Seřadíme podle assigned
    user_tasks = []
    unassigned_tasks = []
    other_tasks = []
    
    for task in main_tasks:
        if task.assigned == user.username:
            user_tasks.append(task)
        elif task.assigned == 'Nikdo':
            unassigned_tasks.append(task)
        else:
            other_tasks.append(task)
            
    return user_tasks + unassigned_tasks + other_tasks

    movies_comments_9 = Moviecomments.objects.select_related('movieid', 'user').order_by(
            '-commentid').values('comment', 'movieid__titlecz', 'movieid__url', 'movieid', 'user', 'user__username')[:5]


def index(request): # hlavní strana
    user = request.user 
    request_qr_code = None
    bankaccount = None
    if request.user.is_authenticated:
         bankaccount = request.user.userprofile.bankaccount

    # Články
    if request.user.is_superuser or request.user.is_staff:
        article_form = ArticleForm(request.POST or None)
        articlenews_form = ArticlenewsForm(request.POST or None)
        
        if request.method == 'POST':
            if 'article_submit' in request.POST and article_form.is_valid():
                article = article_form.save(commit=False)
                article.save()
                return redirect('index')

            if 'articlenews_submit' in request.POST and articlenews_form.is_valid():
                articlenews = articlenews_form.save(commit=False)
                articlenews.userid = request.user
                articlenews.save()
                return redirect('index')
    else:
        article_form = None
        articlenews_form = None

    # Zpracování POST požadavku na vyplacení peněz (pouze pro superuživatele)
    pending_payouts_list = None
    if request.user.is_authenticated and request.user.is_superuser:
        if request.method == 'POST' and 'confirm_user_payment' in request.POST:
            user_id_to_pay = request.POST.get('user_id')
            if user_id_to_pay:
                transactions_to_pay = Booklisting.objects.filter(
                    user_id=user_id_to_pay,
                    status='COMPLETED',
                    paidtoseller=False,
                    requestpayout=True,
                )
                
                total_amount_for_user = transactions_to_pay.aggregate(total_amount=Sum(F('price') + F('shipping')))['total_amount'] or 0

                listing = transactions_to_pay.first()

                if listing:
                    transactions_to_pay.update(
                        paidtoseller=True,
                        paidat=timezone.now(),
                        requestpayout=False,
                        amounttoseller=F('price') + F('shipping'), 
                    )

                    qr_code_base64, vs = qr_code_market(total_amount_for_user, listing)
                    request_qr_code = qr_code_base64

                    # Předáme vypočtenou hodnotu "total_amount_for_user" přímo do funkce.
                    send_listing_payment_request_confirmed(listing, total_amount_for_user)
                    messages.success(request, f'Vyplacení částky {total_amount_for_user} Kč bylo potvrzeno.')
                else:
                    messages.warning(request, 'Pro tohoto uživatele nebyly nalezeny žádné čekající žádosti o vyplacení.')
                return redirect('index')
                
        # Získání záznamů, které mají flag requestpayout=True
        pending_payouts_list = Booklisting.objects.filter(
            status='COMPLETED',
            paidtoseller=False,
            requestpayout=True,
        ).values('user').annotate(
            total_amount=Sum(F('price') + F('shipping')),
            user_name=F('user__first_name'),
            username=F('user__username'),
        )


        # QR 
        if pending_payouts_list:
            first_payout_data = pending_payouts_list.order_by('user').first()
            first_listing = Booklisting.objects.filter(user_id=first_payout_data['user']).first()
            if first_listing:
                # původní volání
                qr_code_base64, vs = qr_code_market(first_payout_data['total_amount'], first_listing)

                import base64, qrcode
                from io import BytesIO

                # převod číslo/kód na IBAN
                def to_iban(account_number: str) -> str:
                    account_number = account_number.replace(" ", "")
                    if "/" not in account_number:
                        # jen zalogovat a nepadat
                        print(f"[!] Účet bez kódu banky: {account_number}")
                        return ""
                    number, bank_code = account_number.split("/")
                    if "-" in number:
                        prefix, base = number.split("-")
                    else:
                        prefix, base = "0", number
                    prefix = prefix.zfill(6)
                    base = base.zfill(10)
                    bban = f"{bank_code}{prefix}{base}"
                    tmp = bban + "123500"  # "CZ00" → C=12, Z=35, 00
                    check = 98 - (int(tmp) % 97)
                    return f"CZ{check:02d}{bban}"

                # IBAN pro účet z profilu nebo fallback
                profile = getattr(first_listing.user, "userprofile", None)
                account_raw = None
                if profile and profile.bankaccount:
                    account_raw = profile.bankaccount.strip().replace(" ", "")
                if not account_raw:
                    account_raw = "2401444218/2010"  # fallback

                iban = to_iban(account_raw)
                amount = float(first_payout_data['total_amount'])
                vs = vs or ""
                msg = "DIV.cz"

                qr_string = (
                    f"SPD*1.0*ACC:{iban}"
                    f"*AM:{amount:.2f}"
                    f"*CC:CZK*MSG:{msg}*X-VS:{vs}"
                )

                img = qrcode.make(qr_string)
                buf = BytesIO()
                img.save(buf, format="PNG")
                request_qr_code = base64.b64encode(buf.getvalue()).decode("utf-8")
            else:
                request_qr_code = qr_code_base64


    # Ostatní výpočty pro všechny uživatele
    movies_list_6 = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:6]
    articles = Article.objects.exclude(typ='Site').order_by('-created').values('url', 'title', 'img', 'img400x250', 'perex')[:2]
    articlenews = Articlenews.objects.all().order_by('-created')[:5]
    movies = Movie.objects.all().order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description')[:40]
    today = date.today()
    current_month = today.month
    current_day = today.day
    creators_list_8 = Creator.objects.filter(
        birthdate__month=current_month,
        birthdate__day=current_day,
        deathdate__isnull=True,
        adult=0
    ).order_by('-divrating')[:8]

    users_list_4 = User.objects.annotate(
        comment_count=Count('moviecomments'),
        rating_count=Count('userrating'),
        comment_rating_sum=Count('moviecomments')+Count('userrating')
        ).order_by('-rating_count')[:9]

    movies_comments_9 = Moviecomments.objects.select_related('movieid', 'user').order_by('-commentid').values('comment', 'movieid__titlecz', 'movieid__url', 'movieid', 'user', 'user__username')[:5]
    movies_comments_5 = Moviecomments.objects.select_related('movieid', 'user').order_by('-commentid').values('comment', 'movieid__titlecz', 'movieid__url', 'movieid', 'user', 'user__username')[:5]
    movies_comments = Moviecomments.objects.select_related('movieid', 'user').order_by('-dateadded')[:10]
    books_comments = Bookcomments.objects.select_related('bookid', 'user').order_by('-dateadded')[:10]
    games_comments = Gamecomments.objects.select_related('gameid', 'user').order_by('-dateadded')[:10]
    latest_comments = sorted(
        chain(movies_comments, books_comments),
        key=attrgetter('dateadded'), 
        reverse=True
    )[:10]

    # Filmy v kinech
    movies_in_cinema = Moviecinema.objects.select_related('movieid', 'distributorid').order_by('-releasedate').values(
        'movieid__title', 'movieid__titlecz', 'movieid__img', 'releasedate', 'distributorid__name', 'movieid__url')[:10]
        
    # Statistiky
    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_movie = Metastats.objects.filter(tablemodel='Movie').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()
        #stats_games = Metastats.objects.filter(tablemodel='Game').first()
        # Žebříčky
    charts = Metacharts.objects.filter(table_model='Movie', store='BoxOfficeMojo').order_by('ranking')


    if request.user.is_authenticated:
        tasks = get_sorted_tasks(request.user)
    else:
        tasks = []

    # Data pro jednotlivé karusely z MetaIndex
    movies_carousel = Metaindex.objects.filter(
        section='Movie'
    ).order_by('-divrating')[:7]  # Můžete upravit počet položek
    
    series_carousel = Metaindex.objects.filter(
        section='TVShow'
    ).order_by('-divrating')[:7]
    
    books_carousel = Metaindex.objects.filter(
        section='Book'
    ).order_by('-divrating')[:7]
    
    games_carousel = Metaindex.objects.filter(
        section='Game'
    ).order_by('-divrating')[:7]
    
    recent_listings = get_market_listings()

    # Poslední nákupy eKnih pro superusera
    last_ebook_purchases = []
    if request.user.is_authenticated:
        user_ebook_purchases = Bookpurchase.objects.filter(user=request.user, status="PAID").order_by('-purchaseid')[:3]
        seller_pending_listings = Booklisting.objects.filter(user=request.user, listingtype__in=['SELL', 'GIVE']).order_by('-createdat')[:5]
        pending_book_purchases = Booklisting.objects.filter(buyer=request.user, status='PENDING').order_by('-createdat')[:5]
        user_wanted_purchases = Booklisting.objects.filter(user=request.user, listingtype='BUY').order_by('-createdat')[:5]
    else:
        user_ebook_purchases = []
        seller_pending_listings = []
        pending_book_purchases = []
        user_wanted_purchases = []

    recent_sell_listings, recent_buy_listings = get_market_listings()
    pending_payouts = Booklisting.objects.filter(paidtoseller=False)[:5]
    request_payouts = Booklisting.objects.filter(paidtoseller=False, requestpayout=True)[:5]

    if request.user.is_authenticated:
        # obchody, kde jsem prodávající nebo kupující
        my_active_actions = Booklisting.objects.filter(
            Q(user=request.user) | Q(buyer=request.user),
            status__in=['RESERVED', 'PAID', 'SHIPPED', 'COMPLETED']
        ).select_related('book', 'user', 'buyer')
    
        # jen ty, kde je opravdu akce
        my_active_actions = [
            l for l in my_active_actions
            if (
                # kupující čeká na zaplacení
                (l.status == 'RESERVED' and l.buyer == request.user) or
                # kupující už zaplatil, čeká na odeslání
                (l.status == 'PAID' and l.user == request.user) or
                # kupující čeká na potvrzení, že kniha došla
                (l.status in ['PAID', 'SHIPPED'] and l.buyer == request.user) or
                # prodávající vidí, že kniha byla odeslána
                (l.status == 'SHIPPED' and l.user == request.user) or
                # hotovo, ale ještě chybí hodnocení
                (l.status == 'COMPLETED' and (
                    (l.user == request.user and not l.buyerrating) or
                    (l.buyer == request.user and not l.sellerrating)
                ))
            )
        ]
    else:
        my_active_actions = []

    return render(request, 'index.html', {
            'movies': movies, 
            'movies_list_6': movies_list_6, 
            'articles': articles, 
            'articlenews': articlenews,
            'article_form': article_form,
            'articlenews_form': articlenews_form,
            'creators_list_8': creators_list_8, 
            'users_list_4': users_list_4, 
            'movies_comments_9': movies_comments_9,
            'movies_comments_5': movies_comments_5,
            'latest_comments': latest_comments,
            'movies_in_cinema': movies_in_cinema, 
            'stats_book': stats_book,
            'stats_movie': stats_movie,
            'stats_writters': stats_writters,
            'charts': charts,
            'tasks': tasks,
            'movies_carousel': movies_carousel,
            'series_carousel': series_carousel,
            'books_carousel': books_carousel, 
            'games_carousel': games_carousel,
            'recent_listings': recent_listings,
            'last_ebook_purchases': last_ebook_purchases,
            'user_ebook_purchases': user_ebook_purchases,
            'seller_pending_listings': seller_pending_listings,
            'pending_book_purchases': pending_book_purchases,
            'user_wanted_purchases': user_wanted_purchases,
            'recent_sell_listings': recent_sell_listings,
            'recent_buy_listings': recent_buy_listings,
            'request_payouts': request_payouts,
            'pending_payouts': pending_payouts,
            'pending_payouts_list': pending_payouts_list,
            #'request_payouts_list': request_payouts_list,
            'my_active_actions': my_active_actions,
            'bank_account': bankaccount,
            'request_qr_code':request_qr_code,
            })  

@login_required
def show_qr_payment(request, listing_id):
    listing = get_object_or_404(Booklisting, id=listing_id, user=request.user)

    # Data pro QR kód
    payment_data = f"Platba za knihu {listing.book.titlecz} - částka: {listing.price} Kč"
    
    # Vytvoření QR kódu
    qr = qrcode.make(payment_data)
    
    # Uložení QR kódu do paměti
    stream = BytesIO()
    qr.save(stream, format="PNG")
    return HttpResponse(stream.getvalue(), content_type="image/png")


def series_genre(request, genre_url):
    genre = get_object_or_404(Metagenre, url=genre_url)
    tvshows = Tvshow.objects.filter(tvgenre__genreid=genre.genreid).order_by('-divrating')[:15]
    
    stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
    return render(request, 'series/series_genre.html', {
        'genre': genre,
        'tvshows': tvshows, 
        'stats_tvshows': stats_tvshows
    })

def series_year(request, year):
    tvshows = Tvshow.objects.annotate(premiere_year=ExtractYear('premieredate')).filter(premiere_year=year).order_by('-divrating')[:15]

    stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
    return render(request, 'series/series_year.html', {
        'year': year,
        'tvshows': tvshows, 
        'stats_tvshows': stats_tvshows
    })




def movies(request, year=None, genre_url=None, movie_url=None):
    if year:
        movies = Movie.objects.filter(releaseyear=year).order_by('-divrating')
        movies_carousel = Movie.objects.filter(releaseyear=year,adult=0).order_by('-divrating').values('titlecz', 'url', 'img', 'description')[:3]
        movies_list_30 = Movie.objects.filter(releaseyear=year,adult=0).order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_year.html', {
            'movies': movies, 
            'movies_carousel': movies_carousel, 
            'movies_list_30': movies_list_30, 
            'year': year
            })

    elif genre_url:
        genre = get_object_or_404(Metagenre, url=genre_url)
        movies_for_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid)
        movies_carousel_genre = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:3]

        #movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).values('title', 'titlecz', 'url', 'img', 'description')[:30]
        movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description', 'divrating')[:30]

        return render(request, 'movies/movies_genre.html', {
            'movies_for_genre': movies_for_genre, 
            'movies_carousel_genre': movies_carousel_genre, 
            'movies_list_30_genre': movies_list_30_genre, 
            'genre': genre
            })

    else:
        movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:4]
        movies = Movie.objects.all().order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description')[:50]
        #movies_list_15 = Movie.objects.filter(adult=0,releaseyear__gt=2018).order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description')[:15]



        # Získáme filmy včetně jejich hodnocení
        movie_content_type = ContentType.objects.get_for_model(Movie)
        movies_list_15 = Movie.objects.filter(adult=0, releaseyear__gt=2018).annotate(
            average_rating=models.Subquery(
                Rating.objects.filter(
                    content_type=movie_content_type,
                    object_id=models.OuterRef('movieid')
                ).values('average')[:1]
            )
        ).order_by('-divrating').values(
            'title', 
            'titlecz', 
            'description', 
            'url', 
            'img',
            'average_rating'
        )[:15]
        # Zaokrouhlíme hodnoty na celá čísla a převedeme na procenta
        for movie in movies_list_15:
            if movie['average_rating'] is not None:
                movie['average_rating'] = round(float(movie['average_rating']) * 20)  # převod z 5 na 100%
            else:
                movie['average_rating'] = 0

        stats_movie = Metastats.objects.filter(tablemodel='Movie').first()
        stats_creator = Metastats.objects.filter(tablemodel="Creator").first()
        stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
        stats_moviecomments = Metastats.objects.filter(tablemodel="MovieComments").first()


        # Filmy v kinech
        movies_in_cinema = Moviecinema.objects.select_related('movieid', 'distributorid').order_by('-releasedate').values(
        'movieid__title', 'movieid__titlecz', 'movieid__img', 'releasedate', 'movieid__url')[:10]

        # Filmy v kinech (Carousel Cinema)
        carousel_cinema = Moviecinema.objects.filter(movieid__img__isnull=False).exclude(movieid__img='noimg.png').select_related('movieid').order_by('-releasedate').values(
            'movieid__title', 'movieid__titlecz', 'movieid__img', 'movieid__url', 'releasedate'
        )[:10]

        latest_comments = Moviecomments.objects.order_by('-dateadded')[:3]
        return render(request, 'movies/movies_list.html', {
            'movies': movies, 
            'movies_carousel': movies_carousel, 
            'movies_list_15': movies_list_15,
            'stats_movie': stats_movie,
            'stats_tvshows': stats_tvshows,
            'stats_moviecomments': stats_moviecomments,
            'movies_in_cinema': movies_in_cinema,
            'carousel_cinema': carousel_cinema,
            'category_key': 'serialy',
            'latest_comments': latest_comments,
            })




# nasazeno z movies.py
def search(request):
    movies = None
    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            movies = (Movie.objects.filter(titlecz__icontains=query, adult=0)
                .values('title', 'titlecz', 'url', 'img', 'description', 'divrating', 'releaseyear', 'averagerating').order_by('-divrating')[:50])
    else:
        form = SearchForm()

    return render(request, 'movies/movies_search.html', {'form': form, 'movies': movies})




class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'



#def rate_movie(request, movie_id):
        # viz users.py


def our_team(request):
    return render(request, "nas_tym.html")


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------