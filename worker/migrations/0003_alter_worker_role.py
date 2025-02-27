# Generated by Django 5.1.6 on 2025-02-25 18:31

import django.db.models.deletion
import worker.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_feature_userrole'),
        ('worker', '0002_workerlocation_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='role',
            field=models.ForeignKey(default=worker.models.get_default_user_role, on_delete=django.db.models.deletion.SET_DEFAULT, to='data.userrole'),
        ),
    ]
