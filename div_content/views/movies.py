# VIEWS.MOVIES.PY

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, Game, Metalocation, Metagenre,
    Movie, Moviecomments, Moviecrew, Moviegenre, Movierating, User, Userlist,
    Userlistmovie, Userprofile
)
from star_ratings.models import Rating, UserRating
# for index
from django.db.models import Avg, Count
import math


#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')
def redirect_view(request):
    # Zde můžete přidat logiku pro určení, kam přesměrovat
    return redirect('https://www.startovac.cz/projekty/div-cz-databaze')




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


