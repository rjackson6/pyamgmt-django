from django_base.models import BaseAuditable, LowerCharField


class MusicTag(BaseAuditable):
    """Genre(s), Soundtrack, Live Album, etc.

    Bands can tend toward certain genres, but they can sometimes release albums
    that are of a different style. Tagging makes a better representation of this
    than a single-value enumeration.
    """

    name = LowerCharField(max_length=31, unique=True)

    def __str__(self) -> str:
        return self.name
