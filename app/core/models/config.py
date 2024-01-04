from django.db.models import CharField, TextChoices

from django_base.models import BaseAuditable


class Options(TextChoices):
    ROOT_HEADER_TEXT = 'ROOT_HEADER_TEXT'


class Config(BaseAuditable):
    """Runtime configuration for the application."""

    option = CharField(primary_key=True, max_length=16, choices=Options.choices)
    value = CharField(max_length=255)
