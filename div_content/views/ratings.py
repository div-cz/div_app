# -------------------------------------------------------------------
#                    VIEWS.RATINGS.PY
# -------------------------------------------------------------------

# -------------------------------------------------------------------
#                    IMPORTY
# -------------------------------------------------------------------

from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect

from django.utils import timezone

from django.views.decorators.http import require_POST

from django.db.models import Avg, Count, Sum

from div_content.models import Movie, Book
from div_content.models.meta import Divrating, Divuserrating
from div_content.models.movies import Tvshow, Tvseason


# -------------------------------------------------------------------
# F:                 RATE MOVIE
# -------------------------------------------------------------------
@require_POST
@login_required
def div_rate_movie(request, movie_url):

    movie = get_object_or_404(Movie, url=movie_url)

    score = int(request.POST.get("score", 0))

    # povolené hodnoty
    if score < 0 or score > 5:
        return redirect("movie_detail", movie_url=movie.url)

    content_type = ContentType.objects.get_for_model(Movie)

    rating_obj, created = Divrating.objects.get_or_create(
        content_type=content_type,
        object_id=movie.movieid,
        defaults={
            "count": 0,
            "total": 0,
            "average": 0
        }
    )

    user_rating, created = Divuserrating.objects.get_or_create(
        user=request.user,
        rating=rating_obj,
        defaults={
            "score": score,
            "created": request.timestamp if hasattr(request, "timestamp") else timezone.now(),
            "modified": request.timestamp if hasattr(request, "timestamp") else timezone.now(),
            "ip": request.META.get("REMOTE_ADDR")
        }
    )

    if not created:
        user_rating.score = score
        user_rating.modified = timezone.now()
        user_rating.save()

    # přepočet ratingu
    agg = Divuserrating.objects.filter(
        rating=rating_obj
    ).aggregate(
        avg=Avg("score"),
        count=Count("id")
    )

    rating_obj.average = agg["avg"] or 0
    rating_obj.count = agg["count"] or 0
    rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Avg("score"))["t"] or 0
    rating_obj.save()

    # uložit do Movie cache
    Movie.objects.filter(movieid=movie.movieid).update(
        averagerating=rating_obj.average
    )

    return redirect("movie_detail", movie_url=movie.url)


# -------------------------------------------------------------------
# F:                 REMOVE MOVIE RATING
# -------------------------------------------------------------------
@require_POST
@login_required
def div_remove_movie_rating(request, movie_url):

    movie = get_object_or_404(Movie, url=movie_url)

    content_type = ContentType.objects.get_for_model(Movie)

    rating_obj = Divrating.objects.filter(
        content_type=content_type,
        object_id=movie.movieid
    ).first()

    if not rating_obj:
        return redirect("movie_detail", movie_url=movie.url)

    user_rating = Divuserrating.objects.filter(
        rating=rating_obj,
        user=request.user
    ).first()

    if user_rating:
        user_rating.delete()

        agg = Divuserrating.objects.filter(
            rating=rating_obj
        ).aggregate(
            avg=Avg("score"),
            count=Count("id")
        )

        rating_obj.average = agg["avg"] or 0
        rating_obj.count = agg["count"] or 0
        rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
        rating_obj.save()

        Movie.objects.filter(movieid=movie.movieid).update(
            averagerating=rating_obj.average
        )

        coins, _ = Userdivcoins.objects.get_or_create(user_id=request.user.id)
        coins.totaldivcoins   = F('totaldivcoins')   - Decimal("0.01")
        coins.weeklydivcoins  = F('weeklydivcoins')  - Decimal("0.01")
        coins.monthlydivcoins = F('monthlydivcoins') - Decimal("0.01")
        coins.yearlydivcoins  = F('yearlydivcoins')  - Decimal("0.01")
        coins.save(update_fields=["totaldivcoins", "weeklydivcoins", "monthlydivcoins", "yearlydivcoins"])

    return redirect("movie_detail", movie_url=movie.url)



