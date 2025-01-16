# VIEWS.MOVIES.PY TEST

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator


from django.db import connection
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.cache import cache_page
from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, MovieCinemaForm, MovieDivRatingForm, SearchForm, TrailerForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, Game, Metalocation, Metagenre,

    Movie, Moviecinema, Moviecomments, Moviecountries, Moviecrew, Moviedistributor, Moviegenre, Movielocation, Moviequotes, Movierating, Movietrailer, Movietrivia, User, Userprofile, Moviekeywords,
    Userlisttype, Userlist, Userlistmovie, FavoriteSum, Userlistitem

)
from star_ratings.models import Rating, UserRating
# for index
from django.db.models import Avg, Count
import math
from django.contrib import messages




# Konstanty
USERLISTTYPE_FAVORITE_MOVIE_ID = 1 # Oblíbený film
USERLISTTYPE_WATCHLIST_ID = 2 # Chci vidět
USERLISTTYPE_WATCHED_ID = 3 # Shlédnuto
USERLISTTYPE_MOVIE_LIBRARY_ID = 11 # Filmotéka

#CONTENT_TYPE_MOVIE_ID = 33
#CONTENT_TYPE použit v books, movies, authors, characters, series, creators
movie_content_type = ContentType.objects.get_for_model(Movie)
CONTENT_TYPE_MOVIE_ID = movie_content_type.id

#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')
def redirect_view(request):
    # Zde můžete přidat logiku pro určení, kam přesměrovat
    return redirect('https://div.cz')




def movie_detail(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)
    genres = movie.moviegenre_set.all()[:3]
    countries = movie.moviecountries_set.all()

    movie_trailer = Movietrailer.objects.filter(movieid=movie.movieid).first()


    user = request.user
    user_rating = None
    comment_form = None  # Default value
    


    if user.is_authenticated:
        try:

            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_MOVIE_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_in_favourites = Userlistitem.objects.filter(object_id=movie.movieid, userlist=favourites_list).exists()

        except Exception as e:
            is_in_favourites = False
    else:
        is_in_favourites = False

    if user.is_authenticated:
        try:

            watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHLIST_ID)
            watchlist_list = Userlist.objects.get(user=user, listtype=watchlist_type)
            is_in_watchlist = Userlistitem.objects.filter(object_id=movie.movieid, userlist=watchlist_list).exists()

        except Exception as e:
            is_in_watchlist = False
    else:
        is_in_watchlist = False

    if user.is_authenticated:
        try:

            watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_ID)
            watched_list = Userlist.objects.get(user=user, listtype=watched_type)
            is_in_watched = Userlistitem.objects.filter(object_id=movie.movieid, userlist=watched_list).exists()

        except Exception as e:
            is_in_watched = False
    else:
        is_in_watched = False
    
    if user.is_authenticated:
        try:

            movie_library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_MOVIE_LIBRARY_ID)
            movie_library_list = Userlist.objects.get(user=user, listtype=movie_library_type)
            is_in_movie_library = Userlistitem.objects.filter(object_id=movie.movieid, userlist=movie_library_list).exists()

        except Exception as e:
            is_in_movie_library = False
    else:
        is_in_movie_library = False


    # Získání hodnocení pro daný film
    movie_content_type = ContentType.objects.get_for_model(Movie)
    #ratings = UserRating.objects.filter(rating__content_type=movie_content_type, rating__object_id=movie.movieid)
    # HODNOCENÍ UŽIVATELE
    base_ratings = UserRating.objects.filter(
        rating__content_type=movie_content_type, 
        rating__object_id=movie.movieid
    )
    
    # Použijeme tento QuerySet pro výpočet průměru
    average_rating_result = base_ratings.aggregate(average=Avg('score'))
    average_rating = average_rating_result.get('average')
    
    if average_rating is not None:
        average_rating = math.ceil(average_rating)
    else:
        average_rating = 0
    
    # Teď teprve seřadíme s uživatelem na začátku
    if user.is_authenticated:
        ratings = list(base_ratings.order_by('-created'))
        user_rating_index = next((i for i, rating in enumerate(ratings) if rating.user == user), None)
        if user_rating_index is not None:
            user_rating = ratings.pop(user_rating_index)
            ratings.insert(0, user_rating)
    else:
        ratings = base_ratings.order_by('-created')



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
    #average_rating_result = ratings.aggregate(average=Avg('score'))
    #average_rating = average_rating_result.get('average')
    #if average_rating is not None:
    #    average_rating = math.ceil(average_rating)
    #else:
    #    average_rating = 0  # nebo jakoukoliv defaultní hodnotu, kterou chcete nastavit

    comments = Moviecomments.objects.filter(movieid=movie).order_by('-commentid')
    

    actors_and_characters = Moviecrew.objects.filter(movieid=movie.movieid, roleid='378').select_related('peopleid', 'characterid')
    
    actors_and_characters_5 = actors_and_characters[:5]
    
    directors = Moviecrew.objects.filter(movieid=movie.movieid, roleid='383').select_related('peopleid')
    
    writers = Moviecrew.objects.filter(movieid=movie.movieid, roleid='12').select_related('peopleid')
    
    all_crew = Moviecrew.objects.filter(movieid=movie.movieid).select_related('peopleid')
    
    
    # # Fetch locations associated with the book
    # locations = Movielocation.objects.filter(movielocationid=movie)

    # # Initialize the locations form
    # if user.is_authenticated:
    #     if request.method == 'POST' and 'quote' in request.POST:
    #         location_form = Movielocationform(request.POST, movielocationid=movie.movieid)
    #         if location_form.is_valid():
    #             new_quote = location_form.save(commit=False)
    #             new_quote.bookid = movie
    #             new_quote.user = request.user
    #             new_quote.authorid = movie.authorid 
    #             new_quote.save()
    #             return redirect('movie_detail', movie_url=movie_url)
    #     else:
    #         location_form = Movielocationform(movielocationid=movie.movieid)
    # else:
    #     location_form = None
        
        
