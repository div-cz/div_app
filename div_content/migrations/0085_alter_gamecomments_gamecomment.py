# Generated by Django 5.1 on 2024-11-30 21:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0084_charactergame_gamedevelopers_gamepublisher_itemgame'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamecomments',
            name='gamecomment',
            field=models.TextField(blank=True, db_column='GameComment', null=True),
        ),
    ]
