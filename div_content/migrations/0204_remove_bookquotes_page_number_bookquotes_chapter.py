# Generated by Django 4.2.4 on 2024-09-01 06:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0203_bookquotes_page_number_bookquotes_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bookquotes',
            name='page_number',
        ),
        migrations.AddField(
            model_name='bookquotes',
            name='chapter',
            field=models.IntegerField(blank=True, db_column='Chapter', null=True),
        ),
    ]