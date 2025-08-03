# -------------------------------------------------------------------
#                    VIEWS.AWARDS.PY
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


from div_content.forms.awards import MetaawardForm, MovieawardForm, BookawardForm, GameawardForm

from div_content.models import (
    Metaaward, Movieaward, Bookaward, Gameaward, 
    Movie, Book, Game, Tvshow
)
from div_content.utils.awards import AwardUtils, get_admin_award_context


from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST



def is_admin(user):
    """Check if user is admin"""
    return user.is_staff or user.is_superuser

def awards_index(request):
    """Main index page for awards"""
    # Získáme statistiky ocenění
    stats = {
        'total_awards': Metaaward.objects.count(),
        'movie_awards': Movieaward.objects.count(),
        'book_awards': Bookaward.objects.count(),
        'game_awards': Gameaward.objects.count(),
        'recent_awards': Metaaward.objects.order_by('-year')[:5]
    }
    
    # Nejnovější ocenění podle typu
    recent_movie_awards = Movieaward.objects.select_related(
        'metaAwardid', 'movieid'
    ).order_by('-metaAwardid__year')[:3]
    
    recent_book_awards = Bookaward.objects.select_related(
        'metaAwardid', 'bookid'
    ).order_by('-metaAwardid__year')[:3]
    
    recent_game_awards = Gameaward.objects.select_related(
        'metaawardid', 'gameid'
    ).order_by('-metaawardid__year')[:3]
    
    context = {
        'stats': stats,
        'recent_movie_awards': recent_movie_awards,
        'recent_book_awards': recent_book_awards,
        'recent_game_awards': recent_game_awards,
    }
    
    return render(request, "awards/awards_index.html", context)

