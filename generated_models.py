

class Bookaward(models.Model):
    bookawardid = models.AutoField(db_column='BookAwardID', primary_key=True)  # Field name made lowercase.
    winner = models.IntegerField(db_column='Winner')  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    metaawardid = models.ForeignKey('Metaaward', models.DO_NOTHING, db_column='MetaAwardID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookAward'






class Bookisbn(models.Model):
    bookisbnid = models.AutoField(db_column='BookISBNID', primary_key=True)  # Field name made lowercase.
    isbn = models.CharField(db_column='ISBN', unique=True, max_length=26)  # Field name made lowercase.
    isbntype = models.CharField(db_column='ISBNtype', max_length=255, blank=True, null=True)  # Field name made lowercase.
    publicationyear = models.IntegerField(db_column='PublicationYear', blank=True, null=True)  # Field name made lowercase.
    format = models.CharField(db_column='Format', max_length=100, blank=True, null=True)  # Field name made lowercase.
    language = models.CharField(db_column='Language', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    coverimg = models.CharField(db_column='CoverIMG', max_length=200, blank=True, null=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    publisherid = models.ForeignKey('Bookpublisher', models.DO_NOTHING, db_column='PublisherID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookISBN'


class Bookkeywords(models.Model):
    bookkeywordid = models.AutoField(db_column='BookKeywordID', primary_key=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    keywordid = models.ForeignKey('Metakeywords', models.DO_NOTHING, db_column='KeywordID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookKeywords'
        unique_together = (('bookid', 'keywordid'),)


class Booklocation(models.Model):
    booklocationid = models.AutoField(db_column='BookLocationID', primary_key=True)  # Field name made lowercase.
    locationrole = models.CharField(db_column='LocationRole', max_length=255)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookLocation'


class Bookpublisher(models.Model):
    publisherid = models.IntegerField(db_column='PublisherID', primary_key=True)  # Field name made lowercase.
    publishername = models.CharField(db_column='PublisherName', unique=True, max_length=255)  # Field name made lowercase.
    publisherurl = models.CharField(db_column='PublisherURL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    publisherdescription = models.CharField(db_column='PublisherDescription', max_length=512, blank=True, null=True)  # Field name made lowercase.
    publisherwww = models.CharField(db_column='PublisherWWW', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookPublisher'


class Bookpurchase(models.Model):
    purchaseid = models.AutoField(db_column='PurchaseID', primary_key=True)  # Field name made lowercase.
    purchasedate = models.DateField(db_column='PurchaseDate')  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookPurchase'


class Bookquotes(models.Model):
    quoteid = models.AutoField(db_column='QuoteID', primary_key=True)  # Field name made lowercase.
    quote = models.TextField(db_column='Quote')  # Field name made lowercase.
    authorid = models.ForeignKey(Bookauthor, models.DO_NOTHING, db_column='AuthorID', blank=True, null=True)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID', blank=True, null=True)  # Field name made lowercase.
    parentquoteid = models.ForeignKey('self', models.DO_NOTHING, db_column='ParentQuoteID', blank=True, null=True)  # Field name made lowercase.
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)
    chapter = models.IntegerField(db_column='Chapter', blank=True, null=True)  # Field name made lowercase.
    thumbsdown = models.IntegerField(db_column='ThumbsDown')  # Field name made lowercase.
    thumbsup = models.IntegerField(db_column='ThumbsUp')  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookQuotes'


class Bookrating(models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)  # Field name made lowercase.
    rating = models.IntegerField(db_column='Rating')  # Field name made lowercase.
    comment = models.TextField(db_column='Comment')  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookRating'


class Bookwriters(models.Model):
    bookwriterid = models.AutoField(db_column='BookWriterID', primary_key=True)  # Field name made lowercase.
    authorid = models.ForeignKey(Bookauthor, models.DO_NOTHING, db_column='AuthorID')  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'BookWriters'
        unique_together = (('bookid', 'authorid'),)


class BookWendy(models.Model):
    bookid = models.AutoField(db_column='BookID', primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=255, blank=True, null=True)  # Field name made lowercase.
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, blank=True, null=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    pages = models.IntegerField(db_column='Pages', blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    img = models.CharField(db_column='IMG', max_length=255)  # Field name made lowercase.
    subtitle = models.CharField(db_column='Subtitle', max_length=255, blank=True, null=True)  # Field name made lowercase.
    author = models.CharField(db_column='Author', max_length=255)  # Field name made lowercase.
    pseudonym = models.CharField(db_column='Pseudonym', max_length=2, blank=True, null=True)  # Field name made lowercase.
    googleid = models.CharField(db_column='GoogleID', max_length=16, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    goodreadsid = models.CharField(db_column='GoodreadsID', max_length=12, blank=True, null=True)  # Field name made lowercase.
    databazeknih = models.CharField(db_column='DatabazeKnih', max_length=16, blank=True, null=True)  # Field name made lowercase.
    language = models.CharField(db_column='Language', max_length=2, blank=True, null=True)  # Field name made lowercase.
    lastupdated = models.DateField(db_column='LastUpdated')  # Field name made lowercase.
    authorid = models.IntegerField(db_column='AuthorID', blank=True, null=True)  # Field name made lowercase.
    countryid = models.IntegerField(db_column='CountryID', blank=True, null=True)  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating', blank=True, null=True)  # Field name made lowercase.
    special = models.IntegerField(db_column='Special', blank=True, null=True)  # Field name made lowercase.
    universumid = models.IntegerField(db_column='UniversumID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Book_Wendy'


class Characterbiography(models.Model):
    biographyid = models.AutoField(primary_key=True)
    characterborn = models.CharField(db_column='CharacterBorn', max_length=16, blank=True, null=True)  # Field name made lowercase.
    characterdeath = models.CharField(db_column='CharacterDeath', max_length=16, blank=True, null=True)  # Field name made lowercase.
    biographytext = models.TextField(db_column='BiographyText', blank=True, null=True)  # Field name made lowercase.
    source = models.CharField(db_column='Source', max_length=255, blank=True, null=True)  # Field name made lowercase.
    lastupdated = models.DateField(db_column='LastUpdated')  # Field name made lowercase.
    language = models.CharField(db_column='Language', max_length=10, blank=True, null=True)  # Field name made lowercase.
    externallink = models.CharField(db_column='ExternalLink', max_length=200, blank=True, null=True)  # Field name made lowercase.
    img = models.CharField(db_column='IMG', max_length=200, blank=True, null=True)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes', blank=True, null=True)  # Field name made lowercase.
    author = models.CharField(db_column='Author', max_length=255, blank=True, null=True)  # Field name made lowercase.
    verificationstatus = models.CharField(db_column='VerificationStatus', max_length=10)  # Field name made lowercase.
    isprimary = models.IntegerField(db_column='IsPrimary')  # Field name made lowercase.
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')  # Field name made lowercase.
    userid = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.
    biographytextcz = models.TextField(db_column='BiographyTextCZ', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CharacterBiography'


class Charactergame(models.Model):
    gamecharacterid = models.AutoField(db_column='GameCharacterID', primary_key=True)  # Field name made lowercase.
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)  # Field name made lowercase.
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')  # Field name made lowercase.
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CharacterGame'


class Charactermeta(models.Model):
    characterid = models.AutoField(db_column='CharacterID', primary_key=True)  # Field name made lowercase.
    charactername = models.CharField(db_column='CharacterName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    characternamecz = models.CharField(db_column='CharacterNameCZ', max_length=255, blank=True, null=True)  # Field name made lowercase.
    characterimg = models.CharField(db_column='CharacterIMG', max_length=128, blank=True, null=True)  # Field name made lowercase.
    characterbio = models.CharField(db_column='CharacterBio', max_length=1, blank=True, null=True)  # Field name made lowercase.
    characterurl = models.CharField(db_column='CharacterURL', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    charactercount = models.IntegerField(db_column='CharacterCount', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CharacterMeta'


class Charactermovie(models.Model):
    moviecharacterid = models.AutoField(db_column='MovieCharacterID', primary_key=True)  # Field name made lowercase.
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)  # Field name made lowercase.
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')  # Field name made lowercase.
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CharacterMovie'


class Charactertvshow(models.Model):
    tvshowcharacterid = models.AutoField(db_column='TVShowCharacterID', primary_key=True)  # Field name made lowercase.
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)  # Field name made lowercase.
    characterid = models.ForeignKey(Charactermeta, models.DO_NOTHING, db_column='CharacterID')  # Field name made lowercase.
    tvshowid = models.ForeignKey('Tvshow', models.DO_NOTHING, db_column='TVShowID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CharacterTVShow'


class Comments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment')  # Field name made lowercase.
    commentdate = models.DateField(db_column='CommentDate')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Comments'





class Creatorbiography(models.Model):
    biographyid = models.AutoField(primary_key=True)
    biographytext = models.TextField(db_column='BiographyText', blank=True, null=True)  # Field name made lowercase.
    biographytextcz = models.TextField(db_column='BiographyTextCZ')  # Field name made lowercase.
    source = models.CharField(db_column='Source', max_length=255)  # Field name made lowercase.
    lastupdated = models.DateField(db_column='LastUpdated')  # Field name made lowercase.
    language = models.CharField(db_column='Language', max_length=10)  # Field name made lowercase.
    externallink = models.CharField(db_column='ExternalLink', max_length=200)  # Field name made lowercase.
    imageurl = models.CharField(db_column='ImageURL', max_length=200)  # Field name made lowercase.
    notes = models.TextField(db_column='Notes')  # Field name made lowercase.
    author = models.CharField(db_column='Author', max_length=255)  # Field name made lowercase.
    verificationstatus = models.CharField(db_column='VerificationStatus', max_length=10)  # Field name made lowercase.
    isprimary = models.IntegerField(db_column='IsPrimary')  # Field name made lowercase.
    creatorid = models.ForeignKey(Creator, models.DO_NOTHING, db_column='CreatorID')  # Field name made lowercase.
    userid = models.ForeignKey('AuthUser', models.DO_NOTHING, db_column='UserID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CreatorBiography'


class Creatorrole(models.Model):
    roleid = models.IntegerField(db_column='RoleID', primary_key=True)  # Field name made lowercase.
    rolename = models.CharField(db_column='RoleName', max_length=255)  # Field name made lowercase.
    rolenamecz = models.CharField(db_column='RoleNameCZ', max_length=255)  # Field name made lowercase.
    department = models.CharField(db_column='Department', max_length=255)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'CreatorRole'


class Drink(models.Model):
    drinkid = models.AutoField(db_column='DrinkID', primary_key=True)  # Field name made lowercase.
    drinkname = models.CharField(db_column='DrinkName', max_length=255)  # Field name made lowercase.
    drinkurl = models.CharField(db_column='DrinkURL', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    drinktype = models.CharField(db_column='DrinkType', max_length=255, blank=True, null=True)  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Drink'


class Drinkmedia(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mediatype = models.IntegerField(db_column='MediaType')  # Field name made lowercase.
    drinkid = models.ForeignKey(Drink, models.DO_NOTHING, db_column='DrinkID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'DrinkMedia'


class Favorite(models.Model):
    favoriteid = models.AutoField(db_column='FavoriteID', primary_key=True)  # Field name made lowercase.
    object_id = models.PositiveIntegerField()
    created_at = models.DateTimeField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Favorite'
        unique_together = (('user', 'content_type', 'object_id'),)


class Favoritesum(models.Model):
    favorite_sum_id = models.AutoField(primary_key=True)
    object_id = models.PositiveIntegerField()
    favorite_count = models.PositiveIntegerField()
    last_updated = models.DateTimeField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'FavoriteSum'
        unique_together = (('content_type', 'object_id'),)


class Food(models.Model):
    foodid = models.AutoField(db_column='FoodID', primary_key=True)  # Field name made lowercase.
    foodname = models.CharField(db_column='FoodName', max_length=255)  # Field name made lowercase.
    foodurl = models.CharField(db_column='FoodURL', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description')  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Food'


class Foodmedia(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)  # Field name made lowercase.
    mediatype = models.IntegerField(db_column='MediaType')  # Field name made lowercase.
    foodid = models.ForeignKey(Food, models.DO_NOTHING, db_column='FoodID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'FoodMedia'


class Forumcomment(models.Model):
    forumcommentid = models.AutoField(db_column='ForumCommentID', primary_key=True)  # Field name made lowercase.
    body = models.TextField()
    created_at = models.DateTimeField(db_column='Created_at')  # Field name made lowercase.
    parentcommentid = models.IntegerField(db_column='ParentCommentID', blank=True, null=True)  # Field name made lowercase.
    topic = models.ForeignKey('Forumtopic', models.DO_NOTHING)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)
    lasteditedat = models.DateTimeField(db_column='LastEditedAt', blank=True, null=True)  # Field name made lowercase.
    isdeleted = models.IntegerField(db_column='IsDeleted')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ForumComment'


class Forumsection(models.Model):
    forumsectionid = models.AutoField(db_column='ForumSectionID', primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', unique=True, max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    slug = models.CharField(db_column='Slug', unique=True, max_length=255, blank=True, null=True)  # Field name made lowercase.
    imageurl = models.CharField(db_column='ImageURL', max_length=200, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ForumSection'


class Forumtopic(models.Model):
    forumtopicid = models.AutoField(db_column='ForumTopicID', primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', unique=True, max_length=255)  # Field name made lowercase.
    created_at = models.DateTimeField(db_column='Created_at')  # Field name made lowercase.
    url = models.CharField(db_column='URL', unique=True, max_length=255)  # Field name made lowercase.
    section = models.ForeignKey(Forumsection, models.DO_NOTHING)
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ForumTopic'


class Game(models.Model):
    gameid = models.AutoField(db_column='GameID', primary_key=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=255)  # Field name made lowercase.
    titlecz = models.CharField(db_column='TitleCZ', max_length=255, blank=True, null=True)  # Field name made lowercase.
    url = models.CharField(db_column='URL', max_length=255, blank=True, null=True)  # Field name made lowercase.
    metacritic = models.IntegerField(db_column='MetaCritic', blank=True, null=True)  # Field name made lowercase.
    descriptioncz = models.TextField(db_column='DescriptionCZ', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    year = models.IntegerField(db_column='Year', blank=True, null=True)  # Field name made lowercase.
    averageratinggame = models.DecimalField(db_column='AverageRatingGame', max_digits=6, decimal_places=3, blank=True, null=True)  # Field name made lowercase.
    countryid = models.ForeignKey('Metacountry', models.DO_NOTHING, db_column='CountryID', blank=True, null=True)  # Field name made lowercase.
    rawgid = models.IntegerField(db_column='RawgID', blank=True, null=True)  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating')  # Field name made lowercase.
    special = models.IntegerField(db_column='Special', blank=True, null=True)  # Field name made lowercase.
    systemrequirements = models.TextField(db_column='SystemRequirements', blank=True, null=True)  # Field name made lowercase.
    universumid = models.ForeignKey('Metauniversumold', models.DO_NOTHING, db_column='UniversumID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Game'


class Gameaward(models.Model):
    gameawardid = models.AutoField(db_column='GameAwardID', primary_key=True)  # Field name made lowercase.
    winner = models.IntegerField(db_column='Winner')  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    metaawardid = models.ForeignKey('Metaaward', models.DO_NOTHING, db_column='MetaAwardID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameAward'


class Gamecomments(models.Model):
    commentid = models.AutoField(db_column='CommentID', primary_key=True)  # Field name made lowercase.
    comment = models.TextField(db_column='Comment', blank=True, null=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    user = models.ForeignKey('AuthUser', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'GameComments'


class Gamedevelopers(models.Model):
    gamedeveloperid = models.AutoField(db_column='GameDeveloperID', primary_key=True)  # Field name made lowercase.
    developerid = models.ForeignKey('Metadeveloper', models.DO_NOTHING, db_column='DeveloperID')  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameDevelopers'





class Gameitem(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    itemimage = models.CharField(db_column='ItemImage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    locationid = models.ForeignKey('Gamelocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.ForeignKey('Gamesession', models.DO_NOTHING, db_column='SessionID', blank=True, null=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey('Gameseason', models.DO_NOTHING, db_column='SeasonID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameItem'


class Gamekeywords(models.Model):
    gamekeywordid = models.AutoField(db_column='GameKeywordID', primary_key=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    keywordid = models.ForeignKey('Metakeywords', models.DO_NOTHING, db_column='KeywordID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameKeywords'
        unique_together = (('gameid', 'keywordid'),)


class Gamelocation(models.Model):
    gamelocationid = models.AutoField(db_column='GameLocationID', primary_key=True)  # Field name made lowercase.
    locationrole = models.CharField(db_column='LocationRole', max_length=255)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.
    locationname = models.CharField(db_column='LocationName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    relatedseason = models.ForeignKey('Gameseason', models.DO_NOTHING, db_column='RelatedSeason', blank=True, null=True)  # Field name made lowercase.
    shortdescription = models.CharField(db_column='ShortDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameLocation'


class Gameplatform(models.Model):
    gameplatformid = models.AutoField(db_column='GamePlatformID', primary_key=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    platformid = models.ForeignKey('Metaplatform', models.DO_NOTHING, db_column='PlatformID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GamePlatform'


class Gamepublisher(models.Model):
    gamepublisherid = models.AutoField(db_column='GamePublisherID', primary_key=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    publisherid = models.ForeignKey('Metapublisher', models.DO_NOTHING, db_column='PublisherID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GamePublisher'


class Gamepurchase(models.Model):
    gamepurchaseid = models.AutoField(db_column='GamePurchaseID', primary_key=True)  # Field name made lowercase.
    purchasedate = models.DateField(db_column='PurchaseDate')  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=10, decimal_places=2)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GamePurchase'


class Gamerating(models.Model):
    ratingid = models.AutoField(db_column='RatingID', primary_key=True)  # Field name made lowercase.
    rating = models.IntegerField(db_column='Rating')  # Field name made lowercase.
    comment = models.TextField(db_column='Comment')  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameRating'


class Gameseason(models.Model):
    seasonid = models.AutoField(db_column='SeasonID', primary_key=True)  # Field name made lowercase.
    seasonname = models.CharField(db_column='SeasonName', max_length=255)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    chapter = models.CharField(db_column='Chapter', max_length=255, blank=True, null=True)  # Field name made lowercase.
    backgroundimage = models.CharField(db_column='BackgroundImage', max_length=255, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameSeason'


class Gamesession(models.Model):
    sessionid = models.AutoField(db_column='SessionID', primary_key=True)  # Field name made lowercase.
    sessionname = models.CharField(db_column='SessionName', max_length=255, blank=True, null=True)  # Field name made lowercase.
    startdate = models.DateField(db_column='StartDate', blank=True, null=True)  # Field name made lowercase.
    enddate = models.DateField(db_column='EndDate', blank=True, null=True)  # Field name made lowercase.
    backgroundimage = models.CharField(db_column='BackgroundImage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    chapter = models.CharField(db_column='Chapter', max_length=255, blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    seasonid = models.ForeignKey(Gameseason, models.DO_NOTHING, db_column='SeasonID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameSession'


class Gamespecial(models.Model):
    specialid = models.AutoField(db_column='SpecialID', primary_key=True)  # Field name made lowercase.
    specialname = models.CharField(db_column='SpecialName', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    gametype = models.CharField(db_column='GameType', max_length=50)  # Field name made lowercase.
    image = models.CharField(db_column='Image', max_length=255, blank=True, null=True)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    locationid = models.ForeignKey(Gamelocation, models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameSpecial'


class Gametask(models.Model):
    taskid = models.AutoField(db_column='TaskID', primary_key=True)  # Field name made lowercase.
    taskname = models.CharField(db_column='TaskName', max_length=255)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    targetquantity = models.IntegerField(db_column='TargetQuantity')  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    seasonid = models.ForeignKey(Gameseason, models.DO_NOTHING, db_column='SeasonID', blank=True, null=True)  # Field name made lowercase.
    sessionid = models.ForeignKey(Gamesession, models.DO_NOTHING, db_column='SessionID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameTask'


class Gametaskitem(models.Model):
    taskitemid = models.AutoField(db_column='TaskItemID', primary_key=True)  # Field name made lowercase.
    hint = models.TextField(db_column='Hint', blank=True, null=True)  # Field name made lowercase.
    description = models.TextField(db_column='Description', blank=True, null=True)  # Field name made lowercase.
    itemimage = models.CharField(db_column='ItemImage', max_length=255, blank=True, null=True)  # Field name made lowercase.
    locationid = models.ForeignKey(Gamelocation, models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.
    taskid = models.ForeignKey(Gametask, models.DO_NOTHING, db_column='TaskID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GameTaskItem'


class Item(models.Model):
    itemid = models.AutoField(db_column='ItemID', primary_key=True)  # Field name made lowercase.
    itemname = models.CharField(db_column='ItemName', unique=True, max_length=255)  # Field name made lowercase.
    itemnamecz = models.CharField(db_column='ItemNameCZ', max_length=255)  # Field name made lowercase.
    itemdescription = models.TextField(db_column='ItemDescription')  # Field name made lowercase.
    itemtype = models.CharField(db_column='ItemType', max_length=3, blank=True, null=True)  # Field name made lowercase.
    locationid = models.ForeignKey('Metalocation', models.DO_NOTHING, db_column='LocationID', blank=True, null=True)  # Field name made lowercase.
    divrating = models.IntegerField(db_column='DIVRating', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Item'


class Itembook(models.Model):
    bookitemid = models.AutoField(db_column='BookItemID', primary_key=True)  # Field name made lowercase.
    itemrole = models.CharField(db_column='ItemRole', max_length=255)  # Field name made lowercase.
    bookid = models.ForeignKey(Book, models.DO_NOTHING, db_column='BookID')  # Field name made lowercase.
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ItemBook'


class Itemgame(models.Model):
    gameitemid = models.AutoField(db_column='GameItemID', primary_key=True)  # Field name made lowercase.
    itemrole = models.CharField(db_column='ItemRole', max_length=255)  # Field name made lowercase.
    gameid = models.ForeignKey(Game, models.DO_NOTHING, db_column='GameID')  # Field name made lowercase.
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ItemGame'


class Itemmedia(models.Model):
    mediaitemid = models.AutoField(db_column='MediaItemID', primary_key=True)  # Field name made lowercase.
    mediatype = models.IntegerField(db_column='MediaType')  # Field name made lowercase.
    role = models.IntegerField(db_column='Role')  # Field name made lowercase.
    mediaid = models.IntegerField(db_column='MediaID')  # Field name made lowercase.
    item = models.ForeignKey(Item, models.DO_NOTHING, db_column='Item')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ItemMedia'


class Itemmovie(models.Model):
    movieitemid = models.AutoField(db_column='MovieItemID', primary_key=True)  # Field name made lowercase.
    itemrole = models.IntegerField(db_column='ItemRole')  # Field name made lowercase.
    itemid = models.ForeignKey(Item, models.DO_NOTHING, db_column='ItemID')  # Field name made lowercase.
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ItemMovie'







