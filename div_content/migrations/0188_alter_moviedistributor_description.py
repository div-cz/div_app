# Generated by Django 4.2.4 on 2024-07-28 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0187_alter_moviedistributor_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moviedistributor',
            name='description',
            field=models.TextField(blank=True, db_column='Description', null=True),
        ),
    ]