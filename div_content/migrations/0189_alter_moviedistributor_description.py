# Generated by Django 4.2.4 on 2024-07-28 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0188_alter_moviedistributor_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviedistributor',
            name='description',
            field=models.CharField(blank=True, db_column='Description', max_length=512, null=True),
        ),
    ]
