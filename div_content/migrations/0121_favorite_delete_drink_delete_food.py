# Generated by Django 5.1 on 2024-12-01 20:39

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('div_content', '0120_alter_favorite_unique_together_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('favoriteid', models.AutoField(db_column='FavoriteID', primary_key=True, serialize=False)),
                ('object_id', models.PositiveIntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'Favorite',
                'unique_together': {('user', 'content_type', 'object_id')},
            },
        ),
        migrations.DeleteModel(
            name='Drink',
        ),
        migrations.DeleteModel(
            name='Food',
        ),
    ]