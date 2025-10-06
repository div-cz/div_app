# DIVKVARIAT 
# management/commands/auto_complete_sales.py
# python manage.py auto_complete_sales
# 15 4 * * * cd /var/www/div_app && /usr/bin/python3 manage.py auto_complete_sales

from django.core.management.base import BaseCommand
from django.utils.timezone import now, timedelta
from div_content.models import Booklisting
from div_content.views.divkvariat import (
    send_listing_auto_completed_email_buyer,
    send_listing_auto_completed_email_seller,
    send_listing_paid_expired_email_buyer,
    send_listing_paid_expired_email_seller,
)

class Command(BaseCommand):
    help = 'Automaticky dokončí nebo zruší obchody v divkvariátu po určité době'

    def handle(self, *args, **kwargs):
        today = now()
        shipped_limit = today - timedelta(days=10)
        paid_limit = today - timedelta(days=10)

        # 1️⃣ SHIPPED -> COMPLETED
        shipped_listings = Booklisting.objects.filter(
            status='SHIPPED',
            updatedat__lt=shipped_limit
        )
        for listing in shipped_listings:
            listing.status = 'COMPLETED'
            listing.completedat = today
            listing.save(update_fields=['status', 'completedat'])
            print(f"[✔] Automaticky dokončeno (SHIPPED -> COMPLETED): {listing.book.titlecz} (ID {listing.booklistingid})")
            try:
                send_listing_auto_completed_email_buyer(listing)
                send_listing_auto_completed_email_seller(listing)
            except Exception as e:
                print(f"[✖] Chyba při posílání e-mailů: {e}")

        # 2️⃣ PAID -> EXPIRED
        paid_listings = Booklisting.objects.filter(
            status='PAID',
            updatedat__lt=paid_limit
        )
        for listing in paid_listings:
            listing.status = 'EXPIRED'
            #listing.cancelreason = "Prodejce nepotvrdil odeslání knihy včas."
            listing.save(update_fields=['status'])
            print(f"[✔] Automaticky zrušeno (PAID -> EXPIRED): {listing.book.titlecz} (ID {listing.booklistingid})")
            try:
                send_listing_paid_expired_email_buyer(listing)
                send_listing_paid_expired_email_seller(listing)
            except Exception as e:
                print(f"[✖] Chyba při posílání e-mailů: {e}")

        print(f"[?] Dokončeno. Uzavřeno: {len(shipped_listings)} dokončených, {len(paid_listings)} zrušených.")
