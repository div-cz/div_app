from django.urls import path
from div_content.views.divkvariat import (
    antikvariat_home, book_listings, listing_add_book, 
    listing_detail, listing_detail_edit, listing_search_books,
    cancel_listing_reservation, confirm_sale, cancel_sell
)
from django.contrib.auth import views as auth_views
from allauth.account.views import LoginView, LogoutView, SignupView

urlpatterns = [

    # Přihlášení / registrace
    path("prihlaseni/", LoginView.as_view(template_name="divkvariat/account/login.html"), name="login"),
    path("registrace/", SignupView.as_view(template_name="divkvariat/account/signup.html"), name="signup"),
    path("odhlaseni/", LogoutView.as_view(template_name="divkvariat/account/logout.html"), name="logout"),

    # Antikvariát — hlavní modul
    path("", antikvariat_home, name="antikvariat_home"),
    path("search/", listing_search_books, name="listing_search_books"),
    path("<str:book_url>/nabidky/", book_listings, name="book_listings"),
    path("<str:book_url>/prodej/<int:listing_id>/", listing_detail, name="listing_detail_sell"),
    path("<str:book_url>/prodej/<int:listing_id>/upravit/", listing_detail_edit, name="listing_detail_edit"),
    path("pridat-knihu/", listing_add_book, name="listing_add_book"),

    # Obchodní operace
    path("zrusit/<int:listing_id>/", cancel_listing_reservation, name="cancel_listing_reservation"),
    path("potvrdit/<int:purchase_id>/", confirm_sale, name="confirm_sale"),
    path("smazat/<int:listing_id>/", cancel_sell, name="cancel_sell"),
]
