# Generated by Django 4.2.4 on 2023-11-18 09:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0047_game_titlecz'),
    ]

    operations = [
        migrations.RenameField(
            model_name='game',
            old_name='titleCZ',
            new_name='titlecz',
        ),
    ]
