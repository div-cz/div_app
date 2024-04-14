# VIEWS.CREATORS.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Creator, Creatorbiography, Metaindex, Movie, Moviecrew
from collections import defaultdict



def creators_list(request):
    creators = Creator.objects.all()[:48] #.order_by('-popularity')
    movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-popularity').values('title', 'url', 'img', 'description')[3:7]

    return render(request, 'creators/creators_list.html', {'creators': creators, 'movies_carousel': movies_carousel})


def creator_detail(request, creator_url):
    creator = get_object_or_404(Creator, url=creator_url)

    current_creator = Creator.objects.get(url=creator_url)
    creatorbiography = Creatorbiography.objects.filter(creator=creator, verificationstatus="Verified").first()
    
    top_10_creators = Creator.objects.all().order_by('-popularity')[:10]


    #filmography = Moviecrew.objects.filter(peopleid=creator.creatorid).select_related('movieid', 'roleid')


    filmography_query = Moviecrew.objects.filter(
        peopleid=creator.creatorid
    ).select_related('movieid', 'roleid').order_by('-movieid__releaseyear')

    # Seskupování podle filmu a agregace rolí
    filmography = defaultdict(list)
    for entry in filmography_query:
        filmography[entry.movieid].append(entry.roleid.rolenamecz)


    return render(request, 'creators/creator_detail.html', 
                {'creator': creator, 
                'creatorbiography': creatorbiography, 
                'top_10_creators': top_10_creators, 
                'filmography': filmography.items(),
})
                

