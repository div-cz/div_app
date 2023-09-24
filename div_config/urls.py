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
    path('filmy2000', views.filmy_z_roku_2000, name='filmy2000'),
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),

#    path('registrace/', RegisterView.as_view(), name='register')
#    path('profil/upravit/', ProfileUpdateView.as_view(), name='edit_profile'),

    path('filmy/', views.filmy, name='index_filmy'),
    path('film/<str:url_filmu>', views.film_detail, name='film_detail'),
    path('knihy/', views.knihy, name='index_knihy'),
    path('kniha/<str:nazev_knihy>', views.kniha_detail, name='kniha_detail'),
    path('hry/', views.hry, name='index_hry'),
    path('hra/<str:nazev_hry>', views.hra_detail, name='hra_detail'),
    path('lokality/', views.lokality, name='index_lokality'),
    path('lokalita/<str:nazev_lokality>', views.lokalita_detail, name='lokalita_detail'),

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
