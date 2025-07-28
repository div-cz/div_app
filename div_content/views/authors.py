# -------------------------------------------------------------------
#                    VIEWS.AUTHORS.PY
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
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import OuterRef, Exists
from django.contrib.contenttypes.models import ContentType
from div_content.models import (
    Book, Bookauthor, Bookwriters, Userlisttype, Userlist, Userlistitem, Userlisttype, FavoriteSum
)
from div_content.forms.creators import Creatorbiography
from django.contrib.auth.decorators import login_required


# Konstanty - Userlisttype, django_content_type
USERLISTTYPE_FAV_AUTHOR_ID = 23 # Oblíbený spisovatel
USERLISTTYPE_READLIST_ID = 6 # Přečteno

#CONTENT_TYPE_BOOKAUTHOR_ID = 10
#CONTENT_TYPE použit v books, movies, authors, characters, series, creators
bookauthor_content_type = ContentType.objects.get_for_model(Bookauthor)
CONTENT_TYPE_BOOKAUTHOR_ID = bookauthor_content_type.id


def authors_list(request):
    # Získání seznamu všech autorů
    authors = Bookauthor.objects.all()  
    return render(request, 'creators/authors_list.html', {'authors': authors})


def author_detail(request, author_url):
    # Zobrazení detailu jednoho autora
    author = get_object_or_404(Bookauthor, url=author_url) 
    user = request.user

    # Definujeme seznam ID knih autora (přes Bookwriters)
    book_ids = Bookwriters.objects.filter(author=author).values_list('book', flat=True)

    if user.is_authenticated:
        read_list_items = Userlistitem.objects.filter(
            userlist__user=user,
            userlist__listtype_id=USERLISTTYPE_READLIST_ID,
            object_id=OuterRef("bookid")
        )

        books = Book.objects.filter(bookid__in=book_ids).annotate(
            is_read=Exists(read_list_items)
        ).order_by("-year")
    else:
        books = Book.objects.filter(bookid__in=book_ids).order_by("-year")




    #Výpis knih podle sérií
    series_books = {}
    non_series_books = []
    
    for book in books:
        if book.universumid:
            universum_id = book.universumid.universumid
            if universum_id not in series_books:
                series_books[universum_id] = {
                    'series': book.universumid,
                    'name': book.universumid.universumnamecz or book.universumid.universumname,
                    'books': []
                }
            series_books[universum_id]['books'].append(book)
        else:
            non_series_books.append(book)


        
    author_list_10 = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]
    author_list_10_minus = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]


    # Zjistí zda je autor v seznamu oblíbených u přihlášeného uživatele   
    if user.is_authenticated:
        try:
            favourites_type = Userlisttype.objects.get(userlisttypeid=USERLISTTYPE_FAV_AUTHOR_ID)
            favourites_list = Userlist.objects.get(user=user, listtype=favourites_type)
            is_favorite = Userlistitem.objects.filter(object_id=author.authorid, userlist=favourites_list).exists()
        except Exception as e:
            is_favorite = False
    else:
        is_favorite = False

    # Získá fanoušky spisovatele na základě filtrování z Userlistitem
    content_type = ContentType.objects.get(id=CONTENT_TYPE_BOOKAUTHOR_ID)
    fans = Userlistitem.objects.filter(
        object_id=author.authorid,
        content_type=content_type
    ).select_related("userlist")


    #TEST Martin
    #'author_list_10': Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10],
    return render(request, 'creators/author_detail.html', {
        'author': author, 
        'books': books, 
        'series_books': series_books,
        'non_series_books': non_series_books,
        'has_series': bool(series_books),
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

