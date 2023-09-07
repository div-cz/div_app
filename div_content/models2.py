# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Book(models.Model):
    bookid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    country = models.ForeignKey('Metacountry', models.DO_NOTHING)
    genre = models.ForeignKey('Metagenre', models.DO_NOTHING)
    publisher = models.ForeignKey('Bookpublisher', models.DO_NOTHING, blank=True, null=True)
    world = models.ForeignKey('Metaworld', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Book'


class Bookpublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'BookPublisher'


class Game(models.Model):
    gameid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    ratingid = models.IntegerField()
    description = models.TextField()
    country = models.ForeignKey('Metacountry', models.DO_NOTHING)
    developer = models.ForeignKey('Gamedevelopers', models.DO_NOTHING)
    genre = models.ForeignKey('Metagenre', models.DO_NOTHING)
    platform = models.ForeignKey('Gameplatform', models.DO_NOTHING)
    publisher = models.ForeignKey('Gamepublisher', models.DO_NOTHING)
    world = models.ForeignKey('Metaworld', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'Game'


class Gamedevelopers(models.Model):
    developerid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'GameDevelopers'


class Gameplatform(models.Model):
    platformid = models.AutoField(primary_key=True)
    platform = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'GamePlatform'


class Gamepublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'GamePublisher'


class Lokalita(models.Model):
    id = models.BigAutoField(primary_key=True)
    nazev = models.CharField(max_length=255)
    popis = models.TextField()
    adresa = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'Lokalita'


class Metacountry(models.Model):
    countryid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'MetaCountry'


class Metagenre(models.Model):
    genreid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'MetaGenre'


class Metaworld(models.Model):
    worldid = models.AutoField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'MetaWorld'


class Movie(models.Model):
    movieid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    titlecz = models.CharField(max_length=255)
    url = models.CharField(max_length=128)
    oldurl = models.CharField(max_length=128, blank=True, null=True)
    description = models.TextField()
    releaseyear = models.CharField(max_length=4)
    duration = models.IntegerField()
    language = models.CharField(max_length=5, blank=True, null=True)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    worldid = models.ForeignKey(Metaworld, models.DO_NOTHING, db_column='WorldID', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Movie'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DivContentArticle(models.Model):
    id = models.BigAutoField(primary_key=True)
    url = models.CharField(unique=True, max_length=200)
    title = models.CharField(unique=True, max_length=255)
    h1 = models.CharField(max_length=255)
    h2 = models.CharField(max_length=255)
    content = models.TextField()
    img1600 = models.CharField(max_length=100)
    img500x500 = models.CharField(max_length=100)
    img400x250 = models.CharField(max_length=100)
    alt = models.CharField(unique=True, max_length=255)
    perex = models.TextField()
    article = models.TextField()
    autor = models.CharField(max_length=255)
    typ = models.CharField(max_length=50)
    counter = models.IntegerField()
    created = models.DateTimeField()
    updated = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'div_content_article'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
