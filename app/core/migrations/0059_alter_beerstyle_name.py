# Generated by Django 5.0 on 2023-12-21 02:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0058_beerstyle_brewery_uscity_beer_brewery_city'),
    ]

    operations = [
        migrations.AlterField(
            model_name='beerstyle',
            name='name',
            field=models.CharField(max_length=63, unique=True),
        ),
    ]