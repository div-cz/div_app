# Generated by Django 5.1 on 2024-12-20 08:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0175_metauniversum_tmdbid_alter_metauniversum_universumid'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='universumid',
            field=models.ForeignKey(db_column='UniversumID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metauniversum'),
        ),
        migrations.AddField(
            model_name='game',
            name='universumid',
            field=models.ForeignKey(blank=True, db_column='UniversumID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metauniversum'),
        ),
        migrations.AddField(
            model_name='movie',
            name='universumid',
            field=models.ForeignKey(blank=True, db_column='UniversumID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metauniversum'),
        ),
        migrations.AddField(
            model_name='tvshow',
            name='universumid',
            field=models.ForeignKey(blank=True, db_column='UniversumID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metauniversum'),
        ),
    ]