# -------------------------------------------------------------------
# F:                 RATE BOOK
# -------------------------------------------------------------------
@require_POST
@login_required
def div_rate_book(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    score = int(request.POST.get("score", 0))

    if score < 0 or score > 5:
        return redirect("book_detail", book_url=book.url)

    content_type = ContentType.objects.get_for_model(Book)
    rating_obj, created = Divrating.objects.get_or_create(
        content_type=content_type,
        object_id=book.bookid,
        defaults={"count": 0, "total": 0, "average": 0}
    )

    user_rating, created = Divuserrating.objects.get_or_create(
        user=request.user,
        rating=rating_obj,
        defaults={
            "score": score,
            "created": timezone.now(),
            "modified": timezone.now(),
            "ip": request.META.get("REMOTE_ADDR")
        }
    )
    if not created:
        user_rating.score = score
        user_rating.modified = timezone.now()
        user_rating.save()

    agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(
        avg=Avg("score"), count=Count("id")
    )
    rating_obj.average = agg["avg"] or 0
    rating_obj.count = agg["count"] or 0
    rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
    rating_obj.save()



    return redirect("book_detail", book_url=book.url)


# -------------------------------------------------------------------
# F:                 REMOVE BOOK RATING
# -------------------------------------------------------------------
@require_POST
@login_required
def div_remove_book_rating(request, book_url):
    book = get_object_or_404(Book, url=book_url)
    content_type = ContentType.objects.get_for_model(Book)

    rating_obj = Divrating.objects.filter(
        content_type=content_type,
        object_id=book.bookid
    ).first()
    if not rating_obj:
        return redirect("book_detail", book_url=book.url)

    user_rating = Divuserrating.objects.filter(
        rating=rating_obj,
        user=request.user
    ).first()
    if user_rating:
        user_rating.delete()
        agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(
            avg=Avg("score"), count=Count("id")
        )
        rating_obj.average = agg["avg"] or 0
        rating_obj.count = agg["count"] or 0
        rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
        rating_obj.save()

        coins, _ = Userdivcoins.objects.get_or_create(user_id=request.user.id)
        coins.totaldivcoins   = F('totaldivcoins')   - Decimal("0.01")
        coins.weeklydivcoins  = F('weeklydivcoins')  - Decimal("0.01")
        coins.monthlydivcoins = F('monthlydivcoins') - Decimal("0.01")
        coins.yearlydivcoins  = F('yearlydivcoins')  - Decimal("0.01")
        coins.save(update_fields=["totaldivcoins", "weeklydivcoins", "monthlydivcoins", "yearlydivcoins"])

    return redirect("book_detail", book_url=book.url)



# -------------------------------------------------------------------
# F:                 RATE GAME
# -------------------------------------------------------------------
@require_POST
@login_required
def div_rate_game(request, game_url):
    from div_content.models import Game
    game = get_object_or_404(Game, url=game_url)
    score = int(request.POST.get("score", 0))

    if score < 0 or score > 5:
        return redirect("game_detail", game_url=game.url)

    content_type = ContentType.objects.get_for_model(Game)
    rating_obj, _ = Divrating.objects.get_or_create(
        content_type=content_type,
        object_id=game.gameid,
        defaults={"count": 0, "total": 0, "average": 0}
    )
    user_rating, created = Divuserrating.objects.get_or_create(
        user=request.user,
        rating=rating_obj,
        defaults={"score": score, "created": timezone.now(), "modified": timezone.now(), "ip": request.META.get("REMOTE_ADDR")}
    )
    if not created:
        user_rating.score = score
        user_rating.modified = timezone.now()
        user_rating.save()

    agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
    rating_obj.average = agg["avg"] or 0
    rating_obj.count = agg["count"] or 0
    rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
    rating_obj.save()

    return redirect("game_detail", game_url=game.url)


# -------------------------------------------------------------------
# F:                 REMOVE GAME RATING
# -------------------------------------------------------------------
@require_POST
@login_required
def div_remove_game_rating(request, game_url):
    from div_content.models import Game
    from decimal import Decimal
    from django.db.models import F
    from div_content.models import Userdivcoins

    game = get_object_or_404(Game, url=game_url)
    content_type = ContentType.objects.get_for_model(Game)

    rating_obj = Divrating.objects.filter(content_type=content_type, object_id=game.gameid).first()
    if not rating_obj:
        return redirect("game_detail", game_url=game.url)

    user_rating = Divuserrating.objects.filter(rating=rating_obj, user=request.user).first()
    if user_rating:
        user_rating.delete()
        agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
        rating_obj.average = agg["avg"] or 0
        rating_obj.count = agg["count"] or 0
        rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
        rating_obj.save()

        coins, _ = Userdivcoins.objects.get_or_create(user_id=request.user.id)
        coins.totaldivcoins   = F('totaldivcoins')   - Decimal("0.01")
        coins.weeklydivcoins  = F('weeklydivcoins')  - Decimal("0.01")
        coins.monthlydivcoins = F('monthlydivcoins') - Decimal("0.01")
        coins.yearlydivcoins  = F('yearlydivcoins')  - Decimal("0.01")
        coins.save(update_fields=["totaldivcoins", "weeklydivcoins", "monthlydivcoins", "yearlydivcoins"])

    return redirect("game_detail", game_url=game.url)




# -------------------------------------------------------------------
# F:                 RATE TVSHOW
# -------------------------------------------------------------------
@require_POST
@login_required
def div_rate_tvshow(request, tv_url):
    from div_content.models import Tvshow
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    score = int(request.POST.get("score", 0))

    if score < 0 or score > 5:
        return redirect("serie_detail", tv_url=tvshow.url)

    content_type = ContentType.objects.get_for_model(Tvshow)
    rating_obj, _ = Divrating.objects.get_or_create(
        content_type=content_type,
        object_id=tvshow.tvshowid,
        defaults={"count": 0, "total": 0, "average": 0}
    )
    user_rating, created = Divuserrating.objects.get_or_create(
        user=request.user,
        rating=rating_obj,
        defaults={"score": score, "created": timezone.now(), "modified": timezone.now(), "ip": request.META.get("REMOTE_ADDR")}
    )
    if not created:
        user_rating.score = score
        user_rating.modified = timezone.now()
        user_rating.save()

    agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
    rating_obj.average = agg["avg"] or 0
    rating_obj.count = agg["count"] or 0
    rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
    rating_obj.save()

    return redirect("serie_detail", tv_url=tvshow.url)


# -------------------------------------------------------------------
# F:                 REMOVE TVSHOW RATING
# -------------------------------------------------------------------
@require_POST
@login_required
def div_remove_tvshow_rating(request, tv_url):
    from div_content.models import Tvshow, Userdivcoins
    from decimal import Decimal
    from django.db.models import F

    tvshow = get_object_or_404(Tvshow, url=tv_url)
    content_type = ContentType.objects.get_for_model(Tvshow)

    rating_obj = Divrating.objects.filter(content_type=content_type, object_id=tvshow.tvshowid).first()
    if not rating_obj:
        return redirect("serie_detail", tv_url=tvshow.url)

    user_rating = Divuserrating.objects.filter(rating=rating_obj, user=request.user).first()
    if user_rating:
        user_rating.delete()
        agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
        rating_obj.average = agg["avg"] or 0
        rating_obj.count = agg["count"] or 0
        rating_obj.total = Divuserrating.objects.filter(rating=rating_obj).aggregate(t=Sum("score"))["t"] or 0
        rating_obj.save()

        coins, _ = Userdivcoins.objects.get_or_create(user_id=request.user.id)
        coins.totaldivcoins   = F('totaldivcoins')   - Decimal("0.01")
        coins.weeklydivcoins  = F('weeklydivcoins')  - Decimal("0.01")
        coins.monthlydivcoins = F('monthlydivcoins') - Decimal("0.01")
        coins.yearlydivcoins  = F('yearlydivcoins')  - Decimal("0.01")
        coins.save(update_fields=["totaldivcoins", "weeklydivcoins", "monthlydivcoins", "yearlydivcoins"])

    return redirect("serie_detail", tv_url=tvshow.url)


@require_POST
@login_required
def div_rate_tvseason(request, tv_url, seasonurl):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    score = int(request.POST.get("score", 0))
    if score < 0 or score > 5:
        return redirect("serie_season", tv_url=season.tvshowid.url, seasonurl=season.seasonurl)
    content_type = ContentType.objects.get_for_model(Tvseason)
    rating_obj, _ = Divrating.objects.get_or_create(content_type=content_type, object_id=season.seasonid, defaults={"count":0,"total":0,"average":0})
    user_rating, created = Divuserrating.objects.get_or_create(user=request.user, rating=rating_obj, defaults={"score":score,"created":timezone.now(),"modified":timezone.now(),"ip":request.META.get("REMOTE_ADDR")})
    if not created:
        user_rating.score = score
        user_rating.modified = timezone.now()
        user_rating.save()
    agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
    rating_obj.average = agg["avg"] or 0
    rating_obj.count = agg["count"] or 0
    rating_obj.save()
    return redirect("serie_season", tv_url=tv_url, seasonurl=season.seasonurl)

@require_POST
@login_required
def div_remove_tvseason_rating(request, tv_url, seasonurl):
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    content_type = ContentType.objects.get_for_model(Tvseason)
    rating_obj = Divrating.objects.filter(content_type=content_type, object_id=season.seasonid).first()
    if rating_obj:
        Divuserrating.objects.filter(rating=rating_obj, user=request.user).delete()
        agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
        rating_obj.average = agg["avg"] or 0
        rating_obj.count = agg["count"] or 0
        rating_obj.save()
    return redirect("serie_season", tv_url=tv_url, seasonurl=season.seasonurl)


@require_POST
@login_required
def div_rate_tvepisode(request, tv_url, seasonurl, episodeurl):
    from div_content.models import Tvshow, Tvseason, Tvepisode
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    episode = get_object_or_404(Tvepisode, seasonid=season.seasonid, episodeurl=episodeurl)
    score = int(request.POST.get("score", 0))
    if score < 0 or score > 5:
        return redirect("serie_episode", tv_url=tv_url, seasonurl=seasonurl, episodeurl=episodeurl)
    content_type = ContentType.objects.get_for_model(Tvepisode)
    rating_obj, _ = Divrating.objects.get_or_create(content_type=content_type, object_id=episode.episodeid, defaults={"count":0,"total":0,"average":0})
    user_rating, created = Divuserrating.objects.get_or_create(user=request.user, rating=rating_obj, defaults={"score":score,"created":timezone.now(),"modified":timezone.now(),"ip":request.META.get("REMOTE_ADDR")})
    if not created:
        user_rating.score = score; user_rating.modified = timezone.now(); user_rating.save()
    agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
    rating_obj.average = agg["avg"] or 0; rating_obj.count = agg["count"] or 0; rating_obj.save()
    return redirect("serie_episode", tv_url=tv_url, seasonurl=seasonurl, episodeurl=episodeurl)

@require_POST
@login_required
def div_remove_tvepisode_rating(request, tv_url, seasonurl, episodeurl):
    from div_content.models import Tvshow, Tvseason, Tvepisode
    tvshow = get_object_or_404(Tvshow, url=tv_url)
    season = get_object_or_404(Tvseason, tvshowid=tvshow.tvshowid, seasonurl=seasonurl)
    episode = get_object_or_404(Tvepisode, seasonid=season.seasonid, episodeurl=episodeurl)
    content_type = ContentType.objects.get_for_model(Tvepisode)
    rating_obj = Divrating.objects.filter(content_type=content_type, object_id=episode.episodeid).first()
    if rating_obj:
        Divuserrating.objects.filter(rating=rating_obj, user=request.user).delete()
        agg = Divuserrating.objects.filter(rating=rating_obj).aggregate(avg=Avg("score"), count=Count("id"))
        rating_obj.average = agg["avg"] or 0; rating_obj.count = agg["count"] or 0; rating_obj.save()
    return redirect("serie_episode", tv_url=tv_url, seasonurl=seasonurl, episodeurl=episodeurl)

