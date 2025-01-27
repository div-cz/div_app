# VIEWS.GAMES.PY TEST
# IMPORT na začátku, řazeno abecedně
import math

from div_content.models import (
    Game, Gamecomments, Gamedevelopers, Gamegenre, Gameplatform, Gamepublisher, Gamepurchase, Gamerating, Metacountry, Metadeveloper, Metagenre, Metaplatform, Metapublisher, Metauniversum, Userlisttype, Userlist, 
    Userlistgame, FavoriteSum, Userlistitem
)
from div_content.forms.games import CommentFormGame, GameForm, GameDivRatingForm

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

from django.db import models
from django.db.models import Avg, Count

from django.http import JsonResponse

from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.http import require_POST
from star_ratings.models import Rating, UserRating






# Konstanty
USERLISTTYPE_FAVORITE_GAME_ID = 7 # Oblíbená hra
USERLISTTYPE_PLAYLIST_ID = 8 # Chci hrát
USERLISTTYPE_PLAYED_GAMES_ID = 9 # Odehráno
USERLISTTYPE_GAME_LIBRARY_ID = 12 # Gamotéka

CONTENT_TYPE_GAME_ID = 19


def games(request):
    carousel_games = Game.objects.all().order_by('-divrating')[:10]

    #games = Game.objects.all().order_by('-divrating')[:20] 
    # Získáme hry včetně jejich hodnocení
    game_content_type = ContentType.objects.get_for_model(Game)
    games = Game.objects.all().annotate(
        average_rating=models.Subquery(
            Rating.objects.filter(
                content_type=game_content_type,
                object_id=models.OuterRef('gameid')
            ).values('average')[:1]
        )
    ).order_by('-divrating').values(
        'title', 
        'titlecz', 
        'description', 
        'descriptioncz', 
        'year',
        'url', 
        'img',
        'average_rating'
    )[:20]

    # Zaokrouhlíme hodnoty na celá čísla a převedeme na procenta
    for game in games:
        if game['average_rating'] is not None:
            game['average_rating'] = round(float(game['average_rating']) * 20)  # převod z 5 na 100%
        else:
            game['average_rating'] = 0
    # //
    return render(request, 'games/games_list.html', {
        'games': games, 
        'carousel_games': carousel_games,
        'category_key': 'hry',
        })



def games_genres(request):
    return render(request, 'games/games_genres.html')


def publishers_list(request):
    publishers = Metapublisher.objects.all().order_by('publisher')  # Seznam všech vydavatelů
    
    paginator = Paginator(publishers, 50)
    page_number = request.GET.get('page')
    publishers = paginator.get_page(page_number)
    return render(request, 'games/publishers_list.html', {'publishers': publishers})

def games_alphabetical(request):
    return render(request, 'games/games_alphabetical.html')

def games_by_developer(request, developer_url):
    developer = get_object_or_404(Metadeveloper, developerurl=developer_url)
    games = Game.objects.filter(
        gamedevelopers__developerid=developer
    ).distinct()

    # Stránkování
    paginator = Paginator(games, 50)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)

    return render(request, 'games/games_by_developer.html', {
        'developer': developer,
        'games': games
    })


def games_by_publisher(request, publisher_url):
    publisher = get_object_or_404(Metapublisher, publisherurl=publisher_url)
    games = Game.objects.filter(gamepublisher__publisherid=publisher).distinct()
    # Stránkování
    paginator = Paginator(games, 50)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)
    return render(request, 'games/games_by_publisher.html', {'publisher': publisher, 'games': games})


def games_by_genre(request, genre_url):
    genre = get_object_or_404(Metagenre, url=genre_url)
    games = Gamegenre.objects.filter(genreid=genre).select_related('gameid')
    # Stránkování
    paginator = Paginator(games, 50)  # 30 her na stránku
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)

    return render(request, 'games/games_by_genre.html', {'games': games, 'genre': genre})


def games_by_year(request, year):
    games = Game.objects.filter(year=year)
    # Stránkování
    paginator = Paginator(games, 50)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)
    return render(request, 'games/games_by_year.html', {'year': year, 'games': games})


