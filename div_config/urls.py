"""divdb URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from div_content import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView 
#from .views import SignUpView, Editace, RegisterView, ProfileUpdateView

urlpatterns = [
#    path("divconfig/", include("divconfig.urls")),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
#    path("register", views.register_request, name="register"),
    path("login", views.login_request, name="login"),
#    path('registrace/', RegisterView.as_view(), name='register')
#    path('profil/upravit/', ProfileUpdateView.as_view(), name='edit_profile'),
    path('<str:article_url>', views.article_detail, name='article_detail'),

    path('filmy/', views.movies, name='movies_index'),
    path('filmy/<int:year>', views.movies, name='movies_year'),
    path('filmy/<slug:genre_url>', views.movies, name='movies_genre'),
#    path('filmy/<str:genre_name>' views.genre_view, name='genre_view'),
#    path('filmy/<int:year>', views.year_view, name='year_view'),
    path('film/<str:movie_url>', views.movie_detail, name='movie_detail'),

    path('knihy/', views.books, name='books_index'),
    path('kniha/<str:book_url>', views.book_detail, name='book_detail'),
    path('hry/', views.games, name='games_index'),
    path('hra/<str:game_url>', views.game_detail, name='game_detail'),
    path('lokality/', views.locations, name='locations_index'),
    path('lokalita/<str:location_url>', views.location_detail, name='location_detail'),

    path('osobnost/', views.creators_list, name='creators_list'),
    path('osobnost/<int:creator_url>', views.creator_detail, name='creator_detail'),

    path('podminky-pouziti/', TemplateView.as_view(template_name='podminky-pouziti.html'), name='podminky-pouziti'),
    path('ochrana-osobnich-udaju/', TemplateView.as_view(template_name='ochrana-osobnich-udaju.html'), name='ochrana-osobnich-udaju'),

#    path('clanky/', views.clanky, name='clanky'),
#    path('<str:url_clanku>', views.clanek_detail, name='clanek_detail'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
#        path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
