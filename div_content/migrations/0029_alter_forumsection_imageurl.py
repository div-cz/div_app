# Generated by Django 4.2.4 on 2024-08-13 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0028_forumsection_imageurl'),
    ]

    operations = [
        migrations.AlterField(
            model_name='forumsection',
            name='imageurl',
            field=models.CharField(blank=True, db_column='ImageURL', help_text='Image URL', max_length=200, null=True),
        ),
    ]