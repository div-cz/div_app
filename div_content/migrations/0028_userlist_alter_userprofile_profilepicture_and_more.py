# Generated by Django 4.2.4 on 2023-10-21 21:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('div_content', '0027_alter_userprofile_userprofileid'),
    ]

    operations = [
        migrations.CreateModel(
            name='Userlist',
            fields=[
                ('userlistid', models.AutoField(db_column='UserListID', primary_key=True, serialize=False)),
                ('namelist', models.CharField(db_column='NameList', max_length=255)),
                ('description', models.TextField(blank=True, db_column='Description', null=True)),
                ('createdat', models.DateTimeField(auto_now_add=True, db_column='CreatedAt')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserList',
            },
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profilepicture',
            field=models.ImageField(blank=True, db_column='ProfilePicture', null=True, upload_to='profiles/2023/'),
        ),
        migrations.CreateModel(
            name='Userlistmovie',
            fields=[
                ('userlistmovieid', models.AutoField(db_column='UserListMovieID', primary_key=True, serialize=False)),
                ('addedat', models.DateTimeField(auto_now_add=True, db_column='AddedAt')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.movie')),
                ('userlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.userlist')),
            ],
            options={
                'db_table': 'UserListMovie',
            },
        ),
        migrations.CreateModel(
            name='Userlistgame',
            fields=[
                ('userlistgameid', models.AutoField(db_column='UserListGameID', primary_key=True, serialize=False)),
                ('addedat', models.DateTimeField(auto_now_add=True, db_column='AddedAt')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.game')),
                ('userlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.userlist')),
            ],
            options={
                'db_table': 'UserListGame',
            },
        ),
        migrations.CreateModel(
            name='Userlistbook',
            fields=[
                ('userlistbookid', models.AutoField(db_column='UserListBookID', primary_key=True, serialize=False)),
                ('addedat', models.DateTimeField(auto_now_add=True, db_column='AddedAt')),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.book')),
                ('userlist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='div_content.userlist')),
            ],
            options={
                'db_table': 'UserListBook',
            },
        ),
    ]
