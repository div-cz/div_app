from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Article, Book, Creator, Game, Metagenre, Movie, Moviegenre, Location
from datetime import date, datetime

#from django.urls import reverse_lazy
#from .forms import CustomUserCreatonForm, CustomUserChangeForm
#from django.contrib.auth.decorators import login_required


def index(request):
        movies_carousel = Movie.objects.filter(releaseyear=2022).order_by('-popularity')[:4]
        movies_list_6 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
        filmy = Movie.objects.all().order_by('-popularity')[:40]
        today = date.today()
        today = datetime.today()
        current_month = today.month
        current_day = today.day
        creators_list_8 = Creator.objects.filter(birthdate__month=current_month, birthdate__day=current_day).order_by('-popularity')[:8]
        return render(request, 'index.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_6': movies_list_6, 'creators_list_8': creators_list_8})

def register_request(request):
    if request.method == "POST":
        # data from forms
        return redirect('user_access/login.html')
    else:
        # Zobrazíte registrační formulář
        return render(request, 'user_access/register.html')


def login_request(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Přesměrování na domovskou stránku po úspěšném přihlášení
            return redirect('/')
        else:
            # Zobrazte chybovou zprávu o neúspěšném přihlášení
            return render(request, 'user_access/login.html', {'error': 'Neplatné uživatelské jméno nebo heslo'})
    else:
        # Zobrazíte přihlašovací formulář
        return render(request, 'user_access/login.html')



def movies(request, year=None, genre_url=None, movie_url=None):
    if year:
        movies = Movie.objects.filter(releaseyear=year).order_by('-popularity')
        movies_carousel = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity')[:3]
        movies_list_30 = Movie.objects.filter(releaseyear=year,adult=0).order_by('-popularity')[:30]
        return render(request, 'movies/movies_year.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30, 'year': year})
    elif genre_url:
        genre = get_object_or_404(Metagenre, url=genre_url)
        movie_genres = Moviegenre.objects.filter(genreid=genre)
        movies = [mg.movieid for mg in movie_genres]
        return render(request, 'movies/movies_genre.html', {'movies': movies})
    else:
        movies_carousel = Movie.objects.filter(releaseyear=2023).order_by('-popularity')[:4]
        movies = Movie.objects.all().order_by('-popularity')[:50]
        movies_list_30 = Movie.objects.filter(adult=0).order_by('-popularity')[:30]
        return render(request, 'movies/movies_list.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_30': movies_list_30})


def movie_detail(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)
    genres = movie.moviegenre_set.all() # get all genres
    countries = movie.moviecountries_set.all() # get all states
    return render(request, 'movies/movie_detail.html', {'movie': movie, 'genres': genres, 'countries': countries})


# Pro články
#def clanky(request):
#    clanky = Article.objects.all()
#    return render(request, 'clanky/clanky_list.html', {'clanky': clanky})

# Pro článek
def article_detail(request, article_url):
    article = get_object_or_404(Article, url=article_url)
    movie_list_6 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
    article_list = Article.objects.filter(typ='Článek').order_by('-id')[:6]
    return render(request, 'articles/article_detail.html', {'article': article, 'movie_list_6': movie_list_6, 'article_list': article_list})


# Pro hry
def games(request):
    games = Game.objects.all()
    return render(request, 'games/games_list.html', {'games': games})

def game_detail(request, game_url):
    game = get_object_or_404(Game, url=game_url)
    return render(request, 'games/game_detail.html', {'game': game})

# Pro knihy
def books(request):
    books = Book.objects.all()
    return render(request, 'books/books_list.html', {'books': books})

def book_detail(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    return render(request, 'books/book_detail.html', {'book': book})

# Pro lokality
def locations(request):
    locations = Location.objects.all()
    return render(request, 'locations/locations_list.html', {'locations': locations})

def location_detail(request, location_url):
    location = get_object_or_404(Locality, url=location_url)
    return render(request, 'locations/location_detail.html', {'location': location})

# osobnost
def creators_list(request):
    creators = Creator.objects.all().order_by('-popularity')[:50]
    return render(request, 'creators/creators_list.html', {'creators': creators})

def creator_detail(request, creator_url):
    creator = get_object_or_404(Creator, url=creator_url)
    return render(request, 'creators/creator_detail.html', {'creator': creator})
