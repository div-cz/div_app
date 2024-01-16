# VIEWS.CREATORS.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Creator, Creatorbiography, Movie, Moviecrew



def creators_list(request):
    creators = Creator.objects.all().order_by('-popularity')[:48]
    movies_carousel = Movie.objects.filter(releaseyear=2023,adult=0).order_by('-popularity')[3:7]

    return render(request, 'creators/creators_list.html', {'creators': creators, 'movies_carousel': movies_carousel})


def creator_detail(request, creator_url):
    creator = get_object_or_404(Creator, url=creator_url)

    current_creator = Creator.objects.get(url=creator_url)
    creatorbiography = Creatorbiography.objects.filter(creator=creator, verificationstatus="Verified").first()
    
    creator_list_10 = Creator.objects.filter(popularity__gt=current_creator.popularity).order_by('-popularity').values('firstname', 'lastname', 'url', 'birthdate')[:10]
    creator_list_10_minus = Creator.objects.filter(popularity__lt=current_creator.popularity).order_by('popularity').values('firstname', 'lastname', 'url', 'birthdate')[:10]

    filmography = Moviecrew.objects.filter(peopleid=creator.creatorid).select_related('movieid', 'roleid')

    return render(request, 'creators/creator_detail.html', 
                {'creator': creator, 
                'creatorbiography': creatorbiography, 
                'creator_list_10': creator_list_10, 
                'creator_list_10_minus': creator_list_10_minus, 
                'filmography': filmography,
})
                

