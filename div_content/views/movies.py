# -------------------------------------------------------------------
#                    VIEWS.MOVIES.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### poznámky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZNÁMKY A TODO
# -------------------------------------------------------------------
# Poznámky a todo
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------

import math

from datetime import date
from decimal import Decimal


from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType

from django.core.paginator import Paginator

from django.db.models import Avg, Count, F


from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render

from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_POST

from django.views.generic import DetailView

from div_content.forms.movies import CommentForm, MovieCinemaForm, MovieDivRatingForm, MovieErrorForm, MovieTitleDIVForm, SearchForm, TrailerForm
from div_content.models import (
    Article, Book, Creator, Creatorbiography, FavoriteSum, Game, 
    Metalocation, Metagenre, Movie, Moviecinema, Moviecomments, Moviecountries, Moviecrew, Moviedistributor, Movieerror, Moviegenre, Movielocation, Moviequotes, Movierating, Movietrailer, Movietranslation, Movietrivia, Moviekeywords,
    User, Userlist, Userlistitem, Userlisttype, Userlistmovie, Userprofile

)
from div_content.utils.metaindex import add_to_metaindex

from star_ratings.models import Rating, UserRating

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



# -------------------------------------------------------------------
# F:                 MOVIE DETAIL
# -------------------------------------------------------------------
def movie_detail(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)

    # =========================================================
    # SAVE TRANSLATIONS (CZ / EN DESCRIPTION)
    # =========================================================
    if request.method == "POST" and request.user.is_staff and "update_descriptions" in request.POST:

        desc_cz = request.POST.get("description_cs", "").strip()
        desc_en = request.POST.get("description_en", "").strip()

        if desc_cz:
            translation = Movietranslation.objects.filter(
                movie=movie,
                language="cs"
            ).order_by("movietranslationid").first()

            if translation:
                translation.description = desc_cz
                translation.save()
            else:
                Movietranslation.objects.create(
                    movie=movie,
                    language="cs",
                    description=desc_cz
                )

        if desc_en:
            translation = Movietranslation.objects.filter(
                movie=movie,
                language="en"
            ).order_by("movietranslationid").first()

            if translation:
                translation.description = desc_en
                translation.save()
            else:
                Movietranslation.objects.create(
                    movie=movie,
                    language="en",
                    description=desc_en
                )

        return redirect("movie_detail", movie_url=movie.url)


    translations = Movietranslation.objects.filter(movie=movie)

    trans_cz = next((t for t in translations if t.language == "cs"), None)
    trans_en = next((t for t in translations if t.language == "en"), None)

    display_desc_cz = trans_cz.description if trans_cz and trans_cz.description else ""
    display_desc_en = trans_en.description if trans_en and trans_en.description else ""


    # TitleDIV
    language = 'cs'
    translation = Movietranslation.objects.filter(
        movie=movie,
        language=language
    ).order_by('movietranslationid').first()
    
    if translation and translation.title:
        display_title = translation.title
    elif movie.titlecz:
        display_title = movie.titlecz
    else:
        display_title = movie.title
        
    if translation and translation.description:
        display_description = translation.description
    else:
        display_description = movie.description


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

    # uložíme průměr do MOVIE
    if average_rating != movie.averagerating:
        Movie.objects.filter(movieid=movie.movieid).update(
            averagerating=average_rating
        )

    if average_rating is not None:
        # přepočet z 0–5 hvězdiček na 0–100 %
        average_rating = round(average_rating * 20)
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
        if 'comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.cleaned_data['comment']
                Moviecomments.objects.create(comment=comment, movieid=movie, user=request.user)
                return redirect('movie_detail', movie_url=movie_url)
            else:
                print(comment_form.errors)
        else:
            comment_form = CommentForm(request=request)


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


    # Formulář pro úpravu TitleDIV
    title_div_form = None
    language = 'cs'
    
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_titlediv' in request.POST:
            title_div_form = MovieTitleDIVForm(request.POST)
    
            if title_div_form.is_valid():
                title = title_div_form.cleaned_data['title']
                description = title_div_form.cleaned_data['description']
    
                translation = Movietranslation.objects.filter(
                    movie=movie,
                    language=language
                ).order_by('movietranslationid').first()
    
                if translation:
                    translation.title = title
                    if description:
                        translation.description = description
                    translation.save()
                else:
                    Movietranslation.objects.create(
                        movie=movie,
                        language=language,
                        title=title,
                        description=description or None
                    )
    
                messages.success(request, "DIV název uložen.")
                return redirect('movie_detail', movie_url=movie_url)
    if request.user.is_superuser:
        translation = Movietranslation.objects.filter(
            movie=movie,
            language=language
        ).order_by('movietranslationid').first()
    
        if translation:
            title_div_form = MovieTitleDIVForm(initial={
                'title': translation.title,
                'description': translation.description,
            })
        else:
            title_div_form = MovieTitleDIVForm()

    

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

    if request.method == 'POST' and 'error_text' in request.POST:
        error_text = request.POST.get('error_text').strip()
        if error_text:
            Movieerror.objects.create(
                error=error_text,
                movieid=movie,
                divrating=0,
                userid=request.user if request.user.is_authenticated else None
            )
            return redirect('movie_detail', movie_url=movie_url)

    quotes = Moviequotes.objects.filter(movie=movie).order_by('-divrating')  
    trivia = Movietrivia.objects.filter(movieid=movie).order_by('-divrating')  
    errors = Movieerror.objects.filter(movieid=movie).order_by('-divrating')


    if request.method == "POST" and request.user.is_superuser and 'add_to_metaindex' in request.POST:
        result = add_to_metaindex(movie, 'Movie')
        if result == "added":
            messages.success(request, "Záznam byl přidán na hlavní stránku.")
        elif result == "exists":
            messages.info(request, "Záznam už existuje.")
        else:
            messages.error(request, "Nepodařilo se přidat.")
        return redirect('movie_detail', movie_url=movie.url)

    return render(request, 'movies/movie_detail.html', {
        'movie': movie,
        'display_title': display_title,
        'display_description': display_description,
        'desc_cz': display_desc_cz,
        'desc_en': display_desc_en,
        'edit_desc_cz': trans_cz.description if trans_cz else '',
        'edit_desc_en': trans_en.description if trans_en else '',
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
        'title_div_form': title_div_form,
        'quotes': quotes,
        'trivia': trivia,
        'errors': errors,
    })


