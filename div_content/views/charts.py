# VIEWS.CHARTS.PY


from django.contrib.contenttypes.models import ContentType
from django.core.cache import cache
from django.db import models

from django.db.models import Avg, Count, Q, F, OuterRef, Subquery, FloatField
from django.shortcuts import get_object_or_404, render

from div_content.models import Book, Bookauthor, Bookaward, Bookpublisher, Creator, Favorite, Game, Gameaward, Gamepublisher, Metagenre, Movie, Moviecrew, Moviegenre, Tvcountries, Tvcrew, Tvshow, Metaaward, Metacountry, Movieaward, Moviecountries

from star_ratings.models import Rating, UserRating

from datetime import datetime



def award_detail(request, award_name, year):
    # Fetch the main award
    award = get_object_or_404(Metaaward, Awardname=award_name, Year=year)

    # Fetch associated movie, book, and game awards
    movie_awards = Movieaward.objects.filter(metaawardid=award)
    serie_awards = Movieaward.objects.filter(metaawardid=award)
    book_awards = Bookaward.objects.filter(metaawardid=award)
    game_awards = Gameaward.objects.filter(metaawardid=award)

    return render(request, 'charts/award_detail.html', {
        'award': award,
        'movie_awards': movie_awards,
        'serie_awards': serie_awards,
        'book_awards': book_awards,
        'game_awards': game_awards
    })




def awards_index(request):
    # Main index page for awards
    return render(request, "charts/awards_index.html")

def awards_movies(request):
    # Fetch all movie awards and winners
    movie_awards = Movieaward.objects.select_related('metaAwardid', 'movieid').all()

    return render(request, "charts/awards_movies.html", {
        'movie_awards': movie_awards
    })

def awards_series(request):
    # Fetch all movie awards and winners
    serie_awards = Movieaward.objects.select_related('metaAwardid', 'serieid').all()

    return render(request, "charts/awards_series.html", {
        'serie_awards': serie_awards
    })

def awards_books(request):
    # Fetch all book awards and winners
    book_awards = Bookaward.objects.select_related('metaAwardid', 'bookid').all()

    return render(request, "charts/awards_books.html", {
        'book_awards': book_awards
    })

def awards_games(request):
    # Fetch all game awards and winners
    game_awards = Gameaward.objects.select_related('metaawardid', 'gameid').all()

    return render(request, "charts/awards_games.html", {
        'game_awards': game_awards
    })




def charts_index(request):
    return render(request, "charts/charts.html")



def charts_books(request):
    # Nejlepší knihy (podle ID)
    best_books_ids = [1, 2, 3, 4, 5, 7, 8, 11]  # Nahraďte skutečnými ID nejlepších knih
    popular_authors_ids = [10501,25224,34328,47783,52431,53235,55412,58512,62011,63760]  # ID nejoblíbenějších spisovatelů
    popular_authoresses_ids = [24465,26829,31044,31086,61009,69005,74162,74167,74205,74214]  # ID nejoblíbenějších spisovatelek

    best_books = Book.objects.filter(bookid__in=best_books_ids).select_related('authorid', 'countryid')
    popular_authors = Bookauthor.objects.filter(authorid__in=popular_authors_ids)
    popular_authoresses = Bookauthor.objects.filter(authorid__in=popular_authoresses_ids)


    # Nejčtenější knihy ze zemí (hardcoded země)
    top_countries = [
        {"name": "USA", "count": 500},
        {"name": "Japonsko", "count": 400},
        {"name": "Německo", "count": 350},
        {"name": "Velká Británie", "count": 300},
        {"name": "Česko", "count": 280},
        {"name": "Španělsko", "count": 250},
    ]

    # Nakladatelství 
    favorite_publishers_ids = [1, 2, 3, 4, 5]
    best_publishers_ids = [6, 7, 8, 9, 10]

    favorite_publishers = Bookpublisher.objects.filter(publisherid__in=favorite_publishers_ids)
    best_publishers = Bookpublisher.objects.filter(publisherid__in=best_publishers_ids)

    return render(request, "charts/charts_books.html", {
        "best_books": best_books,
        "popular_authors": popular_authors,
        "popular_authoresses": popular_authoresses,
        "top_countries": top_countries,
        'favorite_publishers': favorite_publishers,
        'best_publishers': best_publishers,
    })



