from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from django.contrib.auth import authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from div_content.models import Article, Book, Creator, Creatorbiography, Game, Location, Metagenre, Movie, Moviecomments, Moviecrew, Moviegenre, Movierating, Userlist, Userlistmovie, Userprofile
from django.views.generic import DetailView
from django.views.decorators.csrf import csrf_exempt
from star_ratings.models import UserRating, Rating
from django.core.paginator import Paginator, Page
from div_content.forms import CommentForm, SearchForm, UserProfileForm
# Registration


# USER
def myuser_detail(request, user_id=None):
    # Pokud user_id není zadáno, použijte přihlášeného uživatele
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)
    user_ratings = UserRating.objects.filter(user_id=user_id)

    # Získání instance profilu uživatele
    user_profile = Userprofile.objects.get(user=profile_user)

    items_per_page = 10
    paginator = Paginator(user_ratings, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    if profile_user == request.user:
        template_name = 'user/my_profile.html'
    else:
        template_name = 'user/other_profile.html'

    return render(request, template_name, {
        'profile_user': profile_user, 
        'user_ratings': user_ratings, 
        'page': page, 
        'user_profile': user_profile
    })



def update_profile(request):
    # Získání instance profilu, pokud existuje. Jinak vrátí None.
    user_profile, created = Userprofile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('myuser_detail')  # Presmerujte na profilovou stránku
    else:
        form = UserProfileForm(instance=user_profile)
    return render(request, 'user/update_profile.html', {'form': form})




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
        return render(request, 'index.html', {'movies': movies, 'movies_carousel': movies_carousel, 'movies_list_6': movies_list_6, 'creators_list_8': creators_list_8})


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
            movies = (Movie.objects.filter(titlecz__icontains=query)
                .values('title', 'titlecz', 'url', 'img', 'description', 'releaseyear')[:50])
    else:
        form = SearchForm()

    return render(request, 'movies/movies_search.html', {'form': form, 'movies': movies})




class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'


@login_required
def rate_movie(request, movie_id):
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        user = request.user
        movie = Movie.objects.get(id=movie_id)
        # Vytvoření nového záznamu MovieRating s uživatelem
        MovieRating.objects.create(Rating=rating, Movie=movie, User=user)
        return redirect('movie_detail', movie_id=movie_id)
    else:
        # Zobrazte formulář pro hodnocení
        return render(request, 'movies/movie_detail.html', {'movie_id': movie_id})

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from .models import Userlist, Userlistmovie, Userlistbook, Userlistgame


@csrf_exempt
def add_to_list(request):
    if request.method == "POST":
        data = json.loads(request.body)
        media_id = data.get('media_id')
        list_type = data.get('list_type')
        media_type = data.get('media_type').lower()  # převede na malá písmena

        # Vytvořte nebo získejte seznam podle typu seznamu
        if list_type == "favorite":
            list_name = "Oblíbené"
        elif list_type == "want-to-see":
            list_name = "Chci vidět"

        user_list, created = Userlist.objects.get_or_create(user=request.user, namelist=list_name)

        if media_type == "movie":
            existing_entry = Userlistmovie.objects.filter(movie_id=media_id, userlist=user_list)
            if existing_entry.exists():
                existing_entry.delete()
                return JsonResponse({"success": True, "action": "removed"})
            else:
                Userlistmovie.objects.create(movie_id=media_id, userlist=user_list)
        elif media_type == "book":
            book_instance = Book.objects.get(bookid=media_id)
            Userlistbook.objects.create(book=book_instance, userlist=user_list)

        elif media_type == "game":
            game_instance = Game.objects.get(gameid=media_id)
            Userlistgame.objects.create(game=game_instance, userlist=user_list)
        else:
            return JsonResponse({"success": False, "error": "Unknown media type"})

        return JsonResponse({"success": True, "action": "added"})
    return JsonResponse({"success": False})






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
    location = get_object_or_404(Location, url=location_url)
    return render(request, 'locations/location_detail.html', {'location': location})

# creators
def creators_list(request):
    creators = Creator.objects.all().order_by('-popularity')[:48]
    movies_carousel = Movie.objects.filter(releaseyear=2023,adult=0).order_by('-popularity')[3:7]

    return render(request, 'creators/creators_list.html', {'creators': creators, 'movies_carousel': movies_carousel})


def creator_detail(request, creator_url):
    creator = get_object_or_404(Creator, url=creator_url)

    current_creator = Creator.objects.get(url=creator_url)
    creatorbiography = Creatorbiography.objects.filter(creator=creator, verificationstatus="Verified").first()
    
    creator_list_10 = Creator.objects.filter(popularity__gt=current_creator.popularity).order_by('-popularity').values('firstname', 'lastname', 'url', 'birthdate')[:10]
    creator_list_10_minus = Creator.objects.filter(popularity__lt=current_creator.popularity).order_by('popularity').values('firstname', 'lastname', 'url', 'birthdate')[:10]

    filmography = Moviecrew.objects.filter(peopleid=creator.creatorid).select_related('movieid', 'roleid')

    return render(request, 'creators/creator_detail.html', 
                {'creator': creator, 
                'creatorbiography': creatorbiography, 
                'creator_list_10': creator_list_10, 
                'creator_list_10_minus': creator_list_10_minus, 
                'filmography': filmography,
})
                



#####
def ratings_profile(request):
    user_ratings = Movierating.objects.filter(user=request.user)
    return render(request, 'user/ratings_profile.html', {'user_ratings': user_ratings})

# Zobrazení oblíbených filmů uživatele
def favorites_profile(request):
    user_lists = Userlistmovie.objects.filter(userlist__namelist="Oblíbené", userlist__user=request.user).select_related('movie')
    return render(request, 'user/favorites_profile.html', {'user_lists': user_lists})

# Zobrazení filmů, které uživatel chce vidět
def iwantsee_profile(request):
    user_lists = Userlistmovie.objects.filter(userlist__namelist="To chci vidět", userlist__user=request.user).select_related('movie')
    return render(request, 'user/iwantsee_profile.html', {'user_lists': user_lists})


# users
@login_required
def rated_media(request):
    # Implementujte logiku pro zobrazení všeho ohodnoceného média
    user_ratings = Movierating.objects.filter(user=request.user)
    return render(request, 'user/rated_media.html', {'user_ratings': user_ratings})

@login_required
def rated_movies(request):
    # Implementujte logiku pro zobrazení ohodnocených filmů
    return render(request, 'user/rated_movies.html')

@login_required
def rated_books(request):
    # Implementujte logiku pro zobrazení ohodnocených knih
    return render(request, 'user/rated_books.html')

@login_required
def rated_games(request):
    # Implementujte logiku pro zobrazení ohodnocených her
    return render(request, 'user/rated_games.html')

@login_required
def favorite_media(request):
    # Implementujte logiku pro zobrazení všech oblíbených médií
    return render(request, 'user/favorite_media.html')

@login_required
def favorite_actors(request):
    # Implementujte logiku pro zobrazení oblíbených herců
    return render(request, 'user/favorite_actors.html')

@login_required
def favorite_books(request):
    # Implementujte logiku pro zobrazení oblíbených knih
    return render(request, 'user/favorite_books.html')

@login_required
def favorite_drinks(request):
    # Implementujte logiku pro zobrazení oblíbených nápojů
    return render(request, 'user/favorite_drinks.html')

@login_required
def favorite_foods(request):
    # Implementujte logiku pro zobrazení oblíbeného jídla
    return render(request, 'user/favorite_foods.html')

@login_required
def favorite_games(request):
    # Implementujte logiku pro zobrazení oblíbených her
    return render(request, 'user/favorite_games.html')

@login_required
def favorite_items(request):
    # Implementujte logiku pro zobrazení oblíbených předmětů
    return render(request, 'user/favorite_items.html')

@login_required
def favorite_locations(request):
    # Implementujte logiku pro zobrazení oblíbených lokalit
    return render(request, 'user/favorite_locations.html')

@login_required
def favorite_movies(request):
 # Získání seznamu "Oblíbené" pro aktuálně přihlášeného uživatele
    favorites_list = Userlist.objects.filter(user=request.user, namelist="Oblíbené").first()
    if favorites_list:
        favorite_movies = Userlistmovie.objects.filter(userlist=favorites_list)
    else:
        favorite_movies = None

    return render(request, 'user/user_lists_favorites.html', {'favorite_movies': favorite_movies})


@login_required
def user_lists(request):
    # Implementujte logiku pro zobrazení oblíbených předmětů
    return render(request, 'user/user_lists.html')


@login_required
def wantsee_movies(request):
    # Získání seznamu filmů "Chci vidět" pro aktuálně přihlášeného uživatele
    iwantsee_list = Userlist.objects.filter(user=request.user, namelist="Chci vidět").first()
    if iwantsee_list:
        iwantsee_movies = Userlistmovie.objects.filter(userlist=iwantsee_list)
    else:
        iwantsee_movies = None
    return render(request, 'user/my_profile.html', {'iwantsee_movies': iwantsee_movies})

    

    
"""
def registration(request):
    return render(request, 'registration/signup.html')
    
def login(request):
    return render(request, 'registration/login.html')
    """
    
"""
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
"""