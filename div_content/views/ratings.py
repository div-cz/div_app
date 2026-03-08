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

from div_content.models import Movie
from div_content.models.meta import Divrating, Divuserrating


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

    return redirect("movie_detail", movie_url=movie.url)


