from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import Movie, Game, Book, Lokalita
from django.shortcuts import render


def testtest(request):
    context = {
        'title': 'Testovaci titulek',
        'content': 'Testovaci obsah stranky'
        }
    return render(request, 'test.html', context)

def filmy_z_roku_2000(request):
    filmy = Film.objects.filter(rok=2000)
    return render(request, 'filmy.html', {'filmy': filmy})

def index(request):
#        return HttpResponse("Toto je hlavní stránka.kontakt")
        return render(request, 'index.html')

def filmy(request):
        return HttpResponse("hlavni strana fff")
#        filmy = Movie.objects.all()
#        return render(request, 'filmy/filmy_list.html', {'filmy': filmy})
#        return HttpResponse("hlavni strana fff")

def film_detail(request, nazev_filmu):
    film = get_object_or_404(Movie, title=nazev_filmu)
    return render(request, 'filmy/film_detail.html', {'film': film})

# Pro hry
def hry(request):
    hry = Game.objects.all()
    return render(request, 'hry/hry_list.html', {'hry': hry})

def hra_detail(request, nazev_hry):
    hra = get_object_or_404(Game, nazev=nazev_hry)
    return render(request, 'hry/hra_detail.html', {'hra': hra})

# Pro knihy
def knihy(request):
    knihy = Kniha.objects.all()
    return render(request, 'knihy/knihy_list.html', {'knihy': knihy})

def kniha_detail(request, nazev_knihy):
    kniha = get_object_or_404(Kniha, nazev=nazev_knihy)
    return render(request, 'knihy/kniha_detail.html', {'kniha': kniha})

# Pro lokality
def lokality(request):
    lokality = Lokalita.objects.all()
    return render(request, 'lokality/lokality_list.html', {'lokality': lokality})

def lokalita_detail(request, nazev_lokality):
    lokalita = get_object_or_404(Lokalita, nazev=nazev_lokality)
    return render(request, 'lokality/lokalita_detail.html', {'lokalita': lokalita})


def onas(request):
        return HttpResponse("Toto je stranka o nas")

def about(request):
        return HttpResponse("Tot je about")

def kontakt(request):
        return  HttpResponse("Toto je kontaktní stránka.")
