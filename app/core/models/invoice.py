from django.db.models import (
    CharField, DateField, ForeignKey, OneToOneField,
    TextChoices,
    CASCADE, SET_NULL,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names, pascal_case_to_snake_case


class Invoice(BaseAuditable):
    """Payment due to a party for a good or service."""
    invoice_date = DateField()
    invoice_number = CharField(max_length=255)
    party = ForeignKey(
        'Party', on_delete=SET_NULL,
        null=True,
        **default_related_names(__qualname__)
    )


class InvoiceLineItem(BaseAuditable):
    """A line item related to an Invoice."""
    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOGUE_ITEM', 'CATALOGUE_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOGUE_ITEM', 'NON_CATALOGUE_ITEM'
    invoice = ForeignKey(
        Invoice, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    invoice_id: int
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'InvoiceLineItem {self.pk}: {self.invoice_id}'


class InvoiceLineItemXNonCatalogItem(BaseAuditable):
    """Relates a NonCatalogItem record to an InvoiceLineItem record."""
    invoice_line_item = OneToOneField(
        InvoiceLineItem, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    invoice_line_item_id: int
    non_catalog_item = ForeignKey(
        'NonCatalogItem', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    non_catalog_item_id: int

    def __str__(self) -> str:
        return (
            f'InvoiceLineItemXNonCatalogItem {self.invoice_line_item_id}:'
            f' {self.non_catalog_item_id}'
        )
