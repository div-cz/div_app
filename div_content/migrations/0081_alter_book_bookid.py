# Generated by Django 4.2.4 on 2023-12-31 19:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0080_alter_book_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='bookid',
            field=models.AutoField(db_column='BookID', primary_key=True, serialize=False),
        ),
    ]
