
### ### ### ### ###
### ### ### ### ### 
### SERIES SE POUŽÍVÁ PRO SERIALY ### ### ### 
### ### ### ### ### 
### ### ### ### ### 

"""
from django.shortcuts import render, get_object_or_404
from div_content.models import Tvseason, Tvshow, Movie
from div_content.views.login import custom_login_view



def tv(request):



    tvshows_list = Tvshow.objects.all().order_by('-tvshowid').values('title', 'titlecz', 'url', 'img')[:12] #Movie.objects.all().order_by('-popularity').values('title', 'titlecz', 'url', 'img', 'description')[:40]
    return render(request, 'tv/tv_list.html', {'tvshows_list': tvshows_list})


def tv_detail(request, tvshow_url):
    tvser = get_object_or_404(Tvshow, url=tvshow_url)
    return render(request, 'tv/tv_detail.html', {'tvser': tvser})
"""