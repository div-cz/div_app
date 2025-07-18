from django.shortcuts import get_object_or_404, render
from div_content.models import Metalocation, Book, Movie, Game


def eshop_detail(request, item_id):
    # Detail produktu
    item = get_object_or_404(Metalocation, id=item_id)
    return render(request, 'eshop/eshop_detail.html', {'item': item})

def eshop_list(request):
    # Všechno zboží
    items = Metalocation.objects.all()[:10] #filter(for_sale=True)
    return render(request, 'eshop/eshop_list.html', {'items': items})

def eshop_books(request):
    # Pouze knihy
    books = Book.objects.all()[:10]
    return render(request, 'eshop/eshop_books.html', {'books': books})

def eshop_movies(request):
    # Pouze filmy
    movies = Movie.objects.all()[:10] 
    return render(request, 'eshop/eshop_movies.html', {'movies': movies})

def eshop_games(request):
    # Pouze hry
    games = Game.objects.all()[:10]
    return render(request, 'eshop/eshop_games.html', {'games': games})


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------