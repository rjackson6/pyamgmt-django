__all__ = ['Base', 'BaseAuditable']

from django.db.models import Model
from django.db.models.fields import DateTimeField

# from base.db.models.base import Model


class Base(Model):
    """Simple Django abstract Model class.

    Prevents Django from instantiating a Model from a template call.
    """
    do_not_call_in_templates = True

    class Meta:
        abstract = True

    def __str__(self):
        return f"{self.__class__.__name__} {self.pk}"


class BaseAuditable(Base):
    """Adds auto-timestamps as fields."""
    timestamp_created = DateTimeField(auto_now_add=True)
    timestamp_modified = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
