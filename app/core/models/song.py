from django.db.models import (
    BooleanField, CharField, CheckConstraint, DurationField, ForeignKey,
    ManyToManyField, TextField, UniqueConstraint, Q,
    TextChoices,
    CASCADE, PROTECT, SET_NULL,
    Manager,
)

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


class SongDisambiguator(BaseAuditable):
    key = CharField(max_length=255, unique=True)

    def __str__(self) -> str:
        return self.key


class Song(BaseAuditable):
    """A particular rendition of a song.

    This is a bit abstract, in that it does not fully represent the recordings
    or derivative works.
    """
    title = CharField(max_length=255)
    disambiguator = ForeignKey(
        SongDisambiguator, on_delete=SET_NULL,
        null=True, blank=True,
        **default_related_names(__qualname__)
    )
    lyrics = TextField(blank=True, default='')
    arrangements = ManyToManyField(
        'SongArrangement', through='SongXSongArrangement',
        related_name='+', blank=True,
    )
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSong',
        related_name='+', blank=True,
    )
    personnel = ManyToManyField(
        'Person', through='PersonXSong',
        related_name='+', blank=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('title', 'disambiguator'),
                name='unique_song',
                nulls_distinct=False,
            )
        ]

    def __str__(self) -> str:
        return f'{self.title}'


class SongArrangement(BaseAuditable):
    """Original, mix, cover, or other variation on one or more songs."""

    title = CharField(max_length=255)
    disambiguator = ForeignKey(
        SongDisambiguator, on_delete=SET_NULL,
        null=True, blank=True,
        **default_related_names(__qualname__)
    )
    description = CharField(max_length=255, blank=True)
    is_original = BooleanField(default=True)
    music_artists = ManyToManyField(
        'MusicArtist', through='MusicArtistXSongArrangement',
        related_name='+', blank=True,
    )
    personnel = ManyToManyField(
        'Person', through='PersonXSongArrangement',
        related_name='+', blank=True,
    )
    songs = ManyToManyField(
        Song, through='SongXSongArrangement',
        related_name='+', blank=True,
    )

    objects = Manager()
    originals = _managers.SongArrangementOriginalsManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('title', 'disambiguator', 'description'),
                name='unique_song_arrangement',
                nulls_distinct=True,
            ),
            CheckConstraint(
                check=Q(is_original=False) | Q(description=''),
                name='check_song_arrangement_original'
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
        related_name='+', blank=True,
    )
    personnel = ManyToManyField(
        'Person', through='PersonXSongPerformance',
        related_name='+', blank=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('description', 'song_arrangement'),
                name='unique_song_performance'
            )
        ]

    def get_title(self) -> str:
        return f'{self.song_arrangement.title}'


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
        related_name='+', blank=True,
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['duration', 'song_performance'],
                name='unique_song_recording'
            )
        ]

    def get_title(self) -> str:
        return f'{self.song_performance.song_arrangement.title}'


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
