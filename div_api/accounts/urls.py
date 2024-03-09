from django.contrib import admin
from django.urls import include, path

from div_api.accounts import views


urlpatterns = [
    path("csrf_token/", views.csfr_token),
]
