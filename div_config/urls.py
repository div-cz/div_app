""" žlutá
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
from div_content.views.blog import blog_add_post, blog_detail, blog_index, blog_list, blog_new, blog_post_detail, blog_section_detail
from div_content.views.books import (
    book_add, book_detail, books, books_search, add_to_favourite_books, add_to_readlist, add_to_read_books, add_to_book_library,
    remove_from_favourites_books, remove_from_readlist, remove_from_read_books, remove_from_book_library
    )
from div_content.views.creators import creator_detail, creators_list
from div_content.views.forum import (
    forum, forum_section_detail, create_new_topic, forum_topic_detail, comment_edit, comment_delete, comment_reply, forum_search
    )
from div_content.views.games import game_detail, game_add, games
from div_content.views.characters import character_list, character_detail
from div_content.views.index import index, movies

from div_content.views.locations import locations, location_detail
from div_content.views.movies import (
    redirect_view, movie_detail, search, MovieDetailView, add_to_favourites, add_to_watchlist, add_to_watched, 
    remove_from_favourites, remove_from_watchlist, remove_from_watched, add_to_movie_library, remove_from_movie_library
    )
from div_content.views.users import contact_form, myuser_detail, rate_movie, add_to_list, ratings_profile, favorites_profile, iwantsee_profile, favorite_movies, rated_media, rated_movies, rated_books, rated_games, favorite_media, favorite_actors, favorite_books, favorite_drinks, favorite_foods, favorite_games, favorite_items, favorite_locations, user_lists, update_profile
from div_content.views.series import tv, tv_detail
from div_content.views.tv import tv, tv_detail
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

    path('blog/', blog_list, name='blog_list'),  
    path('blogy/', blog_index, name='blog_index'),
    path('blogy/<str:section>-blogy', blog_section_detail, name='blog_section_detail'),
    path('blog/novy-blog', blog_new, name='blog_new'),
    path('blog/novy-prispevek', blog_add_post, name='blog_add_post'),
    path('blog/<slug:slug>', blog_detail, name='blog_detail'),
    path('blog/<slug:blog_slug>/<slug:post_slug>/', blog_post_detail, name='blog_post_detail'),

    path('podpora/', redirect_view),
    path('', index, name='index'),
    path('filmy/', movies, name='movies_index'),
    path('filmy/<int:year>', movies, name='movies_year'),
    path('filmy/<slug:genre_url>', movies, name='movies_genre'),

    path('film/pridat-do-oblibenych-<int:movieid>', add_to_favourites, name="add_to_favourites"),
    path('film/chci-videt-<int:movieid>', add_to_watchlist, name="add_to_watchlist"),
    path('film/shlednuto-<int:movieid>', add_to_watched, name="add_to_watched"),
    path('film/do-filmoteky-<int:movieid>', add_to_movie_library, name="add_to_movie_library"),

    path('film/odebrat-z-oblibenych-<int:movieid>', remove_from_favourites, name='remove_from_favourites'),
    path('film/odebrat-ze-chci-videt-<int:movieid>', remove_from_watchlist, name='remove_from_watchlist'),
    path('film/odebrat-ze-shlednuto-<int:movieid>', remove_from_watched, name='remove_from_watched'),
    path('film/odebrat-z-filmoteky-<int:movieid>', remove_from_movie_library, name='remove_from_movie_library'),

    path('film/<str:movie_url>', movie_detail, name='movie_detail'),
    path('film/<int:pk>/', MovieDetailView.as_view(), name='movie_detail'),
    path('film/<int:pk>/rate/', rate_movie, name='movie_rate'),
    path('film/add-to-list/', add_to_list, name='add_to_list'),


    path('forum/', forum, name='forum'),   
    path('forum/vyhledavani', forum_search, name='forum_search'),   
    path('forum/<slug:slug>', forum_section_detail, name='forum_section_detail'),   
    path('forum/<slug:slug>/pridat-prispevek', create_new_topic, name='create_new_topic'),   
    path('forum/<slug:slug>/<slug:topicurl>', forum_topic_detail, name='forum_topic_detail'),   
    path('forum/<slug:slug>/<slug:topicurl>/upravit-<int:forumcommentid>', comment_edit, name='comment_edit'),   
    path('forum/<slug:slug>/<slug:topicurl>/smazat-<int:forumcommentid>', comment_delete, name='comment_delete'),   
    path('forum/<slug:slug>/<slug:topicurl>/odpovedet-<int:forumcommentid>', comment_reply, name='comment_reply'), 


    path('serialy/', tv, name='tv_index'),
    path('serial/<str:tv_url>', tv_detail, name='tv_detail'),

    path('tv/', tv, name='tv_index'),
    path('tv/<str:tv_url>', tv_detail, name='tv_detail'),


    path('hry/', games, name='games_index'),
    path('hra/<str:game_url>', game_detail, name='game_detail'),
    path('hra/pridat/', game_add, name='game_add'),
    path('hra/add-to-list/', add_to_list, name='add_to_list'),


    path('autori/', authors_list, name='authors_list'),
    path('autor/<str:author_url>', author_detail, name='author_detail'), 
    path('autor/pridat/', author_add, name='author_add'),
    
    path('knihy/', books, name='books_index'),
    path('hledani-knih/', books_search, name='books_search'),

    path('kniha/pridat-do-oblibenych-<int:bookid>', add_to_favourite_books, name="add_to_favourite_books"),
    path('kniha/chci-cist-<int:bookid>', add_to_readlist, name="add_to_readlist"),
    path('kniha/precteno-<int:bookid>', add_to_read_books, name="add_to_read_books"),
    path('kniha/do-knihovny-<int:bookid>', add_to_book_library, name="add_to_book_library"),

    path('kniha/odebrat-z-oblibenych-<int:bookid>', remove_from_favourites_books, name="remove_from_favourites_books"),
    path('kniha/odebrat-z-chci-cist-<int:bookid>', remove_from_readlist, name="remove_from_readlist"),
    path('kniha/odebrat-z-precteno-<int:bookid>', remove_from_read_books, name="remove_from_read_books"),
    path('kniha/odebrat-z-knihovny-<int:bookid>', remove_from_book_library, name="remove_from_book_library"),

    path('kniha/<str:book_url>', book_detail, name='book_detail'),
    path('knihy/pridat/', book_add, name='book_add'),


    path('spisovatele/', authors_list, name='authors_list'),
    path('spisovatel/<str:author_url>', author_detail, name='author_detail'), 
    path('spisovatel/pridat/', author_add, name='author_add'),


    path('lokality/', locations, name='locations_index'),
    path('lokalita/<str:location_url>', location_detail, name='location_detail'),
    path('osobnosti/', creators_list, name='creators_list'),
    path('osobnost/<str:creator_url>', creator_detail, name='creator_detail'),
    path('postavy/', character_list, name='character_list'),
    path('postava/<str:character_url>', character_detail, name='character_detail'),

    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('hledam/', search, name='search'),
    path('<str:article_url>', article_detail, name='article_detail'),


    path('tvurci/', creators_list, name='creators_list'),
    path('tvurce/<str:creator_url>', creator_detail, name='creator_detail'),
    
    
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
]
#    path('ucet/hodnoceni/', views.ratings_profile, name='ratings_profile'),
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