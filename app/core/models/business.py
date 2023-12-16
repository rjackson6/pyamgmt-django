from django.db.models import CharField

from django_base.models import BaseAuditable


class Business(BaseAuditable):
    name = CharField(max_length=255, unique=True)
