import enum
import hashlib

from django.db.models import (
    BooleanField, CharField, ForeignKey, ImageField, Manager, ManyToManyField,
    PositiveSmallIntegerField,
    CASCADE, PROTECT,
    UniqueConstraint, TextField, QuerySet,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_year_not_future

from ._utils import get_default_media_format_audio, resize_image


class MusicAlbum(BaseAuditable):
    """An individual Music album."""
    is_compilation = BooleanField(
        default=False,
        help_text=(
            "Album is a compilation of other songs, such as a Greatest Hits"
            " album."
        )
    )
    title = CharField(max_length=255)
    disambiguator = CharField(max_length=255, blank=True)
    notes = TextField(blank=True)
    music_artists = ManyToManyField(
        'MusicArtist',
        through='MusicAlbumXMusicArtist',
        blank=True
    )
    personnel = ManyToManyField(
        'Person',
        through='MusicAlbumXPerson',
        related_name='+',
        blank=True
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('title', 'disambiguator'),
                name='music_album_unique'
            )
        ]

    def __str__(self) -> str:
        text = f'{self.title}'
        if self.disambiguator:
            text += f' [{self.disambiguator}]'
        return text

    # @cached_property
    # def duration(self):
    #     return self.song_recordings.aggregate(Sum('duration'))['duration__sum']
    #
    # @cached_property
    # def total_songs(self):
    #     return self.song_recordings.count()


class MusicAlbumArtwork(BaseAuditable):
    """Holds zero or many images relating to a MusicAlbum."""

    class ImageSize(enum.Enum):
        THUMBNAIL = (100, 100)
        SMALL = (250, 250)
        MEDIUM = (640, 640)
        LARGE = (1280, 1280)

    music_album_id: int

    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    short_description = CharField(max_length=255, blank=True)
    image_full = ImageField()
    # Programmatic fields
    image_full_sha256 = CharField(
        max_length=64, unique=True, null=True, editable=False
    )
    image_large = ImageField(null=True, blank=True, editable=False)
    image_medium = ImageField(null=True, blank=True, editable=False)
    image_small = ImageField(null=True, blank=True, editable=False)
    image_thumbnail = ImageField(null=True, blank=True, editable=False)

    class Meta:
        verbose_name_plural = 'music album artwork'

    def __str__(self) -> str:
        return f'MusicAlbumArtwork {self.pk}: {self.music_album_id}'

    def save(self, *args, **kwargs) -> None:
        image_file = self.image_full.open()
        self.image_full_sha256 = (
            hashlib.file_digest(image_file, 'sha256')
            .hexdigest()
        )
        images = resize_image(self.image_full, self.ImageSize)
        for field_name, file in images.items():
            field = getattr(self, field_name)
            field.save(file[0], file[1], save=False)
        super().save(*args, **kwargs)


class MusicAlbumEdition(BaseAuditable):
    """Further classification of different releases of an album.

    TODO 2023-12-12: Format here? Probably, or model it after books, e.g.,
     "Production"
     Although formats are sometimes linked to editions. "DigiPak", "Bonus track"
     Remastered albums contain remastered tracks, maybe bonuses
    """
    music_album_edition_x_song_recording_set: Manager

    music_album = ForeignKey(
        MusicAlbum, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    name = CharField(max_length=63)
    # TODO 2023-12-12: likely a property
    total_discs = PositiveSmallIntegerField(default=1)
    year_copyright = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )

    def __str__(self) -> str:
        return self.name

    def get_title(self) -> str:
        return f'{self.music_album.title} [{self.name}]'

    @cached_property
    def tracks(self) -> QuerySet:
        return (
            self.music_album_edition_x_song_recording_set
            .select_related(
                'song_recording__song_performance__song_arrangement')
            .order_by('track_number')
        )


class MusicAlbumEditionXSongRecording(BaseAuditable):
    music_album_edition_id: int
    song_recording_id: int

    music_album_edition = ForeignKey(
        MusicAlbumEdition, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_recording = ForeignKey(
        'SongRecording', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    disc_number = PositiveSmallIntegerField(null=True, blank=True)
    track_number = PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album_edition', 'song_recording'),
                name='unique_music_album_edition_x_song_recording'
            ),
            UniqueConstraint(
                fields=('music_album_edition', 'disc_number', 'track_number'),
                name='unique_music_album_edition_x_song_recording_disc_track'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicAlbumEditionXSongRecording {self.pk}:'
            f' {self.music_album_edition_id}-{self.song_recording_id}')


class MusicAlbumProduction(BaseAuditable):
    """This resolves media formats for album releases.

    Other terms that are of a similar concept would be "pressing" for vinyl.
    That is to say that the same "edition" of an album, like a remaster, could
    be released in multiple formats, like "digital", "CD", or "Vinyl".
    """
    media_format = ForeignKey(
        'MediaFormat', on_delete=PROTECT,
        default=get_default_media_format_audio,
        **default_related_names(__qualname__)
    )
    music_album_edition = ForeignKey(
        MusicAlbumEdition, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    total_discs = PositiveSmallIntegerField(default=1)
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )


class MusicAlbumXMusicArtist(BaseAuditable):
    """Relates a MusicAlbum to a MusicArtist; Album Artist.

    This is assuming that while most albums are released under one artist, there
    are cases where there are actually two artists that collaborate on a single
    album, e.g., "Hans Zimmer & James Newton Howard" for the Christopher Nolan
    Batman movies. Both artists are credited on the soundtrack for composition.
    This does not replace individual song artists, as there are "featured"
    tracks, or compilation albums.
    """
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_id: int
    music_artist = ForeignKey(
        'MusicArtist', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_id: int

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'music_artist'),
                name='unique_music_album_x_music_artist')
        ]

    def __str__(self) -> str:
        return (
            f'MusicAlbumXMusicArtist {self.pk}:'
            f' {self.music_album_id}-{self.music_artist_id}')


class MusicAlbumXMusicTag(BaseAuditable):
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_tag = ForeignKey(
        'MusicTag', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'music_tag'),
                name='unique_music_album_x_music_tag'
            )
        ]

    @cached_property
    def admin_description(self) -> str:
        return f'{self.music_album.title} : {self.music_tag.name}'


class MusicAlbumXPerson(BaseAuditable):
    """Personnel credits for a Music Album."""
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    person = ForeignKey(
        'Person', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    comments = TextField(blank=True, default='')

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'person'),
                name='unique_music_album_x_person'
            )
        ]

    def admin_description(self) -> str:
        return f'{self.music_album.title} : {self.person.full_name}'


class MusicAlbumXPersonXMusicRole(BaseAuditable):
    music_album_x_person = ForeignKey(
        MusicAlbumXPerson, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_role = ForeignKey(
        'MusicRole', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_role', 'music_album_x_person'),
                name='unique_music_album_x_person_role'
            )
        ]


class MusicAlbumXVideoGame(BaseAuditable):
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    video_game = ForeignKey(
        'VideoGame', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'video_game'),
                name='unique_music_album_x_video_game')
        ]

    def admin_description(self) -> str:
        return f'{self.video_game.title} : {self.music_album.title}'
