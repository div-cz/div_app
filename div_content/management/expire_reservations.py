# management/commands/expire_reservations.py
# python manage.py expire_reservations
# 30 3 * * * cd /var/www/div_app && /usr/bin/python3 manage.py expire_reservations

from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from div_content.models import Booklisting
from div_content.views.divkvariat import send_listing_cancel_email
from django.contrib.auth.models import AnonymousUser

class Command(BaseCommand):
    help = 'Zru�� expirovan� rezervace (nap�. star�� ne� 7 dny)'

    def handle(self, *args, **kwargs):
        expiration_limit = now() - timedelta(days=7)
        listings = Booklisting.objects.filter(status='RESERVED', updatedat__lt=expiration_limit)

        for listing in listings:
            book = listing.book
            buyer = listing.buyer

            print(f"[!] Expirace rezervace: {book.titlecz} (ID {listing.booklistingid})")

            # Zm�na stavu zp�t na ACTIVE
            listing.status = 'ACTIVE'
            listing.buyer = None
            listing.cancelreason = "Rezervace expirovala � nebyla uhrazena v�as."
            listing.save()

            book.status = 'ACTIVE'
            book.save()

            # Po�li kupuj�c�mu e-mail
            if buyer:
                send_listing_cancel_email(request=AnonymousUser(), listing=listing)

        print(f"[?] Dokon�eno. Zru�eno: {len(listings)} rezervac�.")
