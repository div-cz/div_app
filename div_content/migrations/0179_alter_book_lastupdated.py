# Generated by Django 5.1 on 2024-12-24 12:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0178_alter_book_lastupdated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='lastupdated',
            field=models.DateField(auto_now=True, db_column='LastUpdated'),
        ),
    ]
