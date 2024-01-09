from django.db.models import (
    CASCADE,
    CharField,
    DateField,
    ForeignKey,
    IntegerField,
    OneToOneField,
    PROTECT,
    SET_NULL,
    TextChoices,
    TextField,
    UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names, pascal_case_to_snake_case


class Asset(BaseAuditable):
    """Any item which implies ownership.

    The subtype is required to distinguish between business logic.
    """

    class Subtype(TextChoices):
        # CONTRACT = 'CONTRACT', 'CONTRACT'
        DISCRETE = 'DISCRETE', 'DISCRETE'
        INVENTORY = 'INVENTORY', 'INVENTORY'

    description = TextField(blank=True, default='')
    subtype = CharField(max_length=9, choices=Subtype.choices)

    class Meta:
        verbose_name = 'Asset'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'Asset {self.pk}: {self.description[:30]}'


class AssetDiscrete(BaseAuditable):
    """An item that is uniquely identifiable.

    Examples: A vehicle, serialized equipment, or property.
    I would perhaps go further to suggest that a discrete asset can be sold and
    resold.
    """

    class Subtype(TextChoices):
        MANUFACTURED = 'MANUFACTURED', 'MANUFACTURED'
        REAL_ESTATE = 'REAL_ESTATE', 'REAL_ESTATE'
        VEHICLE = 'VEHICLE', 'VEHICLE'

    asset_id: int

    asset = OneToOneField(
        Asset, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    date_acquired = DateField(null=True, blank=True)
    date_withdrawn = DateField(null=True, blank=True)
    subtype = CharField(max_length=12, choices=Subtype.choices, blank=True)

    class Meta:
        verbose_name = 'Asset::Discrete'
        verbose_name_plural = verbose_name


class AssetDiscreteManufactured(BaseAuditable):
    """Ownership of a manufactured item.

    Uniquely identifiable by a serial number, which would also be known to the
    manufacturer of the item. This allows lookup for product registration,
    warranties, and services.
    """

    asset = OneToOneField(
        Asset, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    catalog_item_manufactured = ForeignKey(
        'CatalogItemManufactured', on_delete=SET_NULL,
        null=True, blank=True,
        **default_related_names(__qualname__)
    )
    serial = CharField(
        max_length=255,
        help_text="Manufacturer serial number (or other unique identifier)"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('catalog_item_manufactured', 'serial'),
                name='unique_asset_discrete_manufactured_serial',
                nulls_distinct=False
            )
        ]


class AssetDiscreteRealEstate(BaseAuditable):
    """Ownership of a unique parcel of real estate, such as housing or land."""

    asset_discrete = OneToOneField(
        AssetDiscrete, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    real_estate_parcel = OneToOneField(
        'RealEstateParcel', on_delete=PROTECT,
        related_name=pascal_case_to_snake_case(__qualname__)
    )


class AssetDiscreteVehicle(BaseAuditable):
    """A discrete asset that can be associated with a unique vehicle.

    Though Vehicles are Manufactured, this relates to the more detailed Vehicle
    model.
    """

    asset_discrete_id: int
    vehicle_id: int

    asset_discrete = OneToOneField(
        AssetDiscrete, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    vehicle = OneToOneField(
        'Vehicle', on_delete=PROTECT,
        related_name=pascal_case_to_snake_case(__qualname__)
    )

    class Meta:
        verbose_name = 'Asset::Discrete::Vehicle'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f'AssetDiscreteVehicle {self.pk}: {self.vehicle_id}'


class AssetInventory(BaseAuditable):
    """An item that is not uniquely identifiable.

    Example: Copies of DVDs, un-serialized items.

    `quantity` is a reference field. Common consumables, like groceries, aren't
    really going to be inventoried. Spare parts and materials, however, can be
    used for a specific project, or charged against a particular discrete asset.
    I should be able to charge items against events and have the quantity
    consumed; however, I think it's enough to measure rates of consumption
    through purchase frequency, and I don't own anything with capital components
    that warrant a spare parts system.

    That said, `quantity` is a harmless field to keep and use for informational
    purposes.
    """

    asset_id: int
    catalog_item_id: int

    asset = OneToOneField(
        Asset, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    # CatalogItem is OneToOne because inventory should accumulate
    catalog_item = OneToOneField(
        'CatalogItem', on_delete=PROTECT,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    quantity = IntegerField(default=1)

    class Meta:
        verbose_name = 'Asset::Inventory'
        verbose_name_plural = verbose_name


class AssetType(BaseAuditable):
    """Expandable type to support hierarchy

    Not to be confused with AssetSubtype.
    """
    # TODO 2023-12-12: Do I care about this?
    name = CharField(max_length=255)
    parent_asset_type = ForeignKey(
        'self',
        on_delete=SET_NULL,
        related_name='child_asset_types',
        null=True, blank=True,
    )

    def __str__(self) -> str:
        return f'AssetType {self.pk}: {self.name}'
