# Generated by Django 4.2.4 on 2024-06-09 05:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0170_metasoundtrack_movietrailer_moviesoundtrack_and_more'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Movietrailer',
            new_name='Movie_trailer',
        ),
    ]