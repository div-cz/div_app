# Generated by Django 5.1 on 2024-12-20 08:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0173_remove_book_universumid_remove_game_universumid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tvshow',
            name='universumid',
        ),
    ]
