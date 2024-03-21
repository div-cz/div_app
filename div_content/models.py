# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models
from django.contrib.auth.models import User
from star_ratings.models import AbstractBaseRating, Rating


class AAChange(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    description = models.TextField(db_column='Description')
    created = models.DateField(db_column='Created')
    class Meta:
        db_table = 'AAChange'

class Article(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    url = models.CharField(db_column='URL', max_length=255)
    title = models.CharField(db_column='Title', max_length=255)
    h1 = models.CharField(db_column='H1', max_length=255)
    h2 = models.CharField(db_column='H2', max_length=255)
    tagline = models.CharField(db_column='Tagline', max_length=64)
    content = models.TextField(db_column='Content')
    youtube = models.CharField(db_column='Youtube', max_length=20, null=True, blank=True)
    img1600 = models.CharField(db_column='Img1600', max_length=255)
    img500x500 = models.CharField(db_column='Img500x500', max_length=255)
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


class Book(models.Model):
    bookid = models.AutoField(db_column='BookID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255)
    year = models.IntegerField(db_column='Year', null=True, blank=True)
    pages = models.IntegerField(db_column='Pages', null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)
    img = models.CharField(db_column='IMG', max_length=255, default="noimg.png")
    subtitle = models.CharField(db_column='Subtitle', max_length=255, blank=True, null=True)
    author = models.CharField(db_column='Author', max_length=255)
    pseudonym = models.CharField(db_column='Pseudonym', max_length=2, null=True, blank=True)
    authorid = models.ForeignKey('Bookauthor', models.DO_NOTHING, db_column='AuthorID', null=True)
    googleid = models.CharField(db_column='GoogleID', max_length=16, null=True)
    description = models.TextField(db_column='Description', blank=True, null=True)
    goodreads = models.CharField(db_column='GoodreadsID', max_length=12, blank=True, null=True)
    databazeknih = models.CharField(db_column='DatabazeKnih', max_length=16, blank=True, null=True)
    genreid = models.ForeignKey('Metagenre', models.DO_NOTHING, db_column='GenreID', null=True)
    worldid = models.ForeignKey('Metaworld', models.DO_NOTHING, db_column='WorldID', null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)

    class Meta:
        db_table = 'Book'

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

    class Meta:
        db_table = 'BookAuthor'

class Bookcomments(models.Model):
    commentid = models.IntegerField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
##    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookComments'


class Bookcover(models.Model):
    coverid = models.IntegerField(db_column='CoverID', primary_key=True)
    bookid = models.IntegerField(db_column='BookID')
    cover = models.CharField(db_column='Cover', max_length=255)

    class Meta:
        db_table = 'BookCover'


class Bookisbn(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='isbns')
    isbn = models.CharField(max_length=13, unique=True)
    edition = models.CharField(max_length=255, null=True, blank=True)
    publisherid = models.ForeignKey('Bookpublisher', models.DO_NOTHING, db_column='PublisherID', null=True)
    publicationyear = models.IntegerField(null=True, blank=True)
    format = models.CharField(max_length=100, null=True, blank=True) # e.g., Hardcover, Paperback, eBook
    language = models.CharField(max_length=100, null=True, blank=True) # e.g., English, Czech
    description = models.TextField(null=True, blank=True)
    coverimage = models.URLField(max_length=200, null=True, blank=True)
    
    class Meta:
        db_table = 'BookISBN'

class Bookpublisher(models.Model):
    publisherid = models.IntegerField(db_column='PublisherID', primary_key=True)
    publishername = models.CharField(db_column='PublisherName', max_length=255, unique=True)
    publisherurl = models.CharField(db_column='PublisherURL', max_length=255, null=True, blank=True)
    publisherdescription = models.CharField(db_column='PublisherDescription', max_length=512, null=True, blank=True)
    publisherwww = models.CharField(db_column='PublisherWWW', max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'BookPublisher'


class Bookpurchase(models.Model):
    purchaseid = models.IntegerField(db_column='PurchaseID', primary_key=True)
    purchasedate = models.DateField(db_column='PurchaseDate')
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookPurchase'


class Bookrating(models.Model):
    ratingid = models.IntegerField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    comment = models.TextField(db_column='Comment')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'BookRating'


class Characterbook(models.Model):
    bookcharacterid = models.IntegerField(db_column='BookCharacterID', null=True, blank=True)
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'CharacterBook'


class Charactergame(models.Model):
    gamecharacterid = models.IntegerField(db_column='GameCharacterID')
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'CharacterGame'


class Charactermeta(models.Model):
    characterid = models.AutoField(db_column='CharacterID', primary_key=True)
    charactername = models.CharField(db_column='CharacterName', max_length=255, unique=True)
    characternamecz = models.CharField(db_column='CharacterNameCZ', max_length=255, null=True, blank=True)
    characterdescription = models.TextField(db_column='CharacterDescription', null=True, blank=True)
    characterurl = models.URLField(db_column='CharacterURL', max_length=255, null=True, blank=True)  # Nový sloupec pro URL
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
    tvshowcharacterid = models.IntegerField(db_column='TVShowCharacterID')
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')

    class Meta:
        db_table = 'CharacterTVShow'


class Comments(models.Model):
    commentid = models.IntegerField(db_column='CommentID', primary_key=True)
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
    birthdate = models.DateField(db_column='BirthDate', null=True, blank=True)
    deathdate = models.DateField(db_column='DeathDate', null=True, blank=True)
    imdbid = models.CharField(db_column='Imdb_id', max_length=16, null=True)
    popularity = models.CharField(db_column='Popularity', max_length=32, null=True)
    img = models.CharField(db_column='IMG', max_length=32, null=True)
    knownfordepartment = models.CharField(db_column='KnownForDepartment', max_length=255, null=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True)

    class Meta:
        db_table = 'Creator'


class Creatorbiography(models.Model):
    biographyid = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Creator, on_delete=models.CASCADE, db_column='CreatorID', related_name='biographies')
    biographytext = models.TextField(db_column='BiographyText', null=True, blank=True)
    source = models.CharField(db_column='Source', max_length=255, blank=True)
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)
    language = models.CharField(db_column='Language', max_length=10, default='en')
    shortdescription = models.TextField(db_column='ShortDescription', blank=True)
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




class Creatoringame(models.Model):
    creatoringameid = models.IntegerField(db_column='CreatorInGameID', primary_key=True)
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
    creatorid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='CreatorID')

    class Meta:
        db_table = 'CreatorInGame'


class Creatorinmovie(models.Model):
    creatorinmovieid = models.IntegerField(db_column='CreatorInMovieID', primary_key=True)
    creatorid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='CreatorID')
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'CreatorInMovie'