def awards_movies(request):
    """Fetch all movie awards and winners"""
    # Filtrování podle roku a typu ocenění
    year = request.GET.get('year')
    award_name = request.GET.get('award')
    winners_only = request.GET.get('winners_only')
    
    movie_awards = Movieaward.objects.select_related('metaAwardid', 'movieid')
    
    if year:
        movie_awards = movie_awards.filter(metaAwardid__year=year)
    if award_name:
        movie_awards = movie_awards.filter(metaAwardid__awardname__icontains=award_name)
    if winners_only:
        movie_awards = movie_awards.filter(winner=True)
    
    movie_awards = movie_awards.order_by('-metaAwardid__year', 'metaAwardid__awardname')
    
    # Paginating results
    paginator = Paginator(movie_awards, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Získáme roky a názvy ocenění pro filtrování
    years = Metaaward.objects.filter(awardtype='film').values_list('year', flat=True).distinct().order_by('-year')
    award_names = Metaaward.objects.filter(awardtype='film').values_list('awardname', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'years': years,
        'award_names': award_names,
        'current_year': year,
        'current_award': award_name,
        'winners_only': winners_only,
    }
    
    return render(request, "awards/awards_movies.html", context)

def awards_series(request):
    """Awards for TV series - rozšíření pro budoucnost"""
    # Prozatím prázdné, připraveno pro budoucí implementaci
    context = {
        'message': 'Sekce seriálových ocenění bude brzy dostupná.'
    }
    return render(request, "awards/awards_series.html", context)

def awards_books(request):
    """Seskupený přehled knižních ocenění (nominace i vítězové)"""

    winners_only = request.GET.get('winners_only') == '1'
    book_awards = Bookaward.objects.select_related('metaAwardid', 'bookid')
    
    if winners_only:
        book_awards = book_awards.filter(winner=True)

    book_awards = book_awards.order_by('-metaAwardid__year', 'metaAwardid__awardname')

    # --- Skupiny pro hlavní tabulku ---
    grouped = {}
    for ba in book_awards:
        name = ba.metaAwardid.awardname
        if name not in grouped:
            grouped[name] = []
        grouped[name].append(ba)

    # --- Skupiny pro levé menu ---
    sidebar = {}
    for ba in book_awards:
        name = ba.metaAwardid.awardname
        slug = ba.metaAwardid.slug
        year = ba.metaAwardid.year
        if name not in sidebar:
            sidebar[name] = []
        if not any(y.year == year for y in sidebar[name]):
            sidebar[name].append(type('Y', (), {'year': year, 'slug': slug, 'count': 1}))
        else:
            for y in sidebar[name]:
                if y.year == year:
                    y.count += 1

    context = {
        'grouped_awards': grouped,
        'sidebar_awards': sidebar,
        'winners_only': winners_only,
    }
    return render(request, "awards/awards_books.html", context)




def awards_games(request):
    """Fetch all game awards and winners"""
    year = request.GET.get('year')
    award_name = request.GET.get('award')
    winners_only = request.GET.get('winners_only')
    
    game_awards = Gameaward.objects.select_related('metaawardid', 'gameid')
    
    if year:
        game_awards = game_awards.filter(metaawardid__year=year)
    if award_name:
        game_awards = game_awards.filter(metaawardid__awardname__icontains=award_name)
    if winners_only:
        game_awards = game_awards.filter(winner=True)
    
    game_awards = game_awards.order_by('-metaawardid__year', 'metaawardid__awardname')
    
    # Paginating results
    paginator = Paginator(game_awards, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filtry
    years = Metaaward.objects.filter(awardtype='game').values_list('year', flat=True).distinct().order_by('-year')
    award_names = Metaaward.objects.filter(awardtype='game').values_list('awardname', flat=True).distinct()
    
    context = {
        'page_obj': page_obj,
        'years': years,
        'award_names': award_names,
        'current_year': year,
        'current_award': award_name,
        'winners_only': winners_only,
    }
    
    return render(request, "awards/awards_games.html", context)

def award_detail(request, slug, year):
    """Detail konkrétního ocenění pro daný rok"""
    award = get_object_or_404(Metaaward, slug=slug, year=year)
    
    # Získáme všechna související ocenění
    movie_awards = Movieaward.objects.filter(metaAwardid=award).select_related('movieid')
    book_awards = Bookaward.objects.filter(metaAwardid=award).select_related('bookid')
    game_awards = Gameaward.objects.filter(metaawardid=award).select_related('gameid')
    
    # Rozdělíme na vítěze a nominované
    movie_winners = movie_awards.filter(winner=True)
    movie_nominees = movie_awards.filter(winner=False)
    
    book_winners = book_awards.filter(winner=True)
    book_nominees = book_awards.filter(winner=False)
    
    game_winners = game_awards.filter(winner=True)
    game_nominees = game_awards.filter(winner=False)
    
    context = {
        'award': award,
        'movie_awards': movie_awards,
        'book_awards': book_awards,
        'game_awards': game_awards,
        'movie_winners': movie_winners,
        'movie_nominees': movie_nominees,
        'book_winners': book_winners,
        'book_nominees': book_nominees,
        'game_winners': game_winners,
        'game_nominees': game_nominees,
    }
    
    return render(request, "awards/award_detail.html", context)

# ADMIN VIEWS

@login_required
@user_passes_test(is_admin)
def admin_awards(request):
    """Admin přehled všech ocenění"""
    awards = Metaaward.objects.all().order_by('-year', 'awardname')
    
    # Paginating results
    paginator = Paginator(awards, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, "awards/admin_awards.html", context)

@login_required
@user_passes_test(is_admin)
def admin_award_add(request):
    """Přidání nového ocenění"""
    if request.method == 'POST':
        form = MetaawardForm(request.POST)
        if form.is_valid():
            award = form.save()
            messages.success(request, f'Ocenění "{award.awardname}" ({award.year}) bylo úspěšně přidáno.')
            return redirect('admin_awards')
    else:
        form = MetaawardForm()
    
    return render(request, "awards/admin_award_form.html", {'form': form, 'action': 'Přidat'})

@login_required
@user_passes_test(is_admin)
def admin_award_edit(request, award_id):
    """Editace existujícího ocenění"""
    award = get_object_or_404(Metaaward, metaawardid=award_id)
    
    if request.method == 'POST':
        form = MetaawardForm(request.POST, instance=award)
        if form.is_valid():
            award = form.save()
            messages.success(request, f'Ocenění "{award.awardname}" ({award.year}) bylo úspěšně upraveno.')
            return redirect('admin_awards')
    else:
        form = MetaawardForm(instance=award)
    
    return render(request, "awards/admin_award_form.html", {
        'form': form, 
        'award': award, 
        'action': 'Upravit'
    })

@login_required
@user_passes_test(is_admin)
def admin_award_delete(request, award_id):
    """Smazání ocenění"""
    award = get_object_or_404(Metaaward, metaawardid=award_id)
    
    if request.method == 'POST':
        award_name = award.awardname
        award_year = award.year
        award.delete()
        messages.success(request, f'Ocenění "{award_name}" ({award_year}) bylo úspěšně smazáno.')
        return redirect('admin_awards')
    
    return render(request, "awards/admin_award_delete.html", {'award': award})

@login_required
@user_passes_test(is_admin)
def admin_award_nominees(request, award_id):
    """Správa nominovaných pro konkrétní ocenění"""
    award = get_object_or_404(Metaaward, metaawardid=award_id)
    
    # Získáme všechny nominace podle typu ocenění
    context = {'award': award}
    
    if award.awardtype == 'film':
        nominees = Movieaward.objects.filter(metaAwardid=award).select_related('movieid')
        context['movie_nominees'] = nominees
    elif award.awardtype == 'book':
        nominees = Bookaward.objects.filter(metaAwardid=award).select_related('bookid')
        context['book_nominees'] = nominees
    elif award.awardtype == 'game':
        nominees = Gameaward.objects.filter(metaawardid=award).select_related('gameid')
        context['game_nominees'] = nominees
    
    return render(request, "awards/admin_award_nominees.html", context)

@login_required
@user_passes_test(is_admin)
def admin_add_movie_nominee(request, award_id):
    """Přidání filmové nominace"""
    award = get_object_or_404(Metaaward, metaawardid=award_id, awardtype='film')
    
    if request.method == 'POST':
        form = MovieawardForm(request.POST.copy())
        if form.is_valid():
            nominee = form.save(commit=False)
            nominee.metaAwardid = award
            nominee.save()
            messages.success(request, f'Film "{nominee.movieid.title}" byl přidán jako nominovaný.')
            return redirect('admin_award_nominees', award_id=award_id)
    else:
        form = MovieawardForm()
    
    return render(request, "awards/admin_add_nominee.html", {
        'form': form, 
        'award': award, 
        'type': 'film'
    })

@login_required
@user_passes_test(is_admin)
def admin_add_book_nominee(request, award_id):
    """Přidání knižní nominace"""
    award = get_object_or_404(Metaaward, metaawardid=award_id, awardtype='book')
    
    if request.method == 'POST':
        form = BookawardForm(request.POST.copy())
        if form.is_valid():
            nominee = form.save(commit=False)
            nominee.metaAwardid = award
            nominee.save()
            messages.success(request, f'Kniha "{nominee.bookid.title}" byla přidána jako nominovaná.')
            return redirect('admin_award_nominees', award_id=award_id)
    else:
        form = BookawardForm()
    
    return render(request, "awards/admin_add_nominee.html", {
        'form': form, 
        'award': award, 
        'type': 'kniha'
    })

@login_required
@user_passes_test(is_admin)
def admin_add_game_nominee(request, award_id):
    """Přidání herní nominace"""
    award = get_object_or_404(Metaaward, metaawardid=award_id, awardtype='game')
    
    if request.method == 'POST':
        form = GameawardForm(request.POST.copy())
        if form.is_valid():
            nominee = form.save(commit=False)
            nominee.metaawardid = award
            nominee.save()
            messages.success(request, f'Hra "{nominee.gameid.title}" byla přidána jako nominovaná.')
            return redirect('admin_award_nominees', award_id=award_id)
    else:
        form = GameawardForm()
    
    return render(request, "awards/admin_add_nominee.html", {
        'form': form, 
        'award': award, 
        'type': 'hra'
    })

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_toggle_winner(request):
    """AJAX endpoint pro přepínání vítěze/nominovaného"""
    nominee_type = request.POST.get('type')
    nominee_id = request.POST.get('id')
    
    try:
        if nominee_type == 'movie':
            nominee = Movieaward.objects.get(movieawardid=nominee_id)
        elif nominee_type == 'book':
            nominee = Bookaward.objects.get(bookAwardid=nominee_id)
        elif nominee_type == 'game':
            nominee = Gameaward.objects.get(gameawardid=nominee_id)
        else:
            return JsonResponse({'error': 'Neplatný typ nominace'}, status=400)
        
        nominee.winner = not nominee.winner
        nominee.save()
        
        return JsonResponse({
            'success': True,
            'winner': nominee.winner,
            'message': f'Stav {"vítěz" if nominee.winner else "nominovaný"} byl úspěšně nastaven.'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@user_passes_test(is_admin)
@require_POST
def admin_delete_nominee(request):
    """AJAX endpoint pro smazání nominace"""
    nominee_type = request.POST.get('type')
    nominee_id = request.POST.get('id')
    
    try:
        if nominee_type == 'movie':
            nominee = Movieaward.objects.get(movieawardid=nominee_id)
            title = nominee.movieid.title
        elif nominee_type == 'book':
            nominee = Bookaward.objects.get(bookAwardid=nominee_id)
            title = nominee.bookid.title
        elif nominee_type == 'game':
            nominee = Gameaward.objects.get(gameawardid=nominee_id)
            title = nominee.gameid.title
        else:
            return JsonResponse({'error': 'Neplatný typ nominace'}, status=400)
        
        nominee.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Nominace pro "{title}" byla úspěšně smazána.'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# AJAX SEARCH ENDPOINTS

def ajax_search_movies(request):
    """AJAX vyhledávání filmů pro formuláře"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    movies = Movie.objects.filter(
        Q(title__icontains=query) | Q(titlecz__icontains=query)
    )[:10]
    
    results = [{
        'id': movie.movieid,
        'text': f"{movie.titlecz or movie.title} ({movie.releaseyear})"
    } for movie in movies]
    
    return JsonResponse({'results': results})

def ajax_search_books(request):
    """AJAX vyhledávání knih pro formuláře"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    books = Book.objects.filter(
        Q(title__icontains=query) | Q(titlecz__icontains=query)
    )[:10]
    
    results = [{
        'id': book.bookid,
        'text': f"{book.titlecz or book.title} ({book.year}) - {book.author}"
    } for book in books]
    
    return JsonResponse({'results': results})

def ajax_search_games(request):
    """AJAX vyhledávání her pro formuláře"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    games = Game.objects.filter(
        Q(title__icontains=query) | Q(titlecz__icontains=query)
    )[:10]
    
    results = [{
        'id': game.gameid,
        'text': f"{game.titlecz or game.title} ({game.year})"
    } for game in games]
    
    return JsonResponse({'results': results})