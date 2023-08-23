
from django.db import models

class MetaWorld(models.Model):
    worldid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaWorld'
        app_label = 'divdb'

class MetaGenre(models.Model):
    genreid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaGenre'
        app_label = 'divdb'

class GamePlatform(models.Model):
    platformid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'GamePlatform'
        app_label = 'divdb'

class GamePublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'GamePublisher'
        app_label = 'divdb'

class GameDevelopers(models.Model):
    developerid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'GameDevelopers'
        app_label = 'divdb'

class BookPublisher(models.Model):
    publisherid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'BookPublisher'
        app_label = 'divdb'

class MetaCountry(models.Model):
    countryid = models.AutoField(primary_key=True)

    class Meta:
        db_table = 'MetaCountry'
        app_label = 'divdb'

class Movie(models.Model):
    movieid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField()
    releaseyear = models.DateField()
    duration = models.IntegerField()
    language = models.CharField(max_length=5)
    budget = models.DecimalField(max_digits=15, decimal_places=2)
    world = models.ForeignKey(MetaWorld, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Movie'
        app_label = 'divdb'

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
        app_label = 'divdb'

    def __str__(self):
        return self.title

class Book(models.Model):
    bookid = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    description = models.TextField()
    genre = models.ForeignKey(MetaGenre, on_delete=models.CASCADE)
    publisher = models.ForeignKey(BookPublisher, on_delete=models.CASCADE)
    world = models.ForeignKey(MetaWorld, on_delete=models.CASCADE)
    country = models.ForeignKey(MetaCountry, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Book'
        app_label = 'divdb'

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
