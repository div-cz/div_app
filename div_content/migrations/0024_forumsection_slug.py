# Generated by Django 4.2.4 on 2024-08-12 12:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0023_forumsection_forumtopic_forumcomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='forumsection',
            name='slug',
            field=models.SlugField(blank=True, db_column='Slug', max_length=255, null=True, unique=True),
        ),
    ]
