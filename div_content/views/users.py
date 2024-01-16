# VIEWS.USERS.PY

from django.shortcuts import get_object_or_404, render, redirect
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from div_content.models import Book, Game, Movie, Movierating, Userlist, Userlistbook, Userlistgame, Userlistmovie, Userprofile
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from star_ratings.models import UserRating
from div_content.forms.users import ContactForm, UserProfileForm

from django.db.models import Avg, F, Q
from django.http import JsonResponse

import json




def contact_form(request):
    message_sent = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            message_sent = True
    else:
        form = ContactForm()

    return render(request, 'user/contact.html', {'form': form, 'message_sent': message_sent})




# USER
def myuser_detail(request, user_id=None):
    # Pokud user_id není zadáno, použijte přihlášeného uživatele
    if user_id is None:
        user_id = request.user.id

    profile_user = get_object_or_404(User, id=user_id)
    user_ratings = UserRating.objects.filter(user_id=user_id).order_by('-modified')[:5]

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
        'user_profile': user_profile,
    })








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



#####
def ratings_profile(request):
    user_ratings = Movierating.objects.filter(user=request.user)
    return render(request, 'user/ratings_profile.html', {'user_ratings': user_ratings})

# Zobrazení oblíbených filmů uživatele
def favorites_profile(request):
    user_lists = Userlistmovie.objects.filter(
        userlist__namelist="Oblíbené",
        userlist__user=request.user
    ).select_related('movie').annotate(
        average_rating=F('movie__averagerating')  # Use the direct field
    )
    return render(request, 'user/favorites_profile.html', {'user_lists': user_lists})

# Zobrazení filmů, které uživatel chce vidět
def iwantsee_profile(request):
    user_lists2 = Userlistmovie.objects.filter(
        userlist__namelist="Chci vidět",
        userlist__user=request.user
    ).select_related('movie').annotate(
        average_rating=F('movie__averagerating')  # Use the direct field
    )
    return render(request, 'user/iwantsee_profile.html', {'user_lists2': user_lists2})




@login_required
def favorite_movies(request):
 # Získání seznamu "Oblíbené" pro aktuálně přihlášeného uživatele
    favorites_list = Userlist.objects.filter(user=request.user, namelist="Oblíbené").first()
    if favorites_list:
        favorite_movies = Userlistmovie.objects.filter(userlist=favorites_list)
    else:
        favorite_movies = None

    return render(request, 'user/user_lists_favorites.html', {'favorite_movies': favorite_movies})





# users
@login_required
def rated_media(request, user_id=None):
    # Implementujte logiku pro zobrazení všeho ohodnoceného média
    if user_id is None:
        user_id = request.user.id
    profile_user = get_object_or_404(User, id=user_id)
    user_ratings = UserRating.objects.filter(user_id=user_id).order_by('-modified')
    # Získání instance profilu uživatele
    user_profile = Userprofile.objects.get(user=profile_user)
    # Stránkování
    items_per_page = 10
    paginator = Paginator(user_ratings, items_per_page)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    return render(request, 'user/rated_media.html', {
        'profile_user': profile_user, 
        'user_ratings': user_ratings, 
        'page': page, 
        'user_profile': user_profile,
        })

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
def user_lists(request):
    # Implementujte logiku pro zobrazení oblíbených předmětů
    return render(request, 'user/user_lists.html')


"""
@login_required
def wantsee_movies(request):
    # Získání seznamu filmů "Chci vidět" pro aktuálně přihlášeného uživatele
    iwantsee_list = Userlist.objects.filter(user=request.user, namelist="Chci vidět").first()
    if iwantsee_list:
        iwantsee_movies = Userlistmovie.objects.filter(userlist=iwantsee_list)
    else:
        iwantsee_movies = None
    return render(request, 'user/iwantsee_profile.html', {'iwantsee_movies': iwantsee_movies})
"""


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

