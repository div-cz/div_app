from django.core.management.base import BaseCommand
from django.utils import timezone
from div_content.models.meta import Metastats

from div_content.models import (
    Movie, Moviecomments, Moviequotes, Movietrivia, Movieerror, Movietrailer,
    Tvshow, Tvseason, Tvepisode,
    Book, Bookauthor, Bookcomments, Bookquotes,
    Game, Gamecomments,
    Creator, Charactermeta,
    Article, Articlenews,
    Userprofile,
)

from django.contrib.auth.models import User
from star_ratings.models import UserRating


class Command(BaseCommand):
    help = "Ukládá měsíční snapshot MetaStats (přidává nové položky s prefixem Z_)"

    def add_snapshot(self, name, original_tablemodel, value):
        """
        Vytvoří snapshot:
            statname = Z_{name}_{YYYYMM}
            tablemodel = Snapshot{original_tablemodel}
        """
        now = timezone.now()
        yyyymm = now.strftime("%Y%m")

        statname = f"Z_{name}_{yyyymm}"
        snapshot_tablemodel = f"Snapshot{original_tablemodel}"

        obj, created = Metastats.objects.update_or_create(
            statname=statname,
            defaults={
                "value": value,
                "tablemodel": snapshot_tablemodel,
                "updatedat": timezone.now()
            }
        )
        self.stdout.write(f"[Z] {statname}: {value} ({snapshot_tablemodel})")

    def handle(self, *args, **options):
        self.stdout.write("=== Ukládám měsíční snapshoty ===")

        counters = {
            "MoviesCount": ("Movie", Movie.objects.count()),
            "MovieCommentsCount": ("MovieComments", Moviecomments.objects.count()),
            "MovieQuotesCount": ("MovieQuotes", Moviequotes.objects.count()),
            "MovieTriviaCount": ("MovieTrivia", Movietrivia.objects.count()),
            "MovieErrorsCount": ("MovieError", Movieerror.objects.count()),
            "MovieTrailersCount": ("MovieTrailer", Movietrailer.objects.count()),

            "TVShowsCount": ("Tvshow", Tvshow.objects.count()),
            "TVSeasonsCount": ("Tvseason", Tvseason.objects.count()),
            "TVEpisodesCount": ("Tvepisode", Tvepisode.objects.count()),

            "BooksCount": ("Book", Book.objects.count()),
            "BookWritersCount": ("BookAuthor", Bookauthor.objects.count()),
            "BookCommentsCount": ("BookComments", Bookcomments.objects.count()),
            "BookQuotesCount": ("BookQuotes", Bookquotes.objects.count()),

            "GamesCount": ("Game", Game.objects.count()),
            "GameCommentsCount": ("GameComments", Gamecomments.objects.count()),

            "MovieRatingsCount": ("UserRating", UserRating.objects.filter(rating__content_type_id=33).count()),
            "BookRatingsCount": ("UserRating", UserRating.objects.filter(rating__content_type_id=9).count()),
            "GameRatingsCount": ("UserRating", UserRating.objects.filter(rating__content_type_id=19).count()),

            "CreatorsCount": ("Creator", Creator.objects.count()),
            "CharactersCount": ("CharacterMeta", Charactermeta.objects.count()),

            "UsersCount": ("User", User.objects.count()),
            "UserProfilesCount": ("UserProfile", Userprofile.objects.count()),

            "ArticlesCount": ("Article", Article.objects.count()),
            "ArticleNewsCount": ("ArticleNews", Articlenews.objects.count()),
        }

        for key, (tablemodel, value) in counters.items():
            self.add_snapshot(key, tablemodel, value)

        self.stdout.write("=== Snapshot hotov ===")
