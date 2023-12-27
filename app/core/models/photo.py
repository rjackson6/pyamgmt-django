from django.db.models import CharField, ImageField, TextField

from django_base.models import BaseAuditable


class Photo(BaseAuditable):
    short_description = CharField(max_length=255, blank=True)
    description = TextField(blank=True)
    image = ImageField()
