# Generated by Django 4.2.4 on 2024-04-29 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0130_aatask'),
    ]

    operations = [
        migrations.AddField(
            model_name='aatask',
            name='IPadress',
            field=models.CharField(blank=True, db_column='IPadress', max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='aatask',
            name='updated',
            field=models.DateField(auto_now=True, db_column='Updated'),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='category',
            field=models.CharField(choices=[('Frontend', 'Frontend'), ('Backend', 'Backend'), ('Testování', 'Testování'), ('Databáze', 'Databáze'), ('Server', 'Server'), ('iOS', 'iOS')], db_column='Category', default='Střední', max_length=16),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='created',
            field=models.DateField(auto_now=True, db_column='Created'),
        ),
    ]
