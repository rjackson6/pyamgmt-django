from django.db.models import (
    CharField, DateField, ForeignKey, PositiveSmallIntegerField, URLField,
    CASCADE,
    Manager,
    UniqueConstraint, ManyToManyField,
)

from django.utils import timezone
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import (
    validate_date_not_future, validate_year_not_future
)

from . import _managers


class MusicArtist(BaseAuditable):
    """An individual musician or a group of musicians."""
    name = CharField(max_length=255, unique=True)
    website = URLField(
        null=True, blank=True,
        help_text="Website or homepage for this music artist."
    )
    # Relationships
    albums = ManyToManyField(
        'MusicAlbum', through='MusicAlbumXMusicArtist', related_name='+',
        blank=True,
    )
    # songs = ManyXManyField('Song', through='MusicArtistXSong', related_name='+', blank=True)

    def __str__(self) -> str:
        return f'{self.name}'

    @cached_property
    def total_albums(self) -> int:
        return self.music_albums.count()

    # @cached_property
    # def total_songs(self):
    #     return self.songs.count()


class MusicArtistActivity(BaseAuditable):
    """Dates for MusicArtist activity, as bands can go on hiatus."""
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_id: int
    year_active = PositiveSmallIntegerField(
        validators=[validate_year_not_future]
    )
    year_inactive = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'year_active'),
                name='unique_music_artist_activity')
        ]

    @cached_property
    def admin_description(self) -> str:
        text = f'{self.music_artist.name} : {self.year_active}'
        if self.year_inactive:
            text += f' - {self.year_inactive}'
        else:
            text += f' - Present'
        return text


class MusicArtistXPerson(BaseAuditable):
    """Relates a MusicArtist to a Person.

    A MusicArtist may be one or many persons, e.g., solo artists, composers,
    bands, etc.
    These are also optionally bound by time. Band members can leave and re-join
    a group.
    Only "official" members of a band are considered.
    Solo artist activity considers their timeline as a music artist by
    profession.
    """
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_id: int
    person = ForeignKey(
        'Person', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person_id: int

    objects = Manager()
    with_related = _managers.MusicArtistXPersonManager()

    music_artist_x_person_activity_set: Manager

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

    @cached_property
    def admin_description(self) -> str:
        return (
            f'{self.music_artist.name} : {self.person.full_name}'
        )

    @property
    def is_active(self) -> bool | None:
        activity = (
            self.music_artist_x_person_activity_set
            .order_by('date_active')
            .first()
        )
        if activity is None:
            return None
        if activity.date_inactive is None:
            return True
        if activity.date_inactive >= timezone.now():
            return False


class MusicArtistXPersonActivity(BaseAuditable):
    """Holds records of when a person was part of a group or act."""
    music_artist_x_person = ForeignKey(
        MusicArtistXPerson, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_x_person_id: int
    date_active = DateField(validators=[validate_date_not_future])
    date_inactive = DateField(
        null=True, blank=True, validators=[validate_date_not_future]
    )

    @cached_property
    def admin_description(self) -> str:
        return (
            f'{self.music_artist_x_person.music_artist.name}'
            f' : {self.music_artist_x_person.person.full_name}'
            f' : {self.date_active}'
        )


class MusicArtistXSong(BaseAuditable):
    """Relates a MusicArtist to a Song"""
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_id: int
    song = ForeignKey(
        'Song', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_id: int
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


class MusicArtistXSongRecording(BaseAuditable):
    music_artist = ForeignKey(
        MusicArtist, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_id: int
    song_recording = ForeignKey(
        'SongRecording', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_recording_id: int

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'song_recording'),
                name='unique_music_artist_x_song_recording'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXSongRecording {self.pk}:'
            f' {self.music_artist_id}-{self.song_recording_id}'
        )

    @cached_property
    def admin_description(self) -> str:
        return (
            f'{self.song_recording.song.title}'
            f' : {self.music_artist.name}'
        )
