# Generated by Django 4.2.4 on 2024-08-29 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0201_articleblog_articleblogpost_userdivcoins_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metastats',
            fields=[
                ('metastatsid', models.AutoField(db_column='MetaStatsID', primary_key=True, serialize=False)),
                ('statname', models.CharField(db_column='StatName', max_length=255, unique=True)),
                ('tablemodel', models.CharField(blank=True, db_column='TableModel', max_length=255, null=True)),
                ('value', models.IntegerField(db_column='Value', default=0)),
                ('updatedat', models.DateTimeField(auto_now=True, db_column='UpdatedAt')),
            ],
            options={
                'db_table': 'MetaStats',
            },
        ),
    ]