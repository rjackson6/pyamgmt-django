from django.db.models import CharField

from django_base.models import BaseAuditable


class NonCatalogItem(BaseAuditable):
    """A non-tangible or generic item, such as a tax levied."""
    name = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return f'{self.name}'
