from django.core.exceptions import ValidationError
from django.db.models import (
    BooleanField, CharField, DurationField, ForeignKey, ManyToManyField,
    TextField, UniqueConstraint,
    TextChoices,
    CASCADE, PROTECT,
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
    is_original = BooleanField(default=True)

    def __str__(self) -> str:
        return f'{self.title}'

    @cached_property
    def admin_description(self) -> str:
        artists = []
        for n, artist in enumerate(self.music_artists.all()):
            artists.append(artist.name)
            if n > 2:
                artists.append(', ...')
                break
        artists = ', '.join(artists)
        return f'{self.title} ({artists})'


class SongPerformance(BaseAuditable):
    """"""
    class PerformanceType(TextChoices):
        DEMO = 'DEMO', 'Demo Recording'
        LIVE = 'LIVE', 'Live Performance'
        STUDIO = 'STUDIO', 'Studio Recording'

    description = CharField(max_length=63, blank=True)
    lyrics = TextField(blank=True, default='')
    song = ForeignKey(
        Song, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    performance_type = CharField(
        max_length=6,
        choices=PerformanceType.choices,
        default=PerformanceType.STUDIO
    )
    # Relationships
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSongPerformance',
        related_name='+'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('description', 'song'),
                name='unique_song_performance'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        text = f'{self.song.title}'
        if self.description:
            text += f' - {self.description}'
        return text


class SongRecording(BaseAuditable):
    duration = DurationField(
        null=True, blank=True,
        validators=[validate_positive_timedelta],
    )
    song_performance = ForeignKey(
        SongPerformance, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    music_album_editions = ManyToManyField(
        'MusicAlbumEdition',
        through='MusicAlbumEditionXSongRecording',
        related_name='+'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['duration', 'song_performance'],
                name='unique_song_recording'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        text = f'{self.song_performance.song.title}'
        if self.song_performance.description:
            text += f' - {self.song_performance.description}'
        return text


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
