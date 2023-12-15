from django.db.models import (
    CharField, ForeignKey, PositiveSmallIntegerField,
    UniqueConstraint,
    CASCADE, PROTECT,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names


class Book(BaseAuditable):
    """Every CRUD app needs a book model."""
    title = CharField(max_length=255)
    # publisher
    # authors

    def __str__(self) -> str:
        return f'{self.title}'


class BookEdition(BaseAuditable):
    """Version/printing of a book.

    As books may have revisions or updates, this is how they are tracked in the
    database under the same body of work.
    """
    book = ForeignKey(
        Book, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    edition = PositiveSmallIntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('book', 'edition'),
                name='unique_book_edition'
            )
        ]


class BookPublication(BaseAuditable):
    """Not sure about this one.

    - the distributed work, in print, ebook, audio
    - audiobooks present a complication. Similar to music, they are a recorded
    performance with one or more narrators
    - This is where hardcover / paperback would live, I think
        - The ISBN is usually different between the two
    """
    book_edition = ForeignKey(
        BookEdition, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    format = None  # TODO 2023-12-12
    publisher = None  # TODO 2023-12-12


# region BookM2M
class BookXMotionPicture(BaseAuditable):
    """Loose relationship between a book and an adapted film.

    The edition of the book doesn't really matter.
    """
    book = ForeignKey(
        Book, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    motion_picture = ForeignKey(
        'MotionPicture', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('book', 'motion_picture'),
                name='unique_book_x_motion_picture'
            )
        ]
