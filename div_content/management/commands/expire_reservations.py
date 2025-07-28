# management/commands/expire_reservations.py
# python manage.py expire_reservations
# 30 3 * * * cd /var/www/div_app && /usr/bin/python3 manage.py expire_reservations

from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from div_content.models import Booklisting
from div_content.views.divkvariat import send_listing_cancel_email
from django.contrib.auth.models import AnonymousUser

class Command(BaseCommand):
    help = 'Zruší expirované rezervace (např. starší než 7 dny)'

    def handle(self, *args, **kwargs):
        expiration_limit = now() - timedelta(days=7)
        listings = Booklisting.objects.filter(status='RESERVED', updatedat__lt=expiration_limit)

        for listing in listings:
            book = listing.book
            buyer = listing.buyer

            print(f"[!] Expirace rezervace: {book.titlecz} (ID {listing.booklistingid})")

            # Změna stavu zpět na ACTIVE
            listing.status = 'ACTIVE'
            listing.buyer = None
            listing.cancelreason = "Rezervace expirovala – nebyla uhrazena včas."
            listing.save()

            book.status = 'ACTIVE'
            book.save()

            # Pošli kupujícímu e-mail
            if buyer:
                send_listing_cancel_email(request=AnonymousUser(), listing=listing)

        print(f"[?] Dokončeno. Zrušeno: {len(listings)} rezervací.")
