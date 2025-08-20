# management/commands/auto_complete_sales.py
# python manage.py auto_complete_sales
# 15 4 * * * cd /var/www/div_app && /usr/bin/python3 manage.py auto_complete_sales

# DIVKVARIAT 

from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from div_content.models import Booklisting
from div_content.views.divkvariat import (
    send_listing_auto_completed_email_buyer,
    send_listing_auto_completed_email_seller,
)

class Command(BaseCommand):
    help = 'Automaticky dokončí zaplacené obchody v divkvariátu po 10 dnech'

    def handle(self, *args, **kwargs):
        # Obchody, které jsou 10+ dní zaplaceny, ale nejsou dokončené
        completion_limit = now() - timedelta(days=10)
        listings = Booklisting.objects.filter(
            status='PAID',
            updatedat__lt=completion_limit
        )

        for listing in listings:
            book = listing.book
            buyer = listing.buyer
            seller = listing.user

            print(f"[!] Automatické dokončení: {book.titlecz} (ID {listing.booklistingid})")

            # Nastavení stavu na COMPLETED
            listing.status = 'COMPLETED'
            listing.completedat = now()
            listing.save()

            # Poslání e-mailů
            try:
				send_listing_auto_completed_email_buyer(listing)
				send_listing_auto_completed_email_seller(listing)
                print(f"[✔] E-maily o dokončení obchodu odeslány (kupující + prodávající).")
            except Exception as e:
                print(f"[✖] Chyba při odesílání e-mailů: {e}")

        print(f"[?] Dokončeno. Uzavřeno: {len(listings)} obchodů.")
