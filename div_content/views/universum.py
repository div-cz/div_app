# -------------------------------------------------------------------
#                    VIEWS.UNIVERSUM.PY
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

from div_content.models import Book, Bookcharacter, Charactermeta, Game, Charactergame, Movie, Moviecrew,  Metauniversum


from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Prefetch


def universum_list(request):
    universa = Metauniversum.objects.all().order_by('-divrating')[:30]
    return render(request, 'universum/universum_list.html', {'universa': universa})

def universum_detail(request, universum_url):
    universum = get_object_or_404(Metauniversum, universumurl=universum_url)  
    movies = Movie.objects.filter(universumid=universum)[:30]
    books = Book.objects.filter(universumid=universum)[:30] 
    games = Game.objects.filter(universumid=universum)


    book_ids = list(books.values_list('bookid', flat=True))
    movie_ids = list(movies.values_list('movieid', flat=True))
    game_ids = list(games.values_list('gameid', flat=True))
    
    # POSTAVY Z KNIH
    book_characters = Charactermeta.objects.filter(
        characterid__in=Bookcharacter.objects.filter(
            bookid__in=book_ids
        ).values_list('characterid', flat=True)
    ).order_by('-charactercount', 'charactername')[:10]
    
    # POSTAVY Z FILMŮ
    movie_characters = Charactermeta.objects.filter(
        characterid__in=Moviecrew.objects.filter(
            movieid__in=movie_ids
        ).values_list('characterid', flat=True)
    ).annotate(
        num_movies=Count('moviecrew')
    ).exclude(charactername__isnull=True).exclude(charactername__exact="").order_by('-num_movies', 'charactername')[:10]
    
    # POSTAVY Z HER (UPRAVIT NAČÍTÁNÍ - KONZISTENCE bookcharacter vs movieCREW tak aspon gamecharacter)
    game_characters = Charactermeta.objects.filter(
        characterid__in=Charactergame.objects.filter(
            gameid__in=game_ids
        ).values_list('characterid', flat=True)
    ).order_by('-charactercount', 'charactername')[:10]




    return render(request, 'universum/universum_detail.html', {
        'universum': universum,
        'movies': movies,
        'books': books,
        'book_characters': book_characters,
        'movie_characters': movie_characters,
        'game_characters': game_characters,
    })


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------