def charts_games(request):
    # Top hry podle ID
    game_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    top_games = Game.objects.filter(gameid__in=game_ids)
    # Top země podle ID
    country_ids = [232, 74, 58, 82, 84, 106, 108, 231]
    top_countries = Metacountry.objects.filter(countryid__in=country_ids)
    # Top vydavatelé podle ID
    publisher_ids = [1, 2, 3, 4, 5]  # ID vydavatelů
    top_publishers = Gamepublisher.objects.filter(publisherid__in=publisher_ids)

    return render(request, "charts/charts_games.html", {
        "top_games": top_games,
        "top_countries": top_countries,
        "top_publishers": top_publishers,
    })


def charts_movies(request):

    tvshow_content_type = ContentType.objects.get_for_model(Tvshow)
    # Přidání hodnocení k seriálům
    ratings_subquery = Rating.objects.filter(
        content_type_id=tvshow_content_type.id,
        object_id=OuterRef('tvshowid')
    ).values('average', 'count')[:1]


    movie_ids = [912649, 293660, 872585, 603692, 361743, 10625, 672, 808, 218, 285]
    series_ids = [73586, 2288, 1622, 90228, 1396, 4614, 456, 1911, 4057, 1408]

    top_movies = Movie.objects.filter(movieid__in=movie_ids).values("movieid", "title", "titlecz", "url", "imgposter", "releaseyear")
    top_series = Tvshow.objects.filter(tvshowid__in=series_ids).annotate(
        avg_rating=Subquery(ratings_subquery.values('average')[:1], output_field=FloatField()),
        rating_count=Subquery(ratings_subquery.values('count')[:1])
    )
    directors = Moviecrew.objects.filter(roleid=383, movieid__in=movie_ids).select_related('peopleid')
    countries = Moviecountries.objects.filter(movieid__in=movie_ids).select_related('countryid')
    tvdirectors = Tvcrew.objects.filter(roleid=383, tvshowid__in=series_ids).select_related('peopleid')
    tvcountries = Tvcountries.objects.filter(tvshowid__in=series_ids).select_related('countryid')

    # Získání ContentType pro model Creator
    creator_content_type = ContentType.objects.get_for_model(Creator)  
    director_ids = [956, 525, 488, 510, 5026, 138, 578, 2636, 10965, 40]
    directress_ids = [99803, 1586169, 1705464, 1576220, 1478953, 1371324, 80386]

    popular_directors = Creator.objects.filter(creatorid__in=director_ids)
    popular_directresses = Creator.objects.filter(creatorid__in=directress_ids)


    # Nejoblíbenější herci (muži)
    actor_ids = [3, 31, 64, 976, 6384]
    actress_ids = [4, 974169, 1245, 11701, 1152083]
    popular_actors = Creator.objects.filter(creatorid__in=actor_ids)
    popular_actresses = Creator.objects.filter(creatorid__in=actress_ids)

    top_countries = ()
    top_genres = ()


    genre_ids = {
        "Akční": [98,9659,285,912649,335983,634649,823464,786892,1142518,1196470], # 10
        "Animovaný": [698687,519182,823219,1184918,1022789,1371727,354912,1011985,1329336,567811],# 10
        "Dobrodružný": [1118031,1084736,365177,653346,718821,823219,558449,653346,940551,1147710], # 10
        "Horor": [420634,1034541,1118031,1371727,1125510,957452,814889,762441],
        "Komedie": [1104171,573435,1241982,639720,567811,346698,826510,974262,1210794,502356], # 10
        "Sci-fi": [653346,580489,634649,324857,335983,827931,1196470,726139,1144962,365177],# 10

    }
    genre_movies = {}
    for genre, movie_ids in genre_ids.items():
        genre_movies[genre] = Movie.objects.filter(movieid__in=movie_ids).values(
            "movieid", "title", "titlecz", "url", "imgposter", "releaseyear"
        )


    return render(request, 'charts/charts_movies.html', {
        'top_movies': top_movies,
        'top_series': top_series,
        'directors': directors,
        'countries': countries,
        'tvdirectors': tvdirectors,
        'tvcountries': tvcountries,
        'popular_directors': popular_directors,
        'popular_directresses': popular_directresses,
        'popular_actors': popular_actors,
        'popular_actresses': popular_actresses,
        'genre_movies': genre_movies,
        'top_countries': top_countries,
        'top_genres': top_genres,
    })



def charts_users(request):
    return render(request, "charts/charts_users.html")






