# -------------------------------------------------------------------
#                    VIEWS.CREATORS.PY
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
from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Creator, Creatorbiography, Favorite, FavoriteSum, Metaindex, Movie, Moviecrew, Tvcrew, Tvshow, Userlisttype, Userlist, Userlistitem
)
from div_content.forms.creators import FavoriteForm, CreatorBiographyForm, CreatorDivRatingForm

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse

from django.shortcuts import get_object_or_404, render, redirect
#from div_content.forms.creators import SearchFormCreators

from collections import defaultdict

# Konstanty
#CONTENT_TYPE použit v books, movies, authors, characters, series, creators

USERLISTTYPE_FAV_CREATOR_ID = 25 # Oblíbený tvůrce
USERLISTTYPE_WATCHED_MOVIES = 3 # Shlédnuto
#CONTENTTYPE_CREATOR_ID = 15
creator_content_type = ContentType.objects.get_for_model(Creator)
CONTENTTYPE_CREATOR_ID = creator_content_type.id
#CONTENTTYPE_MOVIE_ID = 33
movie_content_type = ContentType.objects.get_for_model(Movie)
CONTENTTYPE_MOVIE_ID = movie_content_type.id


def creators_list(request):
    creators = Creator.objects.all()[:48] #.order_by('-popularity')
    movies_carousel = Metaindex.objects.filter(section='Movie').order_by('-divrating').values('title', 'url', 'img', 'description')[3:7]

    return render(request, 'creators/creators_list.html', {'creators': creators, 'movies_carousel': movies_carousel})


