""" URLS.PY TEST
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
from div_content.views.admins import admin_index, admin_comments, admin_edit_comment, admin_tasks, admin_task_detail, admin_task_edit #admin_task_new, 
from div_content.views.articles import article_detail, articles_index, articles_list
from div_content.views.authors import (
    authors_list, author_detail, author_add, add_to_favourite_authors, remove_from_favourite_authors
    )
from div_content.views.blog import blog_add_post, blog_detail, blog_index, blog_list, blog_new, blog_post_detail, blog_section_detail

from div_content.views.books import (
    book_add, book_detail, books, books_search, add_to_favourite_books, add_to_readlist, add_to_read_books, 
    add_to_book_library, rate_book, ratequote, remove_from_favourites_books, remove_from_readlist, remove_from_read_books, 
    remove_from_book_library, character_list_ajax, set_reading_goal, books_alphabetical, 
    book_listings, listing_detail
    )
from div_content.views.creators import (
    creator_detail, creators_list, toggle_favorite, add_creator_to_favourites, remove_creator_from_favourites
    )
from div_content.views.forum import (
    forum, forum_section_detail, create_new_topic, forum_topic_detail, comment_edit, comment_delete, comment_reply, forum_search
    )
from div_content.views.eshop import eshop_list, eshop_books, eshop_movies, eshop_games, eshop_detail
#from div_content.views.eshop import eshop
from div_content.views.games import (
    game_detail, game_add, games, add_to_favourite_games, rate_game, developer_list_ajax, platform_list_ajax, publisher_list_ajax, country_list_ajax, universum_list_ajax, 
    remove_from_favourite_games, 
    add_to_playlist_games, remove_from_playlist_games, add_to_played, remove_from_played,
    add_to_game_library, remove_from_game_library, 
    publishers_list, games_by_developer, games_by_publisher, games_by_genre, games_by_year, games_alphabetical, games_genres
    )
from div_content.views.characters import (
    add_character_to_favorites, character_list, character_detail, remove_character_from_favorites
    )
from div_content.views.index import index, movies, our_team, series_genre, series_year

from div_content.views.locations import locations, location_detail

from div_content.views.movies import (
    movies_alphabetical, redirect_view, movie_detail, search, MovieDetailView, add_to_favourites, add_to_watchlist, add_to_watched, 
    remove_from_favourites, remove_from_watchlist, remove_from_watched, add_to_movie_library, remove_from_movie_library
    )
from div_content.views.universum import universum_detail, universum_list
from div_content.views.users import (
    contact_form, myuser_detail, rate_movie, add_to_list, ratings_profile, favorites_profile, iwantsee_profile, 
    watched_profile, favorite_movies, rated_media, rated_movies, rated_books, rated_games, favorite_media, 
    favorite_actors, favorite_books, favorite_drinks, favorite_foods, favorite_games, favorite_items, favorite_locations, 
    profile_books_section, profile_games_section, profile_movies_section, profile_series_section, profile_stats_section, profile_show_case, user_lists, 
    update_profile, review_profile, chat, add_to_favorite_users, remove_from_favorite_users, chat_message, load_older_messages, 
    user_book_listings, user_sell_listings, user_buy_listings
    )
from div_content.views.charts import (
    award_detail, charts_index, charts_books, charts_games, charts_movies, charts_users, awards_index, awards_movies, 
    awards_books, awards_games
)
from div_content.views.series import (
    rate_tvshow, serie_detail, series_list, serie_season, search_tvshow, serie_episode, add_to_favourite_tvshow, 
    add_to_tvshow_library, add_to_tvshow_watchlist, add_to_watched_tvshows, remove_from_favourite_tvshow, 
    remove_from_tvshow_library, remove_from_tvshow_watchlist, remove_from_watched_tvshows, add_to_favourite_tvseason,
    add_to_tvseason_watchlist, add_to_watched_tvseasons, remove_from_favourite_tvseasons, remove_from_tvseason_watchlist,
    remove_from_watched_tvseasons, add_to_favourite_tvepisodes, add_to_tvepisode_watchlist, add_to_watched_tvepisode, 
    remove_from_favourite_tvepisodes, remove_from_tvepisode_watchlist, remove_from_watched_tvepisodes, series_alphabetical
)
from div_content.views.tv import tv, tv_detail

from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView 
from django.contrib.auth import views as auth_views
from allauth.account import views as allauth_views
from allauth.account.views import SignupView, LogoutView, LoginView
#from div_content.views.testmovies import my_view
#from . import views 



#from .views import SignUpView, Editace, RegisterView, ProfileUpdateView

urlpatterns = [

    path('spravce/', admin_index, name='admin_index'),
    path('spravce/sprava-komentaru', admin_comments, name='admin_comments'),
    path('spravce/upravit-komentar/<int:commentid>/', admin_edit_comment, name='admin_edit_comment'),

    path('spravce/ukoly/', admin_tasks, name='admin_tasks'),
    path('spravce/ukol/<int:task_id>/', admin_task_detail, name='admin_task_detail'),
    path('spravce/ukol/<int:task_id>/edit/', admin_task_edit, name='admin_task_edit'),
    path('spravce/ukol/novy/', admin_task_edit, name='admin_task_create'),


    path('eshop/', eshop_list, name='eshop_list'),
    path('eshop/knihy/', eshop_books, name='eshop_books'),
    path('eshop/filmy/', eshop_movies, name='eshop_movies'),
    path('eshop/hry/', eshop_games, name='eshop_games'),
    path('eshop/<int:item_id>/', eshop_detail, name='eshop_detail'),

    path('forum/', forum, name='forum'),   
    path('forum/vyhledavani', forum_search, name='forum_search'),   
    path('forum/<slug:slug>', forum_section_detail, name='forum_section_detail'),   
    path('forum/<slug:slug>/pridat-prispevek', create_new_topic, name='create_new_topic'),   
    path('forum/<slug:slug>/<slug:topicurl>', forum_topic_detail, name='forum_topic_detail'),   
    path('forum/<slug:slug>/<slug:topicurl>/upravit-<int:forumcommentid>', comment_edit, name='comment_edit'),   
    path('forum/<slug:slug>/<slug:topicurl>/smazat-<int:forumcommentid>', comment_delete, name='comment_delete'),   
    path('forum/<slug:slug>/<slug:topicurl>/odpovedet-<int:forumcommentid>', comment_reply, name='comment_reply'),   

    path('blog/', blog_list, name='blog_list'),  
    path('blogy/', blog_index, name='blog_index'),
    path('blogy/<str:section>-blogy', blog_section_detail, name='blog_section_detail'),
    path('blog/novy-blog', blog_new, name='blog_new'),
    path('blog/novy-prispevek', blog_add_post, name='blog_add_post'),
    path('blog/<slug:slug>', blog_detail, name='blog_detail'),
    path('blog/<slug:blog_slug>/<slug:post_slug>/', blog_post_detail, name='blog_post_detail'),


    path('admin/', admin.site.urls),
    path('podpora/', redirect_view),
    path('', index, name='index'),
    path('filmy/', movies, name='movies_index'),
    path('filmy/<int:year>', movies, name='movies_year'),
    path('filmy/<slug:genre_url>', movies, name='movies_genre'),
    path('filmy/abecedne/', movies_alphabetical, {'letter': 'A'}, name='movies_alphabetical_default'),
    path('filmy/abecedne/<str:letter>', movies_alphabetical, name='movies_alphabetical'),


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
  

    path('serial/pridat-do-oblibenych-<int:tvshowid>', add_to_favourite_tvshow, name="add_to_favourite_tvshow"),
    path('serial/chci-videt-<int:tvshowid>', add_to_tvshow_watchlist, name="add_to_tvshow_watchlist"),
    path('serial/serialnuto-<int:tvshowid>', add_to_watched_tvshows, name="add_to_watched_tvshows"),
    path('serial/do-serialoteky-<int:tvshowid>', add_to_tvshow_library, name="add_to_tvshow_library"),

    path('serial/odebrat-z-oblibenych-<int:tvshowid>', remove_from_favourite_tvshow, name='remove_from_favourite_tvshow'),
    path('serial/odebrat-ze-chci-videt-<int:tvshowid>', remove_from_tvshow_watchlist, name='remove_from_tvshow_watchlist'),
    path('serial/odebrat-ze-serialnuto-<int:tvshowid>', remove_from_watched_tvshows, name='remove_from_watched_tvshows'),
    path('serial/odebrat-ze-serialoteky-<int:tvshowid>', remove_from_tvshow_library, name='remove_from_tvshow_library'),

    path('serial/<str:tv_url>/pridat-do-oblibenych-<int:tvseasonid>', add_to_favourite_tvseason, name="add_to_favourite_tvseason"),
    path('serial/<str:tv_url>/chci-videt-<int:tvseasonid>', add_to_tvseason_watchlist, name="add_to_tvseason_watchlist"),
    path('serial/<str:tv_url>/shlednuto-<int:tvseasonid>', add_to_watched_tvseasons, name="add_to_watched_tvseasons"),

    path('serial/<str:tv_url>/odebrat-z-oblibenych-<int:tvseasonid>', remove_from_favourite_tvseasons, name='remove_from_favourite_tvseasons'),
    path('serial/<str:tv_url>/odebrat-ze-chci-videt-<int:tvseasonid>', remove_from_tvseason_watchlist, name='remove_from_tvseason_watchlist'),
    path('serial/<str:tv_url>/odebrat-ze-shlednuto-<int:tvseasonid>', remove_from_watched_tvseasons, name='remove_from_watched_tvseasons'),

    path('serial/<str:tv_url>/<str:seasonurl>/pridat-do-oblibenych-<int:tvepisodeid>', add_to_favourite_tvepisodes, name="add_to_favourite_tvepisodes"),
    path('serial/<str:tv_url>/<str:seasonurl>/chci-videt-<int:tvepisodeid>', add_to_tvepisode_watchlist, name="add_to_tvepisode_watchlist"),
    path('serial/<str:tv_url>/<str:seasonurl>/shlednuto-<int:tvepisodeid>', add_to_watched_tvepisode, name="add_to_watched_tvepisode"),

    path('serial/<str:tv_url>/<str:seasonurl>/odebrat-z-oblibenych-<int:tvepisodeid>', remove_from_favourite_tvepisodes, name='remove_from_favourite_tvepisodes'),
    path('serial/<str:tv_url>/<str:seasonurl>/odebrat-ze-chci-videt-<int:tvepisodeid>', remove_from_tvepisode_watchlist, name='remove_from_tvepisode_watchlist'),
    path('serial/<str:tv_url>/<str:seasonurl>/odebrat-ze-shlednuto-<int:tvepisodeid>', remove_from_watched_tvepisodes, name='remove_from_watched_tvepisodes'),



    path('serialy/', series_list, name='series_list'),
    path('serialy/abecedne/', series_alphabetical, name='series_alphabetical'),
    path('serialy/<int:year>', series_year, name='series_year'),
    path('serialy/<slug:genre_url>', series_genre, name='series_genre'),


    path('serial/<str:tv_url>', serie_detail, name='serie_detail'),
    path('serial/<str:tv_url>/rate/', rate_tvshow, name='rate_tvshow'),
    path('serial/<str:tv_url>/<str:seasonurl>/', serie_season, name='serie_season'),
    path('serial/<str:tv_url>/<str:seasonurl>/<str:episodeurl>/', serie_episode, name='serie_episode'),

    path('tv/', tv, name='tv_index'),
    path('tv/<str:tv_url>', tv_detail, name='tv_detail'),


    path('hry/', games, name='games_index'),
    path('hry/abecedne/', games_alphabetical, name='games_alphabetical'),
    path('hry/vydavatele/', publishers_list, name='publishers_list'),
    path('hry/vydavatel/<str:publisher_url>', games_by_publisher, name='games_by_publisher'),
    path('hry/vyvojar/<str:developer_url>', games_by_developer, name='games_by_developer'),
    path('hry/zanry/', games_genres, name='games_genres'),
    path('hry/zanr/<str:genre_url>', games_by_genre, name='games_by_genre'),
    path('hry/rok/<int:year>', games_by_year, name='games_by_year'),



    path('hra/pridat-do-oblibenych-<int:gameid>', add_to_favourite_games, name="add_to_favourite_games"),
    path('hra/chci-hrat-<int:gameid>', add_to_playlist_games, name="add_to_playlist_games"),
    path('hra/odehrano-<int:gameid>', add_to_played, name="add_to_played"),
    path('hra/do-gamoteky-<int:gameid>', add_to_game_library, name="add_to_game_library"),
        
    path('hra/odebrat-z-oblibenych-<int:gameid>', remove_from_favourite_games, name="remove_from_favourite_games"),
    path('hra/odebrat-z-chci-hrat-<int:gameid>', remove_from_playlist_games, name="remove_from_playlist_games"),
    path('hra/odebrat-z-odehrano-<int:gameid>', remove_from_played, name="remove_from_played"),
    path('hra/odebrat-z-gamoteky-<int:gameid>', remove_from_game_library, name="remove_from_game_library"),

    path('hra/<str:game_url>', game_detail, name='game_detail'),
    path('hra/pridat/', game_add, name='game_add'),
    path('hra/add-to-list/', add_to_list, name='add_to_list'),
    path('hra/<int:game_id>/rate/', rate_game, name='rate_game'),

    path('hra/ajax/developers/', developer_list_ajax, name='ajax_developers'),
    path('hra/ajax/platforms/', platform_list_ajax, name='ajax_platforms'),
    path('hra/ajax/publishers/', publisher_list_ajax, name='ajax_publishers'),
    path('hra/ajax/countries/', country_list_ajax, name='ajax_countries'),
    path('hra/ajax/universes/', universum_list_ajax, name='ajax_universes'),


    path('autori/', authors_list, name='authors_list'),
    path('autor/pridat-do-oblibenych-<int:authorid>', add_to_favourite_authors, name='add_to_favourite_authors'),
    path('autor/odebrat-z-oblibenych-<int:authorid>', remove_from_favourite_authors, name='remove_from_favourite_authors'),
    path('autor/<str:author_url>', author_detail, name='author_detail'), 
   
    path('autor/pridat/', author_add, name='author_add'),
    path('knihy/', books, name='books_index'),
    path('knihy/abecedne/', books_alphabetical, name='books_alphabetical'),
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
    path('kniha/<int:book_id>/rate/', rate_book, name='rate_book'),
    
    path('kniha/ajax/postava/', character_list_ajax, name='ajax_character_list'),
    path('set-reading-goal/', set_reading_goal, name='set_reading_goal'),

    # ANTIKVARIÁT
    path('kniha/<str:book_url>/nabidky/', book_listings, name='book_listings'),
    path('kniha/<str:book_url>/prodej/<int:listing_id>/', listing_detail, name='listing_detail'),
    path('kniha/<str:book_url>/poptavka/<int:listing_id>/', listing_detail, name='listing_detail'),
    path('uzivatel/<int:user_id>/prodej-knihy/', user_sell_listings, name='user_sell_listings'),
    path('uzivatel/<int:user_id>/koupim-knihy/', user_buy_listings, name='user_buy_listings'),
    path('uzivatel/<int:user_id>/nabidky/', user_book_listings, name='user_book_listings'),  # Přidáno

    # path('spisovatele/', authors_list, name='authors_list'),
    # path('spisovatel/<str:author_url>', author_detail, name='author_detail'), 
    # path('spisovatel/pridat/', author_add, name='author_add'),


    path('lokality/', locations, name='locations_index'),
    path('lokalita/<str:location_url>', location_detail, name='location_detail'),
    path('osobnosti/', creators_list, name='creators_list'),
    path('osobnost/<str:creator_url>', creator_detail, name='creator_detail'),
    path('postavy/', character_list, name='character_list'),

    path('postava/pridat-do-oblibenych<int:character_id>', add_character_to_favorites, name='add_character_to_favorites'),
    path('postava/odebrat-z-oblibenych-<int:character_id>', remove_character_from_favorites, name='remove_character_from_favorites'),
    path('postava/<str:character_url>', character_detail, name='character_detail'),


    path('quote/<int:quote_id>/rate/', ratequote, name='ratequote'),


    path('ratings/', include('star_ratings.urls', namespace='ratings')),
    path('hledam/', search, name='search'),
    path('hledam-serial/', search_tvshow, name='search_tvshow'),
    path('nas-tym/', our_team, name='our_team'),
    path('clanky/', articles_index, name='articles_index'),
    path('clanek/', articles_list, name='articles_list'),  
    path('<str:article_url>', article_detail, name='article_detail'),
    path('clanky/<str:category>/', articles_list, name='articles_list'),




    path('tvurci/', creators_list, name='creators_list'),
    path('tvurce/pridat-do-oblibenych-<int:creatorid>', add_creator_to_favourites, name='add_creator_to_favourites'),
    path('tvurce/odebrat-z-oblibenych-<int:creatorid>', remove_creator_from_favourites, name='remove_creator_from_favourites'),
    path('tvurce/<str:creator_url>', creator_detail, name='creator_detail'),
    
    
    path('uzivatel/<int:user_id>/', myuser_detail, name='user_profile_with_profil'),


    # OBLÍBENÉ

    path('toggle-favorite/', toggle_favorite, name='toggle_favorite'),
    


    path('svety/', universum_list, name='universum_list'),
    path('svet/<str:universum_url>', universum_detail, name='universum_detail'),


    # Můj profil - Dynamická sekce 
    path('uzivatel/', myuser_detail, name='myuser_detail'),
    path('uzivatel/<int:user_id>/', myuser_detail, name='myuser_detail'),
    path('uzivatel/<int:user_id>/filmy/', profile_movies_section, name='profile_movies_section'),
    path('uzivatel/<int:user_id>/serialy/', profile_series_section, name='profile_series_section'),
    path('uzivatel/<int:user_id>/hry/', profile_games_section, name='profile_games_section'),
    path('uzivatel/<int:user_id>/knihy/', profile_books_section, name='profile_books_section'),
    path('uzivatel/<int:user_id>/statistiky/', profile_stats_section, name='profile_stats_section'),
    path('uzivatel/pridat-do-oblibenych-<int:userprofile_id>', add_to_favorite_users, name='add_to_favorite_users'),
    path('uzivatel/odebrat-z-oblibenych-<int:userprofile_id>', remove_from_favorite_users, name='remove_from_favorite_users'),
    path('uzivatel/<int:user_id>/vitrina/', profile_show_case, name='profile_show_case'),


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
    path('ucet/seznamy/shlednuto/', watched_profile, name='watched_profile'),

    path('ucet/recenze/', review_profile, name='review_profile'),
    path('ucet/zpravy/', chat, name='chat'),
    path('ucet/zprava-pro-<int:user_id>/', chat_message, name='chat_message'),
    path('ucet/zpravy/nacist-starsi-zpravy/<int:user_id>/', load_older_messages, name='load_older_messages'),

    path('zebricky/', charts_index, name='charts_index'),
    path('zebricky/knihy/', charts_books, name='charts_books'),
    path('zebricky/hry/', charts_games, name='charts_games'),
    path('zebricky/filmy/', charts_movies, name='charts_movies'),
    path('zebricky/uzivatele/', charts_users, name='charts_users'),

    path('oceneni/', awards_index, name='awards_index'),
    path('oceneni/filmy/', awards_movies, name='awards_movies'),
    path('oceneni/knihy/', awards_books, name='awards_books'),
    path('oceneni/hry/', awards_games, name='awards_games'),
    path('oceneni/<str:award_name>/<int:year>/', award_detail, name='award_detail'),

        
    path('kontakt/', contact_form, name='contact'),
    path('prihlaseni/', LoginView.as_view(), name='login'),
    path('registrace/', SignupView.as_view(), name='signup'),
    path('odhlaseni/', LogoutView.as_view(), name='logout'),

    # Reset hesla
    path('accounts/password_reset/', 
         auth_views.PasswordResetView.as_view(template_name='account/password_reset.html'), 
         name='account_reset_password'),
    path('accounts/password_reset_done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='account/password_reset_done.html'), 
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='account/password_reset_confirm.html'), 
         name='password_reset_confirm'),
    path('accounts/reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='account/password_reset_complete.html'), 
         name='password_reset_complete'),



    path('ucet/', include('allauth.urls')),
    #path('api/', include('div_api.urls')),
    path('scripts/', include('div_scripts.urls')),
    #path('add_movies/', my_view, name="add_movies"),
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
