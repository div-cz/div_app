# Generated by Django 5.1 on 2024-11-16 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0064_tvcountries_tvkeywords_tvproductions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tvcountries',
            name='tvcountryid',
            field=models.AutoField(db_column='TVCountryID', primary_key=True, serialize=False),
        ),
    ]