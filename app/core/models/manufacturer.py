from django.db.models import CharField, OneToOneField, SET_NULL

from django_base.models import BaseAuditable
from django_base.utils import pascal_case_to_snake_case


class Manufacturer(BaseAuditable):
    business = OneToOneField(
        'Business', on_delete=SET_NULL,
        null=True, blank=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    name = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.name
