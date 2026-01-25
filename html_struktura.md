jen pro HTML do příkazového řádku:

tree -P "*.html" --prune > html_struktura.txt


.
**|-- 404.html DEL**
|-- div_content
`   |-- templates
   `   |-- 403.html
       |-- 404.html
       |-- account
       |   |-- account_inactive.html
       |   |-- base.html
       |   |-- email.html
       |   |-- email_change.html
       |   |-- email_confirm.html
       |   |-- login.html
       |   |-- logout.html
       |   |-- password_change.html
       |   |-- password_reset.html
       |   |-- password_reset_done.html
       |   |-- password_reset_from_key.html
       |   |-- password_reset_from_key_done.html
       |   |-- password_set.html
       |   |-- reauthenticate.html
       |   |-- signup.html
       |   |-- signup_closed.html
       |   |-- snippets
       |   |   |-- already_logged_in.html
       |   |   `-- warn_no_email.html
       
!!! TO JE PRO PŘIHLÁŠENÍ PŘES SOC.SÍTĚ 
!!! NENÍ TO FUNKČNÍ, JE S TÍM DOST PRÁCE TO NAPOJIT, ALE DO BUDOUCNA?
     **|   |-- socialaccount ? 2x**
     **|   |   |-- authentication_error.html**
     **|   |   |-- base_entrance.html**
     **|   |   |-- base_manage.html**
     **|   |   |-- connections.html**
     **|   |   |-- login.html**
     **|   |   |-- login_cancelled.html**
     **|   |   |-- login_redirect.html**
     **|   |   |-- signup.html**
     **|   |   `-- snippets**
     **|   |       |-- login.html**
     **|   |       |-- login_extra.html**
     **|   |       `-- provider_list.html**
     **|   |-- verification_sent.html**
     **|   `-- verified_email_required.html**
       |-- admin + css
       |   |-- admin_comments.html
       |   |-- admin_edit_comment.html
       |   |-- admin_index.html
       |   |-- admin_movies.html
       |   |-- admin_task_detail.html
       |   |-- admin_task_edit.html
       |   |-- admin_tasks.html
       |   |-- banka.html
       |   |-- base.html
       |   |-- fio.html
       |   |-- palmknihy_preview.html
       |   `-- payments.html
       |-- articles + css
       |   |-- article_detail.html
       |   |-- article_edit.html
       |   |-- article_new.html
       |   |-- articles_index.html
       |   |-- articles_list.html
       |   `-- base.html
       |-- awards + css
       |   |-- admin_add_nominee.html
       |   |-- admin_award_form.html - opravit ocenění
       |   |-- admin_award_nominees.html - správa nominací
       |   |-- admin_awards.html - správa ocenění
       |   |-- award_detail.html
       |   |-- awards_books.html
       |   |-- awards_games.html
       |   |-- awards_index.html
       |   |-- awards_movies.html
       |   |-- awards_series.html
       |   `-- base.html
       |-- blog + css
       |   |-- base.html
       |   |-- blog_add_post.html - nový příspěvek
       |   |-- blog_detail.html
       |   |-- blog_index.html

!!! ASI TO NELINKUJEME, ALE JE TO V URLS I VIEWS 
http://div.cz/blog/
     **|   |-- blog_list.html DEL?** to samé jako blog_section_detail.html ?
       |   |-- blog_new.html
       |   |-- blog_post_detail.html
     **|   `-- blog_section_detail.html** - uživatelské blogy

!!! Chybí soubory přesunuto do divkariat a ted to háže errory
       |-- books + css
!!! NEPOUŽÍVÁME, ALE PATŘÍ K NĚJAKÝMU IONNO SCRIPTU
     **|   |-- add_book.html DEL**
       |   |-- base.html
       |   |-- book_add.html
       |   |-- book_detail.html
       |   |-- books_alphabetical.html
       |   |-- books_genres.html
       |   |-- books_list.html
       |   |-- books_search.html
       |   |-- ebook_list.html
       |   |-- listing_add_book.html
       |   |-- listings.html - antikvriát nabídka / poptávka
       |   `-- publisher.html
       |-- characters
       |   |-- base.html
       |   |-- characters_detail.html
       |   `-- characters_list.html
       |-- charts + css

