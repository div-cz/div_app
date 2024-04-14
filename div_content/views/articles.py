# VIEWS.ARTICLES.PY

from django.shortcuts import get_object_or_404, render
from div_content.models import Article, Movie



def article_detail(request, article_url):
    article = get_object_or_404(Article, url=article_url)
    movie_list_6 = Movie.objects.filter(special=1).order_by('-popularity')[:6]
    article_list = Article.objects.filter(typ='Článek').order_by('-id')[:6]
    return render(request, 'articles/article_detail.html', {'article': article, 'movie_list_6': movie_list_6, 'article_list': article_list})




def article_index(request):
    # Vybere poslední tři články typu "Článek", řazené podle data vytvoření sestupně
    latest_articles = Article.objects.filter(typ='Článek').order_by('-created')[:3]

    # Předání článků do šablony
    return render(request, 'index.html', {'latest_articles': latest_articles})
