from django.conf import settings
from django.db.models import (
    BooleanField,
    CASCADE,
    CharField,
    DecimalField,
    ForeignKey,
    SET_NULL,
    TextField,
    UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


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


class BeerXUser(BaseAuditable):
    beer = ForeignKey(
        Beer, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    user = ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    approved = BooleanField(null=True, blank=True)
    has_tried = BooleanField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('beer', 'user'),
                name='unique_beer_x_user'
            )
        ]
        verbose_name = 'Beer <-> User'
        verbose_name_plural = verbose_name


class Brewery(BaseAuditable):
    name = CharField(max_length=63, unique=True)
    city = ForeignKey(
        'USCity', on_delete=SET_NULL,
        null=True, blank=True,
    )

    class Meta:
        verbose_name_plural = 'breweries'

    def __str__(self) -> str:
        return f'{self.name}'
