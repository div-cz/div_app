# VIEWS.USERS.PY

from datetime import date

from div_content.forms.users import ContactForm, UserProfileForm, UserMessageForm

from div_content.models import (
    Avatar, Book, Bookauthor, Bookcomments, Bookgenre, Bookisbn, Booklisting, Bookpurchase, Creator, Favorite, Charactermeta, Game, Gamecomments, Metacountry, Metagenre, Movie, Moviecomments, Moviecountries, 
    Moviegenre, Movierating, Tvshow, Tvshowcomments, Userdivcoins, Userlist, Userlistbook, Userlistgame, Userlistmovie, Userlisttype, Userprofile,
    Usermessage, Userchatsession, Userlisttvshow, Userlistitem
    
    )
from django.contrib.auth.models import User 
from div_content.views.login import custom_login_view

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator
from django.db.models import Avg, Count, F, Q, Max, Prefetch, OuterRef, Subquery
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.csrf import csrf_exempt
from star_ratings.models import UserRating
import json

from django.utils.formats import date_format
from django.utils.timezone import localtime
from django.http import JsonResponse


book_content_type = ContentType.objects.get_for_model(Book)
CONTENT_TYPE_BOOK_ID = book_content_type.id



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
    
    return render(request, 'user/user_book_listings.html', {  # změněna cesta k šabloně
        'profile_user': user,
        'sell_listings': sell_listings,
        'buy_listings': buy_listings,
        'seller_rating': avg_seller_rating,
        'seller_ratings_count': seller_ratings_count,
        'buyer_rating': avg_buyer_rating,
        'buyer_ratings_count': buyer_ratings_count
    })


def user_sell_listings(request, user_id):
    """Seznam všech prodejních nabídek uživatele."""
    user = get_object_or_404(User, id=user_id)
    listings = Booklisting.objects.filter(
        user=user,
        listingtype__in=['SELL', 'GIVE']
    ).order_by('-createdat')
    
    # Získání průměrného hodnocení jako prodejce
    sellerratings = Booklisting.objects.filter(
        user=user,
        status='COMPLETED',
        sellerrating__isnull=False
    )
    avg_rating = sellerratings.aggregate(Avg('sellerrating'))['sellerrating__avg']
    
    return render(request, 'user/user_book_sell.html', {
        'profile_user': user,
        'listings': listings,
        'avg_rating': avg_rating,
        'total_ratings': sellerratings.count()
    })


def user_buy_listings(request, user_id):
   profile_user = get_object_or_404(User, id=user_id)
   listings = Booklisting.objects.filter(
       user=profile_user,
       listingtype='BUY'
   ).order_by('-createdat')
   
   buyer_ratings = Booklisting.objects.filter(
       buyer=profile_user,
       status='COMPLETED',
       buyerrating__isnull=False
   )
   avg_rating = buyer_ratings.aggregate(Avg('buyerrating'))['buyerrating__avg']
   
   return render(request, 'user/user_book_buy.html', {
       'profile_user': profile_user,
       'listings': listings,
       'avg_rating': avg_rating, 
       'total_ratings': buyer_ratings.count()
   })


def profile_show_case(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Count total comments across movies, books, and games
    movie_comments_count = Moviecomments.objects.filter(user=profile_user).count()
    book_comments_count = Bookcomments.objects.filter(user=profile_user).count()
    game_comments_count = Gamecomments.objects.filter(user=profile_user).count()
    total_comments = movie_comments_count + book_comments_count + game_comments_count

    # Award logic based on comment counts
    awards = []
    if total_comments >= 10:
        awards.append({"name": "10 komentářů", "icon": "10_comments.png", "unlocked": True})
    if total_comments >= 50:
        awards.append({"name": "50 komentářů", "icon": "50_comments.png", "unlocked": True})
    if total_comments >= 100:
        awards.append({"name": "100 komentářů", "icon": "100_comments.png", "unlocked": True})
    if total_comments >= 500:
        awards.append({"name": "500 komentářů", "icon": "500_comments.png", "unlocked": True})
    if total_comments >= 1000:
        awards.append({"name": "1000 komentářů", "icon": "1000_comments.png", "unlocked": True})

    return render(request, 'user/profile_show_case.html', {
        'user_div_coins': user_div_coins,
        'profile_user': profile_user,
        'user_profile': user_profile,
        'awards': awards,
        'active_tab': 'vitrina',
    })



@login_required
def add_to_favorite_users(request, userprofile_id):
    userprofile = get_object_or_404(Userprofile, userprofileid=userprofile_id)
    userprofile_content_type_id = ContentType.objects.get_for_model(Userprofile).id
    
    if Favorite.objects.filter(
            user=request.user,
            content_type_id=userprofile_content_type_id,  # ContentType ID pro Userprofile
            object_id=userprofile.userprofileid
        ).exists():
        pass
    else:
        Favorite.objects.create(
            user=request.user,
            content_type_id=userprofile_content_type_id,  # ContentType ID pro Userprofile
            object_id=userprofile.userprofileid
        )
    return redirect("myuser_detail", user_id=userprofile.user.id)

@login_required
def remove_from_favorite_users(request, userprofile_id):
    userprofile = get_object_or_404(Userprofile, userprofileid=userprofile_id)
    userprofile_content_type_id = ContentType.objects.get_for_model(Userprofile).id
    Favorite.objects.filter(
        user=request.user, 
        content_type_id=userprofile_content_type_id, 
        object_id=userprofile.userprofileid
    ).delete()
    return redirect("myuser_detail", user_id=userprofile.user.id)

def contact_form(request):
    message_sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message_sent = True
    else:
        form = ContactForm()
    return render(request, 'user/contact.html', {'form': form, 'message_sent': message_sent})


def get_content_type_for_rating(rating):
    content_object = rating.content_object
    if content_object:
        return ContentType.objects.get_for_model(content_object.__class__)
    return None


# USER
"""
def myuser_detail(request, user_id=None):
    # Pokud user_id není zadáno, použijte přihlášeného uživatele
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)
    user_ratings = UserRating.objects.filter(user_id=user_id).order_by('-modified')[:5]
    all_ratings = UserRating.objects.filter(user_id=user_id).order_by('-modified')
    movie_ratings = [rating for rating in all_ratings if get_content_type_for_rating(rating).model == 'movie']
    book_ratings = [rating for rating in all_ratings if get_content_type_for_rating(rating).model == 'book']


    # Získání instance profilu uživatele
    user_profile = Userprofile.objects.get(user=profile_user)

    items_per_page = 10
    paginator = Paginator(user_ratings, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if profile_user == request.user:
        template_name = 'user/my_profile.html'
    else:
        template_name = 'user/other_profile.html'

    return render(request, template_name, {
        'profile_user': profile_user, 
        'user_ratings': user_ratings, 
        'page': page, 
        'user_profile': user_profile,
        'movie_ratings': movie_ratings,
        'book_ratings': book_ratings,
    })
"""


def myuser_detail(request, user_id=None):
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)

    # Get the user profile
    user_profile = Userprofile.objects.get(user=profile_user)  

    # Get the user's DivCoins data
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Assuming content_type_id for movies is defined
    #movie_content_type_id = 33
    movie_content_type = ContentType.objects.get_for_model(Movie)
    movie_content_type_id = movie_content_type.id

    #book_content_type_id = 9
    book_content_type = ContentType.objects.get_for_model(Book)
    book_content_type_id = book_content_type.id

    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    # 7 = article, --- může být jiné při změně tabulek a nové migrai!!!!

    movie_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=movie_content_type_id).order_by('-modified')[:5]
    book_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=book_content_type_id).order_by('-modified')[:5]
    
    # Vyhledá jestli má uživatel oblíbené uživatele
    favorite_users_query = Favorite.objects.filter(user=user_profile.user.id, content_type_id=userprofile_content_type_id)
    favorite_users = [favorite.content_object for favorite in favorite_users_query]

    # Vyhledá jestli je uživatel mezi oblíbenými u jiných uživatelů 
    im_favorite_user = Favorite.objects.filter(content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid)

    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True

    items_per_page = 10
    movie_paginator = Paginator(movie_ratings, items_per_page)
    book_paginator = Paginator(book_ratings, items_per_page)

    movie_page_number = request.GET.get('movie_page')
    book_page_number = request.GET.get('book_page')

    movie_page = movie_paginator.get_page(movie_page_number)
    book_page = book_paginator.get_page(book_page_number)
    

    template_name = 'user/profile.html' if profile_user == request.user else 'user/profile.html'

    return render(request, template_name, {
        'profile_user': profile_user,
        'user_div_coins': user_div_coins,
        'movie_page': movie_page,
        'book_ratings': book_page,
        'user_profile': user_profile,  
        "movie_ratings": movie_ratings,
        'favorite_users': favorite_users,
        'im_favorite_user': im_favorite_user,
        'is_favorite': is_favorite,
         }
    )



