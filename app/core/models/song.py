from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, DurationField, ForeignKey, ManyToManyField, TextField,
    UniqueConstraint,
    TextChoices,
    CASCADE,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_positive_timedelta


class Song(BaseAuditable):
    """A particular rendition of a song.

    This is a bit abstract, in that it does not fully represent the recordings
    or derivative works.
    """
    lyrics = TextField(blank=True, default='')
    title = CharField(max_length=255)
    # Relationships
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSong',
        related_name='+'
    )

    def __str__(self) -> str:
        return f'{self.title}'


class SongRecording(BaseAuditable):
    """"""
    class RecordingType(TextChoices):
        LIVE = 'LIVE', 'Live Performance'
        STUDIO = 'STUDIO', 'Studio Recording'
    duration = DurationField(
        null=True, blank=True, validators=[validate_positive_timedelta])
    lyrics = TextField(blank=True, default='')
    song = ForeignKey(
        Song, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    recording_type = CharField(
        max_length=6,
        choices=RecordingType.choices,
        default=RecordingType.STUDIO
    )
    # Relationships
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSongRecording',
        related_name='+'
    )

    # def __str__(self) -> str:
    #     return f'Recording of {self.song.title}'

    @cached_property
    def display_name(self) -> str:
        return f'{self.song.title}'


class SongXSong(BaseAuditable):
    """Many to many for Songs.

    Includes covers, arrangements, or other derivative works.
    """
    # relationship: enum or foreign key lookup
    # tagging may play a part in this too (acoustic, instrumental)
    class SongRelationship(TextChoices):
        ARRANGEMENT = 'ARRANGEMENT'
        # COMPILATION = 'COMPILATION'
        COVER = 'COVER'
        # EDIT = 'EDIT'
        INSTRUMENTAL = 'INSTRUMENTAL'
        OVERTURE = 'OVERTURE'
        MASHUP = 'MASHUP', 'Mash-up'
        # REMASTER = 'REMASTER'
        REMIX = 'REMIX'

    song_archetype = ForeignKey(
        Song, on_delete=CASCADE,
        related_name='+'
    )
    song_archetype_id: int
    song_derivative = ForeignKey(
        Song, on_delete=CASCADE,
        related_name='+'
    )
    song_derivative_id: int
    song_relationship = CharField(
        max_length=15, choices=SongRelationship.choices
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('song_archetype', 'song_derivative'),
                name='unique_song_x_song'
            )
        ]

    def clean(self) -> None:
        if self.song_archetype == self.song_derivative:
            raise ValidationError("Original and derivative must be different.")
