# Generated by Django 4.2.4 on 2024-05-19 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0146_alter_movielocation_locationid_gamelocation_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Metatype',
            fields=[
                ('typeid', models.IntegerField(db_column='TypeID', primary_key=True, serialize=False)),
                ('tablename', models.CharField(db_column='TableName', max_length=255)),
                ('typename', models.CharField(db_column='TypeName', max_length=255)),
                ('typedescription', models.CharField(db_column='TypeDescription', max_length=1024)),
            ],
            options={
                'db_table': 'MetaType',
            },
        ),
    ]