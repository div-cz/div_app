# Generated by Django 4.2.4 on 2024-05-19 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0152_metacity_namecitycz_metastreet'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metacity',
            name='cityid',
            field=models.AutoField(db_column='CityID', primary_key=True, serialize=False),
        ),
    ]
