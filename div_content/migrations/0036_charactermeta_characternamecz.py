# Generated by Django 4.2.4 on 2023-10-25 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0035_alter_charactermeta_characterurl'),
    ]

    operations = [
        migrations.AddField(
            model_name='charactermeta',
            name='characternamecz',
            field=models.CharField(blank=True, db_column='CharacterNameCZ', max_length=255, null=True),
        ),
    ]
