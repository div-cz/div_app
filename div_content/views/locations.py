# VIEWS.LOCATIONS.PY

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



