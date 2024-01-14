# Generated by Django 4.2.4 on 2023-10-21 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0024_moviecrew_charactertvshow_charactermovie_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='birthdate',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, null=True, upload_to='img/profiles/2023/'),
        ),
    ]