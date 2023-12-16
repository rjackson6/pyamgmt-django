from django.db.models import (
    CharField,
    TextChoices,
)

from django_base.models import BaseAuditable


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