# -------------------------------------------------------------------
# F:                 RATEQUOTE MOVIE
# -------------------------------------------------------------------
@require_POST
@login_required
def ratequote_movie(request, quote_id):
    from django.utils import timezone
    from datetime import timedelta
    import json
    
    quote = get_object_or_404(Moviequotes, quoteid=quote_id)
    
    # Parse JSON z body
    try:
        body_data = json.loads(request.body.decode('utf-8'))
        action = body_data.get('action')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Neplatný požadavek.'}, status=400)
    
    # Zkontroluje cookies
    cookie_name = f'voted_movie_{quote_id}'
    if request.COOKIES.get(cookie_name):
        return JsonResponse({'error': 'Již jste hlasoval/a.'})

    # Aktualizuje hodnocení
    if action == 'thumbsup':
        quote.thumbsup = (quote.thumbsup or 0) + 1
        quote.divrating = (quote.divrating or 0) + 1
    elif action == 'thumbsdown':
        quote.thumbsdown = (quote.thumbsdown or 0) + 1
        quote.divrating = (quote.divrating or 0) - 1
    else:
        return JsonResponse({'error': 'Neplatná akce.'}, status=400)
    
    quote.save()
    
    response = JsonResponse({
        'thumbsup': quote.thumbsup or 0,
        'thumbsdown': quote.thumbsdown or 0,
        'divrating': quote.divrating or 0
    })
    
    # Nastaví cookie na týden
    expires = timezone.now() + timedelta(days=7)
    response.set_cookie(cookie_name, 'voted', expires=expires)
    
    return response


