from django.db import models

from base.models import Base
from base.utils import default_related_names


class GeneralTestModel(Base):
    name = models.CharField(max_length=31)


class GeneralModelWithFK(Base):
    name = models.CharField(max_length=31)
    fk = models.ForeignKey(
        GeneralTestModel,
        on_delete=models.CASCADE,
        **default_related_names(__qualname__)
    )