def creator_detail(request, creator_url):
    creator = get_object_or_404(Creator, url=creator_url)

    # current_creator = Creator.objects.get(url=creator_url)
    current_creator = Creator.objects.select_related("countryid").get(url=creator_url)

    creatorbiography = Creatorbiography.objects.filter(creator=creator, verificationstatus="Verified").first()
    
    top_10_creators = Creator.objects.all().order_by('-popularity')[:10]


    #filmography = Moviecrew.objects.filter(peopleid=creator.creatorid).select_related('movieid', 'roleid')
    # Zjištění, zda je položka oblíbená
    # is_favorite = False
    # if request.user.is_authenticated:
    #     is_favorite = Favorite.objects.filter(
    #         user=request.user,
    #         content_type_id=15,  # ContentType napevno pro Creator
    #         object_id=creator.creatorid  
    #     ).exists()
    user = request.user
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_CREATOR_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_favorite = Userlistitem.objects.filter(object_id=creator.creatorid, userlist=favourites_list).exists()
        except Exception as e:
            is_favorite = False
    else:
        is_favorite = False

    # Získání seznamu fanoušků (uživatelů, kteří mají tvůrce v oblíbených)
    # fans = Favorite.objects.filter(
    #     content_type_id=15,  # ContentType napevno pro Creator
    #     object_id=creator.creatorid
    # ).select_related('user')  # Získáme informace o uživateli
        # Získá fanoušky spisovatele na základě filtrování z Userlistitem
    content_type = ContentType.objects.get(id=CONTENTTYPE_CREATOR_ID)
    fans = Userlistitem.objects.filter(
        object_id=creator.creatorid,
        content_type=content_type
    ).select_related("userlist")

    movie_content_type = ContentType.objects.get(id=CONTENTTYPE_MOVIE_ID)
    userlisttype = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_WATCHED_MOVIES)


    # OPRAVA ANONYMNÍHO PRISTUPU
    filmography_query = Moviecrew.objects.filter(
        peopleid=creator.creatorid
    ).select_related('movieid', 'roleid').order_by('-movieid__releaseyear')
    
    if request.user.is_authenticated:
        filmography_query = filmography_query.annotate(
            is_watched=Exists(
                Userlistitem.objects.filter(
                    userlist__user=request.user,
                    userlist__listtype=userlisttype,
                    object_id=OuterRef('movieid'),
                    content_type=movie_content_type
                )
            )
        )


    # Seskupování podle filmu a agregace rolí
    filmography = defaultdict(list)
    for entry in filmography_query:
        movie = entry.movieid
        if not request.user.is_anonymous:
            movie.is_watched = entry.is_watched
        filmography[movie].append(entry.roleid.rolenamecz)


    # výpis seriálů 
    tvshow_query = Tvcrew.objects.filter(
    peopleid=creator
    ).select_related('tvshowid', 'roleid').order_by('-tvshowid__premieredate')
    
    if request.user.is_authenticated:
        tvshow_query = tvshow_query.annotate(
            is_watched=Exists(
                Userlistitem.objects.filter(
                    userlist__user=request.user,
                    userlist__listtype=userlisttype,
                    object_id=OuterRef('tvshowid'),
                    content_type=ContentType.objects.get_for_model(Tvshow)
                )
            )
        )
    
    # Seskupení seriálů podle show + role
    tvshows = defaultdict(list)
    for entry in tvshow_query:
        tvshow = entry.tvshowid
        if not request.user.is_anonymous:
            tvshow.is_watched = entry.is_watched
        tvshows[tvshow].append(entry.roleid.rolenamecz)


    # Formulář pro úpravu DIV Ratingu u Creator
    creator_div_rating_form = None
    if request.user.is_superuser:
        if request.method == 'POST' and 'update_divrating' in request.POST:
            creator_div_rating_form = CreatorDivRatingForm(request.POST, instance=creator)
            if creator_div_rating_form.is_valid():
                creator_div_rating_form.save()
                return redirect('creator_detail', creator_url=creator_url)
        else:
            creator_div_rating_form = CreatorDivRatingForm(instance=creator)
    
    # Formulář pro přidání popisu herce
    if request.method == "POST":
        form = CreatorBiographyForm(request.POST)
        if form.is_valid():
            biography = form.save(commit=False)
            biography.userid = request.user
            biography.creator = creator
            biography.save()
            return redirect("creator_detail", creator_url=creator.url)
    else:
        form = CreatorBiographyForm(initial={"creator": creator})



    return render(request, 'creators/creator_detail.html', 
                {'creator': creator, 
                'creatorbiography': creatorbiography, 
                'top_10_creators': top_10_creators, 
                'filmography': filmography.items(),
                'tvshows': tvshows.items(),
                'is_favorite': is_favorite,
                'fans': fans,
                'creator_div_rating_form': creator_div_rating_form,
                'form': form,
})
                
def creators_search(request):
    creators = None
    if 'q' in request.GET:
        form = SearchFormCreators(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            creators = Creator.objects.filter(
                firstname__icontains=query
            ).values('creatorid', 'firstname', 'lastname', 'url', 'popularity')[:50]
    else:
        form = SearchFormCreators()

    return render(request, 'creators/creators_search.html', {'form': form, 'creators': creators})




@login_required
def toggle_favorite(request):
    if request.method == 'POST':
        form = FavoriteForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                is_favorite = form.save()
                return JsonResponse({'is_favorite': is_favorite})
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'Invalid form data', 'form_errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)


# Přidat do seznamu: Oblíbený tvůrce    
@login_required
def add_creator_to_favourites(request, creatorid):
    creator = get_object_or_404(Creator, creatorid=creatorid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_CREATOR_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=creatorid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENTTYPE_CREATOR_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=creatorid
            )
        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=creatorid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect('creator_detail', creator_url=creator.url) 


# Odebrat ze seznamu: Oblíbený tvůrce
@login_required
def remove_creator_from_favourites(request, creatorid):
    creator = get_object_or_404(Creator, creatorid=creatorid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_CREATOR_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)

    userlistitem = Userlistitem.objects.get(userlist=favourites_list, object_id=creatorid)
    userlistitem.delete()

    content_type = ContentType.objects.get(id=CONTENTTYPE_CREATOR_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=creatorid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("creator_detail", creator_url=creator.url)