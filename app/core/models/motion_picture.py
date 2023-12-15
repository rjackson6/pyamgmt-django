from django.db.models import (
    CharField, ForeignKey, PositiveSmallIntegerField,
    CASCADE, PROTECT,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_year_not_future


class MotionPicture(BaseAuditable):
    title = CharField(max_length=255)
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[validate_year_not_future]
    )

    def __str__(self) -> str:
        return f'{self.title}'


class MotionPictureRecording(BaseAuditable):
    """Released edition of a motion picture.

    Takes into account media (digital, DVD, maybe even distributor).
    """
    motion_picture = ForeignKey(
        MotionPicture, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )


# region MotionPictureM2M
class MotionPictureXMusicAlbum(BaseAuditable):
    """Relates a motion picture to its soundtrack and/or score."""
    motion_picture = ForeignKey(
        MotionPicture, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    motion_picture_id: int
    music_album = ForeignKey(
        'MusicAlbum', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_id: int


class MotionPictureXSong(BaseAuditable):
    """Not sure if needed, but would account for one-off non-score
    non-soundtrack songs.

    There are some conventions here. "Original Soundtrack" and "Music from the
    Motion Picture" sometimes imply different meanings. I don't know if
    soundtracks or film scores are always published, either.
    """
    motion_picture = ForeignKey(
        MotionPicture, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    motion_picture_id: int
    song = ForeignKey(
        'Song', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_id: int