!!! NEPOUŽÍVÁME ALE VIEWS EXISTUJE
     **|   |-- award_detail.html DEL**
     **|   |-- awards_books.html DEL**
     **|   |-- awards_games.html DEL**
     **|   |-- awards_index.html DEL**
     **|   |-- awards_movies.html DEL**
       |   |-- base.html
       |   |-- charts.html
       |   |-- charts_books.html
       |   |-- charts_games.html
       |   |-- charts_movies.html
       |   `-- charts_users.html
       |-- contact.html
       |-- creators
       |   |-- author_add.html
       |   |-- author_detail.html
       |   |-- authors_list.html
       |   |-- authors_search.html
       |   |-- birthdays_list.html
       |   |-- creator_detail.html
       |   |-- creators_list.html
       |   `-- creators_search.html
       |-- divkvariat
       |   |-- account
       |   |   |-- account_edit.html
       |   |   |-- account_profile.html
       |   |   |-- email.html
       |   |   |-- email_confirm.html
       |   |   |-- login.html
       |   |   |-- logout.html
       |   |   |-- password_change.html
       |   |   |-- password_reset.html
       |   |   `-- signup.html
       |   |-- antikvariat_home.html
       |   |-- author_detail.html
       |   |-- base.html
       |   |-- blog_detail.html
       |   |-- blog_list.html
       |   |-- book_detail.html
       |   |-- book_listings.html
       |   |-- books_market_offers.html
       |   |-- books_market_wants.html
       |   |-- listing_add_book.html
       |   |-- listing_detail.html
       |   |-- listing_edit.html
       |   |-- listings.html
       |   |-- market_cancel_purchase.html
       |   |-- market_confirm_sale.html
       |   |-- search.html
       |   |-- send_to_reader_email.html
       |   |-- stranky
       |   |   |-- kontakt.html
       |   |   |-- o-nas.html
       |   |   |-- ochrana-osobnich-udaju.html
       |   |   `-- podminky.html
       |   |-- update_book.html
       |   |-- user_book_buy.html
       |   |-- user_book_listings.html
       |   |-- user_book_sell.html
       |   |-- user_buy_listings.html
       |   `-- user_sell_listings.html
       |-- emails
       |   |-- base_emails.html
       |   |-- chat_new_private_message.html
       |   |-- ebook_paid_confirmation_buyer.html
       |   |-- listing_auto_completed_buyer.html
       |   |-- listing_auto_completed_seller.html
       |   |-- listing_cancel_reservation_buyer.html
       |   |-- listing_cancel_reservation_seller.html
       |   |-- listing_completed_confirmation_buyer.html
       |   |-- listing_completed_confirmation_seller.html
       |   |-- listing_expired_buyer.html
       |   |-- listing_paid_confirmation_buyer.html
       |   |-- listing_paid_confirmation_seller.html
       |   |-- listing_paid_expired_buyer.html
       |   |-- listing_paid_expired_seller.html
       |   |-- listing_payment_request_confirmed.html
       |   |-- listing_request_payment_seller.html
       |   |-- listing_reservation_expired_buyer.html
       |   |-- listing_send_reservation_buyer.html
       |   `-- listing_shipped_information_buyer.html
       |-- eshop
       |   |-- base.html
       |   |-- eshop_books.html
       |   |-- eshop_detail.html
       |   |-- eshop_games.html
       |   |-- eshop_list.html
       |   |-- eshop_movies.html
       |   `-- eshop_profile.html
       |-- forum + css
       |   |-- base.html
       |   |-- forum_comment_delete.html
       |   |-- forum_comment_edit.html
       |   |-- forum_comment_reply.html
       |   |-- forum_create_topic.html
       |   |-- forum_index.html
       |   |-- forum_search.html
       |   |-- forum_section_detail.html
       |   |-- forum_topic_detail.html
       |   `-- load_all_comments.html
       |-- gamekvariat + css
       |   |-- games_market_offers.html
       |   |-- games_market_wants.html
       |-- games + css
       |   |-- base.html
     **|   |-- game_add.html ?**
       |   |-- game_add_success.html
       |   |-- game_detail.html
       |   |-- games_alphabetical.html
       |   |-- games_by_developer.html
       |   |-- games_by_genre.html
       |   |-- games_by_publisher.html
       |   |-- games_by_year.html
       |   |-- games_charts.html
       |   |-- games_genres.html
       |   |-- games_list.html
       |   |-- games_search.html
       |   |-- listing_detail.html
       |   `-- publishers_list.html
       |-- inc
       |   |-- base.html

!!! PRO IMPORT KNIHOVEN DO ŠABLON (asi jen někde v base.html)
     **|   |-- div_head.html ?**
       |   |-- footer.html
       |   |-- google.html
       |   |-- head.html
       |   |-- navbar.html
       |   |-- navbar_books.html
       |   |-- navbar_eshop.html
       |   |-- navbar_games.html
       |   |-- navbar_index.html
       |   |-- navbar_movies.html
       |   |-- navbar_series.html
       |   |-- newsletter.html
       |   `-- sidebar.html
       |-- index.html + css

!!! PŘIPRAVENO PRO PROPOJOVACÍ META DATABÁZE A META INFORMACE
!!! SEZNAM PŘEDMĚTŮ, SEZNAM LOKALIT A DALŠÍ
     **|--** **meta ?**
     **|   |-- item_detail.html**
     **|   |-- items_list.html**
     **|   |-- location_detail.html**
     **|   `-- locations_list.html**
       |-- movies + css
       |   |-- base.html
       |   |-- movie_detail.html
       |   |-- movies_alphabetical.html
       |   |-- movies_genre.html
       |   |-- movies_list.html
       |   |-- movies_search.html
       |   |-- movies_search_utf8.html
       |   `-- movies_year.html
       |-- nas_tym.html
       |-- series + css
       |   |-- base.html
       |   |-- serie_detail.html
       |   |-- serie_episode.html
       |   |-- serie_season.html
       |   |-- series_alphabetical.html
       |   |-- series_genre.html
       |   |-- series_list.html
       |   |-- series_search.html
       |   `-- series_year.html
       |-- template.html
     
!!! PŮVODNÍ SERIÁLY - PRESUNUTO DO SERIES
!!! ALE STÁLE FUNKČNÍ (TŘEBA SMAZAT I URLS,VIEWS)
     **|-- tv ?**
     **|   |-- tv_detail.html**
     **|   `-- tv_list.html**
       |-- universum
       |   |-- base.html
       |   |-- universum_detail.html
       |   `-- universum_list.html
       `-- user + css
           |-- base.html
           |-- chat.html
           |-- chat_message.html
           |-- profile.html
           |-- profile_books.html
           |-- profile_community.html
           |-- profile_games.html
           |-- profile_markets.html
           |-- profile_movies.html
           |-- profile_serials.html
           |-- profile_show_case.html
           |-- profile_stats.html
           `-- update_profile.html


30 directories, 245 files


