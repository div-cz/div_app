# -------------------------------------------------------------------
#                    VIEWS.GAMEKVARIAT.PY
# -------------------------------------------------------------------

from django.core.paginator import Paginator
from django.shortcuts import render
from div_content.models import Gamelisting  # předpokládám, že máš model Gamelisting (podobně jako Booklisting)

# -------------------------------------------------------------------
# F:                 GAME MARKET - OFFERS
# -------------------------------------------------------------------
def games_market_offers(request):
    # nabídky k prodeji/daru
    offer_listings = (
        Gamelisting.objects
        .filter(listingtype__in=["SELL", "GIVE"], active=True, status="ACTIVE")
        .select_related("game", "user")
        .order_by("-createdat")
    )

    paginator = Paginator(offer_listings, 12)
    page = request.GET.get("page")
    listings = paginator.get_page(page)

    return render(request, "games/games_market_offers.html", {
        "listings": listings
    })


# -------------------------------------------------------------------
# F:                 GAME MARKET - WANTS
# -------------------------------------------------------------------
def games_market_wants(request):
    # poptávky
    want_listings = (
        Gamelisting.objects
        .filter(listingtype="BUY", active=True, status="ACTIVE")
        .select_related("game", "user")
        .order_by("-createdat")
    )

    paginator = Paginator(want_listings, 12)
    page = request.GET.get("page")
    listings = paginator.get_page(page)

    return render(request, "games/games_market_wants.html", {
        "listings": listings
    })
