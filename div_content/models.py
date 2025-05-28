# Test
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.models import User 

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from star_ratings.models import AbstractBaseRating, Rating
from django.utils.text import slugify
from django.utils import timezone



class AAChange(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    description = models.TextField(db_column='Description')
    created = models.DateField(db_column='Created')
    class Meta:
        db_table = 'AAChange'

class AATask(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    parentid = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='ParentID', related_name='Subtasks')
    title = models.CharField(db_column='Title', max_length=255)
    description = models.TextField(db_column='Description')
    comments = models.TextField(db_column='Comments', blank=True, null=True) 
    assigned = models.CharField(db_column='Assigned', max_length=64, blank=True, null=True)
    Creator = models.CharField(db_column='Creator', max_length=64, blank=True, null=True)
    status = models.CharField(
        db_column='Status',
        max_length=16,
        choices=[
            ('Ke zpracování', 'Ke zpracování'),
            ('Probíhá', 'Probíhá'),
            ('Hotovo', 'Hotovo'),
            ('Nice to have', 'Nice to have')
        ],
        default='Ke zpracování'
    )
    priority = models.CharField(
        db_column='Priority',
        max_length=16,
        choices=[
            ('Vysoká', 'Vysoká'),
            ('Střední', 'Střední'),
            ('Nízká', 'Nízká'),
            ('Nice to have', 'Nice to have')
        ],
        default='Střední'
    )
    category = models.CharField(
        db_column='Category',
        max_length=16,
        choices=[
            ('Knihy', 'Knihy'),
            ('Hry', 'Hry'),
            ('Filmy', 'Filmy'),
            ('eShop', 'eShop'),
            ('Server', 'Server'),
            ('Ostatní', 'Ostatní')
        ],
        default='Knihy'
    )
    IPaddress = models.CharField(db_column='IPaddress', max_length=64, null=True, blank=True)

    updated = models.DateField(db_column='Updated', auto_now=True)
    created = models.DateField(db_column='Created', auto_now_add=True)
    duedate = models.DateField(db_column='DueDate', default='2025-10-10')

    class Meta:
        db_table = 'AATasks'
        
        



class Article(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    url = models.CharField(db_column='URL', max_length=255)
    title = models.CharField(db_column='Title', max_length=255)
    h1 = models.CharField(db_column='H1', max_length=255)
    h2 = models.CharField(db_column='H2', max_length=255)
    tagline = models.CharField(db_column='Tagline', max_length=64)
    content = models.TextField(db_column='Content')
    menu = models.TextField(db_column='Menu', null=True, blank=True)
    youtube = models.CharField(db_column='Youtube', max_length=20, null=True, blank=True)
    img1600 = models.CharField(db_column='Img1600', max_length=255)
    img = models.CharField(db_column='IMG', max_length=32, null=True, blank=True)
    img400x250 = models.CharField(db_column='Img400x250', max_length=255)
    alt = models.CharField(db_column='Alt', max_length=255)
    perex = models.CharField(db_column='Perex', max_length=255)
    autor = models.CharField(db_column='Autor', max_length=255)
    typ = models.CharField(db_column='Typ', max_length=50)
    counter = models.IntegerField(db_column='Counter')
    created = models.DateField(db_column='Created')
    updated = models.DateField(db_column='Updated')

    class Meta:
        db_table = 'Article'


# ArticleBlog - Tabulka pro blogy
class Articleblog(models.Model):
    BLOG_TYPE_CHOICES = [
        ('book', 'Knižní'),
        ('game', 'Herní'),
        ('movie', 'Filmový'),
        ('general', 'Obecný'),
    ]

    articleblogid = models.AutoField(db_column='ArticleBlogID', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255)
    description = models.TextField(db_column='Description', null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', related_name='blogs')
    slug = models.SlugField(db_column='Slug', unique=True, max_length=255)
    blog_type = models.CharField(db_column='BlogType', max_length=10, choices=BLOG_TYPE_CHOICES, default='general')
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UpdatedAt', auto_now=True)

    class Meta:
        db_table = 'ArticleBlog'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug = slugify(self.name)
        unique_slug = slug
        num = 2
        while Articleblog.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug


# ArticleBlogPost - Tabulka pro příspěvky v blogu
class Articleblogpost(models.Model):
    articleblogpostid = models.AutoField(db_column='ArticleBlogPostID', primary_key=True)
    articleblog = models.ForeignKey(Articleblog, on_delete=models.CASCADE, db_column='ArticleBlogID', related_name='posts')
    title = models.CharField(db_column='Title', max_length=255)
    slug = models.SlugField(db_column='Slug', max_length=255, null=True, blank=True, unique=True)
    content = models.TextField(db_column='Content')
    category = models.CharField(db_column='Category', max_length=100, null=True, blank=True)
    published_at = models.DateTimeField(db_column='PublishedAt', auto_now_add=True)
    tags = models.CharField(db_column='Tags', max_length=255, null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updated_at = models.DateTimeField(db_column='UpdatedAt', auto_now=True)
    is_public = models.BooleanField(db_column='IsPublic', default=True)

    class Meta:
        db_table = 'ArticleBlogPost'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 2
        while Articleblogpost.objects.filter(slug=unique_slug).exists():
            unique_slug = f'{slug}-{num}'
            num += 1
        return unique_slug


# ArticleBlogComment - Tabulka pro komentáře k blogovým příspěvkům
class Articleblogcomment(models.Model):
    articleblogcommentid = models.AutoField(db_column='ArticleBlogCommentID', primary_key=True)
    articleblogpost = models.ForeignKey(Articleblogpost, on_delete=models.CASCADE, db_column='ArticleBlogPostID', related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    content = models.TextField(db_column='Content')
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)

    class Meta:
        db_table = 'ArticleBlogComment'

    def __str__(self):
        return f'Comment by {self.user.username}'


# ArticleInteraction - Tabulka pro interakce s příspěvky (např. lajky, sdílení)
class Articleinteraction(models.Model):
    articleinteractionid = models.AutoField(db_column='ArticleInteractionID', primary_key=True)
    articleblogpost = models.ForeignKey(Articleblogpost, on_delete=models.CASCADE, db_column='ArticleBlogPostID', related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID')
    interaction_type = models.CharField(db_column='InteractionType', max_length=50)  # Typ interakce (like 1, dislike 2, etc.)
    created_at = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)

    class Meta:
        db_table = 'ArticleInteraction'

    def __str__(self):
        return f'{self.interaction_type} by {self.user.username}'


class Articlenews(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    url = models.CharField(db_column='URL', max_length=255)
    title = models.CharField(db_column='Title', max_length=255)
    news = models.CharField(db_column='News', max_length=1024)
    img = models.CharField(db_column='IMG', max_length=32, null=True, blank=True)
    alt = models.CharField(db_column='Alt', max_length=64)
    perex = models.CharField(db_column='Perex', max_length=128)
    source = models.CharField(db_column='Source', max_length=32)
    typ = models.CharField(db_column='Typ', max_length=16)
    counter = models.IntegerField(db_column='Counter', default=1)
    created = models.DateField(db_column='Created', auto_now_add=True)
    updated = models.DateField(db_column='Updated', auto_now=True)
    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', blank=True, null=True)

    class Meta:
        db_table = 'ArticleNews'


class Articlenewsassociation(models.Model):
    articlenewsassociationd = models.AutoField(db_column='ArticleNewsAssociationID', primary_key=True)
    news = models.ForeignKey(Articlenews, on_delete=models.CASCADE, db_column='NewsID')
    contenttype = models.CharField(max_length=50, db_column='ContentType')
    objectid = models.IntegerField(db_column='ObjectID')
    
    class Meta:
        db_table = 'ArticleNewsAssociation'
        unique_together = ('news', 'contenttype', 'objectid')



class Avatar(models.Model):
    avatarid = models.AutoField(db_column='AvatarID', primary_key=True)
    imagepath = models.CharField(db_column='ImagePath', max_length=255)
    name = models.CharField(db_column='Name', max_length=100)
    class Meta:
        db_table = 'Avatar'
    def __str__(self):
        return str(self.name)


class Book(models.Model):
    bookid = models.AutoField(db_column='BookID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255, db_index=True)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, db_index=True, blank=True, null=True)
    special = models.IntegerField(db_column='Special', db_index=True, blank=True, null=True)
    year = models.IntegerField(db_column='Year', null=True, blank=True)
    pages = models.IntegerField(db_column='Pages', null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=512, blank=True, null=True, db_index=True)
    img = models.CharField(db_column='IMG', max_length=255, default="noimg.png")
    subtitle = models.CharField(db_column='Subtitle', max_length=255, blank=True, null=True)
    author = models.CharField(db_column='Author', max_length=255)
    pseudonym = models.CharField(db_column='Pseudonym', max_length=2, null=True, blank=True)
    authorid = models.ForeignKey('Bookauthor', models.DO_NOTHING, db_column='AuthorID', null=True)
    googleid = models.CharField(db_column='GoogleID', max_length=16, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    goodreads = models.CharField(db_column='GoodreadsID', max_length=12, blank=True, null=True)
    databazeknih = models.CharField(db_column='SourceID', max_length=16, blank=True, null=True)
    language = models.CharField(db_column='Language', max_length=2, null=True, blank=True)
    universumid = models.ForeignKey('Metauniversum', models.DO_NOTHING, db_column='UniversumID', null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'Book'

        # indexes = [models.Index(fields=['url'], name='url_book_idx')] 


class Booklisting(models.Model):
    LISTING_TYPES = (
        ('SELL', 'Prodám'),
        ('BUY', 'Koupím'),
        ('GIVE', 'Daruji'),
    )
    LISTING_STATUS = (
        ('ACTIVE', 'Aktivní'),
        ('RESERVED', 'Rezervováno'),
        ('COMPLETED', 'Dokončeno'),
        ('CANCELLED', 'Zrušeno'),
        ('DELETED', 'Smazáno'),
    )
    booklistingid = models.AutoField(db_column='BookListingID', primary_key=True)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, db_column='BuyerID', null=True, blank=True, on_delete=models.SET_NULL, related_name='listings_bought')
    book = models.ForeignKey(Book, db_column='book_id', on_delete=models.CASCADE)
    listingtype = models.CharField(db_column='ListingType', max_length=4, choices=LISTING_TYPES)
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, null=True, blank=True)
    shipping = models.DecimalField(db_column='Shipping', max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Poštovné')
    commission = models.IntegerField(db_column='Commission', verbose_name='Provize na chod webu')
    personal_pickup = models.BooleanField(db_column='PersonalPickup', verbose_name='Osobní převzetí')
    description = models.TextField(db_column='Description', max_length=512, blank=True, null=True)
    condition = models.CharField(db_column='Condition', max_length=50, blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=True)
    createdat = models.DateTimeField(db_column='CreateDat', auto_now_add=True)
    completedat = models.DateTimeField(db_column='CompletedAt', null=True, blank=True)
    active = models.BooleanField(db_column='Active', default=True)
    status = models.CharField(db_column='Status', max_length=10, choices=LISTING_STATUS, default='ACTIVE')
    # Hodnocení transakce
    sellerrating = models.IntegerField(db_column='SellerRating', null=True, blank=True)
    sellercomment = models.TextField(db_column='SellerComment', max_length=512, blank=True, null=True)
    buyerrating = models.IntegerField(db_column='BuyerRating', null=True, blank=True)
    buyercomment = models.TextField(db_column='BuyerComment', max_length=512, blank=True, null=True)
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
    coverimage = models.URLField(max_length=200, null=True, blank=True, db_column='CoverIMG')
    palmknihyid = models.CharField(max_length=64, db_column='PalmknihyID', null=True, blank=True) 
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
    orderdate = models.DateTimeField(db_column='OrderDate', auto_now_add=True)
    paymentdate = models.DateTimeField(db_column='PaymentDate', null=True, blank=True)
    expirationdate = models.DateTimeField(db_column='ExpirationDate', null=True, blank=True)  # Např. 3 roky od nákupu
    kindlemail = models.EmailField(db_column='KindleEmail', blank=True, null=True)
    status = models.CharField(db_column='Status', max_length=10, choices=STATUS_CHOICES, default='PENDING')
    cancelreason = models.TextField(db_column='CancelReason', max_length=512, blank=True, null=True)  # Důvod zrušení/reklamace

    class Meta:
        db_table = 'BookPurchase'



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




class Characterbiography(models.Model):
    biographyid = models.AutoField(primary_key=True)
    characterid = models.ForeignKey('Charactermeta', on_delete=models.CASCADE, db_column='CharacterID', related_name='biographies')
    characterborn = models.CharField(db_column='CharacterBorn', max_length=16, blank=True, null=True)
    characterdeath = models.CharField(db_column='CharacterDeath', max_length=16, blank=True, null=True)
    biographytext = models.TextField(db_column='BiographyText', blank=True, null=True)
    biographytextcz = models.TextField(db_column='BiographyTextCZ', blank=True, null=True)
    source = models.CharField(db_column='Source', max_length=255, blank=True, null=True)

    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    language = models.CharField(db_column='Language', max_length=10, default='en')
    externallink = models.URLField(db_column='ExternalLink', blank=True, null=True)
    img = models.URLField(db_column='IMG', blank=True, null=True)
    notes = models.TextField(db_column='Notes', blank=True, null=True)
    author = models.CharField(db_column='Author', max_length=255, blank=True)
    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    verificationstatus = models.CharField(
        db_column='VerificationStatus',
        max_length=10,
        choices=[
            ('Verified', 'Verified'),
            ('Unverified', 'Unverified'),
            ('Pending', 'Pending')
        ],
        default='Unverified'
    )
    is_primary = models.BooleanField(db_column='IsPrimary', default=False)

    class Meta:
        db_table = 'CharacterBiography'




class Charactergame(models.Model):
    gamecharacterid = models.AutoField(db_column='GameCharacterID', primary_key=True)
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'CharacterGame'


class Charactermeta(models.Model):
    characterid = models.AutoField(db_column='CharacterID', primary_key=True)
    charactername = models.CharField(db_column='CharacterName', max_length=255, null=True, blank=True, db_index=True)
    characternamecz = models.CharField(db_column='CharacterNameCZ', max_length=255, null=True, blank=True)
    characterimg = models.CharField(db_column='CharacterIMG', max_length=128, null=True)
    characterbio = models.CharField(db_column='CharacterBio', null=True, blank=True, max_length=1)
    characterurl = models.URLField(db_column='CharacterURL', max_length=255, null=True, blank=True, unique=True) 
    charactercount = models.IntegerField(db_column='CharacterCount', null=True, blank=True)

    class Meta:
        db_table = 'CharacterMeta'


class Charactermovie(models.Model):
    moviecharacterid = models.AutoField(db_column='MovieCharacterID', primary_key=True)
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'CharacterMovie'


class Charactertvshow(models.Model):
    tvshowcharacterid = models.AutoField(db_column='TVShowCharacterID', primary_key=True)
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')

    class Meta:
        db_table = 'CharacterTVShow'


class Comments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
    comment_date = models.DateField(db_column='CommentDate')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)   

    class Meta:
        db_table = 'Comments'


class Creator(models.Model):
    creatorid = models.IntegerField(db_column='CreatorID', primary_key=True)
    firstname = models.CharField(db_column='FirstName', max_length=255)
    lastname = models.CharField(db_column='LastName', max_length=255)
    url = models.CharField(db_column='URL', max_length=512, null=True, blank=True, unique=True)
    url2 = models.CharField(db_column='URL2', max_length=512, null=True, blank=True)
    birthdate = models.DateField(db_column='BirthDate', null=True, blank=True)
    deathdate = models.DateField(db_column='DeathDate', null=True, blank=True)
    imdbid = models.CharField(db_column='Imdb_id', max_length=16, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    popularity = models.IntegerField(db_column='Popularity', null=True)
    img = models.CharField(db_column='IMG', max_length=32, null=True)
    knownfordepartment = models.CharField(db_column='KnownForDepartment', max_length=255, null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)
    gender = models.IntegerField(db_column='Gender', null=True, blank=True, default=0) 
    adult = models.IntegerField(db_column='Adult', default="0")

    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

    class Meta:
        db_table = 'Creator'
        indexes = [
            models.Index(fields=['url'], name='url_idx'),
        ]


class Creatorbiography(models.Model):
    biographyid = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, db_column='CreatorID', related_name='biographies')
    biographytext = models.TextField(db_column='BiographyText', null=True, blank=True)
    biographytextcz = models.TextField(db_column='BiographyTextCZ', null=True, blank=True)
    source = models.CharField(db_column='Source', max_length=255, blank=True)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    language = models.CharField(db_column='Language', max_length=10, default='en')
    externallink = models.URLField(db_column='ExternalLink', blank=True)
    imageurl = models.URLField(db_column='ImageURL', blank=True)
    notes = models.TextField(db_column='Notes', blank=True)
    author = models.CharField(db_column='Author', max_length=255, blank=True)
    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    verificationstatus = models.CharField(
        db_column='VerificationStatus',
        max_length=10,
        choices=[
            ('Verified', 'Verified'),
            ('Unverified', 'Unverified'),
            ('Pending', 'Pending')
        ],
        default='Unverified'
    )
    is_primary = models.BooleanField(db_column='IsPrimary', default=False)

    class Meta:
        db_table = 'CreatorBiography'




class Creatorrole(models.Model):
    roleid = models.IntegerField(db_column='RoleID', primary_key=True)
    rolename = models.CharField(db_column='RoleName', max_length=255)
    rolenamecz = models.CharField(db_column='RoleNameCZ', max_length=255, blank=True)
    department = models.CharField(db_column='Department', max_length=255, blank=True)
    class Meta:

        db_table = 'CreatorRole'


class Drink(models.Model):
    drinkid = models.AutoField(db_column='DrinkID', primary_key=True)
    drinkname = models.CharField(db_column='DrinkName', max_length=255)
    drinkurl = models.CharField(db_column='DrinkURL', max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(db_column='Description')
    drinktype = models.CharField(db_column='DrinkType', max_length=255, null=True, blank=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'Drink'


class Drinkmedia(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    mediatype = models.IntegerField(db_column='MediaType')
    drinkid = models.ForeignKey(Drink, models.DO_NOTHING, db_column='DrinkID')

    class Meta:
        db_table = 'DrinkMedia'


class Favorite(models.Model):
    favoriteid = models.AutoField(db_column='FavoriteID', primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'Favorite'
        unique_together = ('user', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.user} favorites {self.content_object}"

class FavoriteSum(models.Model):
    favorite_sum_id = models.AutoField(primary_key=True)  # Primární klíč
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)  # Typ objektu
    object_id = models.PositiveIntegerField()  # ID objektu v příslušné tabulce
    content_object = GenericForeignKey('content_type', 'object_id')  # Vazba na objekt
    favorite_count = models.PositiveIntegerField(default=0)  # Počet oblíbených
    last_updated = models.DateTimeField(auto_now=True)  # Datum poslední aktualizace

    class Meta:
        db_table = 'FavoriteSum'
        unique_together = ('content_type', 'object_id')  # Unikátní záznam pro každý objekt

    def __str__(self):
        return f"FavoriteSum for {self.content_object} (Count: {self.favorite_count})"


class Food(models.Model):
    foodid = models.AutoField(db_column='FoodID', primary_key=True)
    foodname = models.CharField(db_column='FoodName', max_length=255)
    foodurl = models.CharField(db_column='FoodURL', max_length=255, unique=True, null=True, blank=True)
    description = models.TextField(db_column='Description')
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'Food'


class Foodmedia(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    mediatype = models.IntegerField(db_column='MediaType')
    foodid = models.ForeignKey(Food, models.DO_NOTHING, db_column='FoodID')

    class Meta:
        db_table = 'FoodMedia'


class Forumsection(models.Model):
    forumsectionid = models.AutoField(db_column='ForumSectionID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255, unique=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    slug = models.SlugField(db_column='Slug', max_length=255, unique=True, blank=True, null=True)
    imageurl = models.CharField(db_column='ImageURL', max_length=200, blank=True, null=True, help_text="Image URL")

    class Meta:
        db_table = 'ForumSection'
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Forumtopic(models.Model):
    forumtopicid = models.AutoField(db_column='ForumTopicID', primary_key=True)
    section = models.ForeignKey(Forumsection, on_delete=models.CASCADE)
    title = models.CharField(db_column='Title', max_length=255, unique=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    createdat = models.DateTimeField(db_column='Created_at', auto_now_add=True)
    topicurl = models.SlugField(db_column='URL', max_length=255, unique=True)

    class Meta:
        db_table = 'ForumTopic'
    
    def save(self, *args, **kwargs):
        self.url = slugify(self.title)
        super().save(*args, **kwargs)

class Forumcomment(models.Model):
    forumcommentid = models.AutoField(db_column='ForumCommentID', primary_key=True)
    topic = models.ForeignKey(Forumtopic, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    body = models.TextField()
    createdat = models.DateTimeField(db_column='Created_at', auto_now_add=True)
    lasteditedat = models.DateTimeField(db_column='LastEditedAt', null=True, blank=True)
    parentcommentid = models.IntegerField(db_column='ParentCommentID', blank=True, null=True)
    isdeleted = models.BooleanField(db_column='IsDeleted', default=False)

    class Meta:
        db_table = 'ForumComment'

    def secret_delete(self):
        self.isdeleted = True
        self.save()


class Game(models.Model):
    gameid = models.AutoField(db_column='GameID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, null=True, blank=True)
    special = models.IntegerField(db_column='Special', db_index=True, blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, null=True, blank=True)
    img = models.CharField(db_column='IMG', max_length=255,  null=True, blank=True)
    rawgid = models.IntegerField(db_column='RawgID', null=True, blank=True)
    metacritic = models.IntegerField(db_column='MetaCritic', null=True, blank=True)
    descriptioncz = models.TextField(db_column='DescriptionCZ', null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    systemrequirements = models.TextField(db_column='SystemRequirements', null=True, blank=True)
    year = models.IntegerField(db_column='Year', null=True, blank=True)
    universumid = models.ForeignKey('Metauniversum', models.DO_NOTHING, db_column='UniversumID', null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True, blank=True)
    averageratinggame = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRatingGame')
    divrating = models.IntegerField(db_column='DIVRating', default=0, db_index=True)

    class Meta:
        db_table = 'Game'

    def __str__(self):
        return self.titlecz or self.title


class Gamecomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)   
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)

    class Meta:
        db_table = 'GameComments'

class Gamedevelopers(models.Model):
    gamedeveloperid = models.AutoField(db_column='GameDeveloperID', primary_key=True)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
    developerid = models.ForeignKey('Metadeveloper', models.DO_NOTHING, db_column='DeveloperID')

    class Meta:
        db_table = 'GameDevelopers'
    def __str__(self):
        return str(self.developerid) 

class Gameseason(models.Model):
    seasonid = models.AutoField(db_column='SeasonID', primary_key=True)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID', related_name='seasons')
    chapter = models.CharField(db_column='Chapter', max_length=255, null=True, blank=True)  # Např. "Chapter 2"
    seasonname = models.CharField(db_column='SeasonName', max_length=255)  # Např. "Chapter 2, Season 6"
    start_date = models.DateField(db_column='StartDate', null=True, blank=True)
    end_date = models.DateField(db_column='EndDate', null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    backgroundimage = models.CharField(db_column='BackgroundImage', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'GameSeason'

class Gamesession(models.Model):
    sessionid = models.AutoField(db_column='SessionID', primary_key=True)
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID', related_name='sessions')
    seasonid = models.ForeignKey('Gameseason', models.DO_NOTHING, db_column='SeasonID', related_name='sessions', null=True, blank=True)  # Propojení s Gameseason
    chapter = models.CharField(db_column='Chapter', max_length=255, null=True, blank=True)  # Např. "Chapter 2"
    sessionname = models.CharField(db_column='SessionName', max_length=255, null=True, blank=True)  # Např. "Session 6"
    startdate = models.DateField(db_column='StartDate', null=True, blank=True)
    enddate = models.DateField(db_column='EndDate', null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    backgroundimage = models.CharField(db_column='BackgroundImage', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'GameSession'

class Gamelocation(models.Model):
    gamelocationid = models.AutoField(db_column='GameLocationID', primary_key=True)
    locationname = models.CharField(db_column='LocationName', max_length=255, null=True, blank=True)
    shortdescription = models.CharField(db_column='ShortDescription', max_length=255, null=True, blank=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
    relatedseason = models.ForeignKey(Gameseason, on_delete=models.CASCADE, db_column='RelatedSeason', related_name="locations", null=True, blank=True)

    class Meta:
        db_table = 'GameLocation'

class Gameitem(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)
    name = models.CharField(db_column='ItemName', max_length=255)
    description = models.TextField(db_column='Description', null=True, blank=True)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID', related_name='items', null=True, blank=True,  db_index=True) 
    seasonid = models.ForeignKey('Gameseason', models.DO_NOTHING, db_column='SeasonID', related_name='items', null=True, blank=True)
    sessionid = models.ForeignKey('Gamesession', models.DO_NOTHING, db_column='SessionID', related_name='items', null=True, blank=True) 
    locationid = models.ForeignKey(Gamelocation, models.DO_NOTHING, db_column='LocationID', related_name='items', null=True, blank=True)
    itemimage = models.CharField(db_column='ItemImage', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'GameItem'

class Gamepurchase(models.Model):
    purchaseid = models.AutoField(db_column='PurchaseID', primary_key=True)
    purchasedate = models.DateField(db_column='PurchaseDate')
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'GamePurchase'


class Gamerating(models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    comment = models.TextField(db_column='Comment')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'GameRating'

class Gametask(models.Model):
    taskid = models.AutoField(db_column='TaskID', primary_key=True)
    name = models.CharField(db_column='TaskName', max_length=255)  # Např. "Najdi 20x diamant"
    description = models.TextField(db_column='Description', null=True, blank=True)  # Popis úkolu
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID', related_name='tasks')
    seasonid = models.ForeignKey('Gameseason', models.DO_NOTHING, db_column='SeasonID', related_name='tasks', null=True, blank=True)
    sessionid = models.ForeignKey('Gamesession', models.DO_NOTHING, db_column='SessionID', related_name='tasks', null=True, blank=True)
    target_quantity = models.IntegerField(db_column='TargetQuantity')  # Celkový počet

    class Meta:
        db_table = 'GameTask'

class Gametaskitem(models.Model):
    taskitemid = models.AutoField(db_column='TaskItemID', primary_key=True)
    taskid = models.ForeignKey('Gametask', models.DO_NOTHING, db_column='TaskID', related_name='items')  # Odkaz na hlavní úkol
    locationid = models.ForeignKey('Gamelocation', models.DO_NOTHING, db_column='LocationID', related_name='task_items', null=True, blank=True)  # Volitelná lokalita
    hint = models.TextField(db_column='Hint', null=True, blank=True)  # Nápověda k předmětu
    description = models.TextField(db_column='Description', null=True, blank=True)  # Detaily předmětu nebo úkolu
    itemimage = models.CharField(db_column='ItemImage', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'GameTaskItem'

class Gamespecial(models.Model):
    specialid = models.AutoField(db_column='SpecialID', primary_key=True)
    name = models.CharField(db_column='SpecialName', max_length=255)  # Název speciálního prvku
    description = models.TextField(db_column='Description', null=True, blank=True)  # Popis prvku
    gametype = models.CharField(db_column='GameType', max_length=50)  # Typ (např. "EasterEgg", "Error", "SpecialFeature")
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID', related_name='specials')  # Propojení s hrou
    locationid = models.ForeignKey('Gamelocation', models.DO_NOTHING, db_column='LocationID', related_name='specials', null=True, blank=True)  # Volitelná lokalita
    image = models.CharField(db_column='Image', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'GameSpecial'

class Itemtype(models.TextChoices):
    WEAPON = '1', 'Zbraň'
    TOOL = '2', 'Nástroj'
    CLOTHING = '3', 'Oděv'
    VEHICLE = '4', 'Vozidlo'
    DOCUMENT = '5', 'Dokument'
    JEWEL = '6', 'Klenot'
    HOUSEHOLD = '7', 'Domácí potřeby'
    MAGICAL_ITEM = '8', 'Magický předmět'
    ARTEFACT = '9', 'Artefakt'
    OTHER = '10', 'Ostatní'

class Item(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)
    itemname = models.CharField(db_column='ItemName', max_length=255, unique=True)
    itemname_cz = models.CharField(db_column='ItemNameCZ', max_length=255, blank=True)
    itemdescription = models.TextField(db_column='ItemDescription')
    itemtype = models.CharField(max_length=3, choices=Itemtype.choices, db_column='ItemType', null=True, blank=True)
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)


    class Meta:
        db_table = 'Item'


class Itembook(models.Model):
    bookitemid = models.AutoField(db_column='BookItemID', primary_key=True)
    itemrole = models.CharField(db_column='ItemRole', max_length=255)
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'ItemBook'


class Itemgame(models.Model):
    gameitemid = models.AutoField(db_column='GameItemID', primary_key=True)
    itemrole = models.CharField(db_column='ItemRole', max_length=255)
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'ItemGame'


class Itemmovie(models.Model):
    movieitemid = models.AutoField(db_column='MovieItemID', primary_key=True)
    itemrole = models.IntegerField(db_column='ItemRole')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')

    class Meta:
        db_table = 'ItemMovie'


class Itemmediatype(models.TextChoices):
    BOOK = '1', 'Book'
    GAME = '2', 'Game'
    MOVIE = '3', 'Movie'

class Itemmediarole(models.TextChoices):
    MAIN = '1', 'Main'
    SIDE = '2', 'Side'
    PROP = '3', 'Prop'

class Itemmedia(models.Model):
    mediaitemid = models.AutoField(db_column='MediaItemID', primary_key=True)
    item = models.ForeignKey(Item, on_delete=models.DO_NOTHING, db_column='Item')
    mediatype = models.IntegerField(choices=Itemmediatype.choices, db_column='MediaType')
    role = models.IntegerField(choices=Itemmediarole.choices, db_column='Role')
    mediaid = models.IntegerField(db_column='MediaID')  # FK to the specific media, you might need to handle this differently for each type

    class Meta:
        db_table = 'ItemMedia'




class Metacharts(models.Model):
    MetaChartsID = models.AutoField(db_column='MetaChartsID', primary_key=True)
    table_model = models.CharField(db_column='TableModel', max_length=255)  #Book,Movie,Game
    referenceid = models.IntegerField(db_column='ReferenceID')  # ID záznamu
    ranking = models.IntegerField(db_column='Ranking')
    title = models.CharField(db_column='Title', max_length=255)
    store = models.CharField(db_column='Store', max_length=100, blank=True, null=True)  # Např. Luxor, Alza
    time_period = models.CharField(db_column='TimePeriod', max_length=50, blank=True, null=True)  # Např. Week, Month
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='UpdatedAt', auto_now=True)

    class Meta:
        db_table = 'MetaCharts'

    def __str__(self):
        return f"{self.title} - Rank: {self.ranking} ({self.table_model})"


# Main Awards Model
class Metaaward(models.Model):
    metaawardid = models.AutoField(db_column='MetaAwardID', primary_key=True)
    awardname = models.CharField(db_column='AwardName', max_length=255)
    description = models.TextField(db_column='Description', blank=True, null=True)
    awardtype = models.CharField(
        db_column='AwardType',
        max_length=20,
        choices=[
            ('film', 'Film'),
            ('book', 'Book'),
            ('game', 'Game')
        ]
    )
    year = models.PositiveIntegerField(db_column='Year')

    class Meta:
        db_table = 'MetaAward'
        unique_together = ('awardname', 'year')

    def __str__(self):
        return f"{self.awardname} ({self.year})"




class Metacity(models.Model):
    cityid = models.AutoField(db_column='CityID', primary_key=True)
    namecity = models.CharField(db_column='NameCity', max_length=255)
    namecitycz = models.CharField(db_column='NameCityCZ', max_length=255, blank=True, null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID')
    class Meta:
        db_table = 'MetaCity'

class Metacollection(models.Model):
    collectionid = models.IntegerField(db_column='CollectionID', primary_key=True)
    collectionname = models.CharField(db_column='CollectionName', max_length=255)
    collectionurl = models.CharField(db_column='CollectionNameURL', max_length=255, blank=True, null=True)
    collectiondescription = models.TextField(db_column='CollectionDescription', blank=True, null=True)
    img = models.CharField(db_column='IMG', max_length=64, null=True, blank=True)
    imgposter = models.CharField(db_column='IMGposter', max_length=64, null=True, blank=True)

    class Meta:
        db_table = 'MetaCollection'


class Metacountry(models.Model):
    countryid = models.IntegerField(db_column='CountryID', primary_key=True)
    countryname = models.CharField(db_column='CountryName', max_length=255)
    countrycode = models.CharField(db_column='CountryCode', max_length=4)
    countrycode2 = models.CharField(db_column='CountryCode2', max_length=2, blank=True)
    countrynamecz = models.CharField(db_column='CountryNameCZ', max_length=255)
    class Meta:
        db_table = 'MetaCountry'
    def __str__(self):
        return self.countrynamecz or self.countryname


class Metadeveloper(models.Model):
    developerid = models.AutoField(db_column='DeveloperID', primary_key=True)
    developer = models.CharField(db_column='Developer', max_length=255)
    developerurl = models.CharField(db_column='DeveloperURL', max_length=255, unique=True)
    rawgid = models.IntegerField(db_column='RawgID', null=True, blank=True)

    class Meta:
        db_table = 'MetaDeveloper'
    def __str__(self):
        return self.developer or f"Developer {self.developerid}"


class Metagenre(models.Model):
    genreid = models.AutoField(db_column='GenreID', primary_key=True)
    genrename = models.CharField(db_column='GenreName', max_length=255)
    genrenamecz = models.CharField(db_column='GenreNameCZ', max_length=255)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True, unique=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    class Meta:
        db_table = 'MetaGenre'
    def __str__(self):
        return self.genrenamecz


class Bookgenre(models.Model):
    bookgenreid = models.AutoField(db_column='BookGenreID', primary_key=True)
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'BookGenre'


class Gamegenre(models.Model):
    gamegenreid = models.AutoField(db_column='GameGenreID', primary_key=True)
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'GameGenre'
    def __str__(self):
        return f"{self.game.title} - {self.genre.genrenamecz}"


class Metaindex(models.Model):
    indexid = models.AutoField(db_column='IndexID', primary_key=True)
    section = models.CharField(db_column='Section', max_length=8)  # Např. 'Movie', 'Book', 'Game'
    item_id = models.IntegerField(db_column='ItemID')  # ID položky z příslušné sekce
    title = models.CharField(db_column='Title', max_length=255)  # Název položky
    author = models.CharField(db_column='Author', max_length=255, null=True, blank=True) 
    year = models.CharField(db_column='Year', max_length=255, null=True, blank=True) 
    description = models.CharField(db_column='Description', max_length=255, null=True)
    divrating = models.CharField(db_column='DIVrating', max_length=9, default=0)
    img = models.CharField(db_column='IMG', max_length=255, null=True, blank=True)  # URL obrázku
    url = models.CharField(db_column='URL', max_length=255, null=True, blank=True)  # URL pro detailní stránku položky
    last_updated = models.DateField(db_column='LastUpdated', auto_now=True)  # Datum poslední aktualizace

    class Meta:
        db_table = 'MetaIndex'

class Metapublisher(models.Model):
    publisherid = models.AutoField(db_column='PublisherID', primary_key=True)
    publisher = models.CharField(db_column='Publisher', max_length=255)
    publisherurl = models.CharField(db_column='PublisherURL', max_length=255, unique=True)
    rawgid = models.IntegerField(db_column='RawgID', null=True, blank=True)

    class Meta:
        db_table = 'MetaPublisher'

    def __str__(self):
        return self.publisher

class Gamepublisher(models.Model):
    gamepublisherid = models.AutoField(db_column='GamePublisherID', primary_key=True)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
    publisherid = models.ForeignKey('Metapublisher', models.DO_NOTHING, db_column='PublisherID')

    class Meta:
        db_table = 'GamePublisher'

class Metakeywords(models.Model):
    keywordid = models.AutoField(db_column='KeywordID', primary_key=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    keyword = models.CharField(db_column='Keyword', max_length=255, unique=True)
    keywordcz = models.CharField(db_column='KeywordCZ', max_length=255, blank=True, null=True)
    keywordurl = models.CharField(db_column='KeywordURL', max_length=255, blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    class Meta:
        db_table = 'MetaKeywords'

class Moviekeywords(models.Model):
    moviekeywordid = models.AutoField(db_column='MovieKeywordID', primary_key=True)
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    keywordid = models.ForeignKey('Metakeywords', on_delete=models.CASCADE, db_column='KeywordID')
    class Meta:
        db_table = 'MovieKeywords'
        unique_together = [['movieid', 'keywordid']]

class Bookkeywords(models.Model):
    bookkeywordid = models.AutoField(db_column='BookKeywordID', primary_key=True)
    bookid = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='BookID')
    keywordid = models.ForeignKey('Metakeywords', on_delete=models.CASCADE, db_column='KeywordID')

    class Meta:
        db_table = 'BookKeywords'
        unique_together = [['bookid', 'keywordid']]

class Gamekeywords(models.Model):
    gamekeywordid = models.AutoField(db_column='GameKeywordID', primary_key=True)
    gameid = models.ForeignKey('Game', on_delete=models.CASCADE, db_column='GameID')
    keywordid = models.ForeignKey('Metakeywords', on_delete=models.CASCADE, db_column='KeywordID')

    class Meta:
        db_table = 'GameKeywords'
        unique_together = [['gameid', 'keywordid']]

class Metalocation(models.Model):
    locationid = models.IntegerField(db_column='LocationID', primary_key=True)
    locationname = models.CharField(db_column='LocationName', max_length=255, unique=True)
    locationnamecz = models.CharField(db_column='LocationNameCZ', max_length=255, blank=True, null=True)
    locationurl = models.CharField(db_column='LocationURL', max_length=255, unique=True)
    locationtype = models.CharField(db_column='LocationType', max_length=50)
    locationtypeid = models.ForeignKey('Metatype', models.DO_NOTHING, db_column='TypeID', blank=True, null=True)
    locationdescription = models.TextField(db_column='LocationDescription')
    parentlocationid = models.IntegerField(db_column='ParentLocationID', blank=True, null=True)
    locationadress = models.CharField(db_column='LocationAdress', max_length=255, blank=True, null=True)
    gpsx = models.CharField(db_column='gpsX', max_length=32, blank=True, null=True)
    gpsy = models.CharField(db_column='gpsY', max_length=32, blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'MetaLocation'


class Metaplatform(models.Model):
    platformid = models.AutoField(db_column='PlatformID', primary_key=True)
    platform = models.CharField(db_column='Platform', max_length=255, blank=True, null=True)
    url = models.CharField(db_column='PlatformURL', max_length=255, blank=True, null=True)
    class Meta:
        db_table = 'MetaPlatform'
    def __str__(self):
        return self.platform or "Neznámá Platforma"

class Gameplatform(models.Model):
    gameplatformid = models.AutoField(db_column='GamePlatformID', primary_key=True)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
    platformid = models.ForeignKey('Metaplatform', models.DO_NOTHING, db_column='PlatformID')

    class Meta:
        db_table = 'GamePlatform'
    def __str__(self):
        return self.platformid.platform or f"Platform {self.gameplatformid}"

class Metaproduction(models.Model):
    metaproductionid = models.AutoField(db_column='MetaProductionID', primary_key=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    name = models.CharField(max_length=255, db_column='Name')
    description = models.TextField(db_column='Description', null=True, blank=True)
    headquarters = models.CharField(max_length=255, db_column='Headquarters', null=True, blank=True)
    homepage = models.URLField(db_column='Homepage', null=True, blank=True)
    logopath = models.CharField(max_length=255, db_column='LogoPath', default='n.png')
    origincountry = models.CharField(max_length=4, db_column='OriginCountry', null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True, blank=True)
    parentcompanyid = models.ForeignKey('self', on_delete=models.CASCADE, db_column='ParentCompanyID', null=True, blank=True)

    class Meta:
        db_table = 'MetaProduction'

class Metasoundtrack(models.Model):
    soundtrackid = models.AutoField(db_column='SoundtrackID', primary_key=True)
    title = models.CharField(max_length=255, db_column='Title')
    albumname = models.CharField(max_length=255, db_column='AlbumName', null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    release_date = models.DateField(db_column='ReleaseDate', null=True, blank=True)
    img = models.CharField(db_column='IMG', max_length=255, default='n.png')
    parentid = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='ParentID')

    class Meta:
        db_table = 'MetaSoundtrack'


class Metastats(models.Model):
    metastatsid = models.AutoField(db_column='MetaStatsID', primary_key=True) 
    statname = models.CharField(db_column='StatName', max_length=255, unique=True)
    tablemodel = models.CharField(db_column='TableModel', max_length=255, null=True, blank=True)
    value = models.IntegerField(db_column='Value', default=0)
    updatedat = models.DateTimeField(db_column='UpdatedAt', auto_now=True)

    class Meta:
        db_table = 'MetaStats'

    def __str__(self):
        return f'{self.statname}: {self.value}'


class Metastreet(models.Model):
    StreetID = models.AutoField(db_column='StreetID', primary_key=True)
    StreetName = models.CharField(db_column='StreetName', max_length=255)
    StreetNameCZ = models.CharField(db_column='StreetNameCZ', max_length=255, blank=True, null=True)
    StreetNameURL = models.CharField(db_column='StreetNameURL', max_length=255, blank=True, null=True)
    City = models.ForeignKey(Metacity, on_delete=models.CASCADE, blank=True, null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID')
    class Meta:
        db_table = 'MetaStreet'



class Metatype(models.Model):
    typeid = models.AutoField(db_column='TypeID', primary_key=True)
    tablename = models.CharField(db_column='TableName', max_length=255)
    typename = models.CharField(db_column='TypeName', max_length=255)
    typenamecz = models.CharField(db_column='TypeNameCZ', max_length=255, blank=True, null=True)
    typedescription = models.CharField(db_column='TypeDescription', max_length=1024)
    class Meta:
        db_table = 'MetaType'


class Metauniversum(models.Model):
    universumid = models.AutoField(db_column='UniversumID', primary_key=True)
    universumname = models.CharField(db_column='UniversumName', max_length=255)
    universumnamecz = models.CharField(db_column='UniversumNameCZ', max_length=255, blank=True, null=True)
    universumurl = models.CharField(db_column='UniversumURL', max_length=255, blank=True, null=True)
    universumdescription = models.TextField(db_column='UniversumDescription', null=True)
    universumdescriptioncz = models.TextField(db_column='UniversumDescriptionCZ', null=True)
    universumimg = models.CharField(db_column='UniversumIMG', max_length=64, null=True, blank=True)
    universumimgposter = models.CharField(db_column='UniversumIMGposter', max_length=64, null=True, blank=True)
    universumcounter = models.CharField(db_column='UniversumCounter', max_length=64, null=True, blank=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)


    class Meta:
        db_table = 'MetaUniversum'
    def __str__(self):
        return self.universumnamecz or self.universumname or "Neznámé Universum"

# Special
# 0 - adult
# 1 - žádný popisek
# 2 - AJ popisek
# 3 - Český (cílový stav)

class Movie(models.Model):
    movieid = models.IntegerField(db_column='MovieID', primary_key=True) 
    title = models.CharField(db_column='Title', max_length=255)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, default='', db_index=True)    
    special = models.IntegerField(db_column='Special', db_index=True, blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, unique=True)
    oldurl = models.CharField(db_column='OldURL', max_length=255, null=True)
    ChangeURL = models.CharField(db_column='ChangeURL', max_length=255, null=True)
    img = models.CharField(db_column='IMG', max_length=255, default='noimg.png')
    imgposter = models.CharField(db_column='IMGposter', max_length=64, default='noimg.png')
    description = models.TextField(db_column='Description', null=True)
    releaseyear = models.CharField(db_column='ReleaseYear', max_length=4, null=True) 
    duration = models.IntegerField(db_column='Duration', null=True)
    language = models.CharField(db_column='Language', max_length=5, null=True, blank=True)  # Field
    budget = models.IntegerField(db_column='Budget', null=True)
    adult = models.CharField(db_column='Adult',  max_length=1)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    popularity = models.FloatField(db_column='Popularity', null=True, db_index=True)
    idcsfd = models.CharField(db_column='ID_Csfd', max_length=16, null=True)
    idimdb = models.CharField(db_column='ID_Imdb', max_length=16, null=True)
    iddiv = models.CharField(db_column='ID_DIV', max_length=16, null=True)
    universumid = models.ForeignKey(Metauniversum, models.DO_NOTHING, db_column='UniversumID', null=True, blank=True)
#    ratings = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='movies', null=True, blank=True)
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

    class Meta:
        db_table = 'Movie'


class Moviecinema(models.Model):
    mcid = models.AutoField(db_column='ID', primary_key=True)
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    distributorid = models.ForeignKey('MovieDistributor', on_delete=models.CASCADE, db_column='DistributorID', null=True, blank=True)
    releasedate = models.DateField(db_column='ReleaseDate', null=True, blank=True)

    class Meta:
        db_table = 'MovieCinema'


class Moviecomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True, unique=True) 
    comment = models.TextField(db_column='Comment')
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)
    class Meta:
        db_table = 'MovieComments'


class Moviecountries(models.Model):
    moviecountriesid = models.AutoField(db_column='MovieCountriesID', primary_key=True, unique=True) 
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    countryid = models.ForeignKey(Metacountry, models.DO_NOTHING, db_column='CountryID')

    class Meta:
        db_table = 'MovieCountries'
        unique_together = [['movieid', 'countryid']]


class Moviecrew(models.Model):
    moviecrewid = models.AutoField(db_column='MovieCrewID', primary_key=True, unique=True) 
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    roleid = models.ForeignKey(Creatorrole, models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')
    peopleid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='PeopleID')
    creworder = models.IntegerField(db_column='CrewOrder', null=True, blank=True)

    class Meta:
        db_table = 'MovieCrew'
        indexes = [
            models.Index(fields=['creworder']),
        ]

class Moviedistributor(models.Model):
    distributorid = models.AutoField(db_column='DistributorID', primary_key=True)
    name = models.CharField(max_length=255, db_column='Name')
    description = models.CharField(db_column='Description', max_length=512, null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', on_delete=models.DO_NOTHING, db_column='CountryID', null=True)

    class Meta:
        db_table = 'MovieDistributor'


class Movieduplicity(models.Model):
    duplicityid = models.AutoField(db_column='DuplicityID', primary_key=True, unique=True) 
    url = models.CharField(db_column='URL', max_length=255, unique=True)
    description = models.TextField(db_column='Description', null=True)
    public = models.IntegerField(db_column='Public', default=1)  # 1 pro 'zobraz'
    duplicity = models.IntegerField(db_column='Duplicity', null=True) 
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

    class Meta:
        db_table = 'MovieDuplicity'

class Movieerror(models.Model):
    errorid = models.AutoField(db_column='ErrorID', primary_key=True)
    error = models.CharField(db_column='Error', max_length=1024)
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)

    class Meta:
        db_table = 'MovieError'

class Moviegenre(models.Model):
    moviegenreid = models.AutoField(db_column='MovieGenreID', primary_key=True)
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'MovieGenre'


class Movielinks(models.Model):
    linkid = models.AutoField(db_column='LinkID', primary_key=True, unique=True) 
    link = models.CharField(db_column='Link', max_length=255, unique=True)
    linktext = models.CharField(max_length=255, db_column='LinkText', null=True, blank=True)
    linkdescription = models.CharField(max_length=5125, db_column='LinkDescription', null=True, blank=True)
    linkautor = models.CharField(max_length=255, db_column='LinkAuthor', null=True, blank=True)
    linkType = models.CharField(max_length=255, db_column='LinkType')
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    date_added = models.DateField(db_column='DateAdded', auto_now_add=True)
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'MovieLinks'


class Movielocation(models.Model):
    movielocationid = models.IntegerField(db_column='MovieLocationID', primary_key=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'MovieLocation'  

class Movieproductions(models.Model):
    movieproductiondid = models.AutoField(db_column='MovieProductionID', primary_key=True)
    productionid = models.ForeignKey('Metaproduction', on_delete=models.CASCADE, db_column='MetaProductionID')
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')

    class Meta:
        db_table = 'MovieProductions'
        unique_together = [['productionid', 'movieid']]

class Moviequotes(models.Model):
    quoteid = models.AutoField(db_column='QuoteID', primary_key=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    character = models.ForeignKey('Charactermeta', on_delete=models.CASCADE, db_column='CharacterID', null=True, blank=True)
    actor = models.ForeignKey('Creator', on_delete=models.CASCADE, db_column='ActorID', null=True, blank=True)
    quote = models.TextField(db_column='Quote')
    parentquote = models.ForeignKey('self', on_delete=models.CASCADE, db_column='ParentQuoteID', null=True, blank=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='user_id')  

    class Meta:
        db_table = 'MovieQuotes'

class Movierating(AbstractBaseRating, models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    movieid = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='MovieID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    class Meta:
        db_table = 'MovieRating'

class Moviesoundtrack(models.Model):
    msid = models.AutoField(db_column='ID', primary_key=True)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    soundtrack = models.ForeignKey('MetaSoundtrack', on_delete=models.CASCADE, db_column='SoundtrackID')

    class Meta:
        db_table = 'MovieSoundtrack'

class Movietrailer(models.Model):
    trailerid = models.AutoField(db_column='TrailerID', primary_key=True)
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    youtubeurl = models.CharField(db_column='YoutubeURL', max_length=255)
    duration = models.DurationField(db_column='Duration', null=True, blank=True)
    date_added = models.DateField(db_column='DateAdded', auto_now_add=True)
    views = models.IntegerField(db_column='Views', default=0)

    class Meta:
        db_table = 'MovieTrailer'

class Movietranslation(models.Model):
    movietranslationid = models.AutoField(db_column='MovieTranslationID', primary_key=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='MovieID', related_name="translations")
    language = models.CharField(db_column='Language', max_length=5, blank=True, null=True)  # Např. "en", "cz"
    title = models.CharField(db_column='Title', max_length=255, blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(db_column='Description', blank=True, null=True)

    class Meta:
        db_table = 'MovieTranslation'

class Movietrivia(models.Model):
    triviaid = models.AutoField(db_column='TriviaID', primary_key=True)
    trivia = models.TextField(db_column='Trivia')
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    creatorid = models.ForeignKey('Creator', on_delete=models.CASCADE, db_column='CreatorID', null=True, blank=True)
    parenttriviaid = models.ForeignKey('self', on_delete=models.CASCADE, db_column='ParentTriviaID', null=True, blank=True)
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'MovieTrivia'

class Movieversions(models.Model):
    movieversionid = models.AutoField(db_column='MovieVersionID', primary_key=True)
    versionname = models.CharField(db_column='VersionName', max_length=255)
    duration = models.IntegerField(db_column='Duration')
    releasedate = models.DateField(db_column='ReleaseDate')
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'MovieVersions'



class Tvcrew(models.Model):
    tvcrewid = models.AutoField(db_column='TVCrewID', primary_key=True)
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.DO_NOTHING, db_column='TVShowID')
    roleid = models.ForeignKey(Creatorrole, models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID', null=True, blank=True)
    peopleid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='PeopleID')
    episodecount = models.IntegerField(db_column='EpisodeCount')
    creworder = models.IntegerField(db_column='CrewOrder', null=True, blank=True)

    class Meta:
        db_table = 'TVCrew'
        indexes = [
            models.Index(fields=['creworder']),
        ]

class Tvepisode(models.Model):
    episodeid = models.AutoField(db_column='EpisodeID', primary_key=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    episodeurl = models.CharField(db_column='EpisodeURL', max_length=255, null=True, blank=True)
    episodenumber = models.IntegerField(db_column='EpisodeNumber')
    title = models.CharField(db_column='Title', max_length=255, null=True, blank=True)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, null=True, blank=True)
    episodeimg = models.CharField(db_column='EpisodeIMG', max_length=255, null=True, blank=True)
    airdate = models.DateField(db_column='AirDate')
    description = models.TextField(db_column='Description')
    episodetype = models.CharField(db_column='EpisodeType', max_length=16, null=True, blank=True)
    runtime = models.IntegerField(db_column='Runtime', null=True, blank=True)
    seasonid = models.ForeignKey('Tvseason', models.DO_NOTHING, db_column='SeasonID', null=True, blank=True)

    class Meta:
        unique_together = [['seasonid', 'episodeurl']]
        db_table = 'TVEpisode'

class Tvgenre(models.Model):
    tvgenreid = models.AutoField(db_column='TVGenreID', primary_key=True, unique=True) 
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'TVGenre'

class Tvepisodecrew(models.Model):
    tvepisodecrewid = models.AutoField(db_column='TVEpisodeCrewID', primary_key=True, unique=True) 
    episodeid = models.ForeignKey(Tvepisode, models.DO_NOTHING, db_column='EpisodeID')
    roleid = models.ForeignKey(Creatorrole, models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID', null=True, blank=True)
    peopleid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='PeopleID')
    creworder = models.IntegerField(db_column='CrewOrder', null=True, blank=True)

    class Meta:
        db_table = 'TVEpisodeCrew'
        indexes = [
            models.Index(fields=['creworder']),
        ]

class Tvseason(models.Model):
    seasonid = models.AutoField(db_column='SeasonID', primary_key=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    seasonurl = models.CharField(db_column='SeasonURL', max_length=255, null=True, blank=True)
    seasonnumber = models.IntegerField(db_column='SeasonNumber')
    title = models.CharField(db_column='title', max_length=255, null=True, blank=True)
    titlecz = models.CharField(db_column='titleCZ', max_length=255, null=True, blank=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    img = models.CharField(db_column='IMG', max_length=255, null=True, blank=True)
    seasonepisode = models.IntegerField(db_column='SeasonEpisode', null=True, blank=True)

    premieredate = models.DateField(db_column='PremiereDate')
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')

    class Meta:
        unique_together = ('tvshowid', 'seasonurl')
        db_table = 'TVSeason'

class Tvshow(models.Model):
    tvshowid = models.AutoField(db_column='TVShowID', primary_key=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    title = models.CharField(db_column='Title', max_length=255, null=True, blank=True)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=255, null=True, blank=True, unique=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    status = models.CharField(db_column='Status', max_length=32, null=True, blank=True)
    img = models.CharField(db_column='IMG', max_length=64, null=True, blank=True)
    imgposter = models.CharField(db_column='IMGposter', max_length=64, null=True, blank=True)
    premieredate = models.DateField(db_column='PremiereDate')
    enddate = models.DateField(db_column='EndDate')
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    popularity = models.IntegerField(db_column='Popularity', null=True, db_index=True)
    language = models.CharField(db_column='Language', max_length=4, null=True, blank=True)
    countryid = models.ForeignKey(Metacountry, models.DO_NOTHING, db_column='CountryID')
    universumid = models.ForeignKey(Metauniversum, models.DO_NOTHING, db_column='UniversumID', null=True, blank=True)
    createdby = models.ForeignKey(Creator, models.DO_NOTHING, db_column='CreatorID', null=True, blank=True)

    class Meta:
        db_table = 'TVShow'

class Tvshowcomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
##    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    tvshowkid = models.ForeignKey(Tvshow, models.DO_NOTHING, db_column='TVShowID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)

    class Meta:
        db_table = 'TVShowComments'


class Tvshowtrailer(models.Model):
    trailerid = models.AutoField(db_column='TrailerID', primary_key=True)
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.CASCADE, db_column='TvshowID')
    youtubeurl = models.CharField(db_column='YoutubeURL', max_length=255)
    duration = models.DurationField(db_column='Duration', null=True, blank=True)
    date_added = models.DateField(db_column='DateAdded', auto_now_add=True)
    views = models.IntegerField(db_column='Views', default=0)

    class Meta:
        db_table = 'TvshowTrailer'

class Tvshowtrivia(models.Model):
    triviaid = models.AutoField(db_column='TriviaID', primary_key=True)
    trivia = models.TextField(db_column='Trivia')
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.CASCADE, db_column='TvshowID')
    userid = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID', null=True, blank=True)
    divrating = models.IntegerField(db_column='DIVRating', default=0, db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'TvshowTrivia'


class Tvshowquotes(models.Model):
    quote_id = models.AutoField(primary_key=True, db_column='QuoteID')
    quote = models.TextField(db_column='Quote')
    actor = models.ForeignKey(Creator, on_delete=models.RESTRICT, null=True, db_column='ActorID')
    character = models.ForeignKey(Charactermeta, on_delete=models.RESTRICT, null=True, db_column='CharacterID')
    episode = models.ForeignKey(Tvepisode, on_delete=models.CASCADE, null=True, db_column='EpisodeID')
    season = models.ForeignKey(Tvseason, on_delete=models.SET_NULL, null=True, db_column='SeasonID')
    tv_show = models.ForeignKey(Tvshow, on_delete=models.SET_NULL, null=True, db_column='TVShowID')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='UserID')
    parent_quote = models.IntegerField(null=True, blank=True, db_column='ParentQuoteID')
    div_rating = models.IntegerField(default=0, db_column='DIVRating')

    class Meta:
        db_table = 'TVShowQuotes'

    def __str__(self):
        return f"{self.quote[:50]}..."  


class Tvcountries(models.Model):
    tvcountryid = models.AutoField(db_column='TVCountryID', primary_key=True)
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.CASCADE, db_column='TVShowID')
    countryid = models.ForeignKey('Metacountry', on_delete=models.CASCADE, db_column='CountryID')

    class Meta:
        unique_together = [['tvshowid', 'countryid']]
        db_table = 'TVCountries'

class Tvkeywords(models.Model):
    tvkeywordid = models.AutoField(db_column='TVKeywordID', primary_key=True)
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.CASCADE, db_column='TVShowID')
    keywordid = models.ForeignKey('Metakeywords', on_delete=models.CASCADE, db_column='KeywordID')

    class Meta:
        unique_together = [['tvshowid', 'keywordid']]
        db_table = 'TVKeywords'

class Tvproductions(models.Model):
    tvproductionid = models.AutoField(db_column='TVProductionID', primary_key=True)
    metaproductionid = models.ForeignKey('Metaproduction', on_delete=models.CASCADE, db_column='MetaProductionID')
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.CASCADE, db_column='TVShowID')

    class Meta:
        unique_together = [['metaproductionid', 'tvshowid']]
        db_table = 'TVProductions'



# Movie Award Model
class Movieaward(models.Model):
    movieawardid = models.AutoField(db_column='MovieAwardID', primary_key=True)
    metaAwardid = models.ForeignKey(Metaaward, on_delete=models.CASCADE, db_column='MetaAwardID')
    movieid = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='MovieID')
    winner = models.BooleanField(db_column='Winner', default=False)

    class Meta:
        db_table = 'MovieAward'

# Book Award Model
class Bookaward(models.Model):
    bookAwardid = models.AutoField(db_column='BookAwardID', primary_key=True)
    metaAwardid = models.ForeignKey(Metaaward, on_delete=models.CASCADE, db_column='MetaAwardID')
    bookid = models.ForeignKey(Book, on_delete=models.CASCADE, db_column='BookID')
    winner = models.BooleanField(db_column='Winner', default=False)

    class Meta:
        db_table = 'BookAward'

# Game Award Model
class Gameaward(models.Model):
    gameawardid = models.AutoField(db_column='GameAwardID', primary_key=True)
    metaawardid = models.ForeignKey(Metaaward, on_delete=models.CASCADE, db_column='MetaAwardID')
    gameid = models.ForeignKey(Game, on_delete=models.CASCADE, db_column='GameID')
    winner = models.BooleanField(db_column='Winner', default=False)

    class Meta:
        db_table = 'GameAward'



class Userbookgoal(models.Model):
    userbookgoalid = models.AutoField(db_column='UserBookGoalID', primary_key=True)  # Field name made lowercase.
    goalyear = models.PositiveIntegerField(db_column='GoalYear')  # Field name made lowercase.
    goal = models.PositiveIntegerField(db_column='Goal')  # Field name made lowercase.
    booksread = models.PositiveIntegerField(db_column='BooksRead')  # Field name made lowercase.
    lastupdated = models.DateTimeField(db_column='LastUpdated', blank=True, null=True)  # Field name made lowercase.
    user = models.ForeignKey(User, models.DO_NOTHING)

    class Meta:
        db_table = 'UserBookGoal'
        unique_together = (('user', 'goalyear'),)

class Userdivcoins(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    totaldivcoins = models.DecimalField(db_column='TotalDivCoins', max_digits=10, decimal_places=2, default=0.00)
    weeklydivcoins = models.DecimalField(db_column='WeeklyDivCoins', max_digits=10, decimal_places=2, default=0.00)
    monthlydivcoins = models.DecimalField(db_column='MonthlyDivCoins', max_digits=10, decimal_places=2, default=0.00)
    yearlydivcoins = models.DecimalField(db_column='YearlyDivCoins', max_digits=10, decimal_places=2, default=0.00)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

    class Meta:
        db_table = 'UserDivCoins'
    def __str__(self):
        return f"{self.user.username} - {self.total_points} DIVcoins"

    def update_points(self, points):
        self.totaldivcoins += points
        now = timezone.now()       
        if now - self.last_updated < timedelta(weeks=1):
            self.weeklydivcoins += points
        else:
            self.weeklydivcoins = points

        if now - self.last_updated < timedelta(days=30):
            self.monthlydivcoins += points
        else:
            self.monthlydivcoins = points

        if now - self.last_updated < timedelta(days=365):
            self.yearlydivcoins += points
        else:
            self.yearlydivcoins = points

        self.last_updated = now
        self.save()


class Userchatsession(models.Model):
    userchatsessionid = models.AutoField(db_column='UserChatSessionID', primary_key=True)
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User1', related_name="user1_chats")
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, db_column='User2', related_name="user2_chats")
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True) 

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"

    class Meta:
        unique_together = ('user1', 'user2')
        db_table = 'UserChatSession'

class Usermessage(models.Model):
    usermessageid = models.AutoField(db_column='UserMessageID', primary_key=True)
    chatsession = models.ForeignKey(Userchatsession, on_delete=models.CASCADE, db_column='UserChatSession', related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, db_column='Sender')
    message = models.TextField(db_column='Message', default="", null=True, blank=True)
    sentat = models.DateTimeField(db_column='SentAt', auto_now_add=True) 
    isread = models.BooleanField(db_column='IsRead', default=False)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sentat}"

    class Meta:
        ordering = ['sentat'] 
        db_table = 'UserMessage'


class Userprofile(models.Model):
    userprofileid = models.AutoField(db_column='UserProfileID', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(db_column='Bio', default="", null=True, blank=True)
    profilepicture = models.ImageField(db_column='ProfilePicture', upload_to='profiles/2023/', blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=255, null=True, blank=True)
    birthdate = models.DateField(db_column='BirthDate', null=True, blank=True)
    avatar = models.ForeignKey(Avatar, db_column='Avatar', null=True, blank=True, on_delete=models.SET_NULL)
    
    class Meta:
        db_table = 'UserProfile'


class Userlisttype(models.Model):
    userlisttypeid = models.AutoField(db_column='UserListTypeID', primary_key=True)
    name = models.CharField(db_column='Name', max_length=255, blank=True, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)

    class Meta:
        db_table = 'UserListType'


    
    
class Userlist(models.Model):
    userlistid = models.AutoField(db_column='UserListID', primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    namelist = models.CharField(db_column='NameList', max_length=255)
    description = models.TextField(db_column='Description', blank=True, null=True)
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)
    listtype = models.ForeignKey(Userlisttype, on_delete=models.CASCADE, db_column='ListTypeID', blank=True, null=True)
    
    class Meta:
        db_table = 'UserList'

    
    def __str__(self):
        return f"{self.namelist} ({self.listtype.name if self.listtype else 'No Type'})"   

class Userlistitem(models.Model):
    userlistitemid = models.AutoField(db_column='UserListItemID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE, db_column='UserListID')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, db_column='ContentTypeID')
    object_id = models.PositiveIntegerField(db_column='ObjectID')
    content_object = GenericForeignKey('content_type', 'object_id')
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
        db_table = 'UserListItem'
        unique_together = [['userlist', 'content_type', 'object_id']]  # Zajistí unikátnost položek v seznamu
    def __str__(self):
        return f"{self.userlist.namelist} - {self.content_object}"

    
class Userlistmovie(models.Model):
    userlistmovieid = models.AutoField(db_column='UserListMovieID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
        unique_together = [['userlist', 'movie']]
        db_table = 'UserListMovie'
    
    def __str__(self):
        return f"{self.userlist.namelist} - {self.movie.title}"



class Userlistbook(models.Model):
    userlistbookid = models.AutoField(db_column='UserListBookID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'book']]
        db_table = 'UserListBook'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.book.title}"


class Userlistgame(models.Model):
    userlistgameid = models.AutoField(db_column='UserListGameID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'game']]
        db_table = 'UserListGame'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.game.title}"


class Userlisttvshow(models.Model):
    userlisttvshowid = models.AutoField(db_column='UserListTVShowID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    tvshow = models.ForeignKey(Tvshow, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'tvshow']]
        db_table = 'UserListTVShow'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.tvshow.title}"


class Userlisttvseason(models.Model):
    userlisttvseasonid = models.AutoField(db_column='UserListTVSeasonID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    tvseason = models.ForeignKey(Tvseason, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'tvseason']]
        db_table = 'UserListTVSeason'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.tvseason.title}"


class Userlisttvepisode(models.Model):
    userlisttvepisodeid = models.AutoField(db_column='UserListTVEpisodeID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    tvepisode = models.ForeignKey(Tvepisode, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'tvepisode']]
        db_table = 'UserListTVEpisode'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.tvepisode.title}"

"""
# DEFINOVANÉ NA ŘÁDKU 1743
class Userchatsession(models.Model):
    userchatsessionid = models.AutoField(db_column='UserChatSessionID', primary_key=True) 
    createdat = models.DateTimeField(db_column='CreatedAt')  # Field name made lowercase.
    user1 = models.ForeignKey(User, models.DO_NOTHING, db_column='User1')  # Field name made lowercase.
    user2 = models.ForeignKey(User, models.DO_NOTHING, db_column='User2', related_name='userchatsession_user2_set') 

    class Meta:
        db_table = 'UserChatSession'
        unique_together = (('user1', 'user2'),)

class Usermessage(models.Model):
    usermessageid = models.AutoField(db_column='UserMessageID', primary_key=True)
    chatsession = models.ForeignKey(Userchatsession, on_delete=models.CASCADE, db_column='UserChatSession', related_name='messages')
    sender = models.ForeignKey(User, db_column='Sender', on_delete=models.CASCADE)
    message = models.TextField(db_column='Message', ) 
    sentat = models.DateTimeField(db_column='SentAt', auto_now_add=True) 
    isread = models.BooleanField(db_column='IsRead', default=False)

    def __str__(self):
        return f"Message from {self.sender.username} at {self.sentat}"

    class Meta:
        ordering = ['sentat'] 
        db_table = 'UserMessage'
"""