@login_required
def profile_eshop_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Historie nákupů (příklad, může být upraven podle DB struktury)
    #purchase_history = Userlistitem.objects.filter(
    #    userlist__user=profile_user,
    #    userlist__listtype__name__in=["Zakoupené filmy", "Zakoupené knihy", "Zakoupené hry"]
    #).select_related("content_type").order_by("-addedat")

    # Seznam zakoupených e-knih (status PAID, platnost do budoucna, řazení od nejnovějších)
    purchased_ebooks = Bookpurchase.objects.filter(user=profile_user, status='PAID').select_related('book')
    for p in purchased_ebooks:
        bookisbn = Bookisbn.objects.filter(book=p.book, format__iexact=p.format).first()
        p.isbn = bookisbn.isbn if bookisbn else None

    ebook_isbns = {}
    for p in purchased_ebooks:
        bookisbn = p.book.bookisbn_set.filter(format__iexact=p.format).first()
        p.isbn = bookisbn.isbn if bookisbn else None

    # TODO: případně filtr na expiraci:
    # .filter(Q(expirationdate__isnull=True) | Q(expirationdate__gte=now()))

    return render(request, "user/profile_markets.html", {
        "profile_user": profile_user,
        "user_profile": user_profile,
        "user_div_coins": user_div_coins,
        "active_tab": "obchod",
        "purchased_ebooks": purchased_ebooks,
        "ebook_isbns": ebook_isbns,
    })


### profile
def profile_movies_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Počet položek na stránku
    items_per_page = 20

    # Získání hodnocených filmů
    movie_content_type = ContentType.objects.get_for_model(Movie)
    movie_content_type_id = movie_content_type.id

    movie_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=movie_content_type_id).order_by('-modified')
    movie_paginator = Paginator(movie_ratings, items_per_page)
    movie_page_number = request.GET.get('page', 1)
    movie_page_obj = movie_paginator.get_page(movie_page_number)

    # Získání oblíbených filmů (UserListTypeID = 1)
    userlisttype_fav_movie = Userlisttype.objects.filter(name='Oblíbený film').first()
    favorite_list = Userlist.objects.filter(user=profile_user, listtype=userlisttype_fav_movie.userlisttypeid).first()
    if favorite_list:
        favorite_movie_items = Userlistitem.objects.filter(userlist=favorite_list, content_type=movie_content_type).order_by('-addedat')
        movies_ids = favorite_movie_items.values_list('object_id', flat=True)
        movies = Movie.objects.filter(movieid__in=movies_ids)

        # Create a mapping of book_id to Book object
        movie_map = {movie.movieid: movie for movie in movies}
        
        # Combine Book objects with their Userlistitem data
        favorite_movies = [
            (movie_map[item.object_id], item)
            for item in favorite_movie_items
            if item.object_id in movie_map
        ]
        favorite_paginator = Paginator(favorite_movies, items_per_page)
        favorite_page_number = request.GET.get('favorite_page', 1)
        favorite_page_obj = favorite_paginator.get_page(favorite_page_number)
    else:
        favorite_page_obj = None
        
    # Získání oblíbených herců (ContentType pro Creator)
    userlisttype_fav_creator = Userlisttype.objects.filter(name='Oblíbený tvůrce').first()
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_fav_creator.userlisttypeid)
    favourites_list = Userlist.objects.filter(user=profile_user, listtype=favourite_type).first()
    if favourites_list:
        creator_content_type = ContentType.objects.get_for_model(Creator)
        # Subquery
        addedat_subquery = Userlistitem.objects.filter(
            userlist=favourites_list, content_type=creator_content_type, object_id=OuterRef('creatorid')
        ).values('addedat')[:1]

        # Annotate Creator objects with addedat and sort by addedat
        fav_creators = Creator.objects.filter(
            creatorid__in=Userlistitem.objects.filter(
                userlist=favourites_list, content_type=creator_content_type
            ).values_list('object_id', flat=True)
        ).annotate(
            addedat=Subquery(addedat_subquery)
        ).order_by('-addedat')

        fav_creators_paginator = Paginator(fav_creators, 12)
        fav_creators_page_number = request.GET.get('fav_creators_page', 1)
        fav_creators_page_obj = fav_creators_paginator.get_page(fav_creators_page_number)
    else:
        fav_creators_page_obj = None
        
    # Seznam oblíbených postav
    userlisttype_fav_char = Userlisttype.objects.filter(name='Oblíbená postava').first()
    favorite_char_list = Userlist.objects.filter(user=profile_user, listtype=userlisttype_fav_char.userlisttypeid).first()
    if favorite_char_list:
        character_content_type = ContentType.objects.get_for_model(Charactermeta)
        # Subquery
        addedat_subquery = Userlistitem.objects.filter(
            userlist=favorite_char_list, content_type=character_content_type, object_id=OuterRef('characterid')
        ).values('addedat')[:1]

        fav_characters = Charactermeta.objects.filter(
            characterid__in=Userlistitem.objects.filter(
                userlist=favorite_char_list, content_type=character_content_type
            ).values_list('object_id', flat=True)
        ).annotate(
            addedat=Subquery(addedat_subquery)
        ).order_by('-addedat')

        fav_characters_paginator = Paginator(fav_characters, 12)
        fav_characters_page_number = request.GET.get('fav_characters_page', 1)
        fav_characters_page_obj = fav_characters_paginator.get_page(fav_characters_page_number)
    else:
        fav_characters_page_obj = None

    # Získání recenzí
    reviews = Moviecomments.objects.filter(user_id=user_id, comment__isnull=False).order_by('-dateadded')
    if reviews: 
        moviereviews_paginator = Paginator(reviews, items_per_page)
        moviereviews_page_number = request.GET.get('moviereviews_page', 1)
        moviereviews_page_obj = moviereviews_paginator.get_page(moviereviews_page_number)
    else:
        moviereviews_page_obj = None

    # Chci vidět (UserListTypeID = 2)
    wantsee_list_type = get_object_or_404(Userlisttype, userlisttypeid=2)
    wantsee_list = Userlist.objects.filter(user=profile_user, listtype=wantsee_list_type.userlisttypeid).first()
    if wantsee_list:
        # wantsee_movies = Userlistmovie.objects.filter(userlist=wantsee_list).select_related('movie')
        wantsee_movie_items = Userlistitem.objects.filter(userlist=wantsee_list, content_type=movie_content_type).order_by('-addedat')
        movies_ids = wantsee_movie_items.values_list('object_id', flat=True)
        movies = Movie.objects.filter(movieid__in=movies_ids)

        # Create a mapping of book_id to Book object
        movie_map = {movie.movieid: movie for movie in movies}
        
        # Combine Book objects with their Userlistitem data
        wantsee_movies = [
            (movie_map[item.object_id], item)
            for item in wantsee_movie_items
            if item.object_id in movie_map
        ]
        wantsee_paginator = Paginator(wantsee_movies, items_per_page)
        wantsee_page_number = request.GET.get('wantsee_page', 1)
        wantsee_page_obj = wantsee_paginator.get_page(wantsee_page_number)
    else:
        wantsee_page_obj = None

    # Shlédnuto (UserListTypeID = 3)
    watched_list_type = get_object_or_404(Userlisttype, userlisttypeid=3)
    watched_list = Userlist.objects.filter(user=profile_user, listtype=watched_list_type).first()
    if watched_list:
        watched_movie_items = Userlistitem.objects.filter(userlist=watched_list, content_type=movie_content_type).order_by('-addedat')
        movies_ids = watched_movie_items.values_list('object_id', flat=True)
        movies = Movie.objects.filter(movieid__in=movies_ids)

        # Create a mapping of book_id to Book object
        movie_map = {movie.movieid: movie for movie in movies}
        
        # Combine Book objects with their Userlistitem data
        watched_movies = [
            (movie_map[item.object_id], item)
            for item in watched_movie_items
            if item.object_id in movie_map
        ]
        watched_paginator = Paginator(watched_movies, items_per_page)
        watched_page_number = request.GET.get('watched_page', 1)
        watched_page_obj = watched_paginator.get_page(watched_page_number)
    else:
        watched_page_obj = None

    # Filmotéka (UserListTypeID = 11)
    filmoteka_list_type = get_object_or_404(Userlisttype, userlisttypeid=11)
    filmoteka_list = Userlist.objects.filter(user=profile_user, listtype=filmoteka_list_type).first()
    if filmoteka_list:
        filmoteka_movie_items = Userlistitem.objects.filter(userlist=filmoteka_list, content_type=movie_content_type).order_by('-addedat')
        movies_ids = filmoteka_movie_items.values_list('object_id', flat=True)
        movies = Movie.objects.filter(movieid__in=movies_ids)

        # Create a mapping of book_id to Book object
        movie_map = {movie.movieid: movie for movie in movies}
        
        # Combine Book objects with their Userlistitem data
        filmoteka_movies = [
            (movie_map[item.object_id], item)
            for item in filmoteka_movie_items
            if item.object_id in movie_map
        ]
        filmoteka_paginator = Paginator(filmoteka_movies, items_per_page)
        filmoteka_page_number = request.GET.get('filmoteka_page', 1)
        filmoteka_page_obj = filmoteka_paginator.get_page(filmoteka_page_number)
    else:
        filmoteka_page_obj = None

    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True

    return render(request, 'user/profile_movies.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'user_div_coins': user_div_coins,
        'movie_page_obj': movie_page_obj,
        'favorite_page_obj': favorite_page_obj,
        'fav_creators_page_obj': fav_creators_page_obj,
        'fav_characters_page_obj': fav_characters_page_obj,
        'reviews': reviews,
        'moviereviews_page_obj': moviereviews_page_obj,
        'wantsee_page_obj': wantsee_page_obj,
        'watched_page_obj': watched_page_obj,
        'filmoteka_page_obj': filmoteka_page_obj,
        'is_favorite': is_favorite,
        'active_tab': 'filmy',
    })


