from django.db.models import (
    CASCADE, CharField, ForeignKey, OneToOneField, SET_NULL, TextChoices
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names, pascal_case_to_snake_case


class Party(BaseAuditable):
    class Subtype(TextChoices):
        COMPANY = 'BUSINESS'
        PERSON = 'PERSON'
    name = CharField(max_length=255)
    party_type = ForeignKey(
        'PartyType',
        on_delete=SET_NULL,
        null=True,
        blank=True,
        **default_related_names(__qualname__)
    )
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'{self.name}'


class PartyBusiness(BaseAuditable):
    """A business or corporate entity."""
    party = OneToOneField(
        Party, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    party_id: int
    trade_name = CharField(max_length=255)

    def __str__(self) -> str:
        return f'PartyCompany {self.pk}: {self.trade_name}'


class PartyPerson(BaseAuditable):
    """An individual person."""
    party = OneToOneField(
        Party, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    party_id: int
    person = OneToOneField(
        'Person', on_delete=CASCADE,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    person_id: int
