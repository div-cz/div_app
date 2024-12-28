# VIEWS.ARTICLES.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Article, Movie
from div_content.views.login import custom_login_view



def article_detail(request, article_url):
    article = get_object_or_404(Article, url=article_url)
    movie_list_6 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
    article_list = Article.objects.filter(typ='Článek').order_by('-id')[:6]
    return render(request, 'articles/article_detail.html', {'article': article, 'movie_list_6': movie_list_6, 'article_list': article_list})




def articles_index(request):
    latest_articles = Article.objects.filter(typ='Článek').order_by('-created')[:10]
    sections = [
        {'name': 'Filmové články', 'url': 'filmy'},
        {'name': 'Knižní články', 'url': 'knihy'},
        {'name': 'Herní články', 'url': 'hry'},
        {'name': 'Seriálové články', 'url': 'serialy'},
    ]
    return render(request, 'articles/articles_index.html', {'latest_articles': latest_articles, 'sections': sections})



def articles_list(request, category):
    category_map = {
        'filmy': ('Movie', 'filmové'),
        'knihy': ('Book', 'knižní'),
        'hry': ('Game', 'herní'),
        'serialy': ('General', 'seriálové'),
    }

    category_data = category_map.get(category.lower())
    if not category_data:
        return render(request, '404.html', status=404)

    category_type, category_name = category_data

    articles = Article.objects.filter(typ=category_type).order_by('-created')[:10]

    return render(request, 'articles/articles_list.html', {
        'articles': articles,
        'category': category_name,
    })