def profile_series_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Počet položek na stránku
    items_per_page = 20

    # Získání hodnocených seriálů
    #series_content_type_id = 40
    series_content_type = ContentType.objects.get_for_model(Tvshow)
    series_content_type_id = series_content_type.id

    series_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=series_content_type_id).order_by('-modified')
    series_paginator = Paginator(series_ratings, items_per_page)
    series_page_number = request.GET.get('page', 1)
    series_page_obj = series_paginator.get_page(series_page_number)

    # Získání oblíbených seriálů (UserListTypeID = 13)
    favorite_list_type = get_object_or_404(Userlisttype, userlisttypeid=13)
    favorite_list = Userlist.objects.filter(user=profile_user, listtype=favorite_list_type).first()
    if favorite_list:
        favorite_series_items = Userlistitem.objects.filter(userlist=favorite_list, content_type=series_content_type).order_by('-addedat')
        series_ids = favorite_series_items.values_list('object_id', flat=True)
        series = Tvshow.objects.filter(tvshowid__in=series_ids)

        # Create a mapping of book_id to Book object
        serie_map = {serie.tvshowid: serie for serie in series}
        
        # Combine Book objects with their Userlistitem data
        favorite_series = [
            (serie_map[item.object_id], item)
            for item in favorite_series_items
            if item.object_id in serie_map
        ]
        favorite_paginator = Paginator(favorite_series, items_per_page)
        favorite_page_number = request.GET.get('favorite_page', 1)
        favorite_page_obj = favorite_paginator.get_page(favorite_page_number)
    else:
        favorite_page_obj = None
        
    # Získání oblíbených herců (ContentType pro Creator)
    userlisttype_fav_creator = Userlisttype.objects.filter(name='Oblíbený tvůrce').first()
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_fav_creator.userlisttypeid)
    favourites_list = Userlist.objects.filter(user=profile_user, listtype=favourite_type).first()
    if favourites_list:
        creator_content_type = ContentType.objects.get_for_model(Creator)
        # Subquery
        addedat_subquery = Userlistitem.objects.filter(
            userlist=favourites_list, content_type=creator_content_type, object_id=OuterRef('creatorid')
        ).values('addedat')[:1]

        # Annotate Creator objects with addedat and sort by addedat
        fav_creators = Creator.objects.filter(
            creatorid__in=Userlistitem.objects.filter(
                userlist=favourites_list, content_type=creator_content_type
            ).values_list('object_id', flat=True)
        ).annotate(
            addedat=Subquery(addedat_subquery)
        ).order_by('-addedat')

        fav_creators_paginator = Paginator(fav_creators, 12)
        fav_creators_page_number = request.GET.get('fav_creators_page', 1)
        fav_creators_page_obj = fav_creators_paginator.get_page(fav_creators_page_number)
    else:
        fav_creators_page_obj = None

   # Seznam oblíbených postav
    userlisttype_fav_char = Userlisttype.objects.filter(name='Oblíbená postava').first()
    favorite_char_list = Userlist.objects.filter(user=profile_user, listtype=userlisttype_fav_char.userlisttypeid).first()
    if favorite_char_list:
        character_content_type = ContentType.objects.get_for_model(Charactermeta)
        # Subquery
        addedat_subquery = Userlistitem.objects.filter(
            userlist=favorite_char_list, content_type=character_content_type, object_id=OuterRef('characterid')
        ).values('addedat')[:1]

        fav_characters = Charactermeta.objects.filter(
            characterid__in=Userlistitem.objects.filter(
                userlist=favorite_char_list, content_type=character_content_type
            ).values_list('object_id', flat=True)
        ).annotate(
            addedat=Subquery(addedat_subquery)
        ).order_by('-addedat')

        fav_characters_paginator = Paginator(fav_characters, 12)
        fav_characters_page_number = request.GET.get('fav_characters_page', 1)
        fav_characters_page_obj = fav_characters_paginator.get_page(fav_characters_page_number)
    else:
        fav_characters_page_obj = None


    # Získání recenzí
    reviews = Tvshowcomments.objects.filter(user_id=user_id, comment__isnull=False).order_by('-dateadded')
    if reviews: 
        seriesreviews_paginator = Paginator(reviews, items_per_page)
        seriesreviews_page_number = request.GET.get('seriesreviews_page', 1)
        seriesreviews_page_obj = seriesreviews_paginator.get_page(seriesreviews_page_number)
    else:
        seriesreviews_page_obj = None


    # Chci vidět (UserListTypeID = 14)
    wantsee_list_type = get_object_or_404(Userlisttype, userlisttypeid=14)
    wantsee_list = Userlist.objects.filter(user=profile_user, listtype=wantsee_list_type).first()
    if wantsee_list:
        wantsee_series_items = Userlistitem.objects.filter(userlist=wantsee_list, content_type=series_content_type).order_by('-addedat')
        series_ids = wantsee_series_items.values_list('object_id', flat=True)
        series = Tvshow.objects.filter(tvshowid__in=series_ids)

        # Create a mapping of book_id to Book object
        serie_map = {serie.tvshowid: serie for serie in series}
        
        # Combine Book objects with their Userlistitem data
        wantsee_series = [
            (serie_map[item.object_id], item)
            for item in wantsee_series_items
            if item.object_id in serie_map
        ]
        wantsee_paginator = Paginator(wantsee_series, items_per_page)
        wantsee_page_number = request.GET.get('wantsee_page', 1)
        wantsee_page_obj = wantsee_paginator.get_page(wantsee_page_number)
    else:
        wantsee_page_obj = None

    # Seriálnuto (UserListTypeID = 15)
    watched_list_type = get_object_or_404(Userlisttype, userlisttypeid=15)
    watched_list = Userlist.objects.filter(user=profile_user, listtype=watched_list_type).first()
    if watched_list:
        watched_series_items = Userlistitem.objects.filter(userlist=watched_list, content_type=series_content_type).order_by('-addedat')
        series_ids = watched_series_items.values_list('object_id', flat=True)
        series = Tvshow.objects.filter(tvshowid__in=series_ids)

        # Create a mapping of book_id to Book object
        serie_map = {serie.tvshowid: serie for serie in series}
        
        # Combine Book objects with their Userlistitem data
        watched_series = [
            (serie_map[item.object_id], item)
            for item in watched_series_items
            if item.object_id in serie_map
        ]
        watched_paginator = Paginator(watched_series, items_per_page)
        watched_page_number = request.GET.get('watched_page', 1)
        watched_page_obj = watched_paginator.get_page(watched_page_number)
    else:
        watched_page_obj = None

    # Seriálotéka (UserListTypeID = 16)
    serialoteka_list_type = get_object_or_404(Userlisttype, userlisttypeid=16)
    serialoteka_list = Userlist.objects.filter(user=profile_user, listtype=serialoteka_list_type).first()
    if serialoteka_list:
        serialoteka_series_items = Userlistitem.objects.filter(userlist=serialoteka_list, content_type=series_content_type).order_by('-addedat')
        series_ids = serialoteka_series_items.values_list('object_id', flat=True)
        series = Tvshow.objects.filter(tvshowid__in=series_ids)

        # Create a mapping of book_id to Book object
        serie_map = {serie.tvshowid: serie for serie in series}
        
        # Combine Book objects with their Userlistitem data
        serialoteka_series = [
            (serie_map[item.object_id], item)
            for item in serialoteka_series_items
            if item.object_id in serie_map
        ]
        serialoteka_paginator = Paginator(serialoteka_series, items_per_page)
        serialoteka_page_number = request.GET.get('serialoteka_page', 1)
        serialoteka_page_obj = serialoteka_paginator.get_page(serialoteka_page_number)
    else:
        serialoteka_page_obj = None

    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True

    return render(request, 'user/profile_serials.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'user_div_coins': user_div_coins,
        'series_page_obj': series_page_obj,
        'favorite_page_obj': favorite_page_obj,
        'fav_characters_page_obj': fav_characters_page_obj,
        'fav_creators_page_obj': fav_creators_page_obj,
        # 'fav_creators': fav_creators, 
        # 'fav_characters': fav_characters,
        'seriesreviews_page_obj': seriesreviews_page_obj,
        'wantsee_page_obj': wantsee_page_obj,
        'watched_page_obj': watched_page_obj,
        'serialoteka_page_obj': serialoteka_page_obj,
        'is_favorite': is_favorite,
        'active_tab': 'serialy',
    })


