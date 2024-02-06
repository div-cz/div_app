from django.urls import path
from . import views

urlpatterns = [
    path('getallfilms', views.getData),
]
