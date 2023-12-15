import datetime
from typing import Optional

from django.db.models import (
    BooleanField, CharField, DateField,
    ForeignKey,
    TextField,
    TextChoices,
    PROTECT, SET_NULL,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Manufacturer(BaseAuditable):
    """
    Placeholder while I figure out how crazy to get with business entities.
    """
    name = CharField(max_length=255, unique=True)


class MediaFormat(BaseAuditable):
    name = CharField(max_length=255, unique=True)

    @classmethod
    def get_default_audio(cls) -> int:
        obj, _ = cls.objects.get_or_create(name='Audio')
        return obj.pk


class PartyType(BaseAuditable):
    name = CharField(max_length=255)
    parent_party_type = ForeignKey(
        'self',
        on_delete=SET_NULL,
        null=True, blank=True,
        related_name='child_party_types'
    )

    def __str__(self) -> str:
        return f'{self.name}'


class Payee(BaseAuditable):
    """Within scope of transaction, the entity receiving payment."""
    memo = TextField(null=True, blank=True)
    name = CharField(
        max_length=255,
        unique=True,
        help_text="Name as displayed on transaction ledger."
    )
    party = ForeignKey(
        'Party',
        on_delete=PROTECT,
        null=True,
        blank=True,
        **default_related_names(__qualname__)
    )
    party_id: int

    def __str__(self) -> str:
        return f'{self.name}'


class Person(BaseAuditable):
    """A person. Generally self-explanatory as an entity.

    Maybe a personal acquaintance, and/or a notable individual with some level
    of fame.
    """
    first_name = CharField(max_length=255)
    middle_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255)
    date_of_birth = DateField(null=True, blank=True)
    date_of_death = DateField(null=True, blank=True)
    subtype_acquaintance = BooleanField()
    subtype_notable = BooleanField()
    notes = TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.full_name}'

    @property
    def age(self) -> Optional[int]:
        if self.date_of_birth is None:
            return None
        reference_date = self.date_of_death or datetime.date.today()
        years = reference_date.year - self.date_of_birth.year
        months = reference_date.month - self.date_of_birth.month
        if months < 0:
            return years - 1
        if months == 0:
            days = reference_date.day - self.date_of_birth.day
            if days < 0:
                return years - 1
        return years

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


class Seller(BaseAuditable):
    name = CharField(max_length=255)


class Unit(BaseAuditable):
    """Unit table."""
    class Dimension(TextChoices):
        AREA = 'AREA', 'AREA'
        CURRENT = 'CURRENT', 'CURRENT'
        LENGTH = 'LENGTH', 'LENGTH'
        LIGHT = 'LIGHT', 'LIGHT'
        MASS = 'MASS', 'MASS'
        MATTER = 'MATTER', 'MATTER'
        TEMPERATURE = 'TEMPERATURE', 'TEMPERATURE'
        TIME = 'TIME', 'TIME'
        VOLUME = 'VOLUME', 'VOLUME'

    class System(TextChoices):
        SI = 'SI', 'SI'
        US = 'US', 'US'

    abbr = CharField(max_length=15)
    name = CharField(max_length=63)
    dimension = CharField(max_length=15, choices=Dimension.choices, null=True)
    system = CharField(max_length=2, choices=System.choices, null=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.abbr})'
