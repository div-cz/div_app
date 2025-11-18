

from django.urls import path, include
from div_content.views.divkvariat_cz import (
    antikvariat_home, author_detail_cz, book_detail_cz, book_listings, 
    books_market_offers, books_market_wants, 
    listing_add_book, 
    listing_detail, listing_detail_edit, listing_search_books,
    cancel_listing_reservation, confirm_sale, cancel_sell, 

    user_sell_listings, user_buy_listings, user_book_listings

)

from django.conf import settings

from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView

from allauth.account.views import LoginView, LogoutView, SignupView

import debug_toolbar


urlpatterns = [

    path("ucet/", include("allauth.urls")),
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

    path("nabidky/", books_market_offers, name="books_market_offers"),
    path("poptavky/", books_market_wants, name="books_market_wants"),
    path("<str:book_url>/poptavka/<int:listing_id>/", listing_detail, name="listing_detail_buy"),

    # Uzivatel
    path("uzivatel/<int:user_id>/prodej-knihy/", user_sell_listings, name="user_sell_listings"),
    path("uzivatel/<int:user_id>/koupim-knihy/", user_buy_listings, name="user_buy_listings"),
    path("uzivatel/<int:user_id>/nabidky/", user_book_listings, name="user_book_listings"),
    path("uzivatel/<int:user_id>/", user_book_listings, name="user_book_listings"),
    path("uzivatel/<int:user_id>/prodam-knihy/", user_sell_listings, name="user_sell_listings"),
    path("uzivatel/<int:user_id>/koupim-knihy/", user_buy_listings, name="user_buy_listings"),

    # Databaze
    path("kniha/<str:book_url>/", book_detail_cz, name="book_detail_cz"),
    path("autor/<str:author_url>/", author_detail_cz, name="author_detail_cz"),

    # Stranky
    path("kontakt/", TemplateView.as_view(template_name="divkvariat/stranky/kontakt.html"), name="dk_kontakt"),
    path("podminky/", TemplateView.as_view(template_name="divkvariat/stranky/podminky.html"), name="dk_podminky"),
    path("ochrana-osobnich-udaju/", TemplateView.as_view(template_name="divkvariat/stranky/gdpr.html"), name="dk_gdpr"),

    # Obchodní operace
    path("zrusit/<int:listing_id>/", cancel_listing_reservation, name="cancel_listing_reservation"),
    path("potvrdit/<int:purchase_id>/", confirm_sale, name="confirm_sale"),
    path("smazat/<int:listing_id>/", cancel_sell, name="cancel_sell"),
]



if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]