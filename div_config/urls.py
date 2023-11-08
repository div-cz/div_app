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
from div_content.views import articles, books, creators, games, locations, movies, users
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
    path('', movies.index, name='index'),
    path('filmy/', movies.movies, name='movies_index'),
    path('filmy/<int:year>', movies.movies, name='movies_year'),
    path('filmy/<slug:genre_url>', movies.movies, name='movies_genre'),



    path('film/<str:movie_url>', movies.movie_detail, name='movie_detail'),
    path('film/<int:pk>/', movies.MovieDetailView.as_view(), name='movie_detail'),
    path('film/<int:pk>/rate/', users.rate_movie, name='movie_rate'),
    path('film/add-to-list/', users.add_to_list, name='add_to_list'),
    path('hry/', games.games, name='games_index'),
    path('hra/<str:game_url>', games.game_detail, name='game_detail'),
    path('knihy/', books.books, name='books_index'),
    path('kniha/<str:book_url>', books.book_detail, name='book_detail'),
    path('lokality/', locations.locations, name='locations_index'),
    path('lokalita/<str:location_url>', locations.location_detail, name='location_detail'),
    path('osobnosti/', creators.creators_list, name='creators_list'),
    path('osobnost/<str:creator_url>', creators.creator_detail, name='creator_detail'),
    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('hledam/', movies.search, name='search'),
    path('<str:article_url>', articles.article_detail, name='article_detail'),

    path('uzivatel/<int:user_id>/', users.myuser_detail, name='user_profile_with_profil'),

    path('ucet/', users.myuser_detail, name='myuser_detail'),
    path('ucet/hodnoceni/', users.rated_media, name='rated_media'),
    path('ucet/hodnoceni/filmy/', users.rated_movies, name='rated_movies'),
    path('ucet/hodnoceni/knihy/', users.rated_books, name='rated_books'),
    path('ucet/hodnoceni/hry/', users.rated_games, name='rated_games'),
    
    
    path('ucet/oblibene/', users.favorites_profile, name='favorites_media'),
    path('ucet/oblibene/herci/', users.favorite_actors, name='favorite_actors'),
    path('ucet/oblibene/knihy/', users.favorite_books, name='favorite_books'),
    path('ucet/oblibene/hry/', users.favorite_games, name='favorite_games'),
    path('ucet/oblibene/lokality/', users.favorite_locations, name='favorite_locations'),
    path('ucet/oblibene/napoje/', users.favorite_drinks, name='favorite_drinks'),
    path('ucet/oblibene/jidlo/', users.favorite_foods, name='favorite_foods'),
    path('ucet/oblibene/predmety/', users.favorite_items, name='favorite_items'),
    

    path('ucet/tochcividet/', users.iwantsee_profile, name='iwantsee_profile'),
    path('ucet/upravit/', users.update_profile, name='update_profile'),

    path('ucet/seznamy/', users.user_lists, name='user_lists'),
    path('ucet/seznamy/oblibene/', users.favorites_profile, name='favorites_media'),
    path('ucet/seznamy/chci-videt/', users.wantsee_movies, name='user_lists_iwantsee'),
        
    path('prihlaseni/', LoginView.as_view(), name='login'),
    path('registrace/', SignupView.as_view(), name='signup'),
    path('odhlaseni/', LogoutView.as_view(), name='logout'),

    path('ucet/', include('allauth.urls')),
]#    path('ucet/hodnoceni/', views.ratings_profile, name='ratings_profile'),

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