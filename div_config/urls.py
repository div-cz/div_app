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
#from django.contrib import admin
#from django.urls import path, include
#from div_content import views
#from div_content.views import articles, books, creators, games, locations, movies, users
#from div_content.views.articles import article_detail
#from div_content.views.authors import authors_list, author_detail, author_add
#from div_content.views.books import book_add, book_detail, books, books_search
#from div_content.views.creators import creator_detail, creators_list
#from div_content.views.games import game_detail, game_add, games
#from div_content.views.locations import locations, location_detail
#from div_content.views.movies import movie_detail, movies, index, search, MovieDetailView
#from div_content.views.users import contact_form, myuser_detail, rate_movie, add_to_list, ratings_profile, favorites_profile, iwantsee_profile, favorite_movies, rated_media, rated_movies, rated_books, rated_games, favorite_media, favorite_actors, favorite_books, favorite_drinks, favorite_foods, favorite_games, favorite_items, favorite_locations, user_lists, update_profile
from django.conf import settings
from django.conf.urls.static import static
#from django.views.generic import TemplateView 
#from django.contrib.auth import views as auth_views
#from allauth.account import views as allauth_views
#from allauth.account.views import SignupView, LogoutView, LoginView
#from . import views


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('div_api.urls')),
]


if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)