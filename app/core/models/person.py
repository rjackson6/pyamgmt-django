import datetime

from django.db.models import (
    CharField, DateField, OneToOneField, TextField,
    CASCADE,
)

from django_base.models import BaseAuditable
from django_base.utils import pascal_case_to_snake_case


class Person(BaseAuditable):
    """A person. Generally self-explanatory as an entity.

    Maybe a personal acquaintance, and/or a notable individual with some level
    of fame.
    """
    first_name = CharField(max_length=255)
    middle_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255, blank=True)
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
    def full_name(self) -> str:
        text = f'{self.first_name}'
        if self.last_name:
            text += f' {self.last_name}'
        return text


# class PersonXPerson(BaseAuditable):
#     """Relationships between people."""

