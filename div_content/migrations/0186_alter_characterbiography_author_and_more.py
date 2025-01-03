# Generated by Django 5.1 on 2024-12-25 16:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0185_alter_metauniversum_universumurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='characterbiography',
            name='author',
            field=models.CharField(blank=True, db_column='Author', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='characterborn',
            field=models.CharField(blank=True, db_column='CharacterBorn', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='characterdeath',
            field=models.CharField(blank=True, db_column='CharacterDeath', max_length=16, null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='externallink',
            field=models.URLField(blank=True, db_column='ExternalLink', null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='img',
            field=models.URLField(blank=True, db_column='IMG', null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='notes',
            field=models.TextField(blank=True, db_column='Notes', null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='shortdescription',
            field=models.TextField(blank=True, db_column='ShortDescription', null=True),
        ),
        migrations.AlterField(
            model_name='characterbiography',
            name='source',
            field=models.CharField(blank=True, db_column='Source', max_length=255, null=True),
        ),
    ]
