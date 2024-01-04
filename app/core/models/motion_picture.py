from django.db.models import (
    CharField, ForeignKey, PositiveSmallIntegerField,
    UniqueConstraint,
    CASCADE, PROTECT, SET_NULL, ManyToManyField, TextField,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_year_not_future


class MotionPicture(BaseAuditable):
    title = CharField(max_length=255)
    disambiguator = CharField(max_length=255, blank=True)
    series = ForeignKey(
        'MotionPictureSeries', on_delete=SET_NULL,
        null=True, blank=True,
        **default_related_names(__qualname__)
    )
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[validate_year_not_future]
    )
    notes = TextField(blank=True)

    music_albums = ManyToManyField(
        'MusicAlbum', through='MotionPictureXMusicAlbum',
        related_name='+', blank=True,
    )
    songs = ManyToManyField(
        'Song', through='MotionPictureXSong',
        related_name='+', blank=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('title', 'disambiguator'),
                name='unique_motion_picture'
            )
        ]

    def __str__(self) -> str:
        text = f'{self.title}'
        if self.disambiguator:
            text += f' [{self.disambiguator}]'
        elif self.year_produced:
            text += f' ({self.year_produced})'
        return text


class MotionPictureRecording(BaseAuditable):
    """Released edition of a motion picture.

    Takes into account media (digital, DVD, maybe even distributor).
    """
    # media_format = ForeignKey()
    motion_picture = ForeignKey(
        MotionPicture, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )


class MotionPictureSeries(BaseAuditable):
    name = CharField(max_length=63, unique=True)
    parent_series = ForeignKey(
        'self', on_delete=SET_NULL,
        null=True, blank=True,
        related_name='sub_series',
    )

    class Meta:
        verbose_name_plural = 'motion picture series'

    def __str__(self) -> str:
        return self.name


class MotionPictureXMusicAlbum(BaseAuditable):
    """Relates a motion picture to its soundtrack and/or score."""
    motion_picture_id: int
    music_album_id: int

    motion_picture = ForeignKey(
        MotionPicture, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album = ForeignKey(
        'MusicAlbum', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('motion_picture', 'music_album'),
                name='unique_motion_picture_x_music_album'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        return f'{self.motion_picture.title} : {self.music_album.title}'


class MotionPictureXPerson(BaseAuditable):
    motion_picture = ForeignKey(
        MotionPicture, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person = ForeignKey(
        'Person', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    notes = TextField(blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('motion_picture', 'person'),
                name='unique_motion_picture_x_person'
            )
        ]


class MotionPictureXSong(BaseAuditable):
    """Not sure if needed, but would account for one-off non-score
    non-soundtrack songs.

    There are some conventions here. "Original Soundtrack" and "Music from the
    Motion Picture" sometimes imply different meanings. I don't know if
    soundtracks or film scores are always published, either.
    """
    motion_picture_id: int
    song_id: int

    motion_picture = ForeignKey(
        MotionPicture, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song = ForeignKey(
        'Song', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('motion_picture', 'song'),
                name='unique_motion_picture_x_song'
            )
        ]
