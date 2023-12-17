from django.db.models import (
    CharField, DateField, FileField, ForeignKey,
    TextChoices,
    CASCADE, SET_NULL,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Order(BaseAuditable):
    """A purchase record which is usually paid in advance, but not immediately
    fulfilled.
    """
    order_date = DateField()
    order_number = CharField(max_length=255)
    party = ForeignKey(
        'Party', on_delete=SET_NULL,
        null=True,
        **default_related_names(__qualname__)
    )

    def __str__(self) -> str:
        return f'Order {self.pk}: {self.order_number}'


class OrderDocument(BaseAuditable):
    order = ForeignKey(
        Order, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    document = FileField()


class OrderLineItem(BaseAuditable):
    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOG_ITEM', 'CATALOG_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOG_ITEM', 'NON_CATALOG_ITEM'
    order = ForeignKey(
        Order, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    order_id: int
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'OrderLineItem {self.pk}: {self.order_id}'
