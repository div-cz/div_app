from django.shortcuts import get_object_or_404, render
from div_content.models import Creator, Creatorbiography, Movie, Moviecrew



def games(request):
    games = Game.objects.all()
    return render(request, 'games/games_list.html', {'games': games})

def game_detail(request, game_url):
    game = get_object_or_404(Game, url=game_url)
    return render(request, 'games/game_detail.html', {'game': game})



