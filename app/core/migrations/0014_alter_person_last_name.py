# Generated by Django 5.0 on 2023-12-16 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_invoicedocument_invoicextxn_delete_pointofsalextxn'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='last_name',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]