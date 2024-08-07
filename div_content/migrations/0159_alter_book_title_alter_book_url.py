# Generated by Django 4.2.4 on 2024-05-23 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0158_rename_characterbook_charactercharacter_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='title',
            field=models.CharField(db_column='Title', db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='book',
            name='url',
            field=models.CharField(blank=True, db_column='URL', db_index=True, max_length=255, null=True),
        ),
    ]
