# managements.check_fio_payments
# python manage.py check_fio_payments
# */10 * * * * cd /var/www/div_app && /usr/bin/python3 manage.py check_fio_payments >> /var/log/fio_check.log 2>&1



from django.core.management.base import BaseCommand
from div_content.views.payments import check_payments_from_fio

class Command(BaseCommand):
    help = "Spáruje platby z FIO banky s objednávkami"

    def handle(self, *args, **options):
        check_payments_from_fio()