def profile_books_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)
    
    items_per_page = 20

    # Pro knihy
    #book_content_type_id = 9
    book_content_type = ContentType.objects.get_for_model(Book)
    book_content_type_id = book_content_type.id

    
    # Získání hodnocení knih
    book_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=book_content_type_id).order_by('-modified')[:30]
    book_paginator = Paginator(book_ratings, items_per_page)
    book_page_number = request.GET.get('page', 1)
    book_page_obj = book_paginator.get_page(book_page_number)

    # Oblíbené knihy
    favorite_list_type = get_object_or_404(Userlisttype, userlisttypeid=4)  # Typ seznamu pro oblíbené
    favorite_list = Userlist.objects.filter(user=profile_user, listtype=favorite_list_type).first()
    if favorite_list:
        favorite_book_items = Userlistitem.objects.filter(userlist=favorite_list, content_type=book_content_type).order_by('-addedat')
        book_ids = favorite_book_items.values_list('object_id', flat=True)
        books = Book.objects.filter(bookid__in=book_ids)

        # Create a mapping of book_id to Book object
        book_map = {book.bookid: book for book in books}
        
        # Combine Book objects with their Userlistitem data
        favorite_books = [
            (book_map[item.object_id], item)
            for item in favorite_book_items
            if item.object_id in book_map
        ]

        favorite_paginator = Paginator(favorite_books, items_per_page)
        favorite_page_number = request.GET.get('favorite_page', 1)
        favorite_page_obj = favorite_paginator.get_page(favorite_page_number)
    else:
        favorite_page_obj = None

    # Načítání oblíbených spisovatelů
    bookauthor_content_type = ContentType.objects.get_for_model(Bookauthor)
    userlisttype_fav_creator = Userlisttype.objects.filter(name='Oblíbený spisovatel').first()
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_fav_creator.userlisttypeid)
    favourites_list = Userlist.objects.filter(user=profile_user, listtype=favourite_type).first()
    if favourites_list:
        bookauthor_content_type = ContentType.objects.get_for_model(Bookauthor)
        # Subquery
        addedat_subquery = Userlistitem.objects.filter(
            userlist=favourites_list, content_type=bookauthor_content_type, object_id=OuterRef('authorid')
        ).values('addedat')[:1]

        # Annotate Creator objects with addedat and sort by addedat
        fav_authors = Bookauthor.objects.filter(
            authorid__in=Userlistitem.objects.filter(
                userlist=favourites_list, content_type=bookauthor_content_type
            ).values_list('object_id', flat=True)
        ).annotate(
            addedat=Subquery(addedat_subquery)
        ).order_by('-addedat')

        fav_creators_paginator = Paginator(fav_authors, 12)
        fav_creators_page_number = request.GET.get('fav_creators_page', 1)
        fav_creators_page_obj = fav_creators_paginator.get_page(fav_creators_page_number)
    else:
        fav_creators_page_obj = None


    # Recenze knih (komentáře)
    #     book_comments = Bookcomments.objects.filter(user=profile_user).exclude(comment__isnull=True).exclude(comment__exact='')
    # print(f"Book comments: {book_comments}")  # Debugging line
    # Získání recenzí
    reviews = Bookcomments.objects.filter(user=profile_user, comment__isnull=False).order_by('-dateadded')
    if reviews: 
        bookreviews_paginator = Paginator(reviews, items_per_page)
        bookreviews_page_number = request.GET.get('bookreviews_page', 1)
        bookreviews_page_obj = bookreviews_paginator.get_page(bookreviews_page_number)
    else:
        bookreviews_page_obj = None

    # Knihy, které chce číst (Chci číst)
    wantread_list_type = get_object_or_404(Userlisttype, name="Chci číst")
    wantread_list = Userlist.objects.filter(user=profile_user, listtype=wantread_list_type).first()
    if wantread_list:
        wantread_book_items = Userlistitem.objects.filter(userlist=wantread_list, content_type=book_content_type).order_by('-addedat')
        books_ids = wantread_book_items.values_list('object_id', flat=True)
        books = Book.objects.filter(bookid__in=books_ids)

        # Create a mapping of book_id to Book object
        book_map = {book.bookid: book for book in books}
        
        # Combine Book objects with their Userlistitem data
        wantread_books = [
            (book_map[item.object_id], item)
            for item in wantread_book_items
            if item.object_id in book_map
        ]

        wantread_paginator = Paginator(wantread_books, items_per_page)
        wantread_page_number = request.GET.get('wantread_page', 1)
        wantread_page_obj = wantread_paginator.get_page(wantread_page_number)
    else:
        wantread_page_obj = None

    # Přečtené knihy (Přečteno)
    read_list_type = get_object_or_404(Userlisttype, name='Přečteno')
    read_list = Userlist.objects.filter(user=profile_user, listtype=read_list_type).first()
    if read_list:
        read_book_items = Userlistitem.objects.filter(userlist=read_list, content_type=book_content_type).order_by('-addedat')
        books_ids = read_book_items.values_list('object_id', flat=True)
        books = Book.objects.filter(bookid__in=books_ids)

        # Create a mapping of book_id to Book object
        book_map = {book.bookid: book for book in books}
        
        # Combine Book objects with their Userlistitem data
        read_books = [
            (book_map[item.object_id], item)
            for item in read_book_items
            if item.object_id in book_map
        ]
        read_paginator = Paginator(read_books, items_per_page)
        read_page_number = request.GET.get('read_page', 1)
        read_page_obj = read_paginator.get_page(read_page_number)
    else:
        read_page_obj = None

    # Knihovna
    library_list_type = get_object_or_404(Userlisttype, name='Knihovna')
    library_list = Userlist.objects.filter(user=profile_user, listtype=library_list_type).first()
    if library_list:
        library_items = Userlistitem.objects.filter(userlist=library_list, content_type=book_content_type).order_by('-addedat')
        books_ids = library_items.values_list('object_id', flat=True)
        books = Book.objects.filter(bookid__in=books_ids)

        # Create a mapping of book_id to Book object
        book_map = {book.bookid: book for book in books}
        
        # Combine Book objects with their Userlistitem data
        library_books = [
            (book_map[item.object_id], item)
            for item in library_items
            if item.object_id in book_map
        ]
        library_paginator = Paginator(library_books, items_per_page)
        library_page_number = request.GET.get('library_page', 1)
        library_page_obj = library_paginator.get_page(library_page_number)
    else:
        library_page_obj = None

    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True

    return render(request, 'user/profile_books.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'user_div_coins': user_div_coins,
        'book_ratings': book_ratings,
        'book_page_obj': book_page_obj, 
        'favorite_page_obj': favorite_page_obj,
        'fav_creators_page_obj': fav_creators_page_obj,
        'bookreviews_page_obj': bookreviews_page_obj,
        'wantread_page_obj': wantread_page_obj,
        'read_page_obj': read_page_obj, 
        'library_page_obj': library_page_obj,
        'is_favorite': is_favorite,
        'active_tab': 'knihy',
    })