# -------------------------------------------------------------------
# F:                 SEARCH
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# C:                 MOVIE DETAIL VIEW
# -------------------------------------------------------------------
class MovieDetailView(DetailView):
    model = Movie
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'


# -------------------------------------------------------------------
# F:                 MOVIES ALPHABETICAL
# -------------------------------------------------------------------
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



# -------------------------------------------------------------------
# F:                 ADD TO FAVOURITES
# -------------------------------------------------------------------
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



# -------------------------------------------------------------------
# F:                 ADD TO WATCHLIST
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 ADD TO WATCHED
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 ADD TO MOVIE LIBRARY
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 REMOVE FROM FAVOURITES
# -------------------------------------------------------------------
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


# -------------------------------------------------------------------
# F:                 REMOVE FROM WATCHLIST
# -------------------------------------------------------------------
@login_required
def remove_from_watchlist(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watchlist_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHLIST_ID)
    watchlist_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watchlist_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=watchlist_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# -------------------------------------------------------------------
# F:                 REMOVE FROM WATCHED
# -------------------------------------------------------------------
@login_required
def remove_from_watched(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    watched_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_ID)
    watched_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=watched_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=watched_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# -------------------------------------------------------------------
# F:                 REMOVE FROM MOVIE LIBRARY
# -------------------------------------------------------------------
@login_required
def remove_from_movie_library(request, movieid):
    movie = get_object_or_404(Movie, movieid=movieid)

    movie_library_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_MOVIE_LIBRARY_ID)
    movie_library_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=movie_library_type)
    userlistmovie = Userlistitem.objects.get(object_id=movieid, userlist=movie_library_list)

    userlistmovie.delete()
    
    return redirect("movie_detail", movie_url=movie.url)


# -------------------------------------------------------------------
# F:                 REMOVE MOVIE RATING
# -------------------------------------------------------------------
@login_required
def remove_movie_rating(request, movie_url):
    movie = get_object_or_404(Movie, url=movie_url)
    movie_content_type = ContentType.objects.get_for_model(Movie)

    user_rating = UserRating.objects.filter(
        user=request.user,
        rating__content_type=movie_content_type,
        rating__object_id=movie.movieid
    ).first()

    if user_rating:
        user_rating.delete()
        # přepočet průměru
        rating_obj = Rating.objects.filter(
            content_type=movie_content_type,
            object_id=movie.movieid
        ).first()
        if rating_obj:
            agg = UserRating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
            rating_obj.average = agg["avg"] or 0
            rating_obj.count = agg["count"] or 0
            rating_obj.save()
            # UPDATE MOVIES AVERAGERATING
            Movie.objects.filter(movieid=movie.movieid).update(
                averagerating=agg["avg"]
            )
        # odečti DivCoiny (-0.01 ze všech metrik)
        coins, created = Userdivcoins.objects.get_or_create(user_id=request.user.id)
        coins.totaldivcoins   = F('totaldivcoins')   - Decimal("0.01")
        coins.weeklydivcoins  = F('weeklydivcoins')  - Decimal("0.01")
        coins.monthlydivcoins = F('monthlydivcoins') - Decimal("0.01")
        coins.yearlydivcoins  = F('yearlydivcoins')  - Decimal("0.01")
        coins.save(update_fields=["totaldivcoins", "weeklydivcoins", "monthlydivcoins", "yearlydivcoins"])
        coins.refresh_from_db()

        messages.success(request, f"Hodnocení filmu „{movie.titlecz or movie.title}“ bylo smazáno.")
    else:
        messages.warning(request, "Nemáš žádné hodnocení, které by šlo smazat.")

    return redirect("movie_detail", movie_url=movie.url)

# -------------------------------------------------------------------
#                    KONEC
# -------------------------------------------------------------------