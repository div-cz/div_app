#  VIEWS.CHARACTERS.PY


from django.db.models import Exists, OuterRef
from div_content.forms.characters import FavoriteFormCharacter, CharacterBiographyForm
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Characterbiography, Charactermeta, Favorite, Movie, Moviecrew, Userlisttype, Userlist, Userlistitem, 
    FavoriteSum
    )
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect

from collections import defaultdict


# Konstant
USERLISTTYPE_FAVORITE_CHARACTER_ID = 24
USERLISTTYPE_WATCHED_MOVIES = 3 # Shlédnuto

#CONTENT_TYPE_CHARACTERMETA_ID = 13
#CONTENT_TYPE použit v books, movies, authors, characters, series, creators
charactermeta_content_type = ContentType.objects.get_for_model(Charactermeta)
CONTENT_TYPE_CHARACTERMETA_ID = charactermeta_content_type.id
#CONTENTTYPE_MOVIE_ID = 33
movie_content_type = ContentType.objects.get_for_model(Movie)
CONTENTTYPE_MOVIE_ID = movie_content_type.id


def character_list(request):
    characters = Charactermeta.objects.filter(characterimg__isnull=False).order_by('-characterbio').values(
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
    user = request.user

    movie_content_type = ContentType.objects.get(id=CONTENTTYPE_MOVIE_ID)
    userlisttype = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_MOVIES)

    filmography_query = Moviecrew.objects.filter(
        characterid=character.characterid
    ).select_related('movieid', 'peopleid').order_by('-movieid__releaseyear').annotate(
    is_watched=Exists(
        Userlistitem.objects.filter(
            userlist__user=user,
            userlist__listtype=userlisttype,
            object_id=OuterRef('movieid'),
            content_type=movie_content_type
        )
    ))[:40]

    filmography = defaultdict(list)
    for entry in filmography_query:
        # Zde předpokládám, že model osob má atributy firstname a lastname
        actor_name = f"{entry.peopleid.firstname} {entry.peopleid.lastname}" if entry.peopleid else "Neznámý herec"
        entry.movieid.is_watched = entry.is_watched
        filmography[entry.movieid].append(actor_name)

    # Ověření, zda je postava v oblíbených
    # is_favorite = False
    # if request.user.is_authenticated:
    #     content_type = ContentType.objects.get_for_model(Charactermeta)
    #     is_favorite = Favorite.objects.filter(
    #         user=request.user,
    #         content_type=content_type,
    #         object_id=character.characterid
    #     ).exists()
    
    user = request.user
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_CHARACTER_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_favorite = Userlistitem.objects.filter(object_id=character.characterid, userlist=favourites_list).exists()
        except Exception as e:
            is_favorite = False
    else:
        is_favorite = False

    # Získání seznamu fanoušků (uživatelů, kteří mají tvůrce v oblíbených)
    # fans = Favorite.objects.filter(
    #     content_type_id=13,  # ContentType napevno pro Character
    #     object_id=character.characterid
    # ).select_related('user')  # Získáme informace o uživateli

    # Získá fanoušky postavy na základě filtrování z Userlistitem
    content_type = ContentType.objects.get(id=CONTENT_TYPE_CHARACTERMETA_ID)
    fans = Userlistitem.objects.filter(
        object_id=character.characterid,
        content_type=content_type
    ).select_related("userlist")

    # Formulář pro přidání popisu postavy
    if request.method == 'POST':
        form = CharacterBiographyForm(request.POST)
        if form.is_valid():
            biography = form.save(commit=False)
            biography.userid = request.user
            biography.characterid = character
            biography.save()
            return redirect('character_detail', character_url=character.characterurl)

    else:
        form = CharacterBiographyForm(initial={'characterid': character})

    return render(request, 'characters/characters_detail.html', {
        'character': character, 
        'characterbiography': characterbiography, 
        'filmography': dict(filmography),
        'is_favorite': is_favorite,
        'fans': fans,
        'form': form,
    })


# Přidat do seznamu: Oblíbená postava
@login_required
def add_character_to_favorites(request, character_id):
    character = get_object_or_404(Charactermeta, characterid=character_id)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_CHARACTER_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=character_id).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_CHARACTERMETA_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type = content_type,
            object_id=character_id
            )

        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=character_id)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("character_detail", character_url=character.characterurl)

    # if request.method == 'POST':
    #     form = FavoriteFormCharacter(request.POST, user=request.user)
    #     if form.is_valid():
    #         try:
    #             is_favorite = form.save()
    #             return redirect(request.META.get('HTTP_REFERER', '/'))
    #             #return JsonResponse({'is_favorite': is_favorite})
    #         except Exception as e:
    #             return JsonResponse({'error': str(e)}, status=400)
    #     else:
    #         return JsonResponse({'error': 'Invalid form data', 'form_errors': form.errors}, status=400)
    # return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def remove_character_from_favorites(request, character_id):
    character = get_object_or_404(Charactermeta, characterid=character_id)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAVORITE_CHARACTER_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    userlistitem = Userlistitem.objects.get(userlist=favourites_list, object_id=character_id)
    userlistitem.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_CHARACTERMETA_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=character_id)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("character_detail", character_url=character.characterurl)