def game_detail(request, game_url):
    game = get_object_or_404(Game, url=game_url)
    user = request.user
    comment_form = None

    genres = Gamegenre.objects.filter(gameid=game).select_related('genreid')

    developers = Gamedevelopers.objects.filter(gameid=game)
    platforms = Gameplatform.objects.filter(gameid=game)
    publishers = Gamepublisher.objects.filter(gameid=game)


    # Fetch comments associated with the game
    comments = Gamecomments.objects.filter(gameid=game).order_by('-commentid')



    if user.is_authenticated:
        if 'comment' in request.POST:
            comment_form = CommentFormGame(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data['comment']
                Gamecomments.objects.create(comment=comment, gameid=game, user=request.user)
                return redirect('game_detail', game_url=game_url)
            else:
                print(comment_form.errors)
        else:
            comment_form = CommentFormGame(request=request)

    is_in_favourites, is_in_want_to_play, is_in_played, is_in_game_library = False, False, False, False

    user = request.user
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_GAME_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=game.gameid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False
    
    if user.is_authenticated:
        try:
            playlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYLIST_ID)
            playlist_list = Userlist.objects.get(user=user, listtype=playlist_type)
            is_in_playlist = Userlistitem.objects.filter(object_id=game.gameid, userlist=playlist_list).exists()
        except Exception as e:
            is_in_playlist = False
    else:
        is_in_playlist = False

    if user.is_authenticated:
        try:
            played_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYED_GAMES_ID)
            played_list = Userlist.objects.get(user=user, listtype=played_type)
            is_in_played = Userlistitem.objects.filter(object_id=game.gameid, userlist=played_list).exists()
        except Exception as e:
            is_in_played = False
    else:
        is_in_played = False
    
    if user.is_authenticated:
        try:
            game_library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_GAME_LIBRARY_ID)
            game_library_list = Userlist.objects.get(user=user, listtype=game_library_type)
            is_in_game_library = Userlistitem.objects.filter(object_id=game.gameid, userlist=game_library_list).exists()
        except Exception as e:
            is_in_game_library = False
    else:
        is_in_game_library = False




    # Game rating
    game_content_type = ContentType.objects.get_for_model(Game)
    ratings = UserRating.objects.filter(rating__content_type=game_content_type, rating__object_id=game.gameid)

    average_rating_result = ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result.get('average')
    if average_rating is not None:
        average_rating = math.ceil(average_rating)
    else:
        average_rating = 0

    user_rating = None
    if user.is_authenticated:
        user_rating = UserRating.objects.filter(user=user, rating__object_id=game.gameid).first()


    # Formulář pro úpravu DIV Ratingu u Game
    game_div_rating_form = None
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_divrating' in request.POST:
            game_div_rating_form = GameDivRatingForm(request.POST, instance=game)
            if game_div_rating_form.is_valid():
                game_div_rating_form.save()
                return redirect('game_detail', game_url=game_url)
        else:
            game_div_rating_form = GameDivRatingForm(instance=game)



    return render(request, 'games/game_detail.html', {
        'game': game,
        'genres': genres,
        'developers': developers,
        'platforms': platforms,
        'publishers': publishers,
        "comment_form": comment_form,
        "comments": comments,
        "is_in_favourites": is_in_favourites,
        "is_in_playlist": is_in_playlist,
        "is_in_played": is_in_played,
        "is_in_game_library": is_in_game_library,
        'ratings': ratings,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'game_div_rating_form': game_div_rating_form,
        })




