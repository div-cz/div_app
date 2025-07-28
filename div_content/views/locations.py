# -------------------------------------------------------------------
#                    VIEWS.LOCATIONS.PY
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    OBSAH
# -------------------------------------------------------------------
# ### pozn�mky a todo
# ### importy
# ### konstanty
# ### funkce
# 
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    POZN�MKY A TODO
# -------------------------------------------------------------------
# Pozn�mky a todo
# -------------------------------------------------------------------


# -------------------------------------------------------------------
#                    IMPORTY 
# -------------------------------------------------------------------
# (t�i skupiny - ka�d� zvl�t abecedn�)
# 1) syst�mov� (abecedn�)
# 2) intern� (forms,models,views) (abecedn�)
# 3) third-part (t�et� strana, django, auth) (abecedn�)
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