# Generated by Django 5.1 on 2024-12-01 08:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0098_tvseason'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tvepisode',
            fields=[
                ('episodeid', models.AutoField(db_column='EpisodeID', primary_key=True, serialize=False)),
                ('episodeurl', models.CharField(blank=True, db_column='EpisodeURL', max_length=255, null=True)),
                ('episodenumber', models.IntegerField(db_column='EpisodeNumber')),
                ('title', models.CharField(blank=True, db_column='Title', max_length=255, null=True)),
                ('titlecz', models.CharField(blank=True, db_column='TitleCZ', max_length=255, null=True)),
                ('episodeimg', models.CharField(blank=True, db_column='EpisodeIMG', max_length=255, null=True)),
                ('airdate', models.DateField(db_column='AirDate')),
                ('description', models.TextField(db_column='Description')),
                ('episodetype', models.CharField(blank=True, db_column='EpisodeType', max_length=16, null=True)),
                ('runtime', models.IntegerField(blank=True, db_column='Runtime', null=True)),
                ('seasonid', models.ForeignKey(blank=True, db_column='SeasonID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.tvseason')),
            ],
            options={
                'db_table': 'TVEpisode',
                'unique_together': {('seasonid', 'episodeurl')},
            },
        ),
    ]