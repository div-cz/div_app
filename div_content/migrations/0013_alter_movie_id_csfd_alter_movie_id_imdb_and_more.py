# Generated by Django 4.2.4 on 2023-09-13 20:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0012_alter_movie_description_alter_movie_duration_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='movie',
            name='id_csfd',
            field=models.CharField(db_column='ID_Csfd', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='id_imdb',
            field=models.CharField(db_column='ID_Imdb', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='movie',
            name='id_tmdb',
            field=models.CharField(db_column='ID_Tmdb', max_length=16, null=True),
        ),
    ]