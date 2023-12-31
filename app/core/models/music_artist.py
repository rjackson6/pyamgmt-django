from django.db.models import (
    CharField, ForeignKey, PositiveSmallIntegerField, TextField, URLField,
    CASCADE,
    TextChoices,
    Manager,
    UniqueConstraint, ManyToManyField,
)

from django.utils import timezone
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import (
    validate_year_not_future
)

from . import managers


class MusicArtist(BaseAuditable):
    """An individual musician or a group of musicians."""
    music_artist_activity_set: Manager

    name = CharField(max_length=255)
    disambiguator = CharField(max_length=255, blank=True)
    website = URLField(
        null=True, blank=True,
        help_text="Website or homepage for this music artist."
    )
    comments = TextField(blank=True, default='')
    # Relationships
    music_albums = ManyToManyField(
        'MusicAlbum', through='MusicAlbumXMusicArtist',
        related_name='+', blank=True,
    )
    personnel = ManyToManyField(
        'Person', through='MusicArtistXPerson',
        related_name='+', blank=True,
    )
    songs = ManyToManyField(
        'Song', through='MusicArtistXSong',
        related_name='+', blank=True,
    )
    arrangements = ManyToManyField(
        'SongArrangement', through='MusicArtistXSongArrangement',
        related_name='+', blank=True,
    )
    performances = ManyToManyField(
        'SongPerformance', through='MusicArtistXSongPerformance',
        related_name='+', blank=True,
    )
    tags = ManyToManyField(
        'MusicTag', through='MusicArtistXMusicTag',
        related_name='+', blank=True,
    )

    objects = Manager()
    with_related = managers.music_artist.MusicArtistManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'disambiguator'),
                name='unique_music_artist'
            )
        ]

    def __str__(self) -> str:
        text = f'{self.name}'
        if self.disambiguator:
            text += f' [{self.disambiguator}]'
        return text

    @cached_property
    def is_active(self) -> bool:
        activity = self.music_artist_activity_set.all()
        if not activity:
            return True
        if activity[0].year_inactive:
            return False
        else:
            return True

    @cached_property
    def total_albums(self) -> int:
        return self.music_albums.count()

    # @cached_property
    # def total_songs(self):
    #     return self.songs.count()


class MusicArtistActivity(BaseAuditable):
    """Dates for MusicArtist activity, as bands can go on hiatus."""
    music_artist_id: int

    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    year_active = PositiveSmallIntegerField(
        validators=[validate_year_not_future]
    )
    year_inactive = PositiveSmallIntegerField(
        null=True, blank=True,
        validators=[validate_year_not_future]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'year_active'),
                name='unique_music_artist_activity')
        ]

    def __str__(self) -> str:
        return f'{self.year_active} - {self.year_inactive or "Present"}'

    @property
    def is_active(self) -> bool:
        return self.year_inactive is not None


class MusicArtistXMusicTag(BaseAuditable):
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_tag = ForeignKey(
        'MusicTag', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'music_tag'),
                name='unique_music_artist_x_music_tag'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        return f'{self.music_artist.name} : {self.music_tag.name}'


class MusicArtistXPerson(BaseAuditable):
    """Relates a MusicArtist to a Person.

    A MusicArtist may be one or many persons, e.g., solo artists, composers,
    bands, etc.
    These are also optionally bound by time. Band members can leave and re-join
    a group.
    Solo artist activity considers their timeline as a music artist by
    profession.
    """
    music_artist_id: int
    person_id: int
    music_artist_x_person_activity_set: Manager

    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person = ForeignKey(
        'Person', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    objects = Manager()
    with_related = managers.music_artist.MusicArtistXPersonManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'person'),
                name='unique_music_artist_x_person'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXPerson {self.pk}:'
            f' {self.music_artist_id}-{self.person_id}'
        )

    @property
    def is_active(self) -> bool | None:
        if not self.person.is_living:
            return False
        if not self.music_artist.is_active:
            return False
        activity = self.music_artist_x_person_activity_set.first()
        if activity is None:
            return None
        if activity.year_inactive is None:
            return True
        if activity.year_inactive <= timezone.now().year:
            return False


class MusicArtistXPersonActivity(BaseAuditable):
    """Holds records of when a person was part of a group or act."""

    class ActivityType(TextChoices):
        OFFICIAL = 'OFFICIAL', 'Official Member'
        SESSION = 'SESSION', 'Session Musician'
        TOURING = 'TOURING', 'Touring Member'

    music_artist_x_person_id: int

    music_artist_x_person = ForeignKey(
        MusicArtistXPerson, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    # role : vocalist, drummer, guitarist, lead guitarist, lead vocalist...
    # a person could be multiple roles, guitarist + vocalist
    # contribution: session vocals, session drums, drummer
    # date_active = DateField(validators=[validate_date_not_future])
    # date_inactive = DateField(
    #     null=True, blank=True, validators=[validate_date_not_future]
    # )
    activity_type = CharField(
        max_length=8, choices=ActivityType.choices, blank=True
    )
    year_active = PositiveSmallIntegerField(null=True, blank=True)
    year_inactive = PositiveSmallIntegerField(null=True, blank=True)


class MusicArtistXSong(BaseAuditable):
    """Relates a MusicArtist to a Song"""
    music_artist_id: int
    song_id: int

    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song = ForeignKey(
        'Song', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    # TODO 2023-12-12: role for how an artist contributed to the song
    #  e.g., guitarist, vocalist, engineer

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'song'),
                name='unique_music_artist_x_song')
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXSong {self.pk}:'
            f' {self.music_artist_id}-{self.song_id}'
        )


class MusicArtistXSongArrangement(BaseAuditable):
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_arrangement = ForeignKey(
        'SongArrangement', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'song_arrangement'),
                name='unique_music_artist_x_song_arrangement'
            )
        ]


class MusicArtistXSongPerformance(BaseAuditable):
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_performance = ForeignKey(
        'SongPerformance', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    comments = TextField(blank=True, default='')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'song_performance'),
                name='unique_music_artist_x_song_performance'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXSongPerformance {self.pk}:'
            f' {self.music_artist_id}-{self.song_performance_id}'
        )
