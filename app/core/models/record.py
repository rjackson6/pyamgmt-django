from django.db.models import (
    CharField
)

from django_base.models import BaseAuditable


class RecordLabel(BaseAuditable):
    name = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name
