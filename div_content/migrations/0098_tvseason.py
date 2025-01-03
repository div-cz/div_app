# Generated by Django 5.1 on 2024-12-01 08:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0097_tvshow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tvseason',
            fields=[
                ('seasonid', models.AutoField(db_column='SeasonID', primary_key=True, serialize=False)),
                ('seasonurl', models.CharField(blank=True, db_column='SeasonURL', max_length=255, null=True)),
                ('seasonnumber', models.IntegerField(db_column='SeasonNumber')),
                ('title', models.CharField(blank=True, db_column='title', max_length=255, null=True)),
                ('titlecz', models.CharField(blank=True, db_column='titleCZ', max_length=255, null=True)),
                ('img', models.CharField(blank=True, db_column='IMG', max_length=255, null=True)),
                ('seasonepisode', models.IntegerField(blank=True, db_column='SeasonEpisode', null=True)),
                ('premieredate', models.DateField(db_column='PremiereDate')),
                ('tvshowid', models.ForeignKey(db_column='TVShowID', on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.tvshow')),
            ],
            options={
                'db_table': 'TVSeason',
                'unique_together': {('tvshowid', 'seasonurl')},
            },
        ),
    ]