@login_required
def rate_game(request, game_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        user = request.user
        game = get_object_or_404(Game, id=game_id)

        # Vytvoření nebo aktualizace hodnocení uživatele pro hru
        GameRating.objects.update_or_create(
            Game=game,
            User=user,
            defaults={'Rating': rating}
        )
        
        # Přesměrování na detail hry po úspěšném hodnocení
        return redirect('game_detail', game_id=game_id)
    
    else:
        # Zobrazte formulář pro hodnocení
        return render(request, 'games/game_detail.html', {'game_id': game_id})



# Přidání hry

def game_add(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('games/game_add_success')  # Přesměrování po úspěšném přidání
    else:
        form = GameForm()
    return render(request, 'games/game_add.html', {'form': form})


def developer_list_ajax(request):
    term = request.GET.get('q', '')
    developers = Metadeveloper.objects.filter(developer__icontains=term)[:50]
    results = [{'id': dev.developerid, 'text': dev.developer} for dev in developers]
    return JsonResponse({'results': results})


def platform_list_ajax(request):
    term = request.GET.get('q', '')
    platforms = Metaplatform.objects.filter(platform__icontains=term)[:50]
    results = [{'id': plat.platformid, 'text': plat.platform} for plat in platforms]
    return JsonResponse({'results': results})


def publisher_list_ajax(request):
    term = request.GET.get('q', '')
    publishers = Metapublisher.objects.filter(publisher__icontains=term)[:50]
    results = [{'id': pub.publisherid, 'text': pub.publisher} for pub in publishers]
    return JsonResponse({'results': results})


def country_list_ajax(request):
    term = request.GET.get('q', '')
    countries = Metacountry.objects.filter(countryname__icontains=term)[:50]
    results = [{'id': country.countryid, 'text': country.countryname} for country in countries]
    return JsonResponse({'results': results})


def universum_list_ajax(request):
    term = request.GET.get('q', '')
    universes = Metauniversum.objects.filter(universumname__icontains=term)[:50]
    results = [{'id': universe.universumid, 'text': universe.universumname} for universe in universes]
    return JsonResponse({'results': results})

    

# Přidat do seznamu: Oblíbená hra
@login_required
def add_to_favourite_games(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_GAME_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=gameid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_GAME_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=gameid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=gameid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("game_detail", game_url=game.url)

# Přidat do seznamu: Chci hrát
@login_required
def add_to_playlist_games(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    playlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYLIST_ID)
    playlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=playlist_type)

    if Userlistitem.objects.filter(userlist=playlist_list, object_id=gameid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_GAME_ID)
        Userlistitem.objects.create(
            userlist=playlist_list, 
            content_type=content_type,
            object_id=gameid
            )
    
    return redirect("game_detail", game_url=game.url)


# Přidat do seznamu: Odehráno
@login_required
def add_to_played(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    played_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYED_GAMES_ID)
    played_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=played_type)

    if Userlistitem.objects.filter(userlist=played_list, object_id=gameid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_GAME_ID)
        Userlistitem.objects.create(
            userlist=played_list, 
            content_type=content_type,
            object_id=gameid
            )
    
    return redirect("game_detail", game_url=game.url)


# Přidat do seznamu: Gamotéka (Userlisttypeid=12)
@login_required
def add_to_game_library(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    gamelibrary_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_GAME_LIBRARY_ID)
    gamelibrary_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=gamelibrary_type)

    if Userlistitem.objects.filter(userlist=gamelibrary_list, object_id=gameid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_GAME_ID)
        Userlistitem.objects.create(
            userlist=gamelibrary_list, 
            content_type=content_type,
            object_id=gameid
            )
    
    return redirect("game_detail", game_url=game.url)


# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourite_games(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_GAME_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlistgame = Userlistitem.objects.get(object_id=gameid, userlist=favourites_list)
    userlistgame.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_GAME_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=gameid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("game_detail", game_url=game.url)


# Smazat ze seznamu: Chci hrát
@login_required
def remove_from_playlist_games(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    playlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYLIST_ID)
    playlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=playlist_type)
    userlistgame = Userlistitem.objects.get(object_id=gameid, userlist=playlist_list)
    userlistgame.delete()
    
    return redirect("game_detail", game_url=game.url)


# Smazat ze seznamu: Odehráno
@login_required
def remove_from_played(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    played_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_PLAYED_GAMES_ID)
    played_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=played_type)
    userlistgame = Userlistitem.objects.get(object_id=gameid, userlist=played_list)
    userlistgame.delete()
    
    return redirect("game_detail", game_url=game.url)


# Smazat ze seznamu: Gamotéka
@login_required
def remove_from_game_library(request, gameid):
    game = get_object_or_404(Game, gameid=gameid)
    gamelibrary_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_GAME_LIBRARY_ID)
    gamelibrary_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=gamelibrary_type)
    userlistgame = Userlistitem.objects.get(object_id=gameid, userlist=gamelibrary_list)
    userlistgame.delete()
    
    return redirect("game_detail", game_url=game.url)
