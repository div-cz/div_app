# Generated by Django 4.2.4 on 2024-05-07 15:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0139_alter_aatask_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='creatorinmovie',
            name='creatorid',
        ),
        migrations.RemoveField(
            model_name='creatorinmovie',
            name='movieid',
        ),
        migrations.RemoveField(
            model_name='creatorinmovie',
            name='roleid',
        ),
        migrations.RemoveField(
            model_name='creatorintvshow',
            name='creatorid',
        ),
        migrations.RemoveField(
            model_name='creatorintvshow',
            name='roleid',
        ),
        migrations.RemoveField(
            model_name='creatorintvshow',
            name='tvshowid',
        ),
        migrations.DeleteModel(
            name='Creatoringame',
        ),
        migrations.DeleteModel(
            name='Creatorinmovie',
        ),
        migrations.DeleteModel(
            name='Creatorintvshow',
        ),
    ]
