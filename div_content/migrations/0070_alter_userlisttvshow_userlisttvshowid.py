# Generated by Django 5.1 on 2024-11-17 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0069_userlisttvshow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlisttvshow',
            name='userlisttvshowid',
            field=models.AutoField(db_column='UserListTVShowID', primary_key=True, serialize=False),
        ),
    ]