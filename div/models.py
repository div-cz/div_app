from django.db import models

class Film(models.Model):
    nazev = models.CharField(max_length=255, unique=True)
    popis = models.TextField(blank=True, null=True)
    datum_vydani = models.DateField(blank=True, null=True)

    class Meta: 
        app_label = 'divdb'

    def __str__(self):
        return self.nazev

class Hra(models.Model):
    nazev = models.CharField(max_length=255, unique=True)
    popis = models.TextField(blank=True, null=True)
    datum_vydani = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'divdb'

    def __str__(self):
        return self.nazev

class Kniha(models.Model):
    nazev = models.CharField(max_length=255, unique=True)
    autor = models.CharField(max_length=255)
    popis = models.TextField(blank=True, null=True)
    datum_vydani = models.DateField(blank=True, null=True)

    class Meta:
        app_label = 'divdb'

    def __str__(self):
        return self.nazev

class Lokalita(models.Model):
    nazev = models.CharField(max_length=255, unique=True)
    popis = models.TextField(blank=True, null=True)
    adresa = models.TextField()

    class Meta:
        app_label = 'divdb'

    def __str__(self):
        return self.nazev
