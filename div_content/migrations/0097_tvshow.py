# Generated by Django 5.1 on 2024-12-01 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0096_delete_tvshow'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tvshow',
            fields=[
                ('tvshowid', models.AutoField(db_column='TVShowID', primary_key=True, serialize=False)),
                ('title', models.CharField(blank=True, db_column='Title', max_length=255, null=True)),
                ('titlecz', models.CharField(blank=True, db_column='TitleCZ', max_length=255, null=True)),
                ('url', models.CharField(blank=True, db_column='URL', max_length=255, null=True)),
                ('description', models.TextField(blank=True, db_column='Description', null=True)),
                ('status', models.CharField(blank=True, db_column='Status', max_length=32, null=True)),
                ('img', models.CharField(blank=True, db_column='IMG', max_length=64, null=True)),
                ('imgposter', models.CharField(blank=True, db_column='IMGposter', max_length=64, null=True)),
                ('premieredate', models.DateField(db_column='PremiereDate')),
                ('enddate', models.DateField(db_column='EndDate')),
                ('popularity', models.IntegerField(db_column='Popularity', db_index=True, null=True)),
                ('language', models.CharField(blank=True, db_column='Language', max_length=4, null=True)),
                ('countryid', models.ForeignKey(db_column='CountryID', on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metacountry')),
                ('createdby', models.ForeignKey(blank=True, db_column='CreatorID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.creator')),
                ('universumid', models.ForeignKey(blank=True, db_column='UniversumID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metauniversum')),
            ],
            options={
                'db_table': 'TVShow',
            },
        ),
    ]