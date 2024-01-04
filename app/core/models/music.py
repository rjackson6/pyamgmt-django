from django.db.models import (
    CharField, ForeignKey, CASCADE, TextChoices, UniqueConstraint
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class MusicRole(BaseAuditable):
    """An individual's role for their contribution to a music album.

    E.g., Vocalist, Guitarist, Engineer, Producer
    """

    name = CharField(max_length=31, unique=True)

    def __str__(self):
        return self.name


class MusicRoleXPersonXSong(BaseAuditable):
    music_role = ForeignKey(
        'MusicRole', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person_x_song = ForeignKey(
        'PersonXSong', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )


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
        verbose_name = 'MusicalInstrument <-> Person'
        verbose_name_plural = verbose_name