def profile_community_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    return render(
        request,
        "user/profile_community.html",
        {
            'profile_user': profile_user,
            'user_profile': user_profile,
            'user_div_coins': user_div_coins,
            "active_tab": "komunita"
        }
    )



def profile_games_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Počet položek na stránku
    items_per_page = 20

    # na produkci je to jinak! Tabulka django_content_type
    #game_content_type_id = 19
    game_content_type = ContentType.objects.get_for_model(Game)
    game_content_type_id = game_content_type.id
    
    # Získání hodnocení her
    game_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=game_content_type_id).order_by('-modified')[:30]
    game_paginator = Paginator(game_ratings, items_per_page)
    game_page_number = request.GET.get("page", 1)
    game_page_obj = game_paginator.get_page(game_page_number)

    # Nastavení počtu položek na stránku
    # paginator = Paginator(game_ratings, 6)  # 50 položek na stránku

    # # Získání čísla aktuální stránky z URL parametrů
    # page_number = request.GET.get('page', 1)  # Pokud není parametr v URL, nastaví se stránka 1
    # page_obj = paginator.get_page(page_number)

    # Oblíbené hry
    favorite_list_type = get_object_or_404(Userlisttype, name='Oblíbená hra')  # Typ seznamu pro oblíbené
    favorite_list = Userlist.objects.filter(user=profile_user, listtype=favorite_list_type).first()
    if favorite_list:
        favorite_game_items = Userlistitem.objects.filter(userlist=favorite_list, content_type=game_content_type).order_by('-addedat')
        game_ids = favorite_game_items.values_list('object_id', flat=True)
        games = Game.objects.filter(gameid__in=game_ids)

        # Create a mapping of book_id to Book object
        game_map = {game.gameid: game for game in games}
        
        # Combine Book objects with their Userlistitem data
        favorite_games = [
            (game_map[item.object_id], item)
            for item in favorite_game_items
            if item.object_id in game_map
        ]
        favorite_paginator = Paginator(favorite_games, items_per_page)
        favorite_page_number = request.GET.get("favorite_page", 1)
        favorite_page_obj = favorite_paginator.get_page(favorite_page_number)
    else:
        favorite_page_obj = None


    # Recenze her (komentáře)
    # reviews = Gamecomments.objects.filter(user=profile_user, comment__isnull=False).order_by('-dateadded')
    reviews = Gamecomments.objects.filter(user=profile_user, comment__isnull=False)
    if reviews: 
        reviews_paginator = Paginator(reviews, items_per_page)
        reviews_page_number = request.GET.get('reviews_page', 1)
        reviews_page_obj = reviews_paginator.get_page(reviews_page_number)
    else:
        reviews_page_obj = None

    # Hry, které chci hrát (Chci hrát)
    wantplay_list_type = get_object_or_404(Userlisttype, name='Chci hrát')
    wantplay_list = Userlist.objects.filter(user=profile_user, listtype=wantplay_list_type).first()
    if wantplay_list:
        favorite_game_items = Userlistitem.objects.filter(userlist=wantplay_list, content_type=game_content_type).order_by('-addedat')
        game_ids = favorite_game_items.values_list('object_id', flat=True)
        games = Game.objects.filter(gameid__in=game_ids)

        # Create a mapping of book_id to Book object
        game_map = {game.gameid: game for game in games}
        
        # Combine Book objects with their Userlistitem data
        wantplay_games = [
            (game_map[item.object_id], item)
            for item in favorite_game_items
            if item.object_id in game_map
        ]
        wantplay_paginator = Paginator(wantplay_games, items_per_page)
        wantplay_page_number = request.GET.get("wantplay_page", 1)
        wantplay_page_obj = wantplay_paginator.get_page(wantplay_page_number)
    else:
        wantplay_page_obj = None

    # Odehrané hry (Odehráno)
    played_list_type = get_object_or_404(Userlisttype, name='Hrál jsem')
    played_list = Userlist.objects.filter(user=profile_user, listtype=played_list_type).first()
    if played_list:
        played_game_items = Userlistitem.objects.filter(userlist=played_list, content_type=game_content_type).order_by('-addedat')
        game_ids = played_game_items.values_list('object_id', flat=True)
        games = Game.objects.filter(gameid__in=game_ids)

        # Create a mapping of book_id to Book object
        game_map = {game.gameid: game for game in games}
        
        # Combine Book objects with their Userlistitem data
        played_games = [
            (game_map[item.object_id], item)
            for item in played_game_items
            if item.object_id in game_map
        ]
        played_paginator = Paginator(played_games, items_per_page)
        played_page_number = request.GET.get("playedgames_page", 1)
        played_page_obj = played_paginator.get_page(played_page_number)
    else:
        played_page_obj = None

    # Gamotéka
    library_list_type = get_object_or_404(Userlisttype, name='Gamotéka')
    library_list = Userlist.objects.filter(user=profile_user, listtype=library_list_type).first()
    if library_list:
        played_game_items = Userlistitem.objects.filter(userlist=library_list, content_type=game_content_type).order_by('-addedat')
        game_ids = played_game_items.values_list('object_id', flat=True)
        games = Game.objects.filter(gameid__in=game_ids)

        # Create a mapping of book_id to Book object
        game_map = {game.gameid: game for game in games}
        
        # Combine Book objects with their Userlistitem data
        library_games = [
            (game_map[item.object_id], item)
            for item in played_game_items
            if item.object_id in game_map
        ]
        gamoteka_paginator = Paginator(library_games, items_per_page)
        gamoteka_page_number = request.GET.get("gamoteka_page", 1)
        gamoteka_page_obj = gamoteka_paginator.get_page(gamoteka_page_number)
    else:
        gamoteka_page_obj = None

    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True
    
    return render(request, 'user/profile_games.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'user_div_coins': user_div_coins,
        'game_page_obj': game_page_obj, 
        'favorite_page_obj': favorite_page_obj,
        'wantplay_page_obj': wantplay_page_obj,
        'played_page_obj': played_page_obj,
        'gamoteka_page_obj': gamoteka_page_obj,
        'game_ratings': game_ratings,
        'reviews_page_obj': reviews_page_obj,
        'is_favorite': is_favorite,
        'active_tab': 'hry',
    })



