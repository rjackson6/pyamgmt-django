from django.db import models
from django.db.models import Manager

from base.models import Base
from base.utils import default_related_names


class SuperManager(Manager):
    """Testing inheritance between classes."""

    def get_queryset(self):
        print(f'calling {__class__}.get_queryset()...')
        qs = super().get_queryset().filter(name__icontains='5')
        print(qs.query)
        return qs


class SubManager(SuperManager):
    """"""

    def get_queryset(self):
        print(f'calling {__class__}.get_queryset()...')
        qs = super().get_queryset().filter(name__icontains='7')
        print(qs.query)
        return qs


class GeneralTestModel(Base):
    name = models.CharField(max_length=31)

    objects = SuperManager()
    sub_objects = SubManager()

    def __str__(self):
        return f'{self.name}'


class GeneralModelWithFK(Base):
    name = models.CharField(max_length=31)
    fk = models.ForeignKey(
        GeneralTestModel,
        on_delete=models.CASCADE,
        **default_related_names(__qualname__)
    )
