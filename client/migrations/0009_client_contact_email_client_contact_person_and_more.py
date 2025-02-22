# Generated by Django 5.1.6 on 2025-02-22 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('client', '0008_remove_clientplace_client_machines_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='industry',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='short_name',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive'), ('prospective', 'Prospective')], default='active', max_length=50),
        ),
        migrations.AddField(
            model_name='client',
            name='website',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='dimensions',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='machines/'),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='last_service_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='location_notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='manufacturer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='model',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='next_service_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='operating_hours',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='power_supply',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='purchase_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='serial_number',
            field=models.CharField(blank=True, max_length=50, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('under_repair', 'Under Repair'), ('decommissioned', 'Decommissioned')], default='active', max_length=20),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='warranty_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientmachine',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='contact_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='contact_person',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='contact_phone',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='notes',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='operating_hours',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='place_type',
            field=models.CharField(blank=True, choices=[('warehouse', 'Warehouse'), ('office', 'Office'), ('factory', 'Factory'), ('store', 'Store'), ('other', 'Other')], max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='clientplace',
            name='postal_code',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]
