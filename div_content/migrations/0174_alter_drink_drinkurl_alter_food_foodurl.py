# Generated by Django 4.2.4 on 2024-06-09 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0173_drink_drinkurl_food_foodurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drink',
            name='drinkurl',
            field=models.CharField(blank=True, db_column='DrinkURL', max_length=255, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='food',
            name='foodurl',
            field=models.CharField(blank=True, db_column='FoodURL', max_length=255, null=True, unique=True),
        ),
    ]
