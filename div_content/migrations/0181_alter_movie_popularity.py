# Generated by Django 4.2.4 on 2024-07-18 18:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0180_metauniversum_universumcounter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='popularity',
            field=models.FloatField(db_column='Popularity', db_index=True, null=True),
        ),
    ]
