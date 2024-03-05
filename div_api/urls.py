from django.urls import path
from .views import RegisterView, LoginView, UserView, LogoutView
from .views import MoviesGet,MovieDetailGet, MovieDetailPatch, MovieCreate,MovieDelete

urlpatterns = [
#user
    path('register', RegisterView),
    path('login', LoginView),
    path('logout', LogoutView),
    path('user', UserView),
#movies
    path('movies', MoviesGet, name="movie-list"),
	path('movie/<int:pk>', MovieDetailGet, name="movie-detail-get"),
	path('movie/<int:pk>/edit', MovieDetailPatch, name="movie-detail-patch"),
	path('movie/create', MovieCreate, name="movie-new"),
	path('movie/<int:pk>/delete', MovieDelete, name="movie-delete"),
]
