# Generated by Django 4.2.4 on 2024-06-01 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0167_book_lastupdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookisbn',
            name='isbn',
            field=models.CharField(db_column='ISBN', max_length=26, unique=True),
        ),
    ]