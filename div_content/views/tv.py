# VIEWS.TV.PY čaj
from django.shortcuts import render, get_object_or_404
from div_content.models import Tvseason, Tvshow
def tv(request):



    tvshows_list = Tvshow.objects.all().order_by('-tvshowid').values('title', 'titlecz', 'url', 'img')[:96] #Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:40]
    return render(request, 'tv/tv_list.html', {'tvshows_list': tvshows_list})


def tv_detail(request, tv_url):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    seasons = Tvseason.objects.filter(tvshowid=tvshow.tvshowid).order_by('seasonnumber')

    return render(request, 'tv/tv_detail.html', {'tvshow': tvshow,'seasons': seasons})