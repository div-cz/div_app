# VIEWS.series.list
# IMPORT na začátku, řazeno abecedně
import math

from datetime import timedelta

from div_content.models import (
    Tvcountries, Tvcrew, Tvgenre, Tvkeywords, Tvproductions, Tvseason, Tvshow, Tvshowquotes, Tvepisode, Userlisttype, 
    Userlist, Userlistitem, Userlisttvshow, Userlisttvseason, Userlisttvepisode, FavoriteSum, Tvshowcomments
)

from div_content.forms.series import CommentForm, SearchForm, TVShowDivRatingForm

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

from django.db import models 
from django.db import connection
from django.db.models import Avg, Prefetch

from django.shortcuts import get_object_or_404, redirect, render

from django.utils import timezone

from star_ratings.models import Rating, UserRating


# Konstanty
#CONTENT_TYPE použit v books, movies, authors, characters, series, creators
#CONTENT_TYPE_SERIES_ID = 40 # tvshow
tvshow_content_type = ContentType.objects.get_for_model(Tvshow)
CONTENT_TYPE_SERIES_ID = tvshow_content_type.id
#CONTENT_TYPE_TVSEASON_ID = 41 # tvseason
tvseason_content_type = ContentType.objects.get_for_model(Tvseason)
CONTENT_TYPE_TVSEASON_ID = tvseason_content_type.id
#CONTENT_TYPE_TVEPISODE_ID = 43 # tvepisode
tvepisode_content_type = ContentType.objects.get_for_model(Tvepisode)
CONTENT_TYPE_TVEPISODE_ID = tvepisode_content_type.id

# Userlisttype pro seriály na testu
USERLISTTYPE_OBLIBENY = 13
USERLISTTYPE_CHCI_VIDET = 14
USERLISTTYPE_SERIALNUTO = 15
USERLISTTYPE_SERIALOTEKA = 16
# pro sezóny
USERLISTTYPE_OBLIBENA_SEZONA = 17
USERLISTTYPE_CHCI_VIDET_SEZONU = 18
USERLISTTYPE_SHLEDNUTA_SEZONA = 19
# pro díly
USERLISTTYPE_OBLIBENY_DIL = 20
USERLISTTYPE_CHCI_VIDET_DIL = 21
USERLISTTYPE_SHLEDNUTY_DIL = 22


