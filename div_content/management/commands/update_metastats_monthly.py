from django.core.management.base import BaseCommand
from django.utils import timezone
from div_content.models.meta import Metastats

from datetime import datetime

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

    def add_snapshot(self, name, value):
        """Vytvoří snapshot statname Z_name_RokMesic"""
        now = timezone.now()
        yyyymm = now.strftime("%Y%m")

        statname = f"Z_{name}_{yyyymm}"

        obj, created = Metastats.objects.update_or_create(
            statname=statname,
            defaults={
                "value": value,
                "tablemodel": "Snapshot",
                "updatedat": timezone.now()
            }
        )
        self.stdout.write(f"[Z] {statname}: {value}")

    def handle(self, *args, **options):
        self.stdout.write("=== Ukládám měsíční snapshoty ===")

        # Seznam všech reálných statů, které chceš snapshotovat
        counters = {
            "MoviesCount": Movie.objects.count(),
            "MovieCommentsCount": Moviecomments.objects.count(),
            "MovieQuotesCount": Moviequotes.objects.count(),
            "MovieTriviaCount": Movietrivia.objects.count(),
            "MovieErrorsCount": Movieerror.objects.count(),
            "MovieTrailersCount": Movietrailer.objects.count(),

            "TVShowsCount": Tvshow.objects.count(),
            "TVSeasonsCount": Tvseason.objects.count(),
            "TVEpisodesCount": Tvepisode.objects.count(),

            "BooksCount": Book.objects.count(),
            "BookWritersCount": Bookauthor.objects.count(),
            "BookCommentsCount": Bookcomments.objects.count(),
            "BookQuotesCount": Bookquotes.objects.count(),

            "GamesCount": Game.objects.count(),
            "GameCommentsCount": Gamecomments.objects.count(),

            "MovieRatingsCount": UserRating.objects.filter(rating__content_type_id=33).count(),
            "BookRatingsCount": UserRating.objects.filter(rating__content_type_id=9).count(),
            "GameRatingsCount": UserRating.objects.filter(rating__content_type_id=19).count(),

            "CreatorsCount": Creator.objects.count(),
            "CharactersCount": Charactermeta.objects.count(),

            "UsersCount": User.objects.count(),
            "UserProfilesCount": Userprofile.objects.count(),

            "ArticlesCount": Article.objects.count(),
            "ArticleNewsCount": Articlenews.objects.count(),
        }

        for key, val in counters.items():
            self.add_snapshot(key, val)

        self.stdout.write("=== Snapshot hotov ===")
