# -------------------------------------------------------------------
#                    MODELS.CORE.PY
# -------------------------------------------------------------------

from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType




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
        ('series', 'Seriálový'),
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
    articleblog = models.ForeignKey('Articleblog', on_delete=models.CASCADE, db_column='ArticleBlogID', related_name='posts')
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
    articleblogpost = models.ForeignKey('Articleblogpost', on_delete=models.CASCADE, db_column='ArticleBlogPostID', related_name='comments')
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
    articleblogpost = models.ForeignKey('Articleblogpost', on_delete=models.CASCADE, db_column='ArticleBlogPostID', related_name='interactions')
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
    news = models.ForeignKey('Articlenews', on_delete=models.CASCADE, db_column='NewsID')
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
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')

    class Meta:
        db_table = 'CharacterMovie'


class Charactertvshow(models.Model):
    tvshowcharacterid = models.AutoField(db_column='TVShowCharacterID', primary_key=True)
    characterrole = models.CharField(db_column='CharacterRole', max_length=255)
    characterid = models.ForeignKey('Charactermeta', models.DO_NOTHING, db_column='CharacterID')
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
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, db_column='CreatorID', related_name='biographies')
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
    creator = models.ForeignKey('Creator', on_delete=models.CASCADE, db_column='CreatorID', related_name='biographies')
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
    drinkid = models.ForeignKey('Drink', models.DO_NOTHING, db_column='DrinkID')

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
    foodid = models.ForeignKey('Food', models.DO_NOTHING, db_column='FoodID')

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
    section = models.ForeignKey('Forumsection', on_delete=models.CASCADE)
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
    topic = models.ForeignKey('Forumtopic', on_delete=models.CASCADE)
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
    itemid = models.ForeignKey('Item', models.DO_NOTHING, db_column='ItemID')
    bookid = models.ForeignKey('Book', models.DO_NOTHING, db_column='BookID')

    class Meta:
        db_table = 'ItemBook'


class Itemgame(models.Model):
    gameitemid = models.AutoField(db_column='GameItemID', primary_key=True)
    itemrole = models.CharField(db_column='ItemRole', max_length=255)
    itemid = models.ForeignKey('Item', models.DO_NOTHING, db_column='ItemID')
    gameid = models.ForeignKey('Game', models.DO_NOTHING, db_column='GameID')

    class Meta:
        db_table = 'ItemGame'


class Itemmovie(models.Model):
    movieitemid = models.AutoField(db_column='MovieItemID', primary_key=True)
    itemrole = models.IntegerField(db_column='ItemRole')
    movieid = models.ForeignKey('Movie', models.DO_NOTHING, db_column='MovieID')
    itemid = models.ForeignKey('Item', models.DO_NOTHING, db_column='ItemID')

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
    item = models.ForeignKey('Item', on_delete=models.DO_NOTHING, db_column='Item')
    mediatype = models.IntegerField(choices=Itemmediatype.choices, db_column='MediaType')
    role = models.IntegerField(choices=Itemmediarole.choices, db_column='Role')
    mediaid = models.IntegerField(db_column='MediaID')  # FK to the specific media, you might need to handle this differently for each type

    class Meta:
        db_table = 'ItemMedia'






# Movie Award Model
class Movieaward(models.Model):
    movieawardid = models.AutoField(db_column='MovieAwardID', primary_key=True)
    metaAwardid = models.ForeignKey('Metaaward', on_delete=models.CASCADE, db_column='MetaAwardID')
    movieid = models.ForeignKey('Movie', on_delete=models.CASCADE, db_column='MovieID')
    winner = models.BooleanField(db_column='Winner', default=False)

    class Meta:
        db_table = 'MovieAward'

# Book Award Model
class Bookaward(models.Model):
    bookAwardid = models.AutoField(db_column='BookAwardID', primary_key=True)
    metaAwardid = models.ForeignKey('Metaaward', on_delete=models.CASCADE, db_column='MetaAwardID')
    bookid = models.ForeignKey('Book', on_delete=models.CASCADE, db_column='BookID')
    winner = models.BooleanField(db_column='Winner', default=False)

    class Meta:
        db_table = 'BookAward'

# Game Award Model
class Gameaward(models.Model):
    gameawardid = models.AutoField(db_column='GameAwardID', primary_key=True)
    metaawardid = models.ForeignKey('Metaaward', on_delete=models.CASCADE, db_column='MetaAwardID')
    gameid = models.ForeignKey('Game', on_delete=models.CASCADE, db_column='GameID')
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
    chatsession = models.ForeignKey('Userchatsession', on_delete=models.CASCADE, db_column='UserChatSession', related_name='messages')
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
    avatar = models.ForeignKey('Avatar', db_column='Avatar', null=True, blank=True, on_delete=models.SET_NULL)
    bankaccount = models.CharField(db_column='BankAccount', max_length=32, blank=True, null=True, verbose_name="Číslo účtu")
    shippingaddress = models.CharField(db_column='ShippingAddress', max_length=1024, blank=True, null=True)
    phone = models.CharField(db_column='Phone', max_length=32, blank=True, null=True, verbose_name="Telefon")

    
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
    listtype = models.ForeignKey('Userlisttype', on_delete=models.CASCADE, db_column='ListTypeID', blank=True, null=True)
    
    class Meta:
        db_table = 'UserList'

    
    def __str__(self):
        return f"{self.namelist} ({self.listtype.name if self.listtype else 'No Type'})"   

class Userlistitem(models.Model):
    userlistitemid = models.AutoField(db_column='UserListItemID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE, db_column='UserListID')
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
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    movie = models.ForeignKey('Movie', on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
        unique_together = [['userlist', 'movie']]
        db_table = 'UserListMovie'
    
    def __str__(self):
        return f"{self.userlist.namelist} - {self.movie.title}"



class Userlistbook(models.Model):
    userlistbookid = models.AutoField(db_column='UserListBookID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'book']]
        db_table = 'UserListBook'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.book.title}"


class Userlistgame(models.Model):
    userlistgameid = models.AutoField(db_column='UserListGameID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    game = models.ForeignKey('Game', on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'game']]
        db_table = 'UserListGame'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.game.title}"


class Userlisttvshow(models.Model):
    userlisttvshowid = models.AutoField(db_column='UserListTVShowID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    tvshow = models.ForeignKey('Tvshow', on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'tvshow']]
        db_table = 'UserListTVShow'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.tvshow.title}"


class Userlisttvseason(models.Model):
    userlisttvseasonid = models.AutoField(db_column='UserListTVSeasonID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    tvseason = models.ForeignKey('Tvseason', on_delete=models.CASCADE)
    addedat = models.DateTimeField(db_column='AddedAt', auto_now_add=True)

    class Meta:
#        unique_together = [['userlist', 'tvseason']]
        db_table = 'UserListTVSeason'
    def __str__(self):
        return f"{self.userlist.namelist} - {self.tvseason.title}"


class Userlisttvepisode(models.Model):
    userlisttvepisodeid = models.AutoField(db_column='UserListTVEpisodeID', primary_key=True)
    userlist = models.ForeignKey('Userlist', on_delete=models.CASCADE)
    tvepisode = models.ForeignKey('Tvepisode', on_delete=models.CASCADE)
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


