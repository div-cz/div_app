# -------------------------------------------------------------------
#                    VIEWS.LOCATIONS.PY
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
# (tøi skupiny - každá zvlášt abecednì)
# 1) systémové (abecednì)
# 2) interní (forms,models,views) (abecednì)
# 3) third-part (tøetí strana, django, auth) (abecednì)
# -------------------------------------------------------------------
from django.shortcuts import get_object_or_404, render
from div_content.models import Metacity, Metalocation
from div_content.views.login import custom_login_view



def locations(request):
    locations = Metalocation.objects.all()[:10]
    cities = Metacity.objects.all()[:10]
    
    return render(request, 'meta/locations_list.html', {'locations': locations, 'cities': cities})

def location_detail(request, location_url):
    location = get_object_or_404(Metalocation, url=location_url)
    return render(request, 'meta/location_detail.html', {'location': location})


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------