def series_list(request):

    #tvshows_list = Tvshow.objects.all().order_by('-divrating').values('title', 'titlecz', 'description', 'url', 'img')[:15] 
    tvshow_content_type = ContentType.objects.get_for_model(Tvshow)
    tvshows_list = Tvshow.objects.all().annotate(
        average_rating=models.Subquery(
            Rating.objects.filter(
                content_type=tvshow_content_type,
                object_id=models.OuterRef('tvshowid')
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
    for tvshow in tvshows_list:
        if tvshow['average_rating'] is not None:
            tvshow['average_rating'] = round(float(tvshow['average_rating']) * 20)  # převod z 5 na 100%
        else:
            tvshow['average_rating'] = 0


    #latest_episodes = Tvepisode.objects.select_related(
    #    'seasonid',  # Join s TVSeason
    #    'seasonid__tvshowid'  # Join s TVShow
    #).filter(
    #    seasonid__tvshowid__divrating__gt=4000,  # Pouze z top seriálů
    #    airdate__lte=timezone.now()  # Pouze odvysílané díly
    #).order_by(
    #    '-airdate'  # Seřazení od nejnovějších
    #)[:20]  

    # NOVÉ SEZÓNY
    now = timezone.now()
    two_months_ago = now - timedelta(days=60)
    two_months_future = now + timedelta(days=60)

    # Nejnovější sezóny z top seriálů +- 2 měsíce
    now = timezone.now()
    two_months_ago = now - timedelta(days=60)
    latest_seasons = Tvseason.objects.select_related('tvshowid').filter(
        tvshowid__divrating__gt=3000,  # Top seriály
        premieredate__gte=two_months_ago,  # Od dvou měsíců zpět
        premieredate__isnull=False  # Musí mít datum premiéry
    ).order_by(
        'premieredate'  # Seřadíme podle data premiéry (budoucí na konci)
    )[:9]

    return render(request, 'series/series_list.html', {'tvshows_list': tvshows_list, 'latest_seasons': latest_seasons})


def series_alphabetical(request):
    return render(request, "series/series_alphabetical.html")


def serie_detail(request, tv_url):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    user = request.user
    comment_form = None # Default value

    # Sezóny seriálu
    seasons = Tvseason.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonnumber')
    #episodes = Tvepisode.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonid', 'episodenumber')
    episodes = Tvepisode.objects.filter(seasonid__tvshowid=tvshow.tvshowid).order_by('seasonid', 'episodenumber')

    # Paginator
    items_per_page = 40
    content_items_per_page = 20 # content uprostřed

    season_paginator = Paginator(seasons, items_per_page)
    content_season_paginator = Paginator(seasons, content_items_per_page)

    serie_page_number = request.GET.get('page')
    content_page_number = request.GET.get('content_page')

    serie_page = season_paginator.get_page(serie_page_number)
    content_season_page = content_season_paginator.get_page(content_page_number)

    # Žánry, státy, produkce
    genres = Tvgenre.objects.filter(tvshowid=tvshow.tvshowid).select_related('genreid')
    countries = Tvcountries.objects.filter(tvshowid=tvshow.tvshowid).select_related('countryid')
    productions = Tvproductions.objects.filter(tvshowid=tvshow.tvshowid).select_related('metaproductionid')

    # Hodnocení pro TV Show
    tvshow_content_type = ContentType.objects.get_for_model(Tvshow)
    ratings = UserRating.objects.filter(rating__content_type=tvshow_content_type, rating__object_id=tvshow.tvshowid)

    # Výpočet průměrného hodnocení
    average_rating_result = ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result.get('average')
    if average_rating is not None:
        average_rating = math.ceil(average_rating)
    else:
        average_rating = 0

    # Získání uživatelského hodnocení
    user_rating = None
    if user.is_authenticated:
        user_rating = UserRating.objects.filter(user=user, rating__object_id=tvshow.tvshowid).first()


    # Získání herců a postav pro seriál
    actors_and_characters = Tvcrew.objects.filter(tvshowid=tvshow.tvshowid, roleid='378').select_related('peopleid', 'characterid')
    actors_and_characters2 = Tvcrew.objects.filter(tvshowid=tvshow.tvshowid, roleid='378').select_related('peopleid', 'characterid')[:10]
    directors = Tvcrew.objects.filter(tvshowid=tvshow.tvshowid, roleid='383').select_related('peopleid')  # Režie

    # Zjistí, jestli má uživatel seriál v seznamu Oblíbené
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=tvshow.tvshowid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel seriál v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlistitem.objects.filter(object_id=tvshow.tvshowid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel seriál v seznamu Seriálnuto(=shlédnuto)
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALNUTO)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlistitem.objects.filter(object_id=tvshow.tvshowid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False
    
    # Zjistí, jestli má uživatel seriál v seznamu Seriálotéka
    if user.is_authenticated:
        try:
            library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALOTEKA)
            library_list = Userlist.objects.get(user=user, listtype=library_type)
            is_in_library = Userlistitem.objects.filter(object_id=tvshow.tvshowid, userlist=library_list).exists()
        except Exception as e:
            is_in_library = False
    else:
        is_in_library = False

    #  Recenze k seriálům

    # if user.is_authenticated:
    #     user_rating = Tvshowrating.objects.filter(user=user, tvshowid=tvshow).first()
        
    #     if 'comment' in request.POST:
    #         comment_form = CommentForm(request.POST)
    #         if comment_form.is_valid():
    #             comment = comment_form.cleaned_data['comment']
    #             Tvshowcomments.objects.create(comment=comment, tvshowkid=tvshow, user=request.user)
    #             return redirect('series_detail', tv_url=tvshow.url)
    #         else:
    #             print(comment_form.errors)
    #     else:
    #         comment_form = CommentForm(request=request)

    # Formulář pro úpravu DIV Ratingu u TVShow
    tvshow_div_rating_form = None
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_divrating' in request.POST:
            tvshow_div_rating_form = TVShowDivRatingForm(request.POST, instance=tvshow)
            if tvshow_div_rating_form.is_valid():
                tvshow_div_rating_form.save()
                return redirect('serie_detail', tv_url=tvshow.url)
        else:
            tvshow_div_rating_form = TVShowDivRatingForm(instance=tvshow)


    # Hlášky k dílům
    quotes = Tvshowquotes.objects.filter(tv_show=tvshow).select_related('actor', 'character')

    # Přidávání nové hlášky
    if request.method == 'POST' and 'quote_text' in request.POST:
        quote_text = request.POST.get('quote_text').strip()
        if quote_text:
            Tvshowquotes.objects.create(
                quote=quote_text,
                tv_show=tvshow,
                user=request.user if request.user.is_authenticated else None,
                div_rating=0
            )
            return redirect('serie_detail', tv_url=tvshow.url)


    return render(request, 'series/serie_detail.html', {
        'tvshow': tvshow,
        'genres': genres,
        'countries': countries,
        'productions': productions,
        'seasons': seasons,
        'episodes': episodes,
        'ratings': ratings,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'actors_and_characters': actors_and_characters,
        'actors_and_characters2': actors_and_characters2,
        'directors': directors,
        "is_in_favourites": is_in_favourites,
        "is_in_watchlist": is_in_watchlist,
        "is_in_watched": is_in_watched,
        "is_in_library": is_in_library,
        'tvshow_div_rating_form': tvshow_div_rating_form,
        "serie_page": serie_page,
        "content_season_page": content_season_page,
        'quotes': quotes,
    })


@login_required
def rate_tvshow(request, tvshow_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))  # Získání hodnocení z POST
        user = request.user
        tvshow = get_object_or_404(Tvshow, tvshowid=tvshow_id)  # Používáme tvshowid

        # Vytvoření nebo aktualizace hodnocení uživatele pro seriál
        Tvshowrating.objects.update_or_create(
            tvshow=tvshow,
            user=user,
            defaults={'rating': rating}
        )

        # Přesměrování zpět na detail seriálu po úspěšném hodnocení
        return redirect('series_detail', tv_url=tvshow.url)
    else:
        # Pokud není POST požadavek, vrátit detail seriálu
        return redirect('series_detail', tv_url=tvshow.url)


def search_tvshow(request):
    series = []
    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            series = Tvshow.objects.filter(titlecz__icontains=query)[:50]
    else:
        form = SearchForm()

    return render(request, 'series/series_search.html', {'form': form, 'series': series})


# Přidat do seznamu: Oblíbený seriál
@login_required
def add_to_favourite_tvshow(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=tvshowid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=tvshowid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvshowid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Přidat do seznamu: Chci vidět
@login_required
def add_to_tvshow_watchlist(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)

    if Userlistitem.objects.filter(userlist=watchlist_list, object_id=tvshowid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
        Userlistitem.objects.create(
            userlist=watchlist_list, 
            content_type=content_type,
            object_id=tvshowid
            )
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Přidat do seznamu: Seriálnuto
@login_required
def add_to_watched_tvshows(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALNUTO)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)

    if Userlistitem.objects.filter(userlist=watched_list, object_id=tvshowid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
        Userlistitem.objects.create(
            userlist=watched_list, 
            content_type=content_type,
            object_id=tvshowid
            )
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Přidat do seznamu: Seriálotéka
@login_required
def add_to_tvshow_library(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALOTEKA)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)

    if Userlistitem.objects.filter(userlist=library_list, object_id=tvshowid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
        Userlistitem.objects.create(
            userlist=library_list, 
            content_type=content_type,
            object_id=tvshowid
            )
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourite_tvshow(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)
    userlisttvshow = Userlistitem.objects.get(object_id=tvshowid, userlist=favourites_list)
    userlisttvshow.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvshowid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("serie_detail", tv_url=tvshow.url)

# Smazat ze seznamu: Chci vidět
@login_required
def remove_from_tvshow_watchlist(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET)
    watchlist_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watchlist_type)
    userlisttvshow = Userlistitem.objects.get(object_id=tvshowid, userlist=watchlist_list)
    userlisttvshow.delete()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Smazat ze seznamu: Seriálnuto
@login_required
def remove_from_watched_tvshows(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALNUTO)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlisttvshow = Userlistitem.objects.get(object_id=tvshowid, userlist=watched_list)
    userlisttvshow.delete()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Smazat ze seznamu: Seriálotéka
@login_required
def remove_from_tvshow_library(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SERIALOTEKA)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)
    userlisttvshow = Userlistitem.objects.get(object_id=tvshowid, userlist=library_list)
    userlisttvshow.delete()
    
    return redirect("serie_detail", tv_url=tvshow.url)


def serie_season(request, tv_url, seasonurl):
    user = request.user
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    episodes = Tvepisode.objects.filter(seasonid=season.seasonid)
    if episodes.exists():
        first_episode = episodes[0]  # Get the first episode if it exists
    else:
        first_episode = None 

    # Get the previous season
    previous_season = Tvseason.objects.filter(
        tvshowid=tvshow.tvshowid, 
        seasonnumber__lt=season.seasonnumber
    ).order_by('-seasonnumber').first()
    # Get the next season
    next_season = Tvseason.objects.filter(
        tvshowid=tvshow.tvshowid, 
        seasonnumber__gt=season.seasonnumber
    ).order_by('seasonnumber').first()


    genres = Tvgenre.objects.filter(tvshowid=tvshow.tvshowid).select_related('genreid')
    countries = Tvcountries.objects.filter(tvshowid=tvshow.tvshowid).select_related('countryid')
    productions = Tvproductions.objects.filter(tvshowid=tvshow.tvshowid).select_related('metaproductionid')
    seasons = Tvseason.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonnumber')
    directors = Tvcrew.objects.filter(tvshowid=tvshow.tvshowid, roleid='383').select_related('peopleid')

    # Zjistí, jestli má uživatel sezónu v seznamu Oblíbené
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENA_SEZONA)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=season.seasonid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel sezónu v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_SEZONU)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlistitem.objects.filter(object_id=season.seasonid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel sezónu v seznamu Shlédnuto
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTA_SEZONA)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlistitem.objects.filter(object_id=season.seasonid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False

    # Hlášky pro sezónu
    quotes = Tvshowquotes.objects.filter(season=season).select_related('actor', 'character', 'episode')

    # Přidávání nové hlášky pro sezónu
    if request.method == 'POST' and 'quote_text' in request.POST:
        quote_text = request.POST.get('quote_text').strip()
        if quote_text:
            Tvshowquotes.objects.create(
                quote=quote_text,
                tv_show=tvshow,
                season=season,
                user=request.user if request.user.is_authenticated else None,
                div_rating=0
            )
            return redirect('serie_season', tv_url=tvshow.url, seasonurl=season.seasonurl)


    return render(request, 'series/serie_season.html', {
        'tvshow': tvshow,
        'season': season,
        'genres': genres,
        'countries': countries,
        'productions': productions,
        'seasons': seasons,
        'previous_season': previous_season,
        'next_season': next_season,
        'directors': directors,
        'quotes': quotes,
        'episodes': episodes,
        'is_in_favourites': is_in_favourites,
        'is_in_watchlist': is_in_watchlist,
        'is_in_watched': is_in_watched,
    })


# Přidat do seznamu: Oblíbená sezóna
@login_required
def add_to_favourite_tvseason(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENA_SEZONA)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=tvseasonid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVSEASON_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=tvseasonid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvseasonid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Přidat do seznamu: Chci vidět sezónu
@login_required
def add_to_tvseason_watchlist(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_SEZONU)
    watchlist_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watchlist_type)

    if Userlistitem.objects.filter(userlist=watchlist_list, object_id=tvseasonid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVSEASON_ID)
        Userlistitem.objects.create(
            userlist=watchlist_list, 
            content_type=content_type,
            object_id=tvseasonid
            )
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl) 


# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTA_SEZONA)
    watched_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watched_type)

    if Userlistitem.objects.filter(userlist=watched_list, object_id=tvseasonid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVSEASON_ID)
        Userlistitem.objects.create(
            userlist=watched_list, 
            content_type=content_type,
            object_id=tvseasonid
            )
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourite_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENA_SEZONA)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)
    userlisttvseason = Userlistitem.objects.get(object_id=tvseasonid, userlist=favourites_list)
    userlisttvseason.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_TVSEASON_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvseasonid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Smazat ze seznamu: Chci vidět
@login_required
def remove_from_tvseason_watchlist(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_SEZONU)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlisttvseason = Userlistitem.objects.get(object_id=tvseasonid, userlist=watchlist_list)
    userlisttvseason.delete()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTA_SEZONA)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlisttvseason = Userlistitem.objects.get(object_id=tvseasonid, userlist=watched_list)
    userlisttvseason.delete()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


def serie_episode(request, tv_url, seasonurl, episodeurl):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    episode = get_object_or_404(Tvepisode, seasonid=season.seasonid, episodeurl=episodeurl)

    # PREVIOUS
    previous_episode = Tvepisode.objects.filter(
        seasonid=season.seasonid,
        episodenumber__lt=episode.episodenumber  # Hledáme epizodu s menším číslem
    ).order_by('-episodenumber').first()  # Seřadíme od nejvyššího k nejnižšímu
    # NEXT 
    next_episode = Tvepisode.objects.filter(
        seasonid=season.seasonid,
        episodenumber__gt=episode.episodenumber  # Hledáme epizodu s menším číslem
    ).order_by('episodenumber').first()  # Seřadíme od nejvyššího k nejnižšímu

    genres = Tvgenre.objects.filter(tvshowid=tvshow.tvshowid).select_related('genreid')
    countries = Tvcountries.objects.filter(tvshowid=tvshow.tvshowid).select_related('countryid')
    productions = Tvproductions.objects.filter(tvshowid=tvshow.tvshowid).select_related('metaproductionid')
    seasons = Tvseason.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonnumber')
    directors = Tvcrew.objects.filter(tvshowid=tvshow.tvshowid, roleid='383').select_related('peopleid')

    user = request.user

    # Zjistí, jestli má uživatel díl v seznamu Oblíbené
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY_DIL)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=episode.episodeid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel díl v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_DIL)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlistitem.objects.filter(object_id=episode.episodeid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel díl v seznamu Shlédnuto
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTY_DIL)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlistitem.objects.filter(object_id=episode.episodeid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False

    # Hlášky pro epizodu
    quotes = Tvshowquotes.objects.filter(episode=episode).select_related('actor', 'character')

    # Přidávání nové hlášky pro epizodu
    if request.method == 'POST' and 'quote_text' in request.POST:
        quote_text = request.POST.get('quote_text').strip()
        if quote_text:
            Tvshowquotes.objects.create(
                quote=quote_text,
                tv_show=tvshow,
                season=season,
                episode=episode,
                user=request.user if request.user.is_authenticated else None,
                div_rating=0
            )
            return redirect('serie_episode', tv_url=tvshow.url, seasonurl=season.seasonurl, episodeurl=episode.episodeurl)





    return render(request, 'series/serie_episode.html', {
        'tvshow': tvshow,
        'season': season,
        'genres': genres,
        'countries': countries,
        'productions': productions,
        'seasons': seasons,
        'directors': directors,
        'episode': episode,
        'previous_episode': previous_episode,
        'next_episode': next_episode,
        'is_in_favourites': is_in_favourites,
        'is_in_watchlist': is_in_watchlist,
        'is_in_watched': is_in_watched,
        'quotes': quotes,
    })


# Přidat do seznamu: Oblíbený díl
@login_required
def add_to_favourite_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY_DIL)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=tvepisodeid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVEPISODE_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type = content_type,
            object_id=tvepisodeid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvepisodeid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Přidat do seznamu: Chci vidět díl
