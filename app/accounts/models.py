from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db.models import (
    BooleanField,
    CASCADE,
    ForeignKey,
    UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class User(AbstractUser):
    pass


class UserXBeer(BaseAuditable):
    user = ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    beer = ForeignKey(
        'core.Beer', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    has_tried = BooleanField(null=True, blank=True)
    worthy = BooleanField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('user', 'beer'),
                name='unique_user_x_beer'
            )
        ]
        verbose_name = 'User <-> Beer'
        verbose_name_plural = 'Users <-> Beer'
