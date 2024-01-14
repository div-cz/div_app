# VIEWS.AUTHORS.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Bookauthor

def authors_list(request):
    # Získání seznamu všech autorů
    authors = Bookauthor.objects.all()  
    return render(request, 'creators/authors_list.html', {'authors': authors})

def author_detail(request, author_url):
    # Zobrazení detailu jednoho autora
    author = get_object_or_404(Bookauthor, url=author_url) 
        
    author_list_10 = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]
    author_list_10_minus = Bookauthor.objects.values('firstname', 'lastname', 'url', 'birthyear')[:10]

    return render(request, 'creators/author_detail.html', {'author': author, 'author_list_10': author_list_10, 'author_list_10_minus': author_list_10_minus})

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
