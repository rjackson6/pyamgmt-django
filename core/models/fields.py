from django.db.models.fields import DecimalField


class CurrencyField(DecimalField):
    """Subclass to keep currency Decimal specs consistent."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, max_digits=19, decimal_places=5, **kwargs)
