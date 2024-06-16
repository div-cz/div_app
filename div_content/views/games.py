# VIEWS.GAMES.PY

from django.shortcuts import get_object_or_404, render, redirect
from div_content.models import Game, Gamecomments, Gamedevelopers, Gameplatform, Gamepublisher, Gamepurchase, Gamerating
from div_content.forms.games import GameForm




def games(request):
    games = Game.objects.all()
    return render(request, 'games/games_list.html', {'games': games})

def game_detail(request, game_url):
    game = get_object_or_404(Game, url=game_url)
    return render(request, 'games/game_detail.html', {'game': game})




def game_add(request):
    if request.method == "POST":
        form = GameForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('games/game_add_success')  # Přesměrování po úspěšném přidání
    else:
        form = GameForm()
    return render(request, 'games/game_add.html', {'form': form})



