from django.core.management.base import BaseCommand
from django.db.models import Count
from div_content.models import (
    Article, Articlenews,
    Book, Bookauthor, Bookcomments, Bookquotes,
    Creator, Charactermeta,
    Game, Gamecomments,
    Metastats, 
    Movie, Moviecomments, Movieerror, Moviequotes, Movietrailer, Movietrivia,
    Tvshow, Tvepisode, Tvseason, 
    Userprofile,
)
from django.contrib.auth.models import User
from star_ratings.models import UserRating

from django.utils import timezone


# 0 1 * * * /var/www/div_app/div_env/bin/python /var/www/div_app/manage.py update_metastats


class Command(BaseCommand):
    help = "Aktualizuje rychlé statistiky v tabulce MetaStats"

    def update_stat(self, name, table, queryset):
        """Uloží nebo aktualizuje statistiku."""
        value = queryset.count()
        obj, created = Metastats.objects.update_or_create(
            statname=name,
            defaults={
                "value": value,
                "tablemodel": table,
                "updatedat": timezone.now()
            }
        )
        self.stdout.write(f"[OK] {name}: {value} ({'created' if created else 'updated'})")

    def handle(self, *args, **options):
        self.stdout.write("=== Aktualizuji MetaStats ===")

        # FILMY
        self.update_stat("MoviesCount", "Movie", Movie.objects.all())
        self.update_stat("MovieCommentsCount", "MovieComments", Moviecomments.objects.all())
        self.update_stat("MovieQuotesCount", "MovieQuotes", Moviequotes.objects.all())
        self.update_stat("MovieTriviaCount", "MovieTrivia", Movietrivia.objects.all())
        self.update_stat("MovieErrorsCount", "MovieErrors", Movieerror.objects.all())
        self.update_stat("MovieTrailersCount", "MovieTrailer", Movietrailer.objects.all())

        # SERIÁLY
        self.update_stat("TVShowsCount", "TVShow", Tvshow.objects.all())
        self.update_stat("TVSeasonsCount", "TVSeason", Tvseason.objects.all())
        self.update_stat("TVEpisodesCount", "TVEpisode", Tvepisode.objects.all())

        # KNIHY
        self.update_stat("BooksCount", "Book", Book.objects.all())
        self.update_stat("BookWritersCount", "BookAuthor", Bookauthor.objects.all())
        self.update_stat("BookCommentsCount", "BookComments", Bookcomments.objects.all())
        self.update_stat("BookQuotesCount", "BookQuotes", Bookquotes.objects.all())

        # HRY
        self.update_stat("GamesCount", "Game", Game.objects.all())
        self.update_stat("GameCommentsCount", "GameComments", Gamecomments.objects.all())

        # Ratings
        self.update_stat("MovieRatingsCount", "UserRating", UserRating.objects.filter(rating__content_type_id=33))
        self.update_stat("BookRatingsCount", "UserRating", UserRating.objects.filter(rating__content_type_id=9))
        self.update_stat( "GameRatingsCount", "UserRating", UserRating.objects.filter(rating__content_type_id=19))


        # TVŮRCI & POSTAVY
        self.update_stat("CreatorsCount", "Creator", Creator.objects.all())
        self.update_stat("CharactersCount", "CharacterMeta", Charactermeta.objects.all())

        # Uživatelé
        self.update_stat("UsersCount", "User", User.objects.all())
        self.update_stat("UserProfilesCount", "UserProfile", Userprofile.objects.all())

        # ČLÁNKY
        self.update_stat("ArticlesCount", "Article", Article.objects.all())
        self.update_stat("ArticleNewsCount", "ArticleNews", Articlenews.objects.all())

        self.stdout.write("=== Hotovo ===")
