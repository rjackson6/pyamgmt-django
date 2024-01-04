from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    """Subclass to keep currency Decimal specs consistent."""

    def __init__(self, *args, max_digits=19, decimal_places=5, **kwargs):
        super().__init__(
            *args,
            max_digits=max_digits,
            decimal_places=decimal_places,
            **kwargs
        )