# xsilence8x keywords pro meta tags
    keywords = Moviekeywords.objects.filter(movieid=movie)
    keywordsEN = [keyword.keywordid.keyword for keyword in keywords if keyword.keywordid.keyword]
    keywordsCZ = [keyword.keywordid.keywordcz for keyword in keywords if keyword.keywordid.keywordcz]

# xsilence8x přidán context keywordsCZ, EN 

# Martin trailer
    if request.method == 'POST' and 'youtubeurl' in request.POST:
        trailer_form = TrailerForm(request.POST)
        if trailer_form.is_valid():
            trailer = trailer_form.save(commit=False)
            trailer.movieid = movie
            trailer.save()
            return redirect('movie_detail', movie_url=movie.url)
    else:
        trailer_form = TrailerForm()

    universum = movie.universumid if movie.universumid else None
    same_universe_movies = Movie.objects.filter(universumid=movie.universumid).exclude(movieid=movie.movieid).filter(universumid__gt=1)[:20]


    # Formulář pro úpravu DIV Ratingu
    div_rating_form = None
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_divrating' in request.POST:
            div_rating_form = MovieDivRatingForm(request.POST, instance=movie)
            if div_rating_form.is_valid():
                div_rating_form.save()
                return redirect('movie_detail', movie_url=movie_url)
        else:
            div_rating_form = MovieDivRatingForm(instance=movie)


# xsilence8x keywords pro meta tags
    keywords = Moviekeywords.objects.filter(movieid=movie)
    keywordsEN = [keyword.keywordid.keyword for keyword in keywords if keyword.keywordid.keyword]
    keywordsCZ = [keyword.keywordid.keywordcz for keyword in keywords if keyword.keywordid.keywordcz]

    distributors = Moviedistributor.objects.all()

    # Přidávání nové hlášky
    if request.method == 'POST' and 'quote_text' in request.POST:
        quote_text = request.POST.get('quote_text').strip()
        if quote_text:
            Moviequotes.objects.create(
                quote=quote_text,
                movie=movie,
                divrating=0,  # Defaultní hodnocení
                user=request.user if request.user.is_authenticated else None
                #UserID=request.user  
            )
            return redirect('movie_detail', movie_url=movie_url)

    # Přidávání do kina
    if request.method == 'POST' and "add_distributor" in request.POST:
            distributor_id = request.POST.get("distributor_id")
            release_date = request.POST.get("release_date")
            try:
                distributor = Moviedistributor.objects.get(distributorid=distributor_id)
                Moviecinema.objects.create(
                    movieid=movie,
                    distributorid=distributor,
                    releasedate=release_date
                )
                messages.success(request, "Distributor byl úspěšně přidán.")
                return redirect("movie_detail", movie_url=movie_url)
            except Moviedistributor.DoesNotExist:
                messages.error(request, "Distributor neexistuje.")

    # Přidávání nové zajímavosti
    if request.method == 'POST' and 'trivia_text' in request.POST:
        trivia_text = request.POST.get('trivia_text').strip()
        if trivia_text:
            Movietrivia.objects.create(
                trivia=trivia_text,
                movieid=movie,
                divrating=0,  # Výchozí hodnocení
                userid=request.user if request.user.is_authenticated else None
            )
            return redirect('movie_detail', movie_url=movie_url)

    quotes = Moviequotes.objects.filter(movie=movie).order_by('-divrating')  
    trivia = Movietrivia.objects.filter(movieid=movie).order_by('-divrating')  

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
        'movie_trailer': movie_trailer,
        'distributors': distributors,
        'trailer_form': trailer_form, 
        'same_universe_movies': same_universe_movies,
        'universum': universum,
        'div_rating_form': div_rating_form,
        'quotes': quotes,
        'trivia': trivia,
    })





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



