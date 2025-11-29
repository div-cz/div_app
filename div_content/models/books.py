# -------------------------------------------------------------------
#                    MODELS.BOOKS.PY
# -------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User



class Book(models.Model):
    bookid = models.AutoField(db_column='BookID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255, db_index=True)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, db_index=True, blank=True, null=True)
    special = models.IntegerField(db_column='Special', db_index=True, blank=True, null=True)
    year = models.IntegerField(db_column='Year', null=True, blank=True)
    pages = models.IntegerField(db_column='Pages', null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=512, blank=True, null=True, db_index=True, unique=True)
    img = models.CharField(db_column='IMG', max_length=255, default="noimg.png")
    subtitle = models.CharField(db_column='Subtitle', max_length=255, blank=True, null=True)
    author = models.CharField(db_column='Author', max_length=255)
    pseudonym = models.CharField(db_column='Pseudonym', max_length=2, null=True, blank=True)
    authorid = models.ForeignKey('Bookauthor', models.DO_NOTHING, db_column='AuthorID', null=True)
    googleid = models.CharField(db_column='GoogleID', max_length=16, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    goodreads = models.CharField(db_column='GoodreadsID', max_length=12, blank=True, null=True)
    sourcetype = models.CharField(max_length=16, db_column='SourceType', null=True, blank=True)
    sourceid = models.CharField(db_column='SourceID', max_length=16, blank=True, null=True)
    language = models.CharField(db_column='Language', max_length=2, null=True, blank=True)
    universumid = models.ForeignKey('Metauniversum', models.DO_NOTHING, db_column='UniversumID', null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    parentid = models.ForeignKey( 'self', db_column='ParentID', null=True, blank=True, on_delete=models.SET_NULL, related_name='editions')

    class Meta:
        db_table = 'Book'

        # indexes = [models.Index(fields=['url'], name='url_book_idx')] 


class Booklisting(models.Model):
    CONDITION_CHOICES = [
        ("nova", "Nová"),
        ("jako-nova", "Použitá, jako nová"),
        ("dobry", "Použitá, dobrý stav"),
        ("zachovaly", "Použitá, zachovalý stav"),
        ("spatny", "Špatný stav"),
    ]
    LISTING_TYPES = (
        ('SELL', 'Prodám'),
        ('BUY', 'Koupím'),
        ('GIVE', 'Daruji'),
    )
    LISTING_STATUS = (
        ('ACTIVE', 'Aktivní'),
        ('RESERVED', 'Rezervováno'),
        ('PAID', 'Zaplaceno'), 
        ('SHIPPED', 'Posláno'),
        ('COMPLETED', 'Dokončeno'),
        ('CANCELLED', 'Zrušeno'),
        ('DELETED', 'Smazáno'),
        ('EXPIRED', 'Expirováno'),
    )
    booklistingid = models.AutoField(db_column='BookListingID', primary_key=True)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, db_column='BuyerID', null=True, blank=True, on_delete=models.SET_NULL, related_name='listings_bought')
    book = models.ForeignKey(Book, db_column='book_id', on_delete=models.CASCADE)
    listingtype = models.CharField(db_column='ListingType', max_length=4, choices=LISTING_TYPES)
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, null=True, blank=True)
    shipping = models.DecimalField(db_column='Shipping', max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Poštovné')
    commission = models.IntegerField(db_column='Commission', verbose_name='Provize na chod webu', default=0)
    personal_pickup = models.BooleanField(db_column='PersonalPickup', verbose_name='Osobní převzetí')
    description = models.TextField(db_column='Description', max_length=512, blank=True, null=True)
    condition = models.CharField(db_column='Condition', max_length=50, choices=CONDITION_CHOICES, blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=True)
    createdat = models.DateTimeField(db_column='CreateDat', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='UpdateDat', auto_now=True)
    completedat = models.DateTimeField(db_column='CompletedAt', null=True, blank=True)
    active = models.BooleanField(db_column='Active', default=True)
    status = models.CharField(db_column='Status', max_length=10, choices=LISTING_STATUS, default='ACTIVE')
    # Shipping
    shippingoptions= models.CharField(db_column='ShippingOptions', max_length=255, blank=True, null=True)
    shippingaddress = models.CharField(db_column='ShippingAddress', max_length=1024, blank=True, null=True)
    # Hodnocení transakce
    sellerrating = models.IntegerField(db_column='SellerRating', null=True, blank=True)
    sellercomment = models.TextField(db_column='SellerComment', max_length=512, blank=True, null=True)
    buyerrating = models.IntegerField(db_column='BuyerRating', null=True, blank=True)
    buyercomment = models.TextField(db_column='BuyerComment', max_length=512, blank=True, null=True)
    # Platba prodejci
    paidtoseller = models.BooleanField(db_column='PaidToSeller', default=False)
    paidat = models.DateTimeField(db_column='PaidAt', null=True, blank=True)
    amounttoseller = models.DecimalField(db_column='AmountToSeller', max_digits=8, decimal_places=2, null=True, blank=True)
    requestpayout = models.BooleanField(db_column='RequestPayout', default=False)

    class Meta:
        db_table = 'BookListing'


class Bookauthor(models.Model):
    authorid = models.AutoField(db_column='AuthorID', primary_key=True)
    firstname = models.CharField(db_column='FirstName', max_length=255)
    middlename = models.CharField(db_column='MiddleName', max_length=255, null=True, blank=True)
    lastname = models.CharField(db_column='LastName', max_length=255)
    description = models.CharField(db_column='Description', max_length=2048, null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=512, null=True, blank=True)
    main = models.CharField(db_column='Main', max_length=2, null=True, blank=True)
    alias = models.CharField(db_column='Alias', max_length=2, null=True, blank=True)
    favorites = models.IntegerField(db_column='Favorites', null=True, blank=True)
    birthyear = models.CharField(db_column='BirthYear', max_length=5, null=True, blank=True)
    birthdate = models.DateField(db_column='BirthDate', null=True, blank=True)
    deathyear = models.CharField(db_column='DeathYear', max_length=5, null=True, blank=True)
    deathdate = models.DateField(db_column='DeathDate', null=True, blank=True)
    goodreads = models.CharField(db_column='GoodreadsID', max_length=12, blank=True, null=True)
    databazeknih = models.CharField(db_column='DatabazeKnih', max_length=16, blank=True, null=True)
    img = models.CharField(db_column='IMG', max_length=32, null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)
    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'BookAuthor'



class Bookcharacter(models.Model):
    bookcharacterid = models.AutoField(db_column='BookCharacterID', primary_key=True)
    charactermain = models.CharField(db_column='CharacterMain', max_length=2, null=True, blank=True)
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookCharacter'
    def __str__(self):
        return self.characterid.charactername


class Bookcomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True, unique=True) 
    comment = models.TextField(db_column='Comment')
##    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)
    class Meta:
        db_table = 'BookComments'



class Bookcover(models.Model):
    bookcoverid = models.AutoField(db_column='BookCoverID', primary_key=True)
    bookid = models.IntegerField(db_column='BookID')
    cover = models.CharField(db_column='Cover', max_length=255)

    class Meta:
        db_table = 'BookCover'



class Bookisbn(models.Model):
    bookisbnid = models.AutoField(db_column='BookISBNID', primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    isbn = models.CharField(max_length=26, unique=True, db_column='ISBN')
    ISBNtype = models.CharField(max_length=255, null=True, blank=True, db_column='ISBNtype')
    publisherid = models.ForeignKey('Metapublisher', models.DO_NOTHING, db_column='PublisherID', null=True)
    publicationyear = models.IntegerField(null=True, blank=True, db_column='PublicationYear')
    format = models.CharField(max_length=100, null=True, blank=True, db_column='Format') # e.g., Hardcover, Paperback, eBook
    price = models.DecimalField(max_digits=10, decimal_places=2, db_column='Price', null=True, blank=True) 
    language = models.CharField(max_length=100, null=True, blank=True, db_column='Language') # e.g., English, Czech
    description = models.TextField(null=True, blank=True, db_column='Description')
    url = models.CharField(max_length=255, null=True, blank=True, db_column='URL') 
    coverimage = models.URLField(max_length=200, null=True, blank=True, db_column='CoverIMG')
    sourcetype = models.CharField(max_length=16, db_column='SourceType', null=True, blank=True)
    sourceid = models.CharField(max_length=64, db_column='SourceID', null=True, blank=True)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    class Meta:
        db_table = 'BookISBN'




class Booklocation(models.Model):
    booklocationid = models.AutoField(db_column='BookLocationID', primary_key=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookLocation'



class Bookpublisher(models.Model):
    publisherid = models.IntegerField(db_column='PublisherID', primary_key=True)
    publishername = models.CharField(db_column='PublisherName', max_length=255, unique=True)
    publisherurl = models.CharField(db_column='PublisherURL', max_length=255, null=True, blank=True)
    publisherdescription = models.CharField(db_column='PublisherDescription', max_length=512, null=True, blank=True)
    publisherwww = models.CharField(db_column='PublisherWWW', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'BookPublisher'


class Bookpurchase(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Čeká na platbu'),
        ('PAID', 'Zaplaceno'),
        ('CANCELLED', 'Zrušeno'),
    )
    
    purchaseid = models.AutoField(db_column='PurchaseID', primary_key=True)
    purchasedate = models.DateField(db_column='PurchaseDate', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    format = models.CharField(db_column='Format', max_length=10, choices=[('mobi', 'MOBI'), ('pdf', 'PDF'), ('epub', 'EPUB')])
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)
    sourcetype = models.CharField(max_length=20, null=True, blank=True)  # např. "PALM", "DIV"
    sourceid = models.CharField(max_length=255, null=True, blank=True)   #  ID u Palmknih
    orderdate = models.DateTimeField(db_column='OrderDate', auto_now_add=True)
    paymentdate = models.DateTimeField(db_column='PaymentDate', null=True, blank=True)
    expirationdate = models.DateTimeField(db_column='ExpirationDate', null=True, blank=True)
    shippingaddress = models.CharField(db_column='ShippingAddress', max_length=1024, blank=True, null=True)
    kindlemail = models.EmailField(db_column='KindleEmail', blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=10, choices=STATUS_CHOICES, default='PENDING')
    cancelreason = models.TextField(db_column='CancelReason', max_length=512, blank=True, null=True)  # Důvod zrušení/reklamace

    class Meta:
        db_table = 'BookPurchase'

class Booksource(models.Model):
    booksourceid = models.AutoField(db_column='BookSourceID', primary_key=True)
    bookid = models.ForeignKey('Book', models.DO_NOTHING, db_column='BookID', null=True, blank=True)
    sourcetype = models.CharField(db_column='SourceType', max_length=20)
    externalid = models.CharField(db_column='ExternalID', max_length=100)
    externaltitle = models.CharField(db_column='ExternalTitle', max_length=2048, null=True, blank=True)
    externalauthors = models.CharField(db_column='ExternalAuthors', max_length=2048, null=True, blank=True)
    externalurl = models.CharField(db_column='ExternalURL', max_length=1024)
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)

    class Meta:
        db_table = 'BookSource'
        unique_together = (('sourcetype', 'externalid'),)


class Bookquotes(models.Model):
    quoteid = models.AutoField(db_column='QuoteID', primary_key=True)
    bookid = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='BookID')
    characterid = models.ForeignKey('Charactermeta', on_delete=models.CASCADE, db_column='CharacterID', null=True, blank=True)
    authorid = models.ForeignKey('Bookauthor', on_delete=models.CASCADE, db_column='AuthorID', null=True, blank=True)
    quote = models.TextField(db_column='Quote')
    chapter = models.IntegerField(db_column='Chapter', null=True, blank=True)  # Přidané pole pro stránku
    parentquoteid = models.ForeignKey('self', on_delete=models.CASCADE, db_column='ParentQuoteID', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)  # Přidaný cizí klíč na uživatele
    thumbsup = models.IntegerField(default=0, db_column='ThumbsUp')
    thumbsdown = models.IntegerField(default=0, db_column='ThumbsDown')
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'BookQuotes'
    def __str__(self):
        return self.quote


class Bookrating(models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    comment = models.TextField(db_column='Comment')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookRating'


class Bookwriters(models.Model):
    bookwriterid = models.AutoField(db_column='BookWriterID', primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    author = models.ForeignKey(Bookauthor, on_delete=models.CASCADE, db_column='AuthorID')

    class Meta:
        db_table = 'BookWriters'
        unique_together = (('book', 'author'),)






