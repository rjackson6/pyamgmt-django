from django.core.exceptions import ValidationError
from django.db.models import (
    BooleanField, CharField, DurationField, ForeignKey, ManyToManyField,
    TextField, UniqueConstraint,
    TextChoices,
    CASCADE, PROTECT,
    Manager,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_positive_timedelta

from . import _managers

# TODO 2023-12-20: Roles can apply to a few different models.
#  Songs are arranged, composed, and engineered
#  Performances are...performed.
#  Recordings are engineered and mastered. This is usually credited on the Album
#  unless otherwise noted.

# TODO 2023-12-20: Thinking of adding the arrangement layer back in
#  Songs are written and composed. They're this 'entity' of words, melodies, and
#  intentions of how it might be performed
#  Songs are optionally arranged - same song, different versions. This presents
#  the many-to-many problem again.
#  The arrangement is performed (somebody is actually playing instruments)
#  The recordings capture the performances


class Song(BaseAuditable):
    """A particular rendition of a song.

    This is a bit abstract, in that it does not fully represent the recordings
    or derivative works.
    """
    title = CharField(max_length=255)
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSong',
        related_name='+'
    )
    lyrics = TextField(blank=True, default='')

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


class SongArrangement(BaseAuditable):
    """Original, mix, cover, or other variation on one or more songs."""
    title = CharField(max_length=255)
    description = CharField(max_length=255, blank=True)
    is_original = BooleanField(default=True)
    songs = ManyToManyField(
        Song, through='SongXSongArrangement',
        related_name='arrangements',
    )

    objects = Manager()
    originals = _managers.SongArrangementOriginalsManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('title', 'description'),
                name='unique_song_arrangement',
            )
        ]

    def __str__(self) -> str:
        text = f'{self.title}'
        if self.description:
            text += f' ({self.description})'
        if self.is_original:
            text += f' [Original]'
        return text


class SongPerformance(BaseAuditable):
    """A performance of a given song arrangement.

    The performance should only be of one arrangement. Performances can differ
    for the same arrangement, though there's often one canonical "album version"
    arrangement for a song. A live performance could also be of the album
    version arrangement, but is distinct from a studio performance that may have
    taken place over several sessions.

    Demo performances are their own category, as they tend to vary between live
    one-takes or studio sessions with some engineering.
    """
    class PerformanceType(TextChoices):
        DEMO = 'DEMO', 'Demo Recording'
        LIVE = 'LIVE', 'Live Performance'
        STUDIO = 'STUDIO', 'Studio Recording'

    description = CharField(max_length=63, blank=True)
    lyrics = TextField(blank=True, default='')
    song_arrangement = ForeignKey(
        SongArrangement, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    performance_type = CharField(
        max_length=6,
        choices=PerformanceType.choices,
        default=PerformanceType.STUDIO,
    )
    # Relationships
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSongPerformance',
        related_name='+',
    )
    personnel = ManyToManyField(
        'Person', through='PersonXSongPerformance',
        related_name='+',
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('description', 'song_arrangement'),
                name='unique_song_performance'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        text = f'{self.song_arrangement.title}'
        if self.song_arrangement.description:
            text += f' ({self.song_arrangement.description})'
        if self.description:
            text += f' - {self.description}'
        return text


class SongRecording(BaseAuditable):
    """Capture of a performance to any persistent media."""
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
        text = f'{self.song_performance.song_arrangement.title}'
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


class SongXSongArrangement(BaseAuditable):
    song = ForeignKey(
        Song, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_arrangement = ForeignKey(
        SongArrangement, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('song', 'song_arrangement'),
                name='unique_song_x_song_arrangement',
            )
        ]
