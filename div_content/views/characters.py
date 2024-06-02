from django.shortcuts import render, get_object_or_404
from div_content.models import Characterbiography, Charactermeta, Moviecrew
from collections import defaultdict



def character_list(request):
    characters = Charactermeta.objects.filter(characterimg__isnull=False).values(
        'characterid', 
        'charactername', 
        'characternamecz', 
        'characterimg', 
        'characterbio', 
        'characterurl', 
        'charactercount'
    )[:40]
    return render(request, 'characters/characters_list.html', {'characters': characters})





def character_detail(request, character_url):
    character = get_object_or_404(Charactermeta, characterurl=character_url)
    characterbiography = Characterbiography.objects.filter(characterid=character, verificationstatus="Verified").first()
    
    filmography_query = Moviecrew.objects.filter(
        characterid=character.characterid
    ).select_related('movieid', 'peopleid').order_by('-movieid__releaseyear')[:40]

    filmography = defaultdict(list)
    for entry in filmography_query:
        # Zde předpokládám, že model osob má atributy firstname a lastname
        actor_name = f"{entry.peopleid.firstname} {entry.peopleid.lastname}" if entry.peopleid else "Neznámý herec"
        filmography[entry.movieid].append(actor_name)

    return render(request, 'characters/characters_detail.html', {
        'character': character, 
        'characterbiography': characterbiography, 
        'filmography': dict(filmography),
    })
