# Generated by Django 5.1 on 2024-12-24 23:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0179_alter_book_lastupdated'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Userbookgoal',
            fields=[
                ('userbookgoalid', models.AutoField(db_column='UserBookGoalID', primary_key=True, serialize=False)),
                ('goalyear', models.PositiveIntegerField(db_column='GoalYear')),
                ('goal', models.PositiveIntegerField(db_column='Goal', default=0)),
                ('booksread', models.PositiveIntegerField(db_column='BooksRead', default=0)),
                ('lastupdated', models.DateTimeField(auto_now=True, db_column='LastUpdated')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'UserBookGoal',
                'unique_together': {('user', 'goalyear')},
            },
        ),
    ]
