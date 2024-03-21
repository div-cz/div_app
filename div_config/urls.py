"""
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
#from div_content import views
#from div_content.views import articles, books, creators, games, locations, movies, users
from div_content.views.articles import article_detail
from div_content.views.authors import authors_list, author_detail, author_add
from div_content.views.books import book_add, book_detail, books, books_search
from div_content.views.creators import creator_detail, creators_list
from div_content.views.games import game_detail, game_add, games
from div_content.views.locations import locations, location_detail
from div_content.views.movies import redirect_view, movie_detail, movies, index, search, MovieDetailView
from div_content.views.users import contact_form, myuser_detail, rate_movie, add_to_list, ratings_profile, favorites_profile, iwantsee_profile, favorite_movies, rated_media, rated_movies, rated_books, rated_games, favorite_media, favorite_actors, favorite_books, favorite_drinks, favorite_foods, favorite_games, favorite_items, favorite_locations, user_lists, update_profile
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from allauth.account.views import SignupView, LogoutView, LoginView
#from . import views



#from .views import SignUpView, Editace, RegisterView, ProfileUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('podpora/', redirect_view),
    path('', index, name='index'),
    path('filmy/', movies, name='movies_index'),
    path('filmy/<int:year>', movies, name='movies_year'),
    path('filmy/<slug:genre_url>', movies, name='movies_genre'),

    path('film/<str:movie_url>', movie_detail, name='movie_detail'),
    path('film/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),
    path('film/<int:pk>/rate/', rate_movie, name='movie_rate'),
    path('film/add-to-list/', add_to_list, name='add_to_list'),

    path('hry/', games, name='games_index'),
    path('hra/<str:game_url>', game_detail, name='game_detail'),
    path('hra/pridat/', game_add, name='game_add'),

    path('knihy/', books, name='books_index'),
    path('hledani-knih/', books_search, name='books_search'),
    path('kniha/<str:book_url>', book_detail, name='book_detail'),
    path('knihy/pridat/', book_add, name='book_add'),
    path('spisovatele/', authors_list, name='authors_list'),
    path('spisovatel/<str:author_url>', author_detail, name='author_detail'), 
    path('spisovatel/pridat/', author_add, name='author_add'),


    path('lokality/', locations, name='locations_index'),
    path('lokalita/<str:location_url>', location_detail, name='location_detail'),
    path('osobnosti/', creators_list, name='creators_list'),
    path('osobnost/<str:creator_url>', creator_detail, name='creator_detail'),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('hledam/', search, name='search'),
    path('<str:article_url>', article_detail, name='article_detail'),

    path('uzivatel/<int:user_id>/', myuser_detail, name='user_profile_with_profil'),

    path('ucet/', myuser_detail, name='myuser_detail'),
    path('ucet/hodnoceni/', rated_media, name='rated_media'),
    path('ucet/hodnoceni/filmy/', rated_movies, name='rated_movies'),
    path('ucet/hodnoceni/knihy/', rated_books, name='rated_books'),
    path('ucet/hodnoceni/hry/', rated_games, name='rated_games'),
    
    
    path('ucet/oblibene/', favorites_profile, name='favorites_media'),
    path('ucet/oblibene/herci/', favorite_actors, name='favorite_actors'),
    path('ucet/oblibene/knihy/', favorite_books, name='favorite_books'),
    path('ucet/oblibene/hry/', favorite_games, name='favorite_games'),
    path('ucet/oblibene/lokality/', favorite_locations, name='favorite_locations'),
    path('ucet/oblibene/napoje/', favorite_drinks, name='favorite_drinks'),
    path('ucet/oblibene/jidlo/', favorite_foods, name='favorite_foods'),
    path('ucet/oblibene/predmety/', favorite_items, name='favorite_items'),


    path('ucet/upravit/', update_profile, name='update_profile'),

    path('ucet/seznamy/', user_lists, name='user_lists'),
    path('ucet/seznamy/oblibene/', favorites_profile, name='favorites_media'),
    path('ucet/seznamy/chci-videt/', iwantsee_profile, name='iwantsee_profile'),
        
    path('kontakt/', contact_form, name='contact'),
    path('prihlaseni/', LoginView.as_view(), name='login'),
    path('registrace/', SignupView.as_view(), name='signup'),
    path('odhlaseni/', LogoutView.as_view(), name='logout'),

    path('ucet/', include('allauth.urls')),
]#    path('ucet/hodnoceni/', views.ratings_profile, name='ratings_profile'),
#    path('ucet/tochcividet/', users.iwantsee_profile, name='iwantsee_profile'),

#    path('registrace/', include('allauth.urls')),  predelat na redirect
"""    path('ucet/', include('allauth.urls')),
    path('ucet/ohodnocene/', views.rated_media, name='rated_media'),
    path('ucet/ohodnocene/<str:media_type>/', views.rated_specific_media, name='rated_specific_media'), # Zkonsolidovane
"""

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
#        path(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)