from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Movie
from django.shortcuts import render

#def testtest(request):
#    context = {
#        'title': 'Testovaci titulek',
#        'content': 'Testovaci obsah stranky'
#        }
#    return render(request, 'test.html', context)



#def filmy_z_roku_2000(request):
#    filmy = Film.objects.filter(rok=2000)
#    return render(request, 'filmy.html', {'filmy': filmy})


def carousel_view(request):
    movies = Movie.objects.all()[:4] 
    return render(request, 'filmy/filmy_list.html', {'carousel': carousel})


def filmy(request):
        carousel_movies = Movie.objects.all()[:4]
        filmy = Movie.objects.all().order_by('-popularity')[:200]
        return render(request, 'filmy/filmy_list.html', {'filmy': filmy, 'carousel_movies': carousel_movies})
#        return HttpResponse("hlavni strana fff")

def film_detail(request, url_filmu):
    film = get_object_or_404(Movie, url=url_filmu)
    genres = film.moviegenre_set.all() # get all genres
    return render(request, 'filmy/film_detail.html', {'film': film, 'genres': genres})

