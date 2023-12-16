import datetime

from django.db.models import BooleanField, CharField, DateField, TextField

from django_base.models import BaseAuditable


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
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'
