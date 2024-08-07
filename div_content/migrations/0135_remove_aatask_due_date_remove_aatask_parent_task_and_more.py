# Generated by Django 4.2.4 on 2024-04-29 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('div_content', '0134_alter_aatask_assigned'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aatask',
            name='due_date',
        ),
        migrations.RemoveField(
            model_name='aatask',
            name='parent_task',
        ),
        migrations.AddField(
            model_name='aatask',
            name='duedate',
            field=models.DateField(db_column='DueDate', default='2025-10-10'),
        ),
        migrations.AddField(
            model_name='aatask',
            name='parentid',
            field=models.ForeignKey(blank=True, db_column='ParentID', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Subtasks', to='div_content.aatask'),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='assigned',
            field=models.CharField(blank=True, db_column='Assigned', max_length=64, null=True),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='comments',
            field=models.TextField(blank=True, db_column='Comments', null=True),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='created',
            field=models.DateField(auto_now_add=True, db_column='Created'),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='description',
            field=models.TextField(db_column='Description'),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='id',
            field=models.AutoField(db_column='ID', primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='aatask',
            name='title',
            field=models.CharField(db_column='Title', max_length=255),
        ),
    ]
