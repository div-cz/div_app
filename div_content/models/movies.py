# -------------------------------------------------------------------
#                    MODELS.MOVIES.PY
# -------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User
from star_ratings.models import AbstractBaseRating, Rating



# Special
# 0 - adult
# 1 - žádný popisek
# 2 - AJ popisek
# 3 - Český (cílový stav)

class Movie(models.Model):
    movieid = models.IntegerField(db_column='MovieID', primary_key=True) 
    title = models.CharField(db_column='Title', max_length=255)
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, default='', db_index=True)  
    titlediv = models.CharField(db_column='TitleDIV', max_length=255, null=False, blank=True, default='', db_index=True)    
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
    divrating = models.IntegerField(db_column='DIVRating', default=0, db_index=True, blank=True, null=True)
    popularity = models.FloatField(db_column='Popularity', null=True, db_index=True)
    idcsfd = models.CharField(db_column='ID_Csfd', max_length=16, null=True)
    idimdb = models.CharField(db_column='ID_Imdb', max_length=16, null=True)
    iddiv = models.CharField(db_column='ID_DIV', max_length=16, null=True)
    universumid = models.ForeignKey('Metauniversum', models.DO_NOTHING, db_column='UniversumID', null=True, blank=True)
#    ratings = models.ForeignKey('Rating', on_delete=models.CASCADE, related_name='movies', null=True, blank=True)
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
    lastupdated = models.DateField(db_column='LastUpdated', auto_now=True)

    @property
    def display_title(self):
        return self.titlediv or self.titlecz or self.title
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
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True) 
#    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    dateadded = models.DateTimeField(db_column='DateAdded', auto_now_add=True)
    class Meta:
        db_table = 'MovieComments'


class Moviecountries(models.Model):
    moviecountriesid = models.AutoField(db_column='MovieCountriesID', primary_key=True, unique=True) 
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID')

    class Meta:
        db_table = 'MovieCountries'
        unique_together = [['movieid', 'countryid']]


class Moviecrew(models.Model):
    moviecrewid = models.AutoField(db_column='MovieCrewID', primary_key=True, unique=True) 
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    peopleid = models.ForeignKey('Creator', models.DO_NOTHING, db_column='PeopleID')
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
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    genreid = models.ForeignKey('Metagenre', models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'MovieGenre'


class Movielinks(models.Model):
    linkid = models.AutoField(db_column='LinkID', primary_key=True, unique=True) 
    link = models.CharField(db_column='Link', max_length=255, unique=True)
    linktext = models.CharField(max_length=255, db_column='LinkText', null=True, blank=True)
    linkdescription = models.CharField(max_length=5125, db_column='LinkDescription', null=True, blank=True)
    linkautor = models.CharField(max_length=255, db_column='LinkAuthor', null=True, blank=True)
    linkType = models.CharField(max_length=255, db_column='LinkType')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
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
    divrating = models.IntegerField(db_column='DIVRating', default="0", db_index=True, blank=True, null=True)
    thumbsup = models.IntegerField(default=0, db_column='ThumbsUp')
    thumbsdown = models.IntegerField(default=0, db_column='ThumbsDown')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='user_id')  

    class Meta:
        db_table = 'MovieQuotes'

class Movierating(AbstractBaseRating, models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)
    rating = models.IntegerField(db_column='Rating')
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
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
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID', related_name="translations")
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
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'MovieVersions'

class Moviesource(models.Model):
    moviesourceid = models.AutoField(db_column='MovieSourceID', primary_key=True)
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID', null=True, blank=True)
    sourcetype = models.CharField(db_column='SourceType', max_length=20)
    externalid = models.CharField(db_column='ExternalID', max_length=100)
    externaltitle = models.CharField(db_column='ExternalTitle', max_length=2048, null=True, blank=True)
    releaseyear = models.CharField(db_column='ReleaseYear', max_length=4, null=True, blank=True)
    externalurl = models.CharField(db_column='ExternalURL', max_length=1024)
    createdat = models.DateTimeField(db_column='CreatedAt', auto_now_add=True)

    class Meta:
        db_table = 'MovieSource'
        unique_together = (('sourcetype', 'externalid'),)


