# VIEWS.AUTHORS.PY

from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import OuterRef, Subquery, Exists
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Book, Bookauthor, Bookwriters, Favorite, Userlisttype, Userlist, Userlistitem, Userlisttype, FavoriteSum
)
from div_content.forms.authors import FavoriteForm
from div_content.views.login import custom_login_view

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


# Konstanty - Userlisttype
USERLISTTYPE_FAV_AUTHOR_ID = 23
USERLISTTYPE_READLIST_ID = 6
CONTENT_TYPE_BOOKAUTHOR_ID = 10

def authors_list(request):
    # Získání seznamu všech autorů
    authors = Bookauthor.objects.all()  
    return render(request, 'creators/authors_list.html', {'authors': authors})

def author_detail(request, author_url):
    # Zobrazení detailu jednoho autora
    author = get_object_or_404(Bookauthor, url=author_url) 
    
    # Asi nějaké staré query? bookwriters ani není v Book modelu
    # books = Book.objects.filter(bookwriters__author=author, bookwriters__book__language='cs')¨

    user = request.user

    # Získá userlisttype pro přečtené knihy
    userlisttype = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_READLIST_ID)

    # Získá uživatelovy přečtené knihy
    read_list_items = Userlistitem.objects.filter(
        userlist__user=user,
        userlist__listtype=userlisttype,
        object_id=OuterRef("bookid")
    )

    # Autorovy knihy seřazené od nejnovějších po nejstarší
    # a přidá atribut is_read, pokud uživatel má v seznamu přečtených
    books = Book.objects.filter(authorid=author.authorid).order_by("-year").annotate(
        is_read=Exists(read_list_items)
    )
        
    author_list_10 = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]
    author_list_10_minus = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]



    # Zjištění, zda je autor oblíbený
    # is_favorite = False
    # if request.user.is_authenticated:
    #     is_favorite = Favorite.objects.filter(
    #         user=request.user,
    #         content_type_id=10,  # ContentType ID pro Bookauthor
    #         object_id=author.authorid  
    #     ).exists()
    
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_AUTHOR_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_favorite = Userlistitem.objects.filter(object_id=author.authorid, userlist=favourites_list).exists()
        except Exception as e:
            is_favorite = False
    else:
        is_favorite = False

    # if request.method == 'POST' and request.user.is_authenticated:
    #     form = FavoriteForm(request.POST, user=request.user)
    #     if form.is_valid():
    #         is_favorite = form.save()
    #         return JsonResponse({'is_favorite': is_favorite})
    #     else:
    #         return JsonResponse({'error': 'Invalid form data'}, status=400)


    # Získání seznamu fanoušků (uživatelů, kteří mají tvůrce v oblíbených)
    # fans = Favorite.objects.filter(
    #     content_type_id=10,  # ContentType napevno pro Character
    #     object_id=author.authorid
    # ).select_related('user')  # Získáme informace o uživateli

    # Získá fanoušky spisovatele na základě filtrování z Userlistitem
    content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOKAUTHOR_ID)
    fans = Userlistitem.objects.filter(
        object_id=author.authorid,
        content_type=content_type
    ).select_related("userlist")



    return render(request, 'creators/author_detail.html', {
        'author': author, 
        'books': books, 
        'author_list_10': author_list_10, 
        'author_list_10_minus': author_list_10_minus,
        'is_favorite': is_favorite,
        'fans': fans,
        })


def author_add(request):
    # Logika pro přidání nového autora
    if request.method == 'POST':
        # Zpracování formuláře pro přidání autora
        # Po úspěšném přidání autora můžete přesměrovat uživatele na stránku s detaily autora nebo jinou vhodnou stránku
        pass
    else:
        # Zobrazení formuláře pro přidání autora (GET request)
        # Upravte tuto část pro zobrazení formuláře podle vašich potřeb
        pass
    return render(request, 'creators/author_add.html')


# Přidat do seznamu: Oblíbený spisovatel
@login_required
def add_to_favourite_authors(request, authorid):
    author = get_object_or_404(Bookauthor, authorid=authorid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_AUTHOR_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user = request.user, listtype=favourite_type)

    if Userlistitem.objects.filter(userlist=favourites_list, object_id=authorid).exists():
        pass
    else:
        content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOKAUTHOR_ID)
        Userlistitem.objects.create(
            userlist=favourites_list, 
            content_type=content_type,
            object_id=authorid
            )
        favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=authorid)
        favourite_sum.favorite_count += 1
        favourite_sum.save()
    
    return redirect("author_detail", author_url=author.url)


# Odebrat ze seznamu: Oblíbený spisovatel
@login_required
def remove_from_favourite_authors(request, authorid):
    author = get_object_or_404(Bookauthor, authorid=authorid)
    favourite_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_AUTHOR_ID)
    favourites_list, _ = Userlist.objects.get_or_create(user=request.user, listtype=favourite_type)

    userlistitem = Userlistitem.objects.get(userlist=favourites_list, object_id=authorid)
    userlistitem.delete()

    content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOKAUTHOR_ID)
    favourite_sum, _ = FavoriteSum.objects.get_or_create(content_type=content_type, object_id=authorid)
    favourite_sum.favorite_count -= 1
    favourite_sum.save()
    
    return redirect("author_detail", author_url=author.url)

