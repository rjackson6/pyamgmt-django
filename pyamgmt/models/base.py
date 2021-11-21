from types import SimpleNamespace

from django.db import models

from deform.db.models.fields import DateTimeField


class Base(models.Model):
    do_not_call_in_templates = True

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.__class__.__name__} {self.pk}'

    @staticmethod
    def lookups():
        """Returns a dictionary of helpful values for use with querysets.
        Override this method to specify names/traversals on the target class.
        """
        return {}

    @classmethod
    def lookups_ns(cls):
        """Convenience method which returns lookups() as a SimpleNamespace."""
        return SimpleNamespace(**cls.lookups())


class BaseAuditable(Base):
    timestamp_created = DateTimeField(auto_now_add=True)
    timestamp_modified = DateTimeField(auto_now=True)

    class Meta:
        abstract = True