@cache_page(60 * 60 * 30)
def movies_alphabetical(request, letter='A'):
    letter = letter.upper()

    # Filtrování filmů podle počátečního písmene nebo čísel
    if letter == '0-9':
        movies = Movie.objects.filter(titlecz__regex=r'^[0-9]', adult=0).order_by('titlecz')
    else:
        movies = Movie.objects.filter(titlecz__istartswith=letter, adult=0).order_by('titlecz')

    # Anotace pro výpočet průměrného hodnocení z UserRating (stejně jako ve funkci search)
    movies_with_ratings = movies.annotate(AverageRating=Avg('movierating__rating'))

    # Nastavení stránkování - zobrazíme 50 filmů na jednu stránku
    paginator = Paginator(movies_with_ratings, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'movies/movies_alphabetical.html', {
        'page_obj': page_obj,  # Předáme objekt paginatoru do šablony
        'letter': letter
    })




#def rate_movie(request, movie_id):
        # viz users.py


# Přidat do seznamu: Oblíbený film
@login_required
def add_to_favourites(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_MOVIE_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=movieid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_MOVIE_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type = content_type,
            object_id=movieid
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=movieid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()

    
    return redirect("movie_detail", movie_url=movie.url)

# Přidat do seznamu: Chci vidět
@login_required
def add_to_watchlist(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHLIST_ID)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)

    if Userlistitem.objects.filter(userlist=watchlist_list, object_id=movieid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_MOVIE_ID)
        Userlistitem.objects.create(
            userlist=watchlist_list, 
            content_type=content_type,
            object_id=movieid
            )

    
    return redirect("movie_detail", movie_url=movie.url)    

# Přidat do seznamu: Shlédnuto
@login_required
def add_to_watched(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_ID)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)

    if Userlistitem.objects.filter(userlist=watched_list, object_id=movieid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_MOVIE_ID)
        Userlistitem.objects.create(
            userlist=watched_list, 
            content_type=content_type,
            object_id=movieid
            )

    
    return redirect("movie_detail", movie_url=movie.url)


# Přidat do seznamu: Filmotéka
@login_required
def add_to_movie_library(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    movie_library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_MOVIE_LIBRARY_ID)
    movie_library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=movie_library_type)
    # favourites_list = Userlist.objects.get(user=request.user, listtype__userlisttypeid=1)

    if Userlistitem.objects.filter(userlist=movie_library_list, object_id=movieid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_MOVIE_ID)
        Userlistitem.objects.create(
            userlist=movie_library_list, 
            content_type=content_type,
            object_id=movieid
            )

    
    return redirect("movie_detail", movie_url=movie.url)

# Smazat ze seznamu: Oblíbené
@login_required
def remove_from_favourites(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_MOVIE_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=favourites_list)
    userlistmovie.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_MOVIE_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=movieid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()

    
    return redirect("movie_detail", movie_url=movie.url)

# Smazat ze seznamu: Chci vidět
@login_required
def remove_from_watchlist(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHLIST_ID)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=watchlist_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# Smazat ze seznamu: Shlédnuto
@login_required
def remove_from_watched(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_ID)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=watched_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# Smazat ze seznamu: Filmotéka
@login_required
def remove_from_movie_library(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    movie_library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_MOVIE_LIBRARY_ID)
    movie_library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=movie_library_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=movie_library_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)