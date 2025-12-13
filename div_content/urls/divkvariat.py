# -------------------------------------------------------------------
#                    URLS.DIVKVARIAT.PY
# -------------------------------------------------------------------

from allauth.account.views import confirm_email, LoginView, LogoutView, SignupView, email_verification_sent



from div_content.views.divkvariat_cz import (
    account_edit, account_view, antikvariat_home, author_detail_cz, 
    blog_list, blog_detail, book_detail_cz, book_listings, 
    books_market_offers, books_market_wants, 
    cancel_listing_reservation, cancel_sell, confirm_sale, 
    CustomLoginView, CustomSignupView, CustomLogoutView, 
    chatbot_api,
    
    listing_add_book, listing_detail, listing_detail_edit, listing_search_books,
    listing_upload_image, listing_delete_image, 
    
    search_view, 
    user_book_listings, user_buy_listings, user_profile, user_sell_listings

)



from django.conf import settings

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from django.urls import path, include

from django.views.generic import TemplateView



import debug_toolbar


urlpatterns = [

    #path("ucet/", include("allauth.urls")),
    path("ucet/", login_required(account_view), name="dk_account"),
    path("api/chatbot/", chatbot_api, name="chatbot_api"),
    path('ucet/potvrdit-email/<str:key>/', confirm_email, name='account_confirm_email'),
    path('ucet/overeni-odeslano/', email_verification_sent, name='account_email_verification_sent'),

    # Přihlášení / registrace
    path("prihlaseni/", CustomLoginView.as_view(template_name="divkvariat/account/login.html"), name="account_login"),
    path("registrace/", CustomSignupView.as_view(template_name="divkvariat/account/signup.html"), name="account_signup"),
    path("odhlaseni/", CustomLogoutView.as_view(template_name="divkvariat/account/logout.html"), name="account_logout"),
    path("ucet/upravit/", account_edit, name="account_edit"),

    # Antikvariát — hlavní modul
    path("", antikvariat_home, name="antikvariat_home"),
    path("search/", listing_search_books, name="listing_search_books"),
    path("<str:book_url>/nabidky/", book_listings, name="book_listings"),
    path("<str:book_url>/prodej/<int:listing_id>/", listing_detail, name="listing_detail_sell"),
    path("<str:book_url>/prodej/<int:listing_id>/upravit/", listing_detail_edit, name="listing_detail_edit"),
    path("pridat-knihu/", listing_add_book, name="listing_add_book"),


    path("listing/<int:listing_id>/upload/", listing_upload_image, name="listing_upload_image"),
    path("image/<int:image_id>/delete/", listing_delete_image, name="listing_delete_image"),


    path("nabidky/", books_market_offers, name="books_market_offers"),
    path("poptavky/", books_market_wants, name="books_market_wants"),
    path("<str:book_url>/poptavka/<int:listing_id>/", listing_detail, name="listing_detail_buy"),

    # Uzivatel
    path("uzivatel/<int:user_id>/prodej-knihy/", user_sell_listings, name="user_sell_listings"),
    path("uzivatel/<int:user_id>/koupim-knihy/", user_buy_listings, name="user_buy_listings"),
    path("uzivatel/<int:user_id>/nabidky/", user_book_listings, name="user_book_listings"),
    #path("uzivatel/<int:user_id>/", user_book_listings, name="user_book_listings"),
    path("uzivatel/<int:user_id>/prodam-knihy/", user_sell_listings, name="user_sell_listings"),
    path("uzivatel/<int:user_id>/koupim-knihy/", user_buy_listings, name="user_buy_listings"),
    path("uzivatel/<int:user_id>/", user_profile, name="user_profile"),
    #path("chat/<int:user_id>/", chat_message, name="chat_message"),

    # BLOG
    path("blog/", blog_list, name="dk_blog_list"),
    path("blog/<str:url>/", blog_detail, name="dk_blog_detail"),

    # Databaze
    path("kniha/<str:book_url>/", book_detail_cz, name="book_detail_cz"),
    path("autor/<str:author_url>/", author_detail_cz, name="author_detail_cz"),

    # Hledání
    path("hledat/", search_view, name="dk_search"),

    # Stranky
    path("kontakt/", TemplateView.as_view(template_name="divkvariat/stranky/kontakt.html"), name="dk_kontakt"),
    path("podminky/", TemplateView.as_view(template_name="divkvariat/stranky/podminky.html"), name="dk_podminky"),
    path("ochrana-osobnich-udaju/", TemplateView.as_view(template_name="divkvariat/stranky/ochrana-osobnich-udaju.html"), name="dk_gdpr"),
    path("o-nas/", TemplateView.as_view(template_name="divkvariat/stranky/o-nas.html"), name="dk_o_nas"),

    # Obchodní operace
    path("zrusit/<int:listing_id>/", cancel_listing_reservation, name="cancel_listing_reservation"),
    path("potvrdit/<int:purchase_id>/", confirm_sale, name="confirm_sale"),
    path("smazat/<int:listing_id>/", cancel_sell, name="cancel_sell"),
]



if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]