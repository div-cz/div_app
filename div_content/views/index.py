# VIEWS.MOVIES.PY

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, Game, Metalocation, Metagenre, Metaindex, 
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

def index(request): # hlavní strana
        movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-popularity').values('title', 'url', 'img', 'description')[2:8]
        movies_list_6 = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:6]
        
        #latest_articles = Article.objects.filter(typ='Článek').order_by('-created').values('url', 'title')[:3]

        articles = Article.objects.exclude(typ='Site').order_by('-created').values('url', 'title', 'img', 'img400x250', 'perex')[:2]


        movies = Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:40]
        today = date.today()
        current_month = today.month
        current_day = today.day
        creators_list_8 = Creator.objects.filter(birthdate__month=current_month, birthdate__day=current_day).order_by('-popularity')[:8]
        users_list_4 = User.objects.annotate(
            comment_count=Count('moviecomments'),
            rating_count=Count('userrating'),
            comment_rating_sum=Count('moviecomments')+Count('userrating')
        ).order_by('-rating_count')[:9]
        
        movies_comments_9 = Moviecomments.objects.select_related('movieid', 'user').order_by(
            '-commentid').values('comment', 'movieid__titlecz', 'movieid__url', 'movieid', 'user', 'user__username')[:12]
        
        return render(request, 'index.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_6': movies_list_6, 'articles': articles, 'creators_list_8': creators_list_8, 'users_list_4': users_list_4, 'movies_comments_9': movies_comments_9})


def movies(request, year=None, genre_url=None, movie_url=None):
    if year:
        movies = Movie.objects.filter(releaseyear=year).order_by('-popularity')
        movies_carousel = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity').values('titlecz', 'url', 'img', 'description')[:3]
        movies_list_30 = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_year.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30, 'year': year})

    elif genre_url:
        genre = get_object_or_404(Metagenre, url=genre_url)
        movies_for_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid)
        movies_carousel_genre = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:3]

        movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).values('title', 'titlecz', 'url', 'img', 'description')[:30]

        return render(request, 'movies/movies_genre.html', {'movies_for_genre': movies_for_genre, 'movies_carousel_genre': movies_carousel_genre, 'movies_list_30_genre': movies_list_30_genre, 'genre': genre})

    else:
        movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-popularity').values('title', 'url', 'img', 'description')[:4]
        movies = Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:50]
        movies_list_30 = Movie.objects.filter(adult=0).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_list.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30})






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


