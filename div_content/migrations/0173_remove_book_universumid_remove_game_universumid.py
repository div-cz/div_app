# Generated by Django 5.1 on 2024-12-20 08:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0172_remove_movie_universumid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='book',
            name='universumid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='universumid',
        ),
    ]
