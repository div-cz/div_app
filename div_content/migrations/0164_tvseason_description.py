# Generated by Django 5.1 on 2024-12-13 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0163_book_special_game_special'),
    ]

    operations = [
        migrations.AddField(
            model_name='tvseason',
            name='description',
            field=models.TextField(blank=True, db_column='Description', null=True),
        ),
    ]
