
from django.db import models

class MetaWorld(models.Model):
    worldid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaWorld'
        app_label = 'div_content'

class MetaGenre(models.Model):
    genreid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaGenre'
        app_label = 'div_content'

class GamePlatform(models.Model):
    platformid = models.AutoField(primary_key=True)
    platform = models.CharField(max_length=255)
    class Meta:
        db_table = 'GamePlatform'
        app_label = 'div_content'

class GamePublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)


    class Meta:
        db_table = 'GamePublisher'
        app_label = 'div_content'

class GameDevelopers(models.Model):
    developerid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'GameDevelopers'
        app_label = 'div_content'

class BookPublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'BookPublisher'
        app_label = 'div_content'

class MetaCountry(models.Model):
    countryid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaCountry'
        app_label = 'div_content'

class Movie(models.Model):
    movieid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    titlecz = models.CharField(max_length=255)
    url = models.CharField(max_length=128)
    oldurl = models.CharField(max_length=128, null=True, blank=True)
    description = models.TextField()
    releaseyear = models.DateField()
    duration = models.IntegerField()
    language = models.CharField(max_length=5)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    world = models.ForeignKey(MetaWorld, on_delete=models.CASCADE, db_column='WorldID')

    class Meta:
        db_table = 'Movie'
        app_label = 'div_content'

    def __str__(self):
        return self.title

class Game(models.Model):
    gameid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    ratingid = models.IntegerField()
    description = models.TextField()
    platform = models.ForeignKey(GamePlatform, on_delete=models.CASCADE)
    publisher = models.ForeignKey(GamePublisher, on_delete=models.CASCADE)
    genre = models.ForeignKey(MetaGenre, on_delete=models.CASCADE)
    world = models.ForeignKey(MetaWorld, on_delete=models.CASCADE)
    developer = models.ForeignKey(GameDevelopers, on_delete=models.CASCADE)
    country = models.ForeignKey(MetaCountry, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Game'
        app_label = 'div_content'

    def __str__(self):
        return self.title

class Book(models.Model):
    bookid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.ForeignKey(MetaGenre, on_delete=models.CASCADE)
    publisher = models.ForeignKey('BookPublisher', on_delete=models.SET_NULL, null=True)
    world = models.ForeignKey(MetaWorld, on_delete=models.CASCADE)
    country = models.ForeignKey(MetaCountry, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Book'
        app_label = 'div_content'

    def __str__(self):
        return self.title

class Lokalita(models.Model):
    nazev = models.CharField(max_length=255, verbose_name="Název lokality")
    popis = models.TextField(verbose_name="Popis lokality")
    adresa = models.CharField(max_length=255, verbose_name="Adresa lokality")

    class Meta:
        db_table = 'Lokalita'
        verbose_name = "Lokalita"
        verbose_name_plural = "Lokality"

    def __str__(self):
        return self.nazev

class Article(models.Model):
    url = models.SlugField(max_length=200, unique=True)  # Unikátní URL slug
    title = models.CharField(max_length=255, unique=True)  # Unikátní titulek
    h1 = models.CharField(max_length=255)  # H1 nadpis
    h2 = models.CharField(max_length=255, blank=True)  # H2 nadpis, není povinný
    content = models.TextField()  # Obsah článku
    img1600 = models.ImageField(upload_to='art/1600/')  # Obrázek 1600px
    img500x500 = models.ImageField(upload_to='art/500x500/')  # Obrázek 500x500
    img400x250 = models.ImageField(upload_to='art/400x250/')  # Obrázek 400x250
    alt = models.CharField(max_length=255, unique=True)  # Unikátní ALT text
    perex = models.TextField()  # Krátký perex (úvod) článku
    article = models.TextField()  # Textové tělo článku
    autor = models.CharField(max_length=255)
    typ = models.CharField(max_length=50)  # Typ článku (např. "recenze", "novi>
    counter = models.IntegerField(default=0)  # Počítadlo návštěv
    created = models.DateTimeField(auto_now_add=True)  # Datum a čas vytvoření
    updated = models.DateTimeField(auto_now=True)  # Datum a čas poslední úpravy

    def __str__(self):
        return self.title