class Creatorintvshow(models.Model):
    creatorintvshowid = models.IntegerField(db_column='CreatorInTVShowID', primary_key=True)
    creatorid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='CreatorID')
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')

    class Meta:
        db_table = 'CreatorInTVShow'


class Creatorrole(models.Model):
    roleid = models.IntegerField(db_column='RoleID', primary_key=True)
    rolename = models.CharField(db_column='RoleName', max_length=255)
    rolenamecz = models.CharField(db_column='RoleNameCZ', max_length=255, blank=True)
    department = models.CharField(db_column='Department', max_length=255, blank=True)
    class Meta:

        db_table = 'CreatorRole'


class Drink(models.Model):
    drinkid = models.IntegerField(db_column='DrinkID', primary_key=True)
    drinkname = models.CharField(db_column='DrinkName', max_length=255)
    description = models.TextField(db_column='Description')

    class Meta:
        db_table = 'Drink'


class Drinkmedia(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    mediatype = models.IntegerField(db_column='MediaType')
    drinkid = models.ForeignKey(Drink, models.DO_NOTHING, db_column='DrinkID')

    class Meta:
        db_table = 'DrinkMedia'


class Food(models.Model):
    foodid = models.IntegerField(db_column='FoodID', primary_key=True)
    foodname = models.CharField(db_column='FoodName', max_length=255)
    description = models.TextField(db_column='Description')

    class Meta:
        db_table = 'Food'


class Foodmedia(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    mediatype = models.IntegerField(db_column='MediaType')
    foodid = models.ForeignKey(Food, models.DO_NOTHING, db_column='FoodID')

    class Meta:
        db_table = 'FoodMedia'


class Game(models.Model):
    gameid = models.IntegerField(db_column='GameID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, null=True, blank=True)
    url = models.CharField(db_column='URL', max_length=255, null=True, blank=True)
    ratingid = models.IntegerField(db_column='RatingID', null=True, blank=True)
    description = models.TextField(db_column='Description', null=True, blank=True)
    platformid = models.ForeignKey('Gameplatform', models.DO_NOTHING, db_column='PlatformID', null=True, blank=True)
    publisherid = models.ForeignKey('Gamepublisher', models.DO_NOTHING, db_column='PublisherID', null=True, blank=True)
    genreid = models.ForeignKey('Metagenre', models.DO_NOTHING, db_column='GenreID', null=True, blank=True)
    worldid = models.ForeignKey('Metaworld', models.DO_NOTHING, db_column='WorldID', null=True, blank=True)
    developerid = models.ForeignKey('Gamedevelopers', models.DO_NOTHING, db_column='DeveloperID', null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', null=True, blank=True)
    averageratinggame = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRatingGame')
    class Meta:
        db_table = 'Game'
    def __str__(self):
        return self.titlecz 


class Gamecomments(models.Model):
    commentid = models.IntegerField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)   
    class Meta:
        db_table = 'GameComments'


class Gamedevelopers(models.Model):
    developerid = models.IntegerField(db_column='DeveloperID', primary_key=True)
    developername = models.CharField(db_column='DeveloperName', max_length=255)
    class Meta:
        db_table = 'GameDevelopers'
    def __str__(self):
        return self.developername 



class Gameplatform(models.Model):
    platformid = models.IntegerField(db_column='PlatformID', primary_key=True)
    platform = models.CharField(db_column='Platform', max_length=255)
    url = models.CharField(db_column='PlatformURL', max_length=255, blank=True)
    class Meta:
        db_table = 'GamePlatform'
    def __str__(self):
        return self.platform 


class Gamepublisher(models.Model):
    publisherid = models.IntegerField(db_column='PublisherID', primary_key=True)
    publishername = models.CharField(db_column='PublisherName', max_length=255)
    class Meta:
        db_table = 'GamePublisher'
    def __str__(self):
        return self.publishername 


class Gamepurchase(models.Model):
    purchaseid = models.IntegerField(db_column='PurchaseID', primary_key=True)
    purchasedate = models.DateField(db_column='PurchaseDate')
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'GamePurchase'


class Gamerating(models.Model):
    ratingid = models.IntegerField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    comment = models.TextField(db_column='Comment')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'GameRating'

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
    itemid = models.IntegerField(db_column='ItemID', primary_key=True)
    itemname = models.CharField(db_column='ItemName', max_length=255, unique=True)
    itemname_cz = models.CharField(db_column='ItemNameCZ', max_length=255, blank=True)
    itemdescription = models.TextField(db_column='ItemDescription')
    itemtype = models.CharField(max_length=3, choices=Itemtype.choices, db_column='ItemType', null=True, blank=True)
    locationid = models.ForeignKey('Location', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)


    class Meta:
        db_table = 'Item'


class Itembook(models.Model):
    bookitemid = models.IntegerField(db_column='BookItemID', primary_key=True)
    itemrole = models.CharField(db_column='ItemRole', max_length=255)
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'ItemBook'


class Itemgame(models.Model):
    gameitemid = models.IntegerField(db_column='GameItemID', primary_key=True)
    itemrole = models.CharField(db_column='ItemRole', max_length=255)
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'ItemGame'


class Itemmovie(models.Model):
    movieitemid = models.IntegerField(db_column='MovieItemID', primary_key=True)
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



class Location(models.Model):
    locationid = models.IntegerField(db_column='LocationID', primary_key=True)
    locationname = models.CharField(db_column='LocationName', max_length=255, unique=True)
    locationtype = models.CharField(db_column='LocationType', max_length=50)
    locationdescription = models.TextField(db_column='LocationDescription')
    parentlocationid = models.IntegerField(db_column='ParentLocationID', blank=True, null=True)
    locationadress = models.CharField(db_column='LocationAdress', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Location'


class Locationbook(models.Model):
    booklocationid = models.IntegerField(db_column='BookLocationID', primary_key=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey(Location, models.DO_NOTHING, db_column='LocationID')
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'LocationBook'


class Locationgame(models.Model):
    gamelocationid = models.IntegerField(db_column='GameLocationID', primary_key=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey(Location, models.DO_NOTHING, db_column='LocationID')
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'LocationGame'


class Locationmovie(models.Model):
    movielocationid = models.IntegerField(db_column='MovieLocationID', primary_key=True)
    locationrole = models.CharField(db_column='LocationRole', max_length=255)
    locationid = models.ForeignKey(Location, models.DO_NOTHING, db_column='LocationID')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'LocationMovie'


class Metacity(models.Model):
    cityid = models.IntegerField(db_column='CityID', primary_key=True)
    namecity = models.CharField(db_column='NameCity', max_length=255)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID')

    class Meta:
        db_table = 'MetaCity'

class Metacollection(models.Model):
    collectionid = models.IntegerField(db_column='CollectionID', primary_key=True)
    collectionname = models.CharField(db_column='CollectionName', max_length=255)
    collectiondescription = models.TextField(db_column='CollectionDescription')

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
        return self.countrynamecz

class Metagenre(models.Model):
    genreid = models.IntegerField(db_column='GenreID', primary_key=True)
    genrename = models.CharField(db_column='GenreName', max_length=255)
    genrenamecz = models.CharField(db_column='GenreNameCZ', max_length=255)
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True, unique=True)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    class Meta:
        db_table = 'MetaGenre'
    def __str__(self):
        return self.genrenamecz


class Metaworld(models.Model):
    worldid = models.IntegerField(db_column='WorldID', primary_key=True)
    worldname = models.CharField(db_column='WorldName', max_length=255)
    worldnamecz = models.CharField(db_column='WorldNameCZ', max_length=255, blank=True, null=True)
    worlddescription = models.TextField(db_column='WorldDescription', null=True)
    class Meta:
        db_table = 'MetaWorld'
    def __str__(self):
        return self.worldnamecz

class MovieSpecialSort(models.TextChoices):
    TOP = '1', 'Top'
    CZ = '2', 'CZ'

class Movie(models.Model):
    movieid = models.IntegerField(db_column='MovieID', primary_key=True) 
    title = models.CharField(db_column='Title', max_length=255)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, default='')    
    special = models.IntegerField(choices=MovieSpecialSort.choices, db_column='Special', blank=True, null=True)
    url = models.CharField(db_column='URL', max_length=255, unique=True)
    oldurl = models.CharField(db_column='OldURL', max_length=255, null=True)
    img = models.CharField(db_column='IMG', max_length=255, default='/static/img/filmy/nomovie.jpg')
    description = models.TextField(db_column='Description', null=True)
    releaseyear = models.CharField(db_column='ReleaseYear', max_length=4, null=True) 
    duration = models.IntegerField(db_column='Duration', null=True)
    language = models.CharField(db_column='Language', max_length=5, null=True, blank=True)  # Field
    budget = models.IntegerField(db_column='Budget', null=True)
    adult = models.CharField(db_column='Adult',  max_length=1)
    popularity = models.CharField(db_column='Popularity', max_length=7, null=True, db_index=True)
    idcsfd = models.CharField(db_column='ID_Csfd', max_length=16, null=True)
    idimdb = models.CharField(db_column='ID_Imdb', max_length=16, null=True)
    iddiv = models.CharField(db_column='ID_DIV', max_length=16, null=True)
    worldid = models.ForeignKey(Metaworld, models.DO_NOTHING, db_column='WorldID', null=True, blank=True)
#    ratings = models.ForeignKey(Rating, on_delete=models.CASCADE, related_name='movies', null=True, blank=True)
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

        
    class Meta:
        db_table = 'Movie'



class Moviecomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True, unique=True) 
    comment = models.TextField(db_column='Comment')
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  

    class Meta:
        db_table = 'MovieComments'


class Moviecountries(models.Model):
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

    class Meta:
        db_table = 'MovieCrew'


class Moviegenre(models.Model):
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'MovieGenre'


class Movierating(AbstractBaseRating, models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    movieid = models.ForeignKey(Movie, on_delete=models.CASCADE, db_column='MovieID')
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
    class Meta:
        db_table = 'MovieRating'


class Movieversions(models.Model):
    movieversionid = models.IntegerField(db_column='MovieVersionID', primary_key=True)
    versionname = models.CharField(db_column='VersionName', max_length=255)
    duration = models.IntegerField(db_column='Duration')
    releasedate = models.DateField(db_column='ReleaseDate')
    movieid = models.ForeignKey(Movie, models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'MovieVersions'


class Tvepisode(models.Model):
    episodeid = models.IntegerField(db_column='EpisodeID', primary_key=True)
    episodenumber = models.IntegerField(db_column='EpisodeNumber')
    title = models.CharField(db_column='Title', max_length=255)
    airdate = models.DateField(db_column='AirDate')
    description = models.TextField(db_column='Description')
    sessionid = models.ForeignKey('Tvseason', models.DO_NOTHING, db_column='SessionID')

    class Meta:
        db_table = 'TVEpisode'


class Tvseason(models.Model):
    sessionid = models.IntegerField(db_column='SessionID', primary_key=True)
    seasonnumber = models.IntegerField(db_column='SeasonNumber')
    premieredate = models.DateField(db_column='PremiereDate')
    enddate = models.DateField(db_column='EndDate')
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')

    class Meta:
        db_table = 'TVSeason'


class Tvshow(models.Model):
    tvshowid = models.IntegerField(db_column='TVShowID', primary_key=True)
    title = models.CharField(db_column='Title', max_length=255)
    description = models.TextField(db_column='Description')
    premieredate = models.DateField(db_column='PremiereDate')
    enddate = models.DateField(db_column='EndDate')
    rating = models.IntegerField(db_column='Rating')
    genreid = models.ForeignKey(Metagenre, models.DO_NOTHING, db_column='GenreID')
    countryid = models.ForeignKey(Metacountry, models.DO_NOTHING, db_column='CountryID')

    class Meta:
        db_table = 'TVShow'


class Userprofile(models.Model):
    userprofileid = models.AutoField(db_column='UserProfileID', primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(db_column='Bio', default="", blank=True)
    profilepicture = models.ImageField(db_column='ProfilePicture', upload_to='profiles/2023/', blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=255, null=True, blank=True)
    birthdate = models.DateField(db_column='BirthDate', null=True, blank=True)
    
    class Meta:
        db_table = 'UserProfile'
    
    
class Userlist(models.Model):
    userlistid = models.AutoField(db_column='UserListID', primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, )
    namelist = models.CharField(db_column='NameList', max_length=255)
    description = models.TextField(db_column='Description', blank=True, null=True)
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)

    class Meta:
        db_table = 'UserList'
    def __str__(self):
        return self.name    
    
    
class Userlistmovie(models.Model):
    userlistmovieid = models.AutoField(db_column='UserListMovieID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
        unique_together = [['userlist', 'movie']]
        db_table = 'UserListMovie'
    def __str__(self):
        return f"{self.user_list.name} - {self.movie.title}"



class Userlistbook(models.Model):
    userlistbookid = models.AutoField(db_column='UserListBookID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'book']]
        db_table = 'UserListBook'
    def __str__(self):
        return f"{self.user_list.name} - {self.book.title}"


class Userlistgame(models.Model):
    userlistgameid = models.AutoField(db_column='UserListGameID', primary_key=True)
    userlist = models.ForeignKey(Userlist, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'game']]
        db_table = 'UserListGame'
    def __str__(self):
        return f"{self.user_list.name} - {self.game.title}"

