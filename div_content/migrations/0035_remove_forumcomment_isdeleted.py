# Generated by Django 5.1 on 2024-08-19 20:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0034_forumcomment_isdeleted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='forumcomment',
            name='isdeleted',
        ),
    ]