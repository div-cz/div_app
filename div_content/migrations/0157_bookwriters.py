# Generated by Django 4.2.4 on 2024-05-22 20:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0156_alter_book_universumid_delete_bookwriters'),
    ]

    operations = [
        migrations.CreateModel(
            name='Bookwriters',
            fields=[
                ('bookwriterid', models.AutoField(db_column='BookWriterID', primary_key=True, serialize=False)),
                ('author', models.ForeignKey(db_column='AuthorID', on_delete=django.db.models.deletion.CASCADE, to='div_content.bookauthor')),
                ('book', models.ForeignKey(db_column='BookID', on_delete=django.db.models.deletion.CASCADE, to='div_content.book')),
            ],
            options={
                'db_table': 'BookWriters',
                'unique_together': {('book', 'author')},
            },
        ),
    ]
