from django.db.models import (
    BooleanField, CharField, ForeignKey, ImageField, ManyToManyField,
    PositiveSmallIntegerField,
    CASCADE, PROTECT,
    UniqueConstraint, TextField,
)
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.utils import default_related_names
from django_base.validators import validate_year_not_future

from ._utils import get_default_media_format_audio


class MusicAlbum(BaseAuditable):
    """An individual Music album production."""
    # TODO 2023-12-12: MusicAlbums can also have different "editions", like
    #  special or remastered.
    #  They would still group together under the same title.
    #  Usually they share tracks.
    # TODO 2023-12-12: Move media format? Or would be treat albums as being
    #  different productions?
    is_compilation = BooleanField(
        default=False,
        help_text=(
            "Album is a compilation of other songs, such as a Greatest Hits"
            " album."
        )
    )
    # TODO 2023-12-12
    # media_format = ForeignKey(MediaFormat, on_delete=SET_DEFAULT, default=get_default_media_format_audio)
    # media_format_id: int
    # TODO 2023-12-12: This is a temporary unique constraint
    title = CharField(max_length=255, unique=True)
    # year_copyright = PositiveSmallIntegerField(
    #     null=True, blank=True, validators=[validate_year_not_future]
    # )
    # year_produced = PositiveSmallIntegerField(
    #     null=True, blank=True, validators=[validate_year_not_future]
    # )
    music_artists = ManyToManyField(
        'MusicArtist',
        through='MusicAlbumXMusicArtist',
        related_name='music_albums',
        blank=True
    )
    # TODO 2023-12-20: Personnel would help separate featured musicians from the
    #  headline artists.
    #  Also keeps individual music projects separate from contributions and
    #  collaborations.
    personnel = ManyToManyField(
        'Person',
        through='MusicAlbumXPerson',
        related_name='music_albums',
        blank=True
    )
    # song_recordings = ManyXManyField(
    #     'SongRecording', through='MusicAlbumXSongRecording',
    #     blank=True)

    def __str__(self) -> str:
        return f'{self.title}'

    # @cached_property
    # def duration(self):
    #     return self.song_recordings.aggregate(Sum('duration'))['duration__sum']
    #
    # @cached_property
    # def total_songs(self):
    #     return self.song_recordings.count()


class MusicAlbumArtwork(BaseAuditable):
    """Holds zero or many images relating to a MusicAlbum."""
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_id: int
    image = ImageField()

    class Meta:
        verbose_name_plural = 'music album artwork'

    def __str__(self) -> str:
        return f'MusicAlbumArtwork {self.pk}: {self.music_album_id}'


class MusicAlbumEdition(BaseAuditable):
    """Further classification of different releases of an album.

    TODO 2023-12-12: Format here? Probably, or model it after books, e.g.,
     "Production"
     Although formats are sometimes linked to editions. "DigiPak", "Bonus track"
     Remastered albums contain remastered tracks, maybe bonuses
    """
    music_album = ForeignKey(
        MusicAlbum, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    name = CharField(max_length=31, blank=True)
    # TODO 2023-12-12: likely a property
    total_discs = PositiveSmallIntegerField(default=1)
    year_copyright = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )

    @cached_property
    def admin_description(self) -> str:
        return f'{self.music_album.title} ({self.name})'


class MusicAlbumEditionXSongRecording(BaseAuditable):
    disc_number = PositiveSmallIntegerField(null=True, blank=True)
    music_album_edition = ForeignKey(
        MusicAlbumEdition, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_edition_id: int
    song_recording = ForeignKey(
        'SongRecording', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_recording_id: int
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


class MusicAlbumRole(BaseAuditable):
    """An individual's role for their contribution to a music album.

    E.g., Vocalist, Guitarist, Engineer, Producer
    """
    name = CharField(max_length=31, unique=True)


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

    @cached_property
    def admin_description(self) -> str:
        return f'{self.music_artist.name} : {self.music_album.title}'


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
    # Can have multiple roles, though
    # music_album_role = ForeignKey(
    #     MusicAlbumRole, on_delete=PROTECT,
    #     **default_related_names(__qualname__)
    # )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'person'),
                name='unique_music_album_x_person'
            )
        ]

    def admin_description(self) -> str:
        return f'{self.music_album.title} : {self.person.full_name}'


class MusicAlbumXPersonRole(BaseAuditable):
    music_album_x_person = ForeignKey(
        MusicAlbumXPerson, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_role = ForeignKey(
        MusicAlbumRole, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album_role', 'music_album_x_person'),
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
        return f'{self.music_album.title} : {self.video_game.title}'
