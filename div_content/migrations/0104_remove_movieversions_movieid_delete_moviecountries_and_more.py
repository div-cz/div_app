# Generated by Django 5.1 on 2024-12-01 20:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0103_delete_tvgenre'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='movieversions',
            name='movieid',
        ),
        migrations.DeleteModel(
            name='Moviecountries',
        ),
        migrations.DeleteModel(
            name='Movieversions',
        ),
    ]