# -------------------------------------------------------------------
#                    VIEWS.LOCATIONS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### pozn·mky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZN¡MKY A TODO
# -------------------------------------------------------------------
# Pozn·mky a todo
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (t¯i skupiny - kaûd· zvl·öt abecednÏ)
# 1) systÈmovÈ (abecednÏ)
# 2) internÌ (forms,models,views) (abecednÏ)
# 3) third-part (t¯etÌ strana, django, auth) (abecednÏ)
# -------------------------------------------------------------------
from django.shortcuts import get_object_or_404, render

from div_content.forms.locations import LocationCreateForm, LocationForm


from div_content.models.books import Booklocation
from div_content.models.games import Gamelocation
from div_content.models.movies import Movielocation
from div_content.models.meta import Metacity, Metalocation


from div_content.views.login import custom_login_view



def locations(request):
    locations = Metalocation.objects.all()[:10]
    cities = Metacity.objects.all()[:10]
    
    return render(request, 'meta/locations_list.html', {'locations': locations, 'cities': cities})

def get_breadcrumb(location):
    items = []
    current = location
    while current:
        items.append(current)
        current = current.parentlocation
    return reversed(items)


def location_detail(request, location_url):
    location = get_object_or_404(Metalocation, locationurl=location_url)

    movies = Movielocation.objects.filter(locationid=location).select_related('movieid')
    games = Gamelocation.objects.filter(locationid=location)
    books = Booklocation.objects.filter(locationid=location)

    if request.user.is_staff:
        if request.method == "POST":
            form = LocationForm(request.POST, instance=location)
            if form.is_valid():
                form.save()
        else:
            form = LocationForm(instance=location)
    else:
        form = None

    return render(request, 'meta/location_detail.html', {
        'location': location,
        'movies': movies,
        'games': games,
        'books': books,
        'form': form,
    })


def location_create(request):
    if not request.user.is_staff:
        return redirect('/')

    if request.method == 'POST':
        form = LocationCreateForm(request.POST)
        if form.is_valid():
            location = form.save()
            return redirect(f'/lokalita/{location.locationurl}/')
    else:
        form = LocationCreateForm()

    return render(request, 'meta/location_create.html', {'form': form})
# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------