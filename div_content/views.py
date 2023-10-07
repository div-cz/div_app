from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from div_config.forms import NewUserForm
from .models import Article, Book, Creator, Game, Metagenre, Movie, Moviegenre, Location
from datetime import date


# from django.urls import reverse_lazy
# from django.views import generic
# from .forms import CustomUserCreatonForm, CustomUserChangeForm
# from django.contrib.auth.decorators import login_required


def index(request):
    carousel_movies = Movie.objects.filter(releaseyear=2022).order_by('-popularity')[:4]
    special_movie_15 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
    filmy = Movie.objects.all().order_by('-popularity')[:40]

    today = date.today()
    top_creators = Creator.objects.all().order_by('-popularity')[:8]

    return render(request, 'index.html',
                  {'filmy': filmy, 'carousel_movies': carousel_movies, 'special_movie_15': special_movie_15,
                   'top_creators': top_creators})


def filmy(request, rok=None, url_zanru=None):
    if rok:
        filmy = Movie.objects.filter(releaseyear=rok).order_by('-popularity')
        carousel_movies = Movie.objects.filter(releaseyear=rok, adult=0).order_by('-popularity')[:3]
        vypis_filmu = Movie.objects.filter(releaseyear=rok, adult=0).order_by('-popularity')[:30]
        return render(request, 'filmy/filmy_rok.html',
                      {'filmy': filmy, 'carousel_movies': carousel_movies, 'vypis_filmu': vypis_filmu, 'rok': rok})
    elif url_zanru:
        zanr = get_object_or_404(Metagenre, url=url_zanru)
        movie_genres = Moviegenre.objects.filter(genreid=zanr)
        filmy = [mg.movieid for mg in movie_genres]
        return render(request, 'filmy/filmy_zanr.html', {'filmy': filmy})
    else:
        #        carousel_movies = Movie.objects.all().order_by('-releaseyear', '-popularity')[:4]
        carousel_movies = Movie.objects.filter(releaseyear=2023).order_by('-popularity')[:4]
        filmy = Movie.objects.all().order_by('-popularity')[:50]
        return render(request, 'filmy/filmy_seznam.html', {'filmy': filmy, 'carousel_movies': carousel_movies})


#       === === ===

def film_detail(request, url_filmu):
    film = get_object_or_404(Movie, url=url_filmu)
    genres = film.moviegenre_set.all()  # get all genres
    staty = film.moviecountries_set.all()  # get all states
    return render(request, 'filmy/film_detail.html', {'film': film, 'genres': genres, 'staty': staty})


# Pro články
# def clanky(request):
#    clanky = Article.objects.all()
#    return render(request, 'clanky/clanky_list.html', {'clanky': clanky})

# Pro článek
def clanek_detail(request, url_clanku):
    clanek = get_object_or_404(Article, url=url_clanku)
    special_movie_15 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
    article_list = Article.objects.filter(typ='Článek').order_by('-id')[:6]
    return render(request, 'clanky/clanek_detail.html',
                  {'clanek': clanek, 'special_movie_15': special_movie_15, 'article_list': article_list})


# Pro hry
def hry(request):
    hry = Game.objects.all()
    return render(request, 'hry/hry_list.html', {'hry': hry})


def hra_detail(request, nazev_hry):
    hra = get_object_or_404(Game, nazev=nazev_hry)
    return render(request, 'hry/hra_detail.html', {'hra': hra})


# Pro knihy
def knihy(request):
    knihy = Book.objects.all()
    return render(request, 'knihy/knihy_list.html', {'knihy': knihy})


def kniha_detail(request, nazev_knihy):
    kniha = get_object_or_404(Kniha, nazev=nazev_knihy)
    return render(request, 'knihy/kniha_detail.html', {'kniha': kniha})


# Pro lokality
def lokality(request):
    lokality = Location.objects.all()
    return render(request, 'lokality/lokality_list.html', {'lokality': lokality})


def lokalita_detail(request, nazev_lokality):
    lokalita = get_object_or_404(Lokalita, nazev=nazev_lokality)
    return render(request, 'lokality/lokalita_detail.html', {'lokalita': lokalita})


# osobnost

def osobnost_list(request):
    osobnosti = Creator.objects.all().order_by('-popularity')[:50]
    return render(request, 'osobnost/osobnost_list.html', {'osobnosti': osobnosti})


def osobnost_detail(request, creator_id):
    osobnost = get_object_or_404(Creator, creatorid=creator_id)
    return render(request, 'osobnost/osobnost_detail.html', {'osobnost': osobnost})


def register_request(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect("main:homepage")
        messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render(request=request,
                  template_name="user_access/register.html",
                  context={"register_form": form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Jste přihlášený jako {username}.")
                return redirect("index")
            else:
                messages.error(request, "Neplatné uživatelské jméno nebo heslo.")
        else:
            messages.error(request, "Neplatné uživatelské jméno nebo heslo.")
    form = AuthenticationForm()
    return render(request=request,
                  template_name="user_access/login.html",
                  context={"login_form": form})
