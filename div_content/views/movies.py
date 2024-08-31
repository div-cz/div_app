# VIEWS.MOVIES.PY

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, Game, Metalocation, Metagenre,
    Movie, Moviecomments, Moviecrew, Moviegenre, Movierating, User, Userprofile, Moviekeywords,
    Userlisttype, Userlist, Userlistmovie
)
from star_ratings.models import Rating, UserRating
# for index
from django.db.models import Avg, Count
import math
from django.contrib import messages


#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')
def redirect_view(request):
    # Zde můžete přidat logiku pro určení, kam přesměrovat
    return redirect('https://div.cz')




def movie_detail(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)
    genres = movie.moviegenre_set.all()[:3]
    countries = movie.moviecountries_set.all()

    user = request.user
    user_rating = None
    comment_form = None  # Default value
    


    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=1)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistmovie.objects.filter(movie__movieid=movie.movieid, userlist=favourites_list).exists()
        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    if user.is_authenticated:
        try:
            watchlist_type = Userlisttype.objects.get(userlisttypeid=2)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlistmovie.objects.filter(movie__movieid=movie.movieid, userlist=watchlist_list).exists()
        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    if user.is_authenticated:
        try:
            watched_type = Userlisttype.objects.get(userlisttypeid=3)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlistmovie.objects.filter(movie__movieid=movie.movieid, userlist=watched_list).exists()
        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False
    
    if user.is_authenticated:
        try:
            movie_library_type = Userlisttype.objects.get(userlisttypeid=11)
            movie_library_list = Userlist.objects.get(user=user, listtype=movie_library_type)
            is_in_movie_library = Userlistmovie.objects.filter(movie__movieid=movie.movieid, userlist=movie_library_list).exists()
        except Exception as e:
            is_in_movie_library = False
    else:
        is_in_movie_library = False


    # Získání hodnocení pro daný film
    movie_content_type = ContentType.objects.get_for_model(Movie)
    ratings = UserRating.objects.filter(rating__content_type=movie_content_type, rating__object_id=movie.movieid)

    if user.is_authenticated:
        user_rating = Movierating.objects.filter(user=user, movieid=movie).first()
        
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data['comment']
                Moviecomments.objects.create(comment=comment, movieid=movie, user=request.user)
                return redirect('movie_detail', movie_url=movie_url)
            else:
                print(comment_form.errors)
        else:
            comment_form = CommentForm(request=request)  # Create an empty CommentForm regardless of the request type.


    # Výpočet průměrného hodnocení
    average_rating_result = ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result.get('average')

    if average_rating is not None:
        average_rating = math.ceil(average_rating)
    else:
        average_rating = 0  # nebo jakoukoliv defaultní hodnotu, kterou chcete nastavit

    comments = Moviecomments.objects.filter(movieid=movie).order_by('-commentid')
    

    actors_and_characters = Moviecrew.objects.filter(movieid=movie.movieid, roleid='378').select_related('peopleid', 'characterid')
    
    actors_and_characters_5 = actors_and_characters[:5]
    
    directors = Moviecrew.objects.filter(movieid=movie.movieid, roleid='383').select_related('peopleid')
    
    writers = Moviecrew.objects.filter(movieid=movie.movieid, roleid='12').select_related('peopleid')
    
    all_crew = Moviecrew.objects.filter(movieid=movie.movieid).select_related('peopleid')

# xsilence8x keywords pro meta tags
    keywords = Moviekeywords.objects.filter(movieid=movie)
    keywordsEN = [keyword.keywordid.keyword for keyword in keywords if keyword.keywordid.keyword]
    keywordsCZ = [keyword.keywordid.keywordcz for keyword in keywords if keyword.keywordid.keywordcz]

# xsilence8x přidán context keywordsCZ, EN 
    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'genres': genres,
        'countries': countries,
        'actors_and_characters': actors_and_characters,
        'actors_and_characters_5': actors_and_characters_5,
        'directors': directors,
        'writers': writers,
        'user_rating': user_rating,
        'comments': comments,
        'comment_form': comment_form,
        'ratings': ratings, 
        'average_rating': average_rating,
        'all_crew': all_crew,
        'keywordsEN': keywordsEN,
        'keywordsCZ': keywordsCZ,
        "is_in_favourites": is_in_favourites,
        "is_in_watchlist": is_in_watchlist,
        "is_in_watched": is_in_watched,
        "is_in_movie_library": is_in_movie_library,
    })




