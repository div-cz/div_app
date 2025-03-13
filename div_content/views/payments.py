import requests
from django.utils.timezone import now
from div_content.models import Bookpurchase

FIO_API_URL = "https://www.fio.cz/ib_api/rest/"

def check_payments():
    """FIO API"""
    token = "FIO_TOKEN"  # Uloženo v .env
    response = requests.get(f"{FIO_API_URL}last/{token}/transactions.json")
    
    if response.status_code == 200:
        transactions = response.json().get("accountStatement", {}).get("transactionList", {}).get("transaction", [])
        
        for tx in transactions:
            vs = tx.get("variableSymbol")
            amount = tx.get("amount")
            
            # Platbu podle VS
            purchase = Bookpurchase.objects.filter(purchaseid=vs, status="PENDING").first()
            if purchase and float(purchase.price) == float(amount):
                purchase.status = "PAID"
                purchase.paymentdate = now()
                purchase.expirationdate = now().replace(year=now().year + 3)  # Platnost 3 roky
                purchase.save()

                print(f"Platba potvrzena pro ID {vs}")

    return "Kontrola dokončena"
