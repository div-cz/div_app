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

from datetime import date
from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Creator, Creatorbiography, Bookauthor, Favorite, FavoriteSum, Metaindex, Movie, Moviecrew, Tvcrew, Tvshow, Userlisttype, Userlist, Userlistitem
)
from div_content.forms.creators import FavoriteForm, CreatorBiographyForm, CreatorDivRatingForm

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator

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

MONTHS = {
    "leden": 1, "unor": 2, "březen": 3, "brezen": 3,
    "duben": 4, "kveten": 5, "květen": 5, "cerven": 6, "červen": 6,
    "cervenec": 7, "červenec": 7, "srpen": 8, "zari": 9, "září": 9,
    "rijen": 10, "říjen": 10, "listopad": 11, "prosinec": 12,
}

ZODIAC = [
    ("kozoroh", (12, 22), (1, 19)),
    ("vodnar", (1, 20), (2, 18)),
    ("ryby", (2, 19), (3, 20)),
    ("beran", (3, 21), (4, 19)),
    ("byk", (4, 20), (5, 20)),
    ("blizenci", (5, 21), (6, 20)),
    ("rak", (6, 21), (7, 22)),
    ("lev", (7, 23), (8, 22)),
    ("panna", (8, 23), (9, 22)),
    ("vahy", (9, 23), (10, 22)),
    ("stir", (10, 23), (11, 21)),
    ("strelec", (11, 22), (12, 21)),
]

def filter_creators(request, qs_creators, **kwargs):
    people = []

    # --- CREATORS ---
    creators = qs_creators.filter(**kwargs)

    for c in creators:
        people.append({
            "type": "creator",
            "obj": c,
            "rating": c.divrating or 0,
            "lastname": c.lastname or "",
        })

    # --- AUTHORS ---
    authors = Bookauthor.objects.all()

    for a in authors:
        people.append({
            "type": "author",
            "obj": a,
            "rating": getattr(a, "divrating", 0) or 0,
            "lastname": a.lastname or "",
        })

    # --- ŘAZENÍ ---
    people.sort(key=lambda x: (-x["rating"], x["lastname"]))

    # --- PAGINACE ---
    paginator = Paginator(people, 30)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return {
        "people": page_obj,
        "creators": [],
        "authors": [],
    }


# ----------------------------------------------------
# creators
# ----------------------------------------------------

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


    age = None
    if creator.birthdate:
        today = date.today()
        age = today.year - creator.birthdate.year - (
            (today.month, today.day) < (creator.birthdate.month, creator.birthdate.day)
        )


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
                'age': age,
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



# ----------------------------------------------------
# DNEŠNÍ NAROZENINY
# ----------------------------------------------------
def creators_today(request):
    today = date.today()
    ctx = filter_creators(
        request,
        Creator.objects.all(),
        birthdate__month=today.month,
        birthdate__day=today.day
    )
    ctx["title"] = "Narozeniny dnes"
    return render(request, "creators/birthdays_list.html", ctx)

# ----------------------------------------------------
# podle roku
# ----------------------------------------------------
def creators_by_year(request, year):
    ctx = filter_creators(
        request,
        Creator.objects.all(),
        birthdate__year=year
    )
    ctx["title"] = f"Narozeni {year}"
    return render(request, "creators/birthdays_list.html", ctx)

# ----------------------------------------------------
# podle měsíce (číselně)
# ----------------------------------------------------
def creators_by_month(request, month):
    ctx = filter_creators(
        request,
        Creator.objects.all(),
        birthdate__month=month
    )
    ctx["title"] = f"Narozeni v měsíci {month}"
    return render(request, "creators/birthdays_list.html", ctx)

# ----------------------------------------------------
# podle měsíce slovně
# ----------------------------------------------------
def creators_by_month_slug(request, month_slug):
    ms = month_slug.lower()
    if ms not in MONTHS:
        return render(request, "creators/birthdays_list.html", {
            "creators": [],
            "authors": [],
            "title": f"Měsíc {month_slug} nenalezen"
        })
    return creators_by_month(request, MONTHS[ms])

# ----------------------------------------------------
# podle dne & měsíce
# ----------------------------------------------------
def creators_by_month_day(request, month, day):
    ctx = filter_creators(
        request,
        Creator.objects.all(),
        birthdate__month=month,
        birthdate__day=day
    )
    ctx["title"] = f"Narozeni {day}.{month}."
    return render(request, "creators/birthdays_list.html", ctx)

# ----------------------------------------------------
# přesné datum
# ----------------------------------------------------
def creators_by_exact_date(request, year, month, day):
    ctx = filter_creators(
        request,
        Creator.objects.all(),
        birthdate__year=year,
        birthdate__month=month,
        birthdate__day=day
    )
    ctx["title"] = f"Narozeni {day}.{month}.{year}"
    return render(request, "creators/birthdays_list.html", ctx)

# ----------------------------------------------------
# znamení zvěrokruhu
# ----------------------------------------------------
def creators_by_zodiac(request, sign):
    sign = sign.lower()

    chosen = None
    for name, start, end in ZODIAC:
        if name == sign:
            chosen = (name, start, end)
            break

    if not chosen:
        return render(request, "creators/birthdays_list.html", {
            "creators": [], "authors": [], "title": "Znamení nenalezeno"
        })

    name, (m1, d1), (m2, d2) = chosen

    if m1 <= m2:
        creators = Creator.objects.filter(
            request,
            birthdate__month__gte=m1,
            birthdate__month__lte=m2
        )
    else:
        creators = Creator.objects.filter(
            request,
            birthdate__month__gte=m1
        ) | Creator.objects.filter(
            birthdate__month__lte=m2
        )

    # filtrujeme dny
    result = [c for c in creators if c.birthdate and in_range(c.birthdate, (m1, d1), (m2, d2))]

    ctx = {
        "creators": result,
        "authors": [],   # zatím autoři bez horoskopu
        "title": f"Znamení – {name.capitalize()}",
    }
    return render(request, "creators/birthdays_list.html", ctx)

def in_range(bd, start, end):
    m, d = bd.month, bd.day
    (m1, d1), (m2, d2) = start, end

    if start <= end:
        return (m, d) >= start and (m, d) <= end
    else:
        return (m, d) >= start or (m, d) <= end