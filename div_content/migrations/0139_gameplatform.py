# Generated by Django 5.1 on 2024-12-01 21:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0138_metaplatform'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gameplatform',
            fields=[
                ('gameplatformid', models.AutoField(db_column='GamePlatformID', primary_key=True, serialize=False)),
                ('gameid', models.ForeignKey(db_column='GameID', on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.game')),
                ('platformid', models.ForeignKey(db_column='PlatformID', on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metaplatform')),
            ],
            options={
                'db_table': 'GamePlatform',
            },
        ),
    ]