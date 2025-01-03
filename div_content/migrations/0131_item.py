# Generated by Django 5.1 on 2024-12-01 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0130_delete_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('itemid', models.AutoField(db_column='ItemID', primary_key=True, serialize=False)),
                ('itemname', models.CharField(db_column='ItemName', max_length=255, unique=True)),
                ('itemname_cz', models.CharField(blank=True, db_column='ItemNameCZ', max_length=255)),
                ('itemdescription', models.TextField(db_column='ItemDescription')),
                ('itemtype', models.CharField(blank=True, choices=[('1', 'Zbraň'), ('2', 'Nástroj'), ('3', 'Oděv'), ('4', 'Vozidlo'), ('5', 'Dokument'), ('6', 'Klenot'), ('7', 'Domácí potřeby'), ('8', 'Magický předmět'), ('9', 'Artefakt'), ('10', 'Ostatní')], db_column='ItemType', max_length=3, null=True)),
                ('locationid', models.ForeignKey(blank=True, db_column='LocationID', null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='div_content.metalocation')),
            ],
            options={
                'db_table': 'Item',
            },
        ),
    ]
