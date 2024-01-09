from django.db.models import (
    BooleanField,
    CharField,
    DecimalField,
    TextField,
)


from django_base.models import BaseAuditable


class HouseAreaDecimalField(DecimalField):
    def __init__(self, *args, max_digits=7, decimal_places=2, **kwargs) -> None:
        super().__init__(
            *args,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **kwargs
        )


class RealEstateParcel(BaseAuditable):
    """A unique parcel of land.

    There are a bunch of ways to identify a parcel of real estate. Addresses
    work for houses, but not for land. Houses and land will both have some kind
    of parcel number or tax id, though. The absolute longitude and latitide of
    the plot is the physically unique way of identifying a parcel, but that's
    not realistically feasible.

    Address could be optionally listed. The only place that doesn't work is for
    housing complexes or commercial spaces. I guess they share the same physical
    address in a way, though. Perhaps that's a canonical address. I'm not sure
    of a rule where only one parcel can be given an address. I assume they would
    have to have a canonical address. Or can you only build multiple houses by
    legally subdividing the lots. Subdividing nullifies the old asset and makes
    two new ones, which could be optionally related.

    I guess it's easier to start with a unique address until it becomes an
    issue. The parcel number + tax id plus maybe state-specific, or even
    county-specific attributes would compose the unique index. That would be
    something like "issuing_authority" & ("parcel_number" | "tax_id"). That's a
    bit of a hack around creating lookup tables for city, county, state, etc.
    "record_holder" may be a good name, as the deeds are "recorded" at closing
    through a law office or title company. They do research on the title to make
    sure it's clean - whatever that means.
    """

    address = TextField(blank=True)
    has_residence = BooleanField(null=True)
    lot_number = CharField(blank=True)
    lot_size = DecimalField(
        max_digits=8, decimal_places=3,
        null=True, blank=True,
        help_text="Lot size, in acres"
    )
    finished_area = HouseAreaDecimalField(
        max_digits=7, decimal_places=2,
        null=True, blank=True,
        help_text="Finished housing area, in square feet"
    )
    unfinished_area = HouseAreaDecimalField(
        max_digits=7, decimal_places=2,
        null=True, blank=True,
        help_text="Area of unfinished spaces, in square feet"
    )

    def __str__(self) -> str:
        if self.address:
            return self.address
        else:
            return f"RealEstate {self.pk} (No description)"