@login_required
def add_to_tvepisode_watchlist(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_DIL)
    watchlist_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watchlist_type)

    if Userlistitem.objects.filter(userlist=watchlist_list, object_id=tvepisodeid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVEPISODE_ID)
        Userlistitem.objects.create(
            userlist=watchlist_list, 
            content_type=content_type,
            object_id=tvepisodeid
            )
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched_tvepisode(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTY_DIL)
    watched_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watched_type)

    if Userlistitem.objects.filter(userlist=watched_list, object_id=tvepisodeid).exists():
       pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_TVEPISODE_ID)
        Userlistitem.objects.create(
            userlist=watched_list, 
            content_type=content_type,
            object_id=tvepisodeid
            )
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Smazat ze seznamu: Oblíbený díl
@login_required
def remove_from_favourite_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_OBLIBENY_DIL)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlisttvepisode = Userlistitem.objects.get(object_id=tvepisodeid, userlist=favourites_list)
    userlisttvepisode.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_TVEPISODE_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvepisodeid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)

# Smazat ze seznamu: Chci vidět díl
@login_required
def remove_from_tvepisode_watchlist(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_CHCI_VIDET_DIL)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlisttvepisode = Userlistitem.objects.get(object_id=tvepisodeid, userlist=watchlist_list)
    userlisttvepisode.delete()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_SHLEDNUTY_DIL)
    watched_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=watched_type)
    userlisttvepisode = Userlistitem.objects.get(object_id=tvepisodeid, userlist=watched_list)
    userlisttvepisode.delete()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)