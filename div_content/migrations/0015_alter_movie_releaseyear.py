# Generated by Django 4.2.4 on 2023-09-13 20:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0014_alter_metaworld_worlddescription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='releaseyear',
            field=models.CharField(db_column='ReleaseYear', max_length=4, null=True),
        ),
    ]