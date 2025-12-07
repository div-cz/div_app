# -------------------------------------------------------------------
#                    VIEWS.CHARACTERS.PY
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
# (tři skupiny - každá zvlášt abecedně)
# 1) systémové (abecedně)
# 2) interní (forms,models,views) (abecedně)
# 3) third-part (třetí strana, django, auth) (abecedně)
# -------------------------------------------------------------------

from collections import defaultdict
from datetime import date

from django.db.models import Exists, OuterRef
from div_content.forms.characters import FavoriteFormCharacter, CharacterBiographyForm
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Book, Bookcharacter, Characterbiography, Charactergame, Charactermeta, Favorite, Movie, Moviecrew, Tvcrew, Userlisttype, Userlist, Userlistitem, 
    FavoriteSum
    )
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

from django.shortcuts import render, get_object_or_404, redirect




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
    characterbiography = Characterbiography.objects.filter(
        characterid=character, 
        verificationstatus="Verified"
    ).first()

    user = request.user

    movie_content_type = ContentType.objects.get(id=CONTENTTYPE_MOVIE_ID)
    userlisttype = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_MOVIES)

    # -----------------------------------------------------------
    # FILMY — OŠETŘENÍ ANONYMA
    # -----------------------------------------------------------
    filmography_base_qs = Moviecrew.objects.filter(
        characterid=character.characterid
    ).select_related('movieid', 'peopleid').order_by('-movieid__releaseyear')

    if user.is_authenticated:
        filmography_query = filmography_base_qs.annotate(
            is_watched=Exists(
                Userlistitem.objects.filter(
                    userlist__user=user,
                    userlist__listtype=userlisttype,
                    object_id=OuterRef('movieid'),
                    content_type=movie_content_type
                )
            )
        )[:40]
    else:
        # ANONYMA → přidáme is_watched = False bez DB dotazu
        filmography_query = filmography_base_qs[:40]
        for item in filmography_query:
            item.is_watched = False

    # Vytvoření filmografie
    filmography = defaultdict(list)
    for entry in filmography_query:
        actor_name = (
            f"{entry.peopleid.firstname} {entry.peopleid.lastname}"
            if entry.peopleid else "Neznámý herec"
        )
        entry.movieid.is_watched = entry.is_watched
        filmography[entry.movieid].append(actor_name)

    # -----------------------------------------------------------
    # KNIHY
    # -----------------------------------------------------------
    bibliography = (
        Bookcharacter.objects
        .filter(characterid=character)
        .select_related('bookid')
        .order_by('-bookid__year')[:40]
    )

    # -----------------------------------------------------------
    # SERIÁLY
    # -----------------------------------------------------------
    tvshows_query = (
        Tvcrew.objects
        .filter(characterid=character.characterid)
        .select_related("tvshowid", "peopleid")
        .order_by("-tvshowid__premieredate")
    )

    tvshows = [{
        "show": entry.tvshowid,
        "actor": f"{entry.peopleid.firstname} {entry.peopleid.lastname}"
    } for entry in tvshows_query]

    # -----------------------------------------------------------
    # HRY
    # -----------------------------------------------------------
    games = (
        Charactergame.objects
        .filter(characterid=character.characterid)
        .select_related("gameid")
    )

    # -----------------------------------------------------------
    # OBLÍBENÉ — ANONYM = False
    # -----------------------------------------------------------
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(
                userlisttypeid=USERLISTTYPE_FAVORITE_CHARACTER_ID
            )
            favourites_list = Userlist.objects.get(
                user=user, 
                listtype=favourites_type
            )
            is_favorite = Userlistitem.objects.filter(
                object_id=character.characterid,
                userlist=favourites_list
            ).exists()
        except Exception:
            is_favorite = False
    else:
        is_favorite = False

    # -----------------------------------------------------------
    # FANOUŠCI
    # -----------------------------------------------------------
    content_type = ContentType.objects.get(id=CONTENT_TYPE_CHARACTERMETA_ID)
    fans = (
        Userlistitem.objects
        .filter(object_id=character.characterid, content_type=content_type)
        .select_related("userlist")
    )

    # -----------------------------------------------------------
    # Formulář biografie
    # -----------------------------------------------------------
    form = None
    
    # Primární BIO (Verified nebo první existující)
    characterbiography = Characterbiography.objects.filter(
        characterid=character,
        is_primary=True
    ).first() or Characterbiography.objects.filter(characterid=character).first()
    
    # --- UPRAVA EXISTUJÍCÍ BIO ---
    if characterbiography:
        if request.method == "POST" and "edit_bio" in request.POST and request.user.is_staff:
            form = CharacterBiographyForm(request.POST, instance=characterbiography)
            if form.is_valid():
                bio = form.save(commit=False)
                bio.author = request.user.username
                bio.lastupdated = date.today()
                bio.save()
                return redirect("character_detail", character_url=character.characterurl)
        else:
            form = CharacterBiographyForm(instance=characterbiography) if request.user.is_staff else None
    
    # --- VYTVOŘENÍ NOVÉ BIO ---
    else:
        if request.method == "POST" and "add_bio" in request.POST and request.user.is_authenticated:
            form = CharacterBiographyForm(request.POST)
            if form.is_valid():
                bio = form.save(commit=False)
                bio.characterid = character
                bio.userid = request.user
                bio.author = request.user.username
                bio.is_primary = True
                bio.lastupdated = date.today()
                bio.save()
                return redirect("character_detail", character_url=character.characterurl)
        else:
            form = CharacterBiographyForm() if request.user.is_authenticated else None


    return render(request, 'characters/characters_detail.html', {
        'character': character,
        'characterbiography': characterbiography,
        'filmography': dict(filmography),
        'bibliography': bibliography,
        'tvshows': tvshows,
        'games': games,
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


# -------------------------------------------------------------------
#                    KONEC
#           Catalog DIV.cz by eKultura
# -------------------------------------------------------------------