# Generated by Django 5.0 on 2023-12-16 06:54

import core.validators
import django.core.validators
import django.db.models.deletion
import re
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_motionpicture_unique_motion_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='person',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_set', related_query_name='author', to='core.person'),
        ),
        migrations.AlterField(
            model_name='catalogitem',
            name='isbn_13',
            field=models.CharField(blank=True, max_length=13, null=True, unique=True, validators=[django.core.validators.MinLengthValidator(13), django.core.validators.RegexValidator(code='invalid', message='Enter a valid digit.', regex=re.compile('^\\d+\\Z')), core.validators.validate_isbn_13_check_digit], verbose_name='ISBN-13'),
        ),
        migrations.DeleteModel(
            name='AuthorXPerson',
        ),
    ]