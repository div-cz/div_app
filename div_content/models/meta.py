# -------------------------------------------------------------------
#                    MODELS.META.PY
# -------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User


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
    slug = models.CharField(db_column='Slug', max_length=255, unique=False, blank=True)
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
    universumcounter = models.IntegerField(db_column='UniversumCounter', null=True, blank=True, default=0)
    tmdbid = models.IntegerField(db_column='TmdbID', blank=True, null=True)
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)


    class Meta:
        db_table = 'MetaUniversum'
    def __str__(self):
        return self.universumnamecz or self.universumname or "Neznámé Universum"
