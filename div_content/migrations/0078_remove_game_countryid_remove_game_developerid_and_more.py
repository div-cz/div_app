# Generated by Django 5.1 on 2024-11-30 20:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0077_tvcrew_episodecount'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='game',
            name='countryid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='developerid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='genreid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='platformid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='publisherid',
        ),
        migrations.RemoveField(
            model_name='game',
            name='universumid',
        ),
        migrations.RemoveField(
            model_name='gamerating',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='itemgame',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gamepurchase',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gamelocation',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gameplatform',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gamekeywords',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gameaward',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='gamecomments',
            name='gameid',
        ),
        migrations.RemoveField(
            model_name='userlistgame',
            name='game',
        ),
        migrations.RemoveField(
            model_name='gamegenre',
            name='movieid',
        ),
        migrations.RemoveField(
            model_name='gameaward',
            name='metaawardid',
        ),
        migrations.RemoveField(
            model_name='gamecomments',
            name='user',
        ),
        migrations.RemoveField(
            model_name='gamegenre',
            name='genreid',
        ),
        migrations.AlterUniqueTogether(
            name='gamekeywords',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='gamekeywords',
            name='keywordid',
        ),
        migrations.RemoveField(
            model_name='gamelocation',
            name='locationid',
        ),
        migrations.RemoveField(
            model_name='gameplatform',
            name='platformid',
        ),
        migrations.RemoveField(
            model_name='itemgame',
            name='itemid',
        ),
        migrations.RemoveField(
            model_name='userlistgame',
            name='userlist',
        ),
        migrations.DeleteModel(
            name='Charactergame',
        ),
        migrations.DeleteModel(
            name='Gamedevelopers',
        ),
        migrations.DeleteModel(
            name='Gamepublisher',
        ),
        migrations.DeleteModel(
            name='Gamerating',
        ),
        migrations.DeleteModel(
            name='Gamepurchase',
        ),
        migrations.DeleteModel(
            name='Game',
        ),
        migrations.DeleteModel(
            name='Gameaward',
        ),
        migrations.DeleteModel(
            name='Gamecomments',
        ),
        migrations.DeleteModel(
            name='Gamegenre',
        ),
        migrations.DeleteModel(
            name='Gamekeywords',
        ),
        migrations.DeleteModel(
            name='Gamelocation',
        ),
        migrations.DeleteModel(
            name='Gameplatform',
        ),
        migrations.DeleteModel(
            name='Itemgame',
        ),
        migrations.DeleteModel(
            name='Userlistgame',
        ),
    ]