# Generated by Django 5.1 on 2024-08-25 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0044_alter_bookcomments_dateadded'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookcomments',
            name='commentid',
            field=models.AutoField(db_column='CommentID', primary_key=True, serialize=False),
        ),
    ]