# VIEWS.series.list

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import Avg
import math
from django.core.paginator import Paginator
from star_ratings.models import Rating, UserRating
from django.shortcuts import render, get_object_or_404, redirect
from div_content.forms.series import SearchForm, TVShowDivRatingForm, CommentForm
from django.db import connection
from div_content.models import (
    Tvcountries, Tvcrew, Tvgenre, Tvkeywords, Tvproductions, Tvseason, Tvshow, Tvepisode, Userlisttype, 
    Userlist, Userlisttvshow, Userlisttvseason, Userlisttvepisode, FavoriteSum, Tvshowcomments
)

# Konstanty
CONTENT_TYPE_SERIES_ID = 40

# Userlisttype pro seriály na testu
userlisttype_oblibeny = 13
userlisttype_chci_videt = 14
userlisttype_serialnuto = 15
userlisttype_serialoteka = 16
# pro sezóny
userlisttype_oblibena_sezona = 17
userlisttype_chci_videt_sezonu = 18
userlisttype_shlednuta_sezona = 19
# pro díly
userlisttype_oblibeny_dil = 20
userlisttype_chci_videt_dil = 21
userlisttype_shlednuty_dil = 22


def series_list(request):

    tvshows_list = Tvshow.objects.all().order_by('-divrating').values('title', 'titlecz', 'description', 'url', 'img')[:15] 
    return render(request, 'series/series_list.html', {'tvshows_list': tvshows_list})


def serie_detail(request, tv_url):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    user = request.user
    comment_form = None # Default value

    # Sezóny seriálu
    seasons = Tvseason.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonnumber')

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
            favourites_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlisttvshow.objects.filter(tvshow__tvshowid=tvshow.tvshowid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel seriál v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlisttvshow.objects.filter(tvshow__tvshowid=tvshow.tvshowid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel seriál v seznamu Seriálnuto(=shlédnuto)
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialnuto)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlisttvshow.objects.filter(tvshow__tvshowid=tvshow.tvshowid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False
    
    # Zjistí, jestli má uživatel seriál v seznamu Seriálotéka
    if user.is_authenticated:
        try:
            library_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialoteka)
            library_list = Userlist.objects.get(user=user, listtype=library_type)
            is_in_library = Userlisttvshow.objects.filter(tvshow__tvshowid=tvshow.tvshowid, userlist=library_list).exists()
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


    return render(request, 'series/serie_detail.html', {
        'tvshow': tvshow,
        'genres': genres,
        'countries': countries,
        'productions': productions,
        'seasons': seasons,
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
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlisttvshow.objects.filter(userlist=favourites_list, tvshow=tvshow).exists():
        pass
    else:
        Userlisttvshow.objects.create(userlist=favourites_list, tvshow=tvshow)
        content_type = ContentType.objects.get(id=CONTENT_TYPE_SERIES_ID)
        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=tvshowid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Přidat do seznamu: Chci vidět
@login_required
def add_to_tvshow_watchlist(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)

    if Userlisttvshow.objects.filter(userlist=watchlist_list, tvshow=tvshow).exists():
       pass
    else:
        Userlisttvshow.objects.create(userlist=watchlist_list, tvshow=tvshow)
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Přidat do seznamu: Seriálnuto
@login_required
def add_to_watched_tvshows(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialnuto)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)

    if Userlisttvshow.objects.filter(userlist=watched_list, tvshow=tvshow).exists():
       pass
    else:
        Userlisttvshow.objects.create(userlist=watched_list, tvshow=tvshow)
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Přidat do seznamu: Seriálotéka
@login_required
def add_to_tvshow_library(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    library_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialoteka)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)

    if Userlisttvshow.objects.filter(userlist=library_list, tvshow=tvshow).exists():
        pass
    else:
        Userlisttvshow.objects.create(userlist=library_list, tvshow=tvshow)
    
    return redirect("serie_detail", tv_url=tvshow.url) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourite_tvshow(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlisttvshow = Userlisttvshow.objects.get(tvshow=tvshow, userlist=favourites_list)
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
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlisttvshow = Userlisttvshow.objects.get(tvshow=tvshow, userlist=watchlist_list)
    userlisttvshow.delete()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Smazat ze seznamu: Seriálnuto
@login_required
def remove_from_watched_tvshows(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialnuto)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlisttvshow = Userlisttvshow.objects.get(tvshow=tvshow, userlist=watched_list)
    userlisttvshow.delete()
    
    return redirect("serie_detail", tv_url=tvshow.url)


# Smazat ze seznamu: Seriálotéka
@login_required
def remove_from_tvshow_library(request, tvshowid):
    tvshow = get_object_or_404(Tvshow, tvshowid=tvshowid)
    library_type = Userlisttype.objects.get(userlisttypeid=userlisttype_serialoteka)
    library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=library_type)
    userlisttvshow = Userlisttvshow.objects.get(tvshow=tvshow, userlist=library_list)
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
            favourites_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibena_sezona)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlisttvseason.objects.filter(tvseason__seasonid=season.seasonid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel sezónu v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_sezonu)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlisttvseason.objects.filter(tvseason__seasonid=season.seasonid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel sezónu v seznamu Shlédnuto
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuta_sezona)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlisttvseason.objects.filter(tvseason__seasonid=season.seasonid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False
    
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
        'episodes': episodes,
        'is_in_favourites': is_in_favourites,
        'is_in_watchlist': is_in_watchlist,
        'is_in_watched': is_in_watched,
    })


