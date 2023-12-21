from django.db.models import CharField

from django_base.models import BaseAuditable

from ._enums import USState


class USCity(BaseAuditable):
    name = CharField(max_length=255)
    us_state = CharField(max_length=2, choices=USState.choices)

    def __str__(self):
        return f'{self.name}, {self.us_state}'
