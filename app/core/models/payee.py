from django.db.models import (
    CharField, ForeignKey, TextField,
    PROTECT,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Payee(BaseAuditable):
    """Within scope of transaction, the entity receiving payment."""

    party_id: int

    memo = TextField(null=True, blank=True)
    name = CharField(
        max_length=255,
        unique=True,
        help_text="Name as displayed on transaction ledger."
    )
    party = ForeignKey(
        'Party',
        on_delete=PROTECT,
        null=True,
        blank=True,
        **default_related_names(__qualname__)
    )

    def __str__(self) -> str:
        return f'{self.name}'
