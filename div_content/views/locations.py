# VIEWS.LOCATIONS.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Location



def locations(request):
    locations = Location.objects.all()
    return render(request, 'meta/locations_list.html', {'locations': locations})

def location_detail(request, location_url):
    location = get_object_or_404(Location, url=location_url)
    return render(request, 'meta/location_detail.html', {'location': location})