# Přidat do seznamu: Oblíbená sezóna
@login_required
def add_to_favourite_tvseason(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibena_sezona)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlisttvseason.objects.filter(userlist=favourites_list, tvseason=tvseason).exists():
        pass
    else:
        Userlisttvseason.objects.create(userlist=favourites_list, tvseason=tvseason)

    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Přidat do seznamu: Chci vidět sezónu
@login_required
def add_to_tvseason_watchlist(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_sezonu)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)

    if Userlisttvseason.objects.filter(userlist=watchlist_list, tvseason=tvseason).exists():
       pass
    else:
        Userlisttvseason.objects.create(userlist=watchlist_list, tvseason=tvseason)
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl) 


# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuta_sezona)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)

    if Userlisttvseason.objects.filter(userlist=watched_list, tvseason=tvseason).exists():
       pass
    else:
        Userlisttvseason.objects.create(userlist=watched_list, tvseason=tvseason)
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl) 


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourite_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibena_sezona)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlisttvseason = Userlisttvseason.objects.get(tvseason=tvseason, userlist=favourites_list)
    userlisttvseason.delete()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Smazat ze seznamu: Chci vidět
@login_required
def remove_from_tvseason_watchlist(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_sezonu)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlisttvseason = Userlisttvseason.objects.get(tvseason=tvseason, userlist=watchlist_list)
    userlisttvseason.delete()
    
    return redirect("serie_season", tv_url=tvseason.tvshowid.url, seasonurl=tvseason.seasonurl)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched_tvseasons(request, tv_url, tvseasonid):
    tvseason = get_object_or_404(Tvseason, seasonid=tvseasonid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuta_sezona)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlisttvseason = Userlisttvseason.objects.get(tvseason=tvseason, userlist=watched_list)
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

    # Zjistí, jestli má uživatel sezónu v seznamu Oblíbené
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny_dil)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlisttvepisode.objects.filter(tvepisode__episodeid=episode.episodeid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    # Zjistí, jestli má uživatel sezónu v seznamu Chci vidět
    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_dil)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlisttvepisode.objects.filter(tvepisode__episodeid=episode.episodeid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    # Zjistí, jestli má uživatel sezónu v seznamu Shlédnuto
    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuty_dil)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlisttvepisode.objects.filter(tvepisode__episodeid=episode.episodeid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False


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
    })


# Přidat do seznamu: Oblíbený díl
@login_required
def add_to_favourite_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny_dil)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlisttvepisode.objects.filter(userlist=favourites_list, tvepisode=tvepisode).exists():
        pass
    else:
        Userlisttvepisode.objects.create(userlist=favourites_list, tvepisode=tvepisode)
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Přidat do seznamu: Chci vidět díl
@login_required
def add_to_tvepisode_watchlist(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_dil)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)

    if Userlisttvepisode.objects.filter(userlist=watchlist_list, tvepisode=tvepisode).exists():
       pass
    else:
        Userlisttvepisode.objects.create(userlist=watchlist_list, tvepisode=tvepisode)
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched_tvepisode(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuty_dil)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)

    if Userlisttvepisode.objects.filter(userlist=watched_list, tvepisode=tvepisode).exists():
       pass
    else:
        Userlisttvepisode.objects.create(userlist=watched_list, tvepisode=tvepisode)
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Smazat ze seznamu: Oblíbený díl
@login_required
def remove_from_favourite_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=userlisttype_oblibeny_dil)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlisttvepisode = Userlisttvepisode.objects.get(tvepisode=tvepisode, userlist=favourites_list)
    userlisttvepisode.delete()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)

# Smazat ze seznamu: Chci vidět díl
@login_required
def remove_from_tvepisode_watchlist(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=userlisttype_chci_videt_dil)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlisttvepisode = Userlisttvepisode.objects.get(tvepisode=tvepisode, userlist=watchlist_list)
    userlisttvepisode.delete()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched_tvepisodes(request, tv_url, seasonurl, tvepisodeid):
    tvepisode = get_object_or_404(Tvepisode, episodeid=tvepisodeid)
    watched_type = Userlisttype.objects.get(userlisttypeid=userlisttype_shlednuty_dil)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlisttvepisode = Userlisttvepisode.objects.get(tvepisode=tvepisode, userlist=watched_list)
    userlisttvepisode.delete()
    
    return redirect("serie_episode", tv_url=tvepisode.seasonid.tvshowid.url, seasonurl=tvepisode.seasonid.seasonurl, episodeurl=tvepisode.episodeurl)