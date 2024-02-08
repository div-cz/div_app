from django.urls import path
from .views import getData, RegisterView, LoginView, UserView, LogoutView

urlpatterns = [
    path('register', RegisterView),
    path('login', LoginView),
    path('logout', LogoutView),
    path('user', UserView),
    path('getallfilms', getData),
]
