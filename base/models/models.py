__all__ = ['Base', 'BaseAuditable']

from django.db import models
from django.db.models.fields import DateTimeField


# Create your models here.
class Base(models.Model):
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
