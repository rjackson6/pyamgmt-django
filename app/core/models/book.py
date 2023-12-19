from django.db.models import (
    CharField, ForeignKey, PositiveSmallIntegerField,
    UniqueConstraint,
    CASCADE, PROTECT, SET_NULL,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names, ordinal


class Book(BaseAuditable):
    """Every CRUD app needs a book model."""
    title = CharField(max_length=255)
    series = ForeignKey(
        'BookSeries', on_delete=SET_NULL, null=True, blank=True,
        **default_related_names(__qualname__)
    )
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

    @cached_property
    def admin_description(self):
        return f'{self.book.title}, {ordinal(self.edition)} Edition'


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


class BookSeries(BaseAuditable):
    name = CharField(max_length=63, unique=True)
    parent_series = ForeignKey(
        'self', on_delete=SET_NULL,
        null=True, blank=True,
        related_name='sub_series',
    )

    class Meta:
        verbose_name_plural = 'book series'

    def __str__(self) -> str:
        return self.name


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

    @cached_property
    def admin_description(self) -> str:
        return (
            f'{self.book.title} (book) <-> {self.motion_picture.title}'
            f' ({self.motion_picture.year_produced} film)'
        )
