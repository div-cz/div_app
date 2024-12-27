from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from .books.add_book import add_book,fetch_book_details,get_book_details, update_book_details, update_book
from .others.helpers import check_isbn_exists, check_book_exists
from .others.metadatas import ajax_search_genres, ajax_search_publisher
from .book_authors.search_author import ajax_search_authors



urlpatterns = [
#movies
    path('add_book/', add_book, name='add_book'),
    path('update_book/', update_book, name='update_book'),
    path('fetch_book_details/', fetch_book_details, name='fetch_book_details'),
    path('get_book_details/<int:book_id>/', get_book_details, name='get_book_details'),
    path('check_book_exists/', check_book_exists, name='check_book_exists'),
    path('check_isbn_exists/', check_isbn_exists, name='check_isbn_exists'),
    path('update_book/<int:book_id>/', update_book_details, name='update_book'),
    path('search_authors/', ajax_search_authors, name='search_authors'),
    path('search_genres/',ajax_search_genres, name='search_genres'),
    path('search_publisher/',ajax_search_publisher, name='search_publisher'),


]