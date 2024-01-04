from decimal import Decimal

from django.db.models import (
    CharField, DateField, FileField, ForeignKey, OneToOneField, TimeField,
    TextChoices,
    PROTECT, SET_NULL,
    F, Sum,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names, pascal_case_to_snake_case


class PointOfSale(BaseAuditable):
    """A PointOfSale transaction, usually accompanied by a physical receipt.

    Similar to an invoice or order, but is typically both paid and fulfilled at
    the time of the transaction.
    """

    party_id: int

    barcode = CharField(max_length=255, null=True, blank=True)
    party = ForeignKey(
        'Party', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    point_of_sale_date = DateField()
    point_of_sale_time = TimeField(null=True, blank=True)
    txn = OneToOneField(
        'Txn', on_delete=SET_NULL, null=True, blank=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )

    @property
    def line_item_total(self) -> Decimal:
        qs = (
            self.line_items.all()
            .aggregate(
                total=Sum(
                    F('catalog_item_to_point_of_sale_line_item__quantity') *
                    F('catalog_item_to_point_of_sale_line_item__unit_price')
                )
            )
        )
        return qs['total']


class PointOfSaleDocument(BaseAuditable):
    """Scanned document(s) related to a PointOfSale transaction."""

    point_of_sale = ForeignKey(
        PointOfSale, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    point_of_sale_id: int
    document = FileField()


class PointOfSaleLineItem(BaseAuditable):
    """Line items of a PointOfSale transaction."""

    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOGUE_ITEM', 'CATALOGUE_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOGUE_ITEM', 'NON_CATALOGUE_ITEM'

    point_of_sale_id: int

    point_of_sale = ForeignKey(
        PointOfSale, on_delete=PROTECT,
        related_name='line_items'
    )
    short_memo = CharField(max_length=255, null=True)
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'PointOfSaleLineItem {self.pk}: {self.point_of_sale_id}'
