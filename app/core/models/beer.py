from django.db.models import CharField, DecimalField, ForeignKey, SET_NULL, TextField

from django_base.models import BaseAuditable


class Beer(BaseAuditable):
    name = CharField(max_length=63)
    short_description = CharField(max_length=255, blank=True)
    description = TextField(blank=True)
    abv = DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    brewery = ForeignKey(
        'Brewery', on_delete=SET_NULL,
        null=True, blank=True,
    )
    style = ForeignKey(
        'BeerStyle', on_delete=SET_NULL,
        null=True, blank=True,
    )

    def __str__(self) -> str:
        return self.name


class BeerStyle(BaseAuditable):
    name = CharField(max_length=63, unique=True)

    def __str__(self) -> str:
        return self.name


class Brewery(BaseAuditable):
    name = CharField(max_length=63, unique=True)
    city = ForeignKey(
        'USCity', on_delete=SET_NULL,
        null=True, blank=True,
    )

    def __str__(self) -> str:
        return f'{self.name}'
