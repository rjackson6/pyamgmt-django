import datetime

from django.db.models import (
    CharField, DateField, ForeignKey, TextField,
    CASCADE, UniqueConstraint
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Person(BaseAuditable):
    """A person. Generally self-explanatory as an entity.

    Maybe a personal acquaintance, and/or a notable individual with some level
    of fame.
    """
    first_name = CharField(max_length=255)
    middle_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255, blank=True)
    nickname = CharField(max_length=255, blank=True)
    preferred_name = CharField(max_length=255, blank=True)
    suffix = CharField(max_length=31, blank=True)
    date_of_birth = DateField(null=True, blank=True)
    date_of_death = DateField(null=True, blank=True)
    notes = TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.full_name}'

    @property
    def age(self) -> int | None:
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
    def is_living(self) -> bool:
        return not self.date_of_death

    @property
    def birth_name(self) -> str:
        text = f'{self.first_name}'
        if self.middle_name:
            text += f' {self.middle_name}'
        if self.last_name:
            text += f' {self.last_name}'
        if self.suffix:
            text += f' {self.suffix}'
        return text

    @property
    def full_name(self) -> str:
        if self.preferred_name:
            return self.preferred_name
        text = f'{self.first_name}'
        if self.nickname:
            text += f' "{self.nickname}"'
        if self.middle_name:
            text += f' {self.middle_name}'
        if self.last_name:
            text += f' {self.last_name}'
        if self.suffix:
            text += f' {self.suffix}'
        return text


class PersonXSongPerformance(BaseAuditable):
    person = ForeignKey(
        Person, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_performance = ForeignKey(
        'SongPerformance', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('person', 'song_performance'),
                name='unique_person_x_song_performance'
            )
        ]


# Symmetrical vs. asymmetrical modeling
# Service-layer logic. If an attribute is symmetrical, create both entries.
# if an attribute is reflective (father <-> son), create the appropriate
# entries
# if an attribute is one-way - which is rare - only make one entry
# These are just pairs of attributes.
# class PersonXPerson(BaseAuditable):
#     """Relationships between people."""
