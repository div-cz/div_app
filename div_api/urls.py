from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .other.views import CreatorViewSet,GenreViewSet
from .movie.views import MovieViewSet,TopMovieListView
from .tvshows.views import TvshowViewSet
from .book.views import BookViewSet,BookAuthorViewSet,BookpublisherViewSet
#from .add_book import add_book,fetch_book_details,create_author,verify_author


# Vytvoření instance routeru
router = DefaultRouter()

# Zaregistrování viewsetů
router.register(r'movie', MovieViewSet, basename='movie')
router.register(r'creator', CreatorViewSet, basename='creator')
router.register(r'book', BookViewSet, basename='book')
router.register(r'book_authors', BookAuthorViewSet, basename='book_authors')
router.register(r'tvshow', TvshowViewSet, basename='tvshow')
router.register(r'top_movies',TopMovieListView, basename="movie-list")

router.register(r'book_publisher', BookpublisherViewSet, basename='publisher')
router.register(r'genres', GenreViewSet, basename='genres')

urlpatterns = [
#movies
    #path('add-book/', add_book, name='add_book'),
    #path('create-author/', create_author, name='create_author'),
    #path('fetch-book-details/', fetch_book_details, name='fetch_book_details'),
	#path('verify-author/', verify_author, name='verify_author'),
	#path('',include(router.urls)),


]

