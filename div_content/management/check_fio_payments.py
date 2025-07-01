# managements.check_fio_payments
# python manage.py check_fio_payments
# */10 * * * * cd /var/www/div_app && /usr/bin/python3 manage.py check_fio_payments >> /var/log/fio_check.log 2>&1

from django.core.management.base import BaseCommand
from div_content.views.payments import check_payments_from_fio



class Command(BaseCommand):
    help = "Spáruje platby z FIO banky s objednávkami"

    def handle(self, *args, **options):
        check_payments_from_fio()



"""
class Command(BaseCommand):
    help = "Spáruje platby z FIO banky s objednávkami"

    response = requests.get(f"{FIO_API_URL}last/{token}/transactions.json")
    if response.status_code != 200:
        print("FIO API chyba:", response.status_code, response.text)
        return
    
    try:
        data = response.json()
    except Exception as e:
        print("Chyba při parsování JSON z FIO API:", str(e))
        print("Odpověď z FIO:", response.text)
        return
    
    transactions = data.get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
    # ... dál páruj jak doteď ...


    def handle(self, *args, **options):
        check_payments_from_fio()