def profile_stats_section(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    # Získání content type ID pro filmy
    movie_content_type = ContentType.objects.get_for_model(Movie)
    
    # Načtení filmů hodnocených uživatelem (jen filmy)
    rated_movies = UserRating.objects.filter(user_id=profile_user.id, rating__content_type_id=movie_content_type.id).values_list('rating__object_id', flat=True)
    
    # Načtení žánrů filmů hodnocených uživatelem
    genre_stats = Moviegenre.objects.filter(movieid__in=rated_movies) \
                    .values('genreid') \
                    .annotate(count=Count('genreid')) \
                    .order_by('-count')


    # Načtení zemí filmů hodnocených uživatelem
    country_stats = Moviecountries.objects.filter(movieid__in=rated_movies) \
                    .values('countryid') \
                    .annotate(count=Count('countryid')) \
                    .order_by('-count')


    # Celkový počet hodnocených filmů
    total_movies = len(rated_movies)

    # Vypočítat procenta podle žánrů
    genre_percentages = []
    for stat in genre_stats:
        genre_name = Metagenre.objects.get(genreid=stat['genreid']).genrenamecz  # Získání názvu žánru
        percentage = (stat['count'] / total_movies) * 100 if total_movies > 0 else 0
        genre_percentages.append({
            'genre': genre_name,
            'percentage': percentage
        })

    # Omezit výsledek na prvních pět žánrů
    genre_percentages = genre_percentages[:5]


    # Vypočítat procenta podle zemí
    country_percentages = []
    for stat in country_stats:
        country_name = Metacountry.objects.get(countryid=stat['countryid']).countrynamecz  # Získání názvu země
        percentage = (stat['count'] / total_movies) * 100 if total_movies > 0 else 0
        country_percentages.append({
            'country': country_name,
            'percentage': percentage
        })

    # Omezit výsledek na prvních pět zemí
    country_percentages = country_percentages[:5]


# === B O O K S ===
    # === B O O K S ===
    # Nastavení typu obsahu pro knihy (Django ContentType pro knihy)
    book_content_type = ContentType.objects.get_for_model(Book)
    
    # Načtení ID hodnocených knih uživatelem
    rated_books = UserRating.objects.filter(
        user_id=user_id,  # Použij skutečné uživatelské ID
        rating__content_type_id=book_content_type.id
    ).values_list('rating__object_id', flat=True)
    
    print(list(rated_books))  # Pro ladění, zobrazí hodnocené knihy
    
    # Získání celkového počtu hodnocených knih
    total_books = len(rated_books)
    
    # Načtení žánrů hodnocených knih
    book_genre_stats = Bookgenre.objects.filter(bookid__in=rated_books) \
        .values('genreid') \
        .annotate(count=Count('genreid')) \
        .order_by('-count')
    
    # Výpočet procent pro knižní žánry
    book_genre_percentages = []
    for stat in book_genre_stats:
        genre_name = Metagenre.objects.get(genreid=stat['genreid']).genrenamecz
        percentage = (stat['count'] / total_books) * 100 if total_books > 0 else 0
        book_genre_percentages.append({
            'genre': genre_name,
            'percentage': percentage
        })
    
    print(book_genre_percentages)  # Pro ladění
    
    # Načtení zemí hodnocených knih
    country_stats = Book.objects.filter(bookid__in=rated_books, countryid__isnull=False) \
        .values('countryid', 'countryid__countrynamecz') \
        .annotate(count=Count('countryid')) \
        .order_by('-count')
    
    # Výpočet procent pro země knih
    book_country_percentages = []  # Inicializace prázdného seznamu
    for stat in country_stats:
        country_name = stat['countryid__countrynamecz']
        percentage = (stat['count'] / total_books) * 100 if total_books > 0 else 0
        book_country_percentages.append({
            'country': country_name,
            'percentage': percentage
        })
    
    # Omezit výsledek na prvních pět zemí
    book_country_percentages = book_country_percentages[:5]
    
    print(book_country_percentages)  # Pro ladění






    # Zjistí jestli je uživatel můj oblíbený (pro tlačítko "Oblíbený")
    #userprofile_content_type_id = 37
    userprofile_content_type = ContentType.objects.get_for_model(Userprofile)
    userprofile_content_type_id = userprofile_content_type.id

    is_favorite = False
    if Favorite.objects.filter(user=request.user.id, content_type_id=userprofile_content_type_id, object_id=user_profile.userprofileid).exists():
        is_favorite = True

    return render(request, 'user/profile_stats.html', {
        'profile_user': profile_user,
        'user_profile': user_profile,
        'user_div_coins': user_div_coins,
        'genre_percentages': genre_percentages,
        'country_percentages': country_percentages,
        'book_genre_percentages': book_genre_percentages,
        'book_country_percentages': book_country_percentages,
        'is_favorite': is_favorite,
        'active_tab': 'statistiky',
    })


@login_required
def rate_movie(request, movie_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        user = request.user
        movie = Movie.objects.get(id=movie_id)
        # Vytvoření nového záznamu MovieRating s uživatelem
        MovieRating.objects.create(Rating=rating, Movie=movie, User=user)
        return redirect('movie_detail', movie_id=movie_id)
    else:
        # Zobrazte formulář pro hodnocení
        return render(request, 'movies/movie_detail.html', {'movie_id': movie_id})


@csrf_exempt
def add_to_list(request):
    if request.method == "POST":
        data = json.loads(request.body)
        media_id = data.get('media_id')
        list_type = data.get('list_type')
        media_type = data.get('media_type').lower()  # převede na malá písmena

        # Vytvořte nebo získejte seznam podle typu seznamu
        if list_type == "favorite":
            list_name = "Oblíbené"
        elif list_type == "want-to-see":
            list_name = "Chci vidět"

        user_list, created = Userlist.objects.get_or_create(user=request.user, namelist=list_name)

        if media_type == "movie":
            existing_entry = Userlistmovie.objects.filter(movie_id=media_id, userlist=user_list)
            if existing_entry.exists():
                existing_entry.delete()
                return JsonResponse({"success": True, "action": "removed"})
            else:
                Userlistmovie.objects.create(movie_id=media_id, userlist=user_list)


        elif media_type == "book":
            book_instance = Book.objects.get(bookid=media_id)
            Userlistbook.objects.create(book=book_instance, userlist=user_list)



        elif media_type == "game":
            game_instance = Game.objects.get(gameid=media_id)
            Userlistgame.objects.create(game=game_instance, userlist=user_list)
        else:
            return JsonResponse({"success": False, "error": "Unknown media type"})


        return JsonResponse({"success": True, "action": "added"})
    return JsonResponse({"success": False})


#####
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, movieid=movie_id)
    user = request.user

    is_favorite = False
    is_want_to_see = False

    if user.is_authenticated:
        favorite_list = Userlist.objects.filter(user=user, namelist="Oblíbené").first()
        if favorite_list:
            is_favorite = Userlistmovie.objects.filter(userlist=favorite_list, movie=movie).exists()
        
        want_to_see_list = Userlist.objects.filter(user=user, namelist="Chci vidět").first()
        if want_to_see_list:
            is_want_to_see = Userlistmovie.objects.filter(userlist=want_to_see_list, movie=movie).exists()

    # ostatní logika pro zobrazování detailů filmu...

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'is_favorite': is_favorite,
        'is_want_to_see': is_want_to_see,
        # další kontextové proměnné
    })


