# Generated by Django 5.0 on 2023-12-14 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='videogameplatform',
            name='name',
            field=models.CharField(max_length=31, unique=True),
        ),
    ]