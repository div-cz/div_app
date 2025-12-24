# -------------------------------------------------------------------
#                    MODELS.DIVKVARIAT.PY
# -------------------------------------------------------------------

from django.db import models

# models/divkvariat.py

class Divkvariatbookmoodtag(models.Model):
    TAG_TYPES = (
        ('WHEN', 'Kdy číst'),
        ('NOT_FOR', 'Pro koho není'),
    )

    tagid = models.AutoField(primary_key=True, db_column='TagID')
    tagtype = models.CharField(max_length=16, choices=TAG_TYPES, db_column='TagType')
    label = models.CharField(max_length=255, db_column='Label')
    slug = models.SlugField(max_length=255, db_column='Slug', unique=True)

    active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'DivkvariatBookMoodTag'
        ordering = ['order', 'label']

    def __str__(self):
        return self.label

class Divkvariatbookmood(models.Model):
    bookmoodid = models.AutoField(primary_key=True, db_column='BookMoodID')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='BookID', related_name='divkvariat_moods')
    tag = models.ForeignKey('Divkvariatbookmoodtag', on_delete=models.CASCADE, db_column='TagID', related_name='book_links')

    class Meta:
        db_table = 'DivkvariatBookMood'
        unique_together = (('book', 'tag'),)


class Divkvariatbookannotation(models.Model):
    ANNOTATION_TYPES = (
        ('ONELINER', 'Jedna věta, která zůstane'),
        ('EDITOR_NOTE', 'Poznámka divkvariátu'),
        ('KNOWN_FOR', 'Známá tím, že…'),
        ('ADAPTATION', 'Adaptace / zpracování'),
        #('RECOMMENDED_BY', 'Doporučuje'),
        #('AI_NOTE', 'AI poznámka'),
        #('HISTORICAL_CONTEXT', 'Historický kontext'),
        #('WHY_IT_MATTERS', 'Proč je důležitá dnes'),
    )

    annotationid = models.AutoField(primary_key=True, db_column='AnnotationID')
    book = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='BookID', related_name='divkvariat_annotations')
    annotationtype = models.CharField(max_length=32, choices=ANNOTATION_TYPES, db_column='AnnotationType')
    text = models.TextField(db_column='Text')

    active = models.BooleanField(default=True)
    createdat = models.DateTimeField(auto_now_add=True)
    updatedat = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'DivkvariatBookAnnotation'
        unique_together = (('book', 'annotationtype'),)
        indexes = [
            models.Index(fields=['annotationtype']),
            models.Index(fields=['active']),
        ]


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