#####
def ratings_profile(request):
    user_ratings = Movierating.objects.filter(user=request.user)
    return render(request, 'user/ratings_profile.html', {'user_ratings': user_ratings})

# Zobrazení oblíbených filmů uživatele
def favorites_profile(request):
    # Získání instance profilu uživatele
    profile_user = get_object_or_404(User, id=request.user.id)
    user_profile = Userprofile.objects.get(user=profile_user)

    # user_lists = Userlistmovie.objects.filter(
    #     userlist__namelist="Oblíbené",
    #     userlist__user=request.user
    # ).select_related('movie').annotate(
    #     average_rating=F('movie__averagerating')  # Use the direct field
    # )
    user_lists = Userlistmovie.objects.filter(
        userlist__listtype_id=1,
        userlist__user=request.user
    ).select_related('movie').annotate(
        average_rating=F('movie__averagerating')  # Use the direct field
    )

    user_favorites_books = Userlistbook.objects.filter(userlist__listtype_id=4, userlist__user=request.user)

    return render(request, 'user/favorites_profile.html', {
        'user_lists': user_lists,
        "user_favorites_books": user_favorites_books,
        "user_profile": user_profile,
        })

# Zobrazení filmů, které uživatel chce vidět
def iwantsee_profile(request):
    user_lists2 = Userlistmovie.objects.filter(
        userlist__listtype_id=2,
        userlist__user=request.user
    ).select_related('movie').annotate(
        average_rating=F('movie__averagerating')  # Use the direct field
    )
    profile_user = get_object_or_404(User, id=request.user.id)
    user_profile = Userprofile.objects.get(user=profile_user)
    user_wantsee_books = Userlistbook.objects.filter(userlist__listtype_id=5, userlist__user=request.user)
    return render(request, 'user/iwantsee_profile.html', {
        'user_lists2': user_lists2,
        "user_profile": user_profile,
        })

# Zobrazení filmů, které uživatel viděl
def watched_profile(request):
    user_lists3 = Userlistmovie.objects.filter(
        userlist__listtype_id=3,
        userlist__user=request.user
    ).select_related('movie').annotate(
        average_rating=F('movie__averagerating')  # Use the direct field
    )
    profile_user = get_object_or_404(User, id=request.user.id)
    user_profile = Userprofile.objects.get(user=profile_user)
    return render(request, 'user/watched_profile.html', {
        'user_lists3': user_lists3,
        "user_profile": user_profile,
        })


@login_required
def favorite_movies(request):
 # Získání seznamu "Oblíbené" pro aktuálně přihlášeného uživatele
    favorites_list = Userlist.objects.filter(user=request.user, namelist="Oblíbené").first()
    if favorites_list:
        favorite_movies = Userlistmovie.objects.filter(userlist=favorites_list)
    else:
        favorite_movies = None

    return render(request, 'user/user_lists_favorites.html', {'favorite_movies': favorite_movies})