from django.db import connection
from django.shortcuts import render
from div_content.forms.movies import SearchForm

def search(request):
    movies = []
    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            sql_query = """
                SELECT Title, TitleCZ, URL, IMG, Description, ReleaseYear, Popularity, AverageRating
                FROM Movie
                WHERE Adult = 0 AND MATCH(TitleCZ) AGAINST(%s IN NATURAL LANGUAGE MODE)
                ORDER BY Popularity DESC
                LIMIT 50;
            """
            with connection.cursor() as cursor:
                cursor.execute(sql_query, [query])
                rows = cursor.fetchall()
                # Map rows to a dictionary for easier access in template
                columns = [col[0] for col in cursor.description]
                movies = [dict(zip(columns, row)) for row in rows]
    else:
        form = SearchForm()

    return render(request, 'movies/movies_search.html', {'form': form, 'movies': movies})


class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'



#def rate_movie(request, movie_id):
        # viz users.py


# Přidat do seznamu: Oblíbený film
@login_required
def add_to_favourites(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=1)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    # favourites_list = Userlist.objects.get(user=request.user, listtype__userlisttypeid=1)

    if Userlistmovie.objects.filter(userlist=favourites_list, movie=movie).exists():
        messages.info(request, f"{movie.title} už máš v Oblíbených.")
        print("already in favourites")
    else:
        Userlistmovie.objects.create(userlist=favourites_list, movie=movie)
        messages.success(request, f"{movie.title} byl přidán do Oblíbených")
        print("new list created")
    
    return redirect("movie_detail", movie_url=movie.url)

# Přidat do seznamu: Chci vidět
@login_required
def add_to_watchlist(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=2)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    # favourites_list = Userlist.objects.get(user=request.user, listtype__userlisttypeid=1)

    if Userlistmovie.objects.filter(userlist=watchlist_list, movie=movie).exists():
        messages.info(request, f"{movie.title} už máš v Oblíbených.")
        print("already in favourites")
    else:
        Userlistmovie.objects.create(userlist=watchlist_list, movie=movie)
        messages.success(request, f"{movie.title} byl přidán do Oblíbených")
        print("new list created")
    
    return redirect("movie_detail", movie_url=movie.url)    

# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    watched_type = Userlisttype.objects.get(userlisttypeid=3)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    # favourites_list = Userlist.objects.get(user=request.user, listtype__userlisttypeid=1)

    if Userlistmovie.objects.filter(userlist=watched_list, movie=movie).exists():
        messages.info(request, f"{movie.title} už máš v Oblíbených.")
    else:
        Userlistmovie.objects.create(userlist=watched_list, movie=movie)
        messages.success(request, f"{movie.title} byl přidán do Oblíbených")
    
    return redirect("movie_detail", movie_url=movie.url)


# Přidat do seznamu: Filmotéka
@login_required
def add_to_movie_library(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    movie_library_type = Userlisttype.objects.get(userlisttypeid=11)
    movie_library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=movie_library_type)
    # favourites_list = Userlist.objects.get(user=request.user, listtype__userlisttypeid=1)

    if Userlistmovie.objects.filter(userlist=movie_library_list, movie=movie).exists():
        messages.info(request, f"{movie.title} už máš v Oblíbených.")
        print("already in favourites")
    else:
        Userlistmovie.objects.create(userlist=movie_library_list, movie=movie)
        messages.success(request, f"{movie.title} byl přidán do Oblíbených")
        print("new list created")
    
    return redirect("movie_detail", movie_url=movie.url)

# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourites(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=1)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)
    userlistmovie = Userlistmovie.objects.get(movie=movie, userlist=favourites_list)
    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)

# Smazat ze seznamu: Chci vidět
@login_required
def remove_from_watchlist(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    watchlist_type = Userlisttype.objects.get(userlisttypeid=2)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlistmovie = Userlistmovie.objects.get(movie=movie, userlist=watchlist_list)
    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    watched_type = Userlisttype.objects.get(userlisttypeid=3)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlistmovie = Userlistmovie.objects.get(movie=movie, userlist=watched_list)
    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# Smazat ze seznamu: Filmotéka
@login_required
def remove_from_movie_library(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)
    movie_library_type = Userlisttype.objects.get(userlisttypeid=11)
    movie_library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=movie_library_type)
    userlistmovie = Userlistmovie.objects.get(movie=movie, userlist=movie_library_list)
    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)