class Tvcrew(models.Model):
    tvcrewid = models.AutoField(db_column='TVCrewID', primary_key=True)
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.DO_NOTHING, db_column='TVShowID')
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID', null=True, blank=True)
    peopleid = models.ForeignKey('Creator', models.DO_NOTHING, db_column='PeopleID')
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
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
    seasonid = models.ForeignKey('Tvseason', models.DO_NOTHING, db_column='SeasonID', null=True, blank=True)

    class Meta:
        unique_together = [['seasonid', 'episodeurl']]
        db_table = 'TVEpisode'

class Tvgenre(models.Model):
    tvgenreid = models.AutoField(db_column='TVGenreID', primary_key=True, unique=True) 
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')
    genreid = models.ForeignKey('Metagenre', models.DO_NOTHING, db_column='GenreID')

    class Meta:
        db_table = 'TVGenre'

class Tvepisodecrew(models.Model):
    tvepisodecrewid = models.AutoField(db_column='TVEpisodeCrewID', primary_key=True, unique=True) 
    episodeid = models.ForeignKey('Tvepisode', models.DO_NOTHING, db_column='EpisodeID')
    roleid = models.ForeignKey('Creatorrole', models.DO_NOTHING, db_column='RoleID')
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID', null=True, blank=True)
    peopleid = models.ForeignKey('Creator', models.DO_NOTHING, db_column='PeopleID')
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
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
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
    averagerating = models.DecimalField(max_digits=6, decimal_places=3, null=True, blank=True, db_column='AverageRating')
    language = models.CharField(db_column='Language', max_length=4, null=True, blank=True)
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID')
    universumid = models.ForeignKey('Metauniversum', models.DO_NOTHING, db_column='UniversumID', null=True, blank=True)
    createdby = models.ForeignKey('Creator', models.DO_NOTHING, db_column='CreatorID', null=True, blank=True)

    class Meta:
        db_table = 'TVShow'

class Tvshowcomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)
    comment = models.TextField(db_column='Comment')
##    userid = models.ForeignKey(User, on_delete=models.DO_NOTHING, db_column='UserID', default=1)  
    tvshowkid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')
    tvseason = models.ForeignKey('Tvseason', on_delete=models.CASCADE, null=True, blank=True, db_column='TVSeasonID')
    tvepisode = models.ForeignKey('Tvepisode', on_delete=models.CASCADE, null=True, blank=True, db_column='TVEpisodeID')
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

    # Vazby
    tvshowid = models.ForeignKey('Tvshow', on_delete=models.SET_NULL, null=True, db_column='TVShowID')
    seasonid = models.ForeignKey('Tvseason', on_delete=models.SET_NULL, null=True, db_column='SeasonID')
    episodeid = models.ForeignKey('Tvepisode', on_delete=models.SET_NULL, null=True, db_column='EpisodeID')

    userid = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, db_column='UserID')
    parenttriviaid = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='ParentTriviaID')

    divrating = models.IntegerField(db_column='DIVRating', default=0, db_index=True, blank=True, null=True)

    class Meta:
        db_table = 'TVShowTrivia'

    def __str__(self):
        return f"{self.trivia[:50]}..."



class Tvshowquotes(models.Model):
    quote_id = models.AutoField(primary_key=True, db_column='QuoteID')
    quote = models.TextField(db_column='Quote')
    actor = models.ForeignKey('Creator', on_delete=models.RESTRICT, null=True, db_column='ActorID')
    character = models.ForeignKey('Charactermeta', on_delete=models.RESTRICT, null=True, db_column='CharacterID')
    episode = models.ForeignKey('Tvepisode', on_delete=models.CASCADE, null=True, db_column='EpisodeID')
    season = models.ForeignKey('Tvseason', on_delete=models.SET_NULL, null=True, db_column='SeasonID')
    tv_show = models.ForeignKey('Tvshow', on_delete=models.SET_NULL, null=True, db_column='TVShowID')
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






