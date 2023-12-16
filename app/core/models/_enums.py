from django.db.models import TextChoices


class Region(TextChoices):
    """Region codes for media and game platforms."""
    AU = 'AU', 'Australia'
    EU = 'EU', 'Europe'
    JP = 'JP', 'Japan'
    NA = 'NA', 'North America'
