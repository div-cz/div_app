# Generated by Django 4.2.4 on 2024-04-29 14:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0131_aatask_ipadress_aatask_updated_alter_aatask_category_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='aatask',
            old_name='IPadress',
            new_name='IPaddress',
        ),
    ]
