from django.db.models import (
    CharField, ForeignKey, CASCADE, TextChoices, UniqueConstraint
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class MusicalInstrument(BaseAuditable):
    class Section(TextChoices):
        BRASS = 'B', 'Brass'
        PERCUSSION = 'P', 'Percussion'
        STRINGS = 'S', 'Strings'
        WOODWIND = 'W', 'Woodwind'

    name = CharField(max_length=63, unique=True)
    section = CharField(max_length=1, choices=Section.choices, blank=True)

    def __str__(self) -> str:
        return self.name


class MusicalInstrumentXPerson(BaseAuditable):
    musical_instrument = ForeignKey(
        MusicalInstrument, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person = ForeignKey(
        'Person', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('musical_instrument', 'person'),
                name='unique_musical_instrument_x_person'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        return f'{self.musical_instrument.name} : {self.person.full_name}'
