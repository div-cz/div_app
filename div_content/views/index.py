# VIEWS.INDEX.PY

from datetime import date

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import user_passes_test

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView
from div_content.views.login import custom_login_view

from div_content.forms.admins import TaskForm, TaskCommentForm
from div_content.forms.index import ArticleForm, ArticlenewsForm
from div_content.forms.movies import CommentForm, SearchForm
from div_content.models import (
    AATask, Article, Articlenews, Book, Creator, Creatorbiography, Game, Metacharts,Metagenre, Metaindex, Metalocation,  Metastats, Movie, Moviecinema, Moviedistributor, Moviecomments, Moviecrew, Moviegenre, Movierating, Tvgenre, Tvshow, User, Userprofile
)
from star_ratings.models import Rating, UserRating
# for index
from django.db.models import Avg, Count
from django.db.models.functions import ExtractYear
import math



def wendy_index(request):
    return render(request, 'wendy/index.html')

def wendy_detail(request):
    return render(request, 'wendy/detail_filmu.html')

def wendy_list(request):
    return render(request, 'wendy/vypis_filmu.html')



#Carouse = .values('title', 'titlecz', 'url', 'img', 'description')
#List = .values('title', 'titlecz', 'url', 'img', 'description')
def redirect_view(request):
    # Zde můžete přidat logiku pro určení, kam přesměrovat
    return redirect('https://div.cz')




# TASK MANAGEMENT 
def get_sorted_tasks(user):
    # Získáme všechny hlavní úkoly (bez parentid)
    main_tasks = AATask.objects.filter(
        parentid__isnull=True,
        status__in=['Ke zpracování', 'Probíhá']
    ).order_by('-created')[:10]
    
    # Seřadíme podle assigned
    user_tasks = []
    unassigned_tasks = []
    other_tasks = []
    
    for task in main_tasks:
        if task.assigned == user.username:
            user_tasks.append(task)
        elif task.assigned == 'Nikdo':
            unassigned_tasks.append(task)
        else:
            other_tasks.append(task)
            
    return user_tasks + unassigned_tasks + other_tasks




def index(request): # hlavní strana
    #ARTICLE NEWS
    if request.user.is_superuser or request.user.is_staff:
        article_form = ArticleForm(request.POST or None)
        articlenews_form = ArticlenewsForm(request.POST or None)
        
        if request.method == 'POST':
            if 'article_submit' in request.POST and article_form.is_valid():
                article = article_form.save(commit=False)
                article.save()
                return redirect('index')

            if 'articlenews_submit' in request.POST and articlenews_form.is_valid():
                articlenews = articlenews_form.save(commit=False)
                articlenews.userid = request.user
                articlenews.save()
                return redirect('index')
    else:
        article_form = None
        articlenews_form = None



#        movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-popularity').values('title', 'url', 'img', 'description')[2:8]
    movies_list_6 = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:6]
        
        #latest_articles = Article.objects.filter(typ='Článek').order_by('-created').values('url', 'title')[:3]

    articles = Article.objects.exclude(typ='Site').order_by('-created').values('url', 'title', 'img', 'img400x250', 'perex')[:2]
    articlenews = Articlenews.objects.all().order_by('-created')[:5]


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
        
    movies_comments_5 = Moviecomments.objects.select_related('movieid', 'user').order_by(
            '-commentid').values('comment', 'movieid__titlecz', 'movieid__url', 'movieid', 'user', 'user__username')[:5]


    # Filmy v kinech
    movies_in_cinema = Moviecinema.objects.select_related('movieid', 'distributorid').order_by('-releasedate').values(
        'movieid__title', 'movieid__titlecz', 'movieid__img', 'releasedate', 'distributorid__name', 'movieid__url')[:10]
        

        # Statistiky
    stats_book = Metastats.objects.filter(tablemodel='Book').first()
    stats_movie = Metastats.objects.filter(tablemodel='Movie').first()
    stats_writters = Metastats.objects.filter(tablemodel='BookAuthor').first()
        #stats_games = Metastats.objects.filter(tablemodel='Game').first()
        # Žebříčky
    charts = Metacharts.objects.filter(table_model='Movie', store='BoxOfficeMojo').order_by('ranking')


    if request.user.is_authenticated:
        tasks = get_sorted_tasks(request.user)
    else:
        tasks = []

    return render(request, 'index.html', {
            'movies': movies, 
            'movies_list_6': movies_list_6, 
            'articles': articles, 
            'articlenews': articlenews,
            'article_form': article_form,
            'articlenews_form': articlenews_form,
            'creators_list_8': creators_list_8, 
            'users_list_4': users_list_4, 
            'movies_comments_5': movies_comments_5,
            'movies_in_cinema': movies_in_cinema, 
            'stats_book': stats_book,
            'stats_movie': stats_movie,
            'stats_writters': stats_writters,
            'charts': charts,
            'tasks': tasks
            })  


