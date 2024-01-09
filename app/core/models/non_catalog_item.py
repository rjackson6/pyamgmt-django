from django.db.models import (
    CharField, ForeignKey,
    CASCADE, UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class NonCatalogItem(BaseAuditable):
    """A non-tangible or generic item, such as a tax levied."""

    name = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f'{self.name}'


class NonCatalogItemXOrderLineItem(BaseAuditable):
    non_catalog_item = ForeignKey(
        NonCatalogItem, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    order_line_item = ForeignKey(
        'OrderLineItem', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['non_catalog_item', 'order_line_item'],
                name='unique_non_catalog_item_x_order_line_item'
            )
        ]


class NonCatalogItemXPointOfSaleLineItem(BaseAuditable):
    non_catalog_item = ForeignKey(
        NonCatalogItem, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    point_of_sale_line_item = ForeignKey(
        'PointOfSaleLineItem', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('non_catalog_item', 'point_of_sale_line_item'),
                name='unique_non_catalog_item_x_point_of_sale_line_item'
            )
        ]