# users
@login_required
def rated_media(request, user_id=None):
    # Implementujte logiku pro zobrazení všeho ohodnoceného média
    if user_id is None:
        user_id = request.user.id
    profile_user = get_object_or_404(User, id=user_id)

    # Assuming content_type_id for movies is defined
    #movie_content_type_id = 33
    movie_content_type = ContentType.objects.get_for_model(Movie)
    movie_content_type_id = movie_content_type.id

    #book_content_type_id = 9
    book_content_type = ContentType.objects.get_for_model(Book)
    book_content_type_id = book_content_type.id

    movie_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=movie_content_type_id).order_by('-modified')
    book_ratings = UserRating.objects.filter(user_id=user_id, rating__content_type_id=book_content_type_id).order_by('-modified')


    user_ratings = UserRating.objects.filter(user_id=user_id).order_by('-modified')
    # Získání instance profilu uživatele
    user_profile = Userprofile.objects.get(user=profile_user)
    # Stránkování pro filmy
    items_per_page = 10
    paginator = Paginator(movie_ratings, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    # Stránkování pro knihy
    book_paginator = Paginator(book_ratings, items_per_page)
    book_page_number = request.GET.get("book_page")
    book_page = book_paginator.get_page(book_page_number)
    
    return render(request, 'user/rated_media.html', {
        'profile_user': profile_user, 
        'user_ratings': user_ratings, 
        'page': page, 
        "book_page": book_page,
        'user_profile': user_profile,
        "movie_ratings": movie_ratings,
        })


@login_required
def review_profile(request):
    profile_user = get_object_or_404(User, id=request.user.id)
    user_profile = Userprofile.objects.get(user=profile_user)
    return render(request, "user/review_profile.html", {
        "user_profile": user_profile,
    })


@login_required
def rated_movies(request):
    # Implementujte logiku pro zobrazení ohodnocených filmů
    return render(request, 'user/rated_movies.html')

@login_required
def rated_books(request):
    # Implementujte logiku pro zobrazení ohodnocených knih
    return render(request, 'user/rated_books.html')

@login_required
def rated_games(request):
    # Implementujte logiku pro zobrazení ohodnocených her
    return render(request, 'user/rated_games.html')

@login_required
def favorite_media(request):
    # Implementujte logiku pro zobrazení všech oblíbených médií
    return render(request, 'user/favorite_media.html')

@login_required
def favorite_actors(request):
    # Implementujte logiku pro zobrazení oblíbených herců
    return render(request, 'user/favorite_actors.html')

@login_required
def favorite_books(request):
    # Implementujte logiku pro zobrazení oblíbených knih
    return render(request, 'user/favorite_books.html')

@login_required
def favorite_drinks(request):
    # Implementujte logiku pro zobrazení oblíbených nápojů
    return render(request, 'user/favorite_drinks.html')

@login_required
def favorite_foods(request):
    # Implementujte logiku pro zobrazení oblíbeného jídla
    return render(request, 'user/favorite_foods.html')

@login_required
def favorite_games(request):
    # Implementujte logiku pro zobrazení oblíbených her
    return render(request, 'user/favorite_games.html')

@login_required
def favorite_items(request):
    # Implementujte logiku pro zobrazení oblíbených předmětů
    return render(request, 'user/favorite_items.html')

@login_required
def favorite_locations(request):
    # Implementujte logiku pro zobrazení oblíbených lokalit
    return render(request, 'user/favorite_locations.html')


@login_required
def user_lists(request):
    # Implementujte logiku pro zobrazení oblíbených předmětů
    return render(request, 'user/user_lists.html')


"""
@login_required
def wantsee_movies(request):
    # Získání seznamu filmů "Chci vidět" pro aktuálně přihlášeného uživatele
    iwantsee_list = Userlist.objects.filter(user=request.user, namelist="Chci vidět").first()
    if iwantsee_list:
        iwantsee_movies = Userlistmovie.objects.filter(userlist=iwantsee_list)
    else:
        iwantsee_movies = None
    return render(request, 'user/iwantsee_profile.html', {'iwantsee_movies': iwantsee_movies})
"""


def update_profile(request):
    avatars = Avatar.objects.all()
    # Získání instance profilu, pokud existuje, nebo vytvoření nového.
    user_profile, created = Userprofile.objects.get_or_create(user=request.user)

    # Získání objektu User a Userdivcoins na základě přihlášeného uživatele
    profile_user = request.user  # Přihlášený uživatel
    user_div_coins = get_object_or_404(Userdivcoins, user_id=profile_user.id)

    profile_of_user = get_object_or_404(User, id=request.user.id)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        avatarid = request.POST.get('avatar')
        
        if form.is_valid():
            if avatarid:
                avatar = Avatar.objects.filter(avatarid=avatarid).first()
                user_profile.avatar = avatar
                # user_profile.save()
            form.save()
            return redirect('myuser_detail')  # Presmerujte na profilovou stránku
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'user/update_profile.html', {
        'form': form,
        'avatars': avatars,
        'user_profile': user_profile,
        'profile_user': profile_of_user,
        'user_div_coins': user_div_coins
        })

# Index chatu (s přehledem všech zpráv)
@login_required
def chat(request):
    sender = request.user.id
    all_chat_sessions = Userchatsession.objects.filter(
        Q(user1=sender) | Q(user2=sender)
    ).select_related('user1__userprofile', 'user2__userprofile'
                     ).prefetch_related('messages'
                     ).annotate(last_message=Max('messages__sentat')).order_by('-last_message')
    
    return render(request, "user/chat.html", {
        "all_chat_sessions": all_chat_sessions,
    })


# posilani zpravy konkretnimu uzivateli pres jeho profil
@login_required
def chat_message(request, user_id):
    sender = request.user.id
    receiver = get_object_or_404(User, id=user_id)
    receiver_userprofile = get_object_or_404(Userprofile, user=receiver.id)

    if sender == receiver.id:
        return render(request, "403.html")

    chat_session, created = Userchatsession.objects.get_or_create(
        user1=request.user if request.user.id < receiver.id else receiver,
        user2=receiver if request.user.id < receiver.id else request.user
    )

    # Když otevřu zprávu, bude mít stav je přečtená – isread=True; kvůli notifikacím
    Usermessage.objects.filter(chatsession=chat_session, sender=receiver, isread=False).update(isread=True)

    if request.method == "POST":
        form = UserMessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.sender = request.user
            new_message.chatsession = chat_session
            new_message.save()
            return redirect("chat_message", user_id=receiver.id)
    else:
        form = UserMessageForm()

    # Vypisuje všechny uživatele, se kterými je založena session -> seznam uživatelů vlevo
    all_chat_sessions = Userchatsession.objects.filter(
        Q(user1=sender) | Q(user2=sender)
    ).select_related('user1__userprofile', 'user2__userprofile'
                     ).prefetch_related('messages'
                     ).annotate(last_message=Max('messages__sentat')).order_by('-last_message')

    # Vypisuje posledních x zpráv z db mezi 2 uživateli 
    chat_sessions = Userchatsession.objects.filter(
        (Q(user1=sender) | Q(user2=sender)) & (Q(user1=receiver) | Q(user2=receiver))
    ).prefetch_related(Prefetch(
        'messages',
        queryset=Usermessage.objects.order_by('-sentat')[:20], 
        to_attr='latest_messages'
    ))
    has_older_messages = (Usermessage.objects.filter(chatsession__in=chat_sessions).count() > 20
)
    last_message_id = (
        chat_sessions[0].latest_messages[0].usermessageid
        if chat_sessions and chat_sessions[0].latest_messages
        else None
    )
    return render(request, "user/chat_message.html", {
        "receiver": receiver,
        "receiver_userprofile": receiver_userprofile,
        "chat_sessions": chat_sessions,
        "all_chat_sessions": all_chat_sessions,
        "has_older_messages": has_older_messages,
        "form": form,
        "last_message_id": last_message_id,
    })


# Načte starší zprávy
@login_required
def load_older_messages(request, user_id):
    sender = request.user
    receiver = get_object_or_404(User, id=user_id)

    chat_session = Userchatsession.objects.filter(
        (Q(user1=sender) | Q(user2=sender)) & (Q(user1=receiver) | Q(user2=receiver))
    ).first()

    if not chat_session:
        return JsonResponse({"error": "Nenalezeno"}, status=404)
    
    last_message_id = request.GET.get("last_message_id", None)
    if not last_message_id:
        return JsonResponse({"error": "No last message ID provided"}, status=400)

    messages = Usermessage.objects.filter(
        chatsession=chat_session,
        usermessageid__lt=last_message_id
    ).order_by('-usermessageid')[:10]

    # messages = messages[::-1]

    messages_data = [
       {
            'id': message.usermessageid,
            'message': message.message,
            'sender': message.sender.username,
            'sender_avatar': message.sender.userprofile.avatar.imagepath if message.sender.userprofile.avatar else 'default_avatar.jpg',
            'sentat': date_format(localtime(message.sentat), format='d. F Y H:i'),
        }
        for message in messages
    ]
    return JsonResponse({"messages": messages_data}, safe=False)


# vyhleda uživatele ve zprávách v searchboxu
def search_user_in_chat(request):
    query = request.GET.get("q", "").strip()
    if not query:
        return JsonResponse({"users": []})

    matching_users = User.objects.filter(username__icontains=query).values("id", "username")[:10]
    return JsonResponse({"users": list(matching_users)})