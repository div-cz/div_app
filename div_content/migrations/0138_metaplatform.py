# Generated by Django 5.1 on 2024-12-01 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0137_delete_metaplatform'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metaplatform',
            fields=[
                ('platformid', models.AutoField(db_column='PlatformID', primary_key=True, serialize=False)),
                ('platform', models.CharField(blank=True, db_column='Platform', max_length=255, null=True)),
                ('url', models.CharField(blank=True, db_column='PlatformURL', max_length=255, null=True)),
            ],
            options={
                'db_table': 'MetaPlatform',
            },
        ),
    ]