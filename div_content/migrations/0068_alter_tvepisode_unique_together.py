# Generated by Django 5.1 on 2024-11-17 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0067_alter_tvseason_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='tvepisode',
            unique_together={('seasonid', 'episodeurl')},
        ),
    ]