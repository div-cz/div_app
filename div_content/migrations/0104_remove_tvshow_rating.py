# Generated by Django 4.2.4 on 2024-04-07 08:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0103_tvshow_popularity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tvshow',
            name='rating',
        ),
    ]