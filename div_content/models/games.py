# -------------------------------------------------------------------
#                    MODELS.GAMES.PY
# -------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User



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
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
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


class Gamelisting(models.Model):
    LISTING_TYPES = (
        ('SELL', 'Prodám'),
        ('BUY', 'Koupím'),
        ('GIVE', 'Daruji'),
    )
    LISTING_STATUS = (
        ('ACTIVE', 'Aktivní'),
        ('RESERVED', 'Rezervováno'),
        ('PAID', 'Zaplaceno'),
        ('COMPLETED', 'Dokončeno'),
        ('CANCELLED', 'Zrušeno'),
        ('DELETED', 'Smazáno'),
    )

    gamelistingid = models.AutoField(db_column='GameListingID', primary_key=True)
    user = models.ForeignKey(User, db_column='user_id', on_delete=models.CASCADE)
    buyer = models.ForeignKey(
        User,
        db_column='BuyerID',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='games_bought'
    )
    game = models.ForeignKey('Game', db_column='game_id', on_delete=models.CASCADE)
    listingtype = models.CharField(db_column='ListingType', max_length=4, choices=LISTING_TYPES)
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2, null=True, blank=True)
    shipping = models.DecimalField(db_column='Shipping', max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='Poštovné')
    commission = models.IntegerField(db_column='Commission', verbose_name='Provize na chod webu')
    personal_pickup = models.BooleanField(db_column='PersonalPickup', verbose_name='Osobní převzetí')
    description = models.TextField(db_column='Description', max_length=512, blank=True, null=True)
    condition = models.CharField(db_column='Condition', max_length=50, blank=True, null=True)
    location = models.CharField(db_column='Location', max_length=100, blank=True, null=True)
    createdat = models.DateTimeField(db_column='CreateDat', auto_now_add=True)
    updatedat = models.DateTimeField(db_column='UpdateDat', auto_now=True)
    completedat = models.DateTimeField(db_column='CompletedAt', null=True, blank=True)
    active = models.BooleanField(db_column='Active', default=True)
    status = models.CharField(db_column='Status', max_length=10, choices=LISTING_STATUS, default='ACTIVE')
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
        db_table = 'GameListing'

    def __str__(self):
        return f"{self.game} ({self.listingtype})"


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
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID', related_name='sessions')
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
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
    relatedseason = models.ForeignKey('Gameseason', on_delete=models.CASCADE, db_column='RelatedSeason', related_name="locations", null=True, blank=True)

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
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')
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







