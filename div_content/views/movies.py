# VIEWS.MOVIES.PY

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, Game, Location, Metagenre,
    Movie, Moviecomments, Moviecrew, Moviegenre, Movierating, User, Userlist,
    Userlistmovie, Userprofile
)
from star_ratings.models import Rating, UserRating
# for index
from django.db.models import Count


#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')

def index(request):
        movies_carousel = Movie.objects.filter(releaseyear=2022).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:4]
        movies_list_6 = Movie.objects.filter(special=1).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:6]
        movies = Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:40]
        today = date.today()
        current_month = today.month
        current_day = today.day
        creators_list_8 = Creator.objects.filter(birthdate__month=current_month, birthdate__day=current_day).order_by('-popularity')[:8]
        users_list_4 = User.objects.annotate(
            comment_count=Count('moviecomments'),
            rating_count=Count('userrating'),
            comment_rating_sum=Count('moviecomments')+Count('userrating')
        ).order_by('-comment_count', '-rating_count')[:6]
        
        return render(request, 'index.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_6': movies_list_6, 'creators_list_8': creators_list_8, 'users_list_4': users_list_4})


def movies(request, year=None, genre_url=None, movie_url=None):
    if year:
        movies = Movie.objects.filter(releaseyear=year).order_by('-popularity')
        movies_carousel = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:3]
        movies_list_30 = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_year.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30, 'year': year})
    
    elif genre_url:
        genre = get_object_or_404(Metagenre, url=genre_url)
        movies_for_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid)
        movies_carousel_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid, adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:3]
        
        movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:30]

        return render(request, 'movies/movies_genre.html', {'movies_for_genre': movies_for_genre, 'movies_carousel_genre': movies_carousel_genre, 'movies_list_30_genre': movies_list_30_genre, 'genre': genre})
    
    else:
        movies_carousel = Movie.objects.filter(releaseyear=2023).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:4]
        movies = Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:50]
        movies_list_30 = Movie.objects.filter(adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_list.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30})




def movie_detail(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)
    genres = movie.moviegenre_set.all()[:3]
    countries = movie.moviecountries_set.all()

    user = request.user
    user_rating = None
    comment_form = None  # Default value
    
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

    comments = Moviecomments.objects.filter(movieid=movie).order_by('-commentid')

    actors_and_characters = Moviecrew.objects.filter(movieid=movie.movieid, roleid='378').select_related('peopleid', 'characterid')[:5]
    directors = Moviecrew.objects.filter(movieid=movie.movieid, roleid='383').select_related('peopleid')
    writers = Moviecrew.objects.filter(movieid=movie.movieid, roleid='12').select_related('peopleid')
    all_crew = Moviecrew.objects.filter(movieid=movie.movieid).select_related('peopleid')

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'genres': genres,
        'countries': countries,
        'actors_and_characters': actors_and_characters,
        'directors': directors,
        'writers': writers,
        'user_rating': user_rating,
        'comments': comments,
        'comment_form': comment_form,
        'ratings': ratings, 
        'all_crew': all_crew
    })




def search(request):
    movies = None
    if 'q' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            movies = (Movie.objects.filter(titlecz__icontains=query, adult=0)
                .values('title', 'titlecz', 'url', 'img', 'description', 'releaseyear', 'averagerating')[:50])
    else:
        form = SearchForm()

    return render(request, 'movies/movies_search.html', {'form': form, 'movies': movies})




class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'



#def rate_movie(request, movie_id):
        # viz users.py


