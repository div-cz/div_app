# -------------------------------------------------------------------
#                    MODELS.DIVKVARIAT.PY
# -------------------------------------------------------------------


# navrh navrh 

"""
class BookListingTransaction(models.Model):
    listing = models.ForeignKey(Booklisting, on_delete=models.CASCADE)
    
    amount_item = models.DecimalField(max_digits=10, decimal_places=2)
    amount_shipping = models.DecimalField(max_digits=10, decimal_places=2)
    amount_commission = models.DecimalField(max_digits=10, decimal_places=2)
    amount_total = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=[
            ('RESERVED', 'Rezervováno'),
            ('PAID', 'Zaplaceno'),
            ('REFUNDED', 'Vráceno'),
            ('EXPIRED', 'Expirováno'),
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)

    variable_symbol = models.CharField(max_length=20, null=True, blank=True)


class BookListingStatusLog(models.Model):
    listing = models.ForeignKey(Booklisting, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

class BookListingEvent(models.Model):
    listing = models.ForeignKey(Booklisting, on_delete=models.CASCADE)
    event = models.CharField(
        max_length=30,
        choices=[
            ('VIEW', 'Zobrazení'),
            ('RESERVE_CLICK', 'Klik na rezervaci'),
            ('COMPLETED', 'Dokončeno'),
        ]
    )
    source = models.CharField(max_length=50, null=True, blank=True)  # web, email, soc
    created_at = models.DateTimeField(auto_now_add=True)

"""