def series_genre(request, genre_url):
    genre = get_object_or_404(Metagenre, url=genre_url)
    tvshows = Tvshow.objects.filter(tvgenre__genreid=genre.genreid).order_by('-divrating')[:15]
    
    stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
    return render(request, 'series/series_genre.html', {
        'genre': genre,
        'tvshows': tvshows, 
        'stats_tvshows': stats_tvshows
    })

def series_year(request, year):
    tvshows = Tvshow.objects.annotate(premiere_year=ExtractYear('premieredate')).filter(premiere_year=year).order_by('-divrating')[:15]

    stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
    return render(request, 'series/series_year.html', {
        'year': year,
        'tvshows': tvshows, 
        'stats_tvshows': stats_tvshows
    })




def movies(request, year=None, genre_url=None, movie_url=None):
    if year:
        movies = Movie.objects.filter(releaseyear=year).order_by('-divrating')
        movies_carousel = Movie.objects.filter(releaseyear=year,adult=0).order_by('-divrating').values('titlecz', 'url', 'img', 'description')[:3]
        movies_list_30 = Movie.objects.filter(releaseyear=year,adult=0).order_by('-divrating').values('title', 'titlecz', 'url', 'img', 'description')[:30]
        return render(request, 'movies/movies_year.html', {
            'movies': movies, 
            'movies_carousel': movies_carousel, 
            'movies_list_30': movies_list_30, 
            'year': year
            })

    elif genre_url:
        genre = get_object_or_404(Metagenre, url=genre_url)
        movies_for_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid)
        movies_carousel_genre = Metaindex.objects.filter(section='Movie').order_by('-indexid').values('title', 'url', 'img', 'description')[:3]

        #movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).values('title', 'titlecz', 'url', 'img', 'description')[:30]
        movies_list_30_genre = Movie.objects.filter(moviegenre__genreid=genre.genreid).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description', 'popularity')[:30]

        return render(request, 'movies/movies_genre.html', {
            'movies_for_genre': movies_for_genre, 
            'movies_carousel_genre': movies_carousel_genre, 
            'movies_list_30_genre': movies_list_30_genre, 
            'genre': genre
            })

    else:
        movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-popularity').values('title', 'url', 'img', 'description')[:4]
        movies = Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:50]
        movies_list_15 = Movie.objects.filter(adult=0,releaseyear__gt=2018).order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:15]
        
        stats_movie = Metastats.objects.filter(tablemodel='Movie').first()
        stats_creator = Metastats.objects.filter(tablemodel="Creator").first()
        stats_tvshows = Metastats.objects.filter(tablemodel="TVShow").first()
        stats_moviecomments = Metastats.objects.filter(tablemodel="MovieComments").first()


        # Filmy v kinech
        movies_in_cinema = Moviecinema.objects.select_related('movieid', 'distributorid').order_by('-releasedate').values(
        'movieid__title', 'movieid__titlecz', 'movieid__img', 'releasedate', 'movieid__url')[:10]

        # Filmy v kinech (Carousel Cinema)
        carousel_cinema = Moviecinema.objects.filter(movieid__img__isnull=False).exclude(movieid__img='noimg.png').select_related('movieid').order_by('-releasedate').values(
            'movieid__title', 'movieid__titlecz', 'movieid__img', 'movieid__url', 'releasedate'
        )[:10]


        return render(request, 'movies/movies_list.html', {
            'movies': movies, 
            'movies_carousel': movies_carousel, 
            'movies_list_15': movies_list_15,
            'stats_movie': stats_movie,
            'stats_tvshows': stats_tvshows,
            'stats_moviecomments': stats_moviecomments,
            'movies_in_cinema': movies_in_cinema,
            'carousel_cinema': carousel_cinema,
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


def our_team(request):
    return render(request, "nas_tym.html")