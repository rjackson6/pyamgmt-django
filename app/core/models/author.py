from django.db.models import (
    CharField, ForeignKey,
    CASCADE, SET_NULL, UniqueConstraint,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Author(BaseAuditable):
    pen_name = CharField(max_length=63)
    person = ForeignKey(
        'Person', on_delete=SET_NULL, null=True, blank=True,
        **default_related_names(__qualname__)
    )

    def __str__(self):
        return self.pen_name


class AuthorXBook(BaseAuditable):
    author = ForeignKey(
        Author, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    book = ForeignKey(
        'Book', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'book'],
                name='unique_author_x_book'
            )
        ]
