# Generated by Django 5.1.6 on 2025-02-21 14:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0003_delete_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tag',
            options={'verbose_name': 'Tag', 'verbose_name_plural': 'Tags'},
        ),
        migrations.AlterModelOptions(
            name='taskcategory',
            options={'verbose_name': 'Task category', 'verbose_name_plural': 'Task categories'},
        ),
    ]
