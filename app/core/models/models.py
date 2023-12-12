__all__ = [
    'AssetType',
    'CatalogItemXInvoiceLineItem', 'CatalogItemXOrderLineItem',
    'CatalogItemXPointOfSaleLineItem',
    'Invoice', 'InvoiceLineItem', 'InvoiceLineItemXNonCatalogItem',
    'MediaFormat',
    'MotionPicture',
    'MusicAlbum',
    'MusicAlbumArtwork',
    'MusicAlbumXMusicArtist',
    'MusicAlbumXSongRecording',
    'MusicArtist', 'MusicArtistXPerson', 'MusicArtistXSong',
    'MusicArtistXSongRecording',
    'Order', 'OrderLineItem',
    'PartyType', 'Payee', 'Person',
    'PointOfSale', 'PointOfSaleDocument', 'PointOfSaleLineItem',
    'Seller',
    'Song', 'SongRecording',  # 'SongXSong',
    'Txn', 'TxnLineItem',
    'Unit',
    'Vehicle', 'VehicleMake', 'VehicleMileage', 'VehicleModel', 'VehicleTrim',
    'VehicleYear',
    'get_default_media_format_audio',
]

import datetime
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db.models import (
    # Fields
    BooleanField, CharField, DateField, DecimalField, DurationField, FileField,
    ForeignKey,
    ImageField, IntegerField,
    ManyToManyField,
    OneToOneField,
    PositiveIntegerField, PositiveSmallIntegerField, TextField,
    TimeField, URLField,
    # Indexes
    UniqueConstraint,
    # Model Managers
    Manager,
    # Enum
    TextChoices,
    # on_delete callbacks
    CASCADE, PROTECT, SET_NULL,
    # SQL
    F, Sum,
)
from django.utils import timezone
from django.utils.functional import cached_property

from django_base.models import BaseAuditable
from django_base.models.fields import UpperCharField
from django_base.utils import default_related_names, pascal_case_to_snake_case
from django_base.validators import (
    validate_date_not_future,
    validate_positive_timedelta,
    validate_year_not_future,
)

from core.models import managers, querysets
from core.models.fields import CurrencyField


##########
# MODELS #
##########


def get_default_media_format_audio() -> int:
    return MediaFormat.get_default_audio()


class AssetType(BaseAuditable):
    """Expandable type to support hierarchy

    Not to be confused with AssetSubtype.
    """
    # TODO 2023-12-12: Do I care about this?
    name = CharField(max_length=255)
    parent_asset_type = ForeignKey(
        'self',
        on_delete=SET_NULL,
        related_name='child_asset_types',
        null=True, blank=True,
    )

    def __str__(self) -> str:
        return f'AssetType {self.pk}: {self.name}'


class Book(BaseAuditable):
    """Every CRUD app needs a book model."""
    title = CharField(max_length=255)
    # publisher
    # authors

    def __str__(self) -> str:
        return f'{self.title}'


class BookEdition(BaseAuditable):
    """Version/printing of a book.

    As books may have revisions or updates, this is how they are tracked in the
    database under the same body of work.
    """
    book = ForeignKey(
        Book, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    edition = PositiveSmallIntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('book', 'edition'),
                name='unique_book_edition'
            )
        ]


class BookPublication(BaseAuditable):
    """Not sure about this one.

    - the distributed work, in print, ebook, audio
    - audiobooks present a complication. Similar to music, they are a recorded
    performance with one or more narrators
    - This is where hardcover / paperback would live, I think
        - The ISBN is usually different between the two
    """
    book_edition = ForeignKey(
        BookEdition, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    format = None  # TODO 2023-12-12
    publisher = None  # TODO 2023-12-12


# region BookM2M
class BookXMotionPicture(BaseAuditable):
    """Loose relationship between a book and an adapted film.

    The edition of the book doesn't really matter.
    """
    book = ForeignKey(
        Book, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    motion_picture = ForeignKey(
        'MotionPicture', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('book', 'motion_picture'),
                name='unique_book_to_motion_picture'
            )
        ]
# endregion BookM2M


# region CatalogItemM2M
class CatalogItemXCatalogItem(BaseAuditable):
    """Holds relationships between CatalogItems to account for bundles.

    A "bundle" can contain individual items that may be listed separately. A
    bundle probably shouldn't contain bundles, though there's no real
    enforcement mechanism for that.
    """
    catalog_item_a = ForeignKey('CatalogItem', on_delete=CASCADE, related_name='+')
    catalog_item_b = ForeignKey('CatalogItem', on_delete=CASCADE, related_name='+')
    relationship = None


class CatalogItemXInvoiceLineItem(BaseAuditable):
    """Relates a CatalogItem record to an InvoiceLineItem record."""
    invoice_line_item = OneToOneField(
        'InvoiceLineItem', on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    invoice_line_item_id: int
    catalog_item = ForeignKey(
        'CatalogItem', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    catalog_item_id: int
    unit_price = CurrencyField()
    # seller?
    quantity = IntegerField()

    def __str__(self) -> str:
        return f'CatalogItemXInvoiceLineItem {self.pk}: {self.catalog_item_id}'


class CatalogItemXOrderLineItem(BaseAuditable):
    """Relates a CatalogItem record to an OrderLineItem record."""
    order_line_item = OneToOneField(
        'OrderLineItem', on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    order_line_item_id: int
    catalog_item = ForeignKey(
        'CatalogItem', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    catalog_item_id: int

    def __str__(self) -> str:
        return f'CatalogItemXOrderLineItem {self.pk}: {self.catalog_item_id}'


class CatalogItemXPointOfSaleLineItem(BaseAuditable):
    """Relates a CatalogItem record to a PointOfSaleLineItem record"""
    point_of_sale_line_item = OneToOneField(
        'PointOfSaleLineItem', on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    point_of_sale_line_item_id: int
    catalog_item = ForeignKey(
        'CatalogItem', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    catalog_item_id: int
    quantity = DecimalField(max_digits=19, decimal_places=5, default=1)
    unit_price = CurrencyField()
    unit = ForeignKey(
        'Unit', on_delete=SET_NULL, null=True, blank=True,
        **default_related_names(__qualname__)
    )
    unit_id: int

    def __str__(self) -> str:
        return (
            f'CatalogItemXPointOfSaleLineItem {self.pk}:'
            f' {self.catalog_item_id}'
        )

    @property
    def price(self) -> Decimal:
        return self.quantity * self.unit_price
# endregion CatalogItemM2M


# region Invoice
class Invoice(BaseAuditable):
    """Payment due to a party for a good or service."""
    invoice_date = DateField()
    invoice_number = CharField(max_length=255)
    party = ForeignKey(
        'Party', on_delete=SET_NULL,
        null=True,
        **default_related_names(__qualname__)
    )


class InvoiceLineItem(BaseAuditable):
    """A line item related to an Invoice."""
    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOGUE_ITEM', 'CATALOGUE_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOGUE_ITEM', 'NON_CATALOGUE_ITEM'
    invoice = ForeignKey(
        Invoice, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    invoice_id: int
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'InvoiceLineItem {self.pk}: {self.invoice_id}'
# endregion Invoice


# region InvoiceLineItemM2M
class InvoiceLineItemXNonCatalogItem(BaseAuditable):
    """Relates a NonCatalogItem record to an InvoiceLineItem record."""
    invoice_line_item = OneToOneField(
        InvoiceLineItem, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    invoice_line_item_id: int
    non_catalog_item = ForeignKey(
        'NonCatalogItem', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    non_catalog_item_id: int

    def __str__(self) -> str:
        return (
            f'InvoiceLineItemXNonCatalogItem {self.invoice_line_item_id}:'
            f' {self.non_catalog_item_id}'
        )
# endregion InvoiceLineItemM2M


class Manufacturer(BaseAuditable):
    """
    Placeholder while I figure out how crazy to get with business entities.
    """
    name = CharField(max_length=255, unique=True)


class MediaFormat(BaseAuditable):
    name = CharField(max_length=255, unique=True)

    @classmethod
    def get_default_audio(cls) -> int:
        obj, _ = cls.objects.get_or_create(name='Audio')
        return obj.pk


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
# endregion MotionPictureM2M


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
        help_text="Album is a compilation of other songs, such as a Greatest Hits album."
    )
    # TODO 2023-12-12
    # media_format = ForeignKey(MediaFormat, on_delete=SET_DEFAULT, default=get_default_media_format_audio)
    # media_format_id: int
    # TODO 2023-12-12: This is a temporary unique constraint
    title = CharField(max_length=255, unique=True)
    # TODO 2023-12-12: This is really a property
    total_discs = PositiveSmallIntegerField(default=1)
    year_copyright = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )
    # Relationships
    music_artists = ManyToManyField(
        'MusicArtist',
        through='MusicAlbumXMusicArtist',
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
    # TODO 2023-12-12: likely a property
    total_discs = PositiveSmallIntegerField(default=1)
    year_copyright = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )
    year_produced = PositiveSmallIntegerField(
        null=True, blank=True, validators=[validate_year_not_future]
    )


class MusicAlbumProduction(BaseAuditable):
    """This resolves media formats for album releases.

    Other terms that are of a similar concept would be "pressing" for vinyl.
    That is to say that the same "edition" of an album, like a remaster, could
    be released in multiple formats, like "digital", "CD", or "Vinyl".
    """
    media_format = ForeignKey(
        MediaFormat, on_delete=PROTECT,
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


# region MusicAlbumM2M
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
                name='unique_music_album_to_music_artist')
        ]

    def __str__(self) -> str:
        return (
            f'MusicAlbumXMusicArtist {self.pk}:'
            f' {self.music_album_id}-{self.music_artist_id}')


class MusicAlbumXSongRecording(BaseAuditable):
    disc_number = PositiveSmallIntegerField(null=True, blank=True)
    music_album = ForeignKey(
        MusicAlbum, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_album_id: int
    song_recording = ForeignKey(
        'SongRecording', on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    song_recording_id: int
    track_number = PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_album', 'song_recording'),
                name='unique_music_album_to_song_recording'
            ),
            UniqueConstraint(
                fields=('music_album', 'disc_number', 'track_number'),
                name='unique_music_album_to_song_recording_disc_track'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicAlbumXSongRecording {self.pk}:'
            f' {self.music_album_id}-{self.song_recording_id}')
# endregion MusicAlbumM2M


class MusicArtist(BaseAuditable):
    """An individual musician or a group of musicians."""
    name = CharField(max_length=255, unique=True)
    website = URLField(
        null=True, blank=True,
        help_text="Website or homepage for this music artist."
    )
    # Relationships
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


class MusicArtistXPerson(BaseAuditable):
    """Relates a MusicArtist to a Person.

    A MusicArtist may be one or many persons, e.g., solo artists, composers,
    bands, etc.
    These are also optionally bound by time. Band members can leave and re-join
    a group.
    Only "official" members of a band are considered.
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
    with_related = managers.MusicArtistXPersonManager()

    music_artist_x_person_activity_set: Manager

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('music_artist', 'person'),
                name='unique_music_artist_to_person'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXPerson {self.pk}:'
            f' {self.music_artist_id}-{self.person_id}'
        )

    @property
    def is_active(self) -> Optional[bool]:
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
    music_artist_to_person = ForeignKey(
        MusicArtistXPerson, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    music_artist_to_person_id: int
    date_active = DateField(validators=[validate_date_not_future])
    date_inactive = DateField(
        null=True, blank=True, validators=[validate_date_not_future]
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
                name='unique_music_artist_to_song')
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
                name='unique_music_artist_to_song_recording'
            )
        ]

    def __str__(self) -> str:
        return (
            f'MusicArtistXSongRecording {self.pk}:'
            f' {self.music_artist_id}-{self.song_recording_id}'
        )


class Order(BaseAuditable):
    """A purchase record which is usually paid in advance, but not immediately
    fulfilled.
    """
    order_date = DateField()
    order_number = CharField(max_length=255)
    party = ForeignKey(
        'Party', on_delete=SET_NULL,
        null=True,
        **default_related_names(__qualname__)
    )

    def __str__(self) -> str:
        return f'Order {self.pk}: {self.order_number}'


class OrderLineItem(BaseAuditable):
    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOG_ITEM', 'CATALOG_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOG_ITEM', 'NON_CATALOG_ITEM'
    order = ForeignKey(
        Order, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    order_id: int
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'OrderLineItem {self.pk}: {self.order_id}'


class PartyType(BaseAuditable):
    name = CharField(max_length=255)
    parent_party_type = ForeignKey(
        'self',
        on_delete=SET_NULL,
        null=True, blank=True,
        related_name='child_party_types'
    )

    def __str__(self) -> str:
        return f'{self.name}'


class Payee(BaseAuditable):
    """Within scope of transaction, the entity receiving payment."""
    memo = TextField(null=True, blank=True)
    name = CharField(
        max_length=255,
        unique=True,
        help_text="Name as displayed on transaction ledger."
    )
    party = ForeignKey(
        'Party',
        on_delete=PROTECT,
        null=True,
        blank=True,
        **default_related_names(__qualname__)
    )
    party_id: int

    def __str__(self) -> str:
        return f'{self.name}'


class Person(BaseAuditable):
    """A person. Generally self-explanatory as an entity.

    Maybe a personal acquaintance, and/or a notable individual with some level
    of fame.
    """
    first_name = CharField(max_length=255)
    middle_name = CharField(max_length=255, blank=True)
    last_name = CharField(max_length=255)
    date_of_birth = DateField(null=True, blank=True)
    date_of_death = DateField(null=True, blank=True)
    subtype_acquaintance = BooleanField()
    subtype_notable = BooleanField()
    notes = TextField(blank=True)

    def __str__(self) -> str:
        return f'{self.full_name}'

    @property
    def age(self) -> Optional[int]:
        if self.date_of_birth is None:
            return None
        reference_date = self.date_of_death or datetime.date.today()
        years = reference_date.year - self.date_of_birth.year
        months = reference_date.month - self.date_of_birth.month
        if months < 0:
            return years - 1
        if months == 0:
            days = reference_date.day - self.date_of_birth.day
            if days < 0:
                return years - 1
        return years

    @property
    def full_name(self) -> str:
        return f'{self.first_name} {self.last_name}'


class PointOfSale(BaseAuditable):
    """A PointOfSale transaction, usually accompanied by a physical receipt.

    Similar to an invoice or order, but is typically both paid and fulfilled at
    the time of the transaction.
    """
    barcode = CharField(max_length=255, null=True, blank=True)
    party = ForeignKey(
        'Party', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    party_id: int
    point_of_sale_date = DateField()
    point_of_sale_time = TimeField(null=True, blank=True)
    txn = OneToOneField(
        'Txn', on_delete=SET_NULL, null=True, blank=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )

    @property
    def line_item_total(self) -> Decimal:
        qs = (
            self.line_items.all()
            .aggregate(
                total=Sum(
                    F('catalog_item_to_point_of_sale_line_item__quantity') *
                    F('catalog_item_to_point_of_sale_line_item__unit_price')
                )
            )
        )
        return qs['total']


class PointOfSaleDocument(BaseAuditable):
    """Scanned document(s) related to a PointOfSale transaction."""
    point_of_sale = ForeignKey(
        PointOfSale, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    point_of_sale_id: int
    document = FileField()


class PointOfSaleLineItem(BaseAuditable):
    """Line items of a PointOfSale transaction."""
    class Subtype(TextChoices):
        CATALOGUE_ITEM = 'CATALOGUE_ITEM', 'CATALOGUE_ITEM'
        NON_CATALOGUE_ITEM = 'NON_CATALOGUE_ITEM', 'NON_CATALOGUE_ITEM'
    point_of_sale = ForeignKey(
        PointOfSale, on_delete=PROTECT,
        related_name='line_items'
    )
    point_of_sale_id: int
    short_memo = CharField(max_length=255, null=True)
    subtype = CharField(max_length=31, choices=Subtype.choices)

    def __str__(self) -> str:
        return f'PointOfSaleLineItem {self.pk}: {self.point_of_sale_id}'


class PointOfSaleXTxn(BaseAuditable):
    """Relates a PointOfSale purchase to its correlated Transaction.

    In a PointOfSale scenario, these are settled paid in-full at the time of
    purchase.
    I would think that only one TXN record would relate to one PointOfSale
    record.
    By this logic, one of these tables MUST contain a reference to the other;
    however, this is intentionally modeled as a separate table for consistency
    and to avoid a refactor for any edge cases.
    """
    point_of_sale = OneToOneField(
        PointOfSale, on_delete=CASCADE,
        related_name=pascal_case_to_snake_case(__qualname__)
    )  # maybe foreign key?
    point_of_sale_id: int
    txn = OneToOneField(
        'Txn', on_delete=CASCADE,
        related_name=pascal_case_to_snake_case(__qualname__)
    )  # definitely one-to-one
    txn_id: int


class Seller(BaseAuditable):
    name = CharField(max_length=255)


class Song(BaseAuditable):
    """A particular rendition of a song.

    This is a bit abstract, in that it does not fully represent the recordings
    or derivative works.
    """
    lyrics = TextField(blank=True, default='')
    title = CharField(max_length=255)
    # Relationships
    music_artists = ManyToManyField(
        MusicArtist, through='MusicArtistXSong',
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
        MusicArtist, through='MusicArtistXSongRecording',
        related_name='+'
    )


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
    song_derivative = ForeignKey(
        Song, on_delete=CASCADE,
        related_name='+'
    )
    song_derivative_id: int
    song_archetype = ForeignKey(
        Song, on_delete=CASCADE,
        related_name='+'
    )
    song_archetype_id: int
    song_relationship = CharField(
        max_length=15, choices=SongRelationship.choices
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('song_archetype', 'song_derivative'),
                name='unique_song_to_song'
            )
        ]

    def clean(self) -> None:
        if self.song_archetype == self.song_derivative:
            raise ValidationError("Original and derivative must be different.")


class Txn(BaseAuditable):
    """A (financial) transaction.

    Should have properties for "total debit" and "total credit" derived from its
    line items, and those values should be equal.
    """
    memo = TextField(null=True, blank=True)
    payee = ForeignKey(
        Payee, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    payee_id: int
    ref_total = CurrencyField(
        null=True, blank=True,
        verbose_name="Reference Total",
        help_text="Total transaction amount reflected on statement."
    )
    txn_date = DateField()

    objects = querysets.TxnQuerySet.as_manager()

    @property
    def _is_balanced(self) -> bool:
        return self._total_debits == self._total_credits

    @property
    def _total_credits(self) -> Decimal:
        qs = (
            self.line_items.filter(debit=False)
            .aggregate(
                total_credits=Sum('amount')
            )
        )
        return qs['total_credits'] or 0

    @property
    def _total_debits(self) -> Decimal:
        qs = (
            self.line_items.filter(debit=True)
            .aggregate(
                total_debits=Sum('amount')
            )
        )
        return qs['total_debits'] or 0


class TxnLineItem(BaseAuditable):
    """A line item of a Transaction.

    To support double-entry style accounting, this is where different accounts
    are related to individual debits/credits, and the outer "Transaction" groups
    them together as a total.
    Every transaction should have at least two line items representing the
    "from" and "to" accounts.
    """
    account = ForeignKey(
        'Account', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    account_id: int
    amount = CurrencyField()
    debit = BooleanField(default=False)
    memo = TextField(null=True, blank=True)
    txn = ForeignKey(
        Txn, on_delete=PROTECT,
        related_name='line_items'
    )
    txn_id: int

    def __str__(self) -> str:
        return f'TxnLineItem {self.pk}: {self.txn_id}'


class Unit(BaseAuditable):
    """Unit table."""
    class Dimension(TextChoices):
        AREA = 'AREA', 'AREA'
        CURRENT = 'CURRENT', 'CURRENT'
        LENGTH = 'LENGTH', 'LENGTH'
        LIGHT = 'LIGHT', 'LIGHT'
        MASS = 'MASS', 'MASS'
        MATTER = 'MATTER', 'MATTER'
        TEMPERATURE = 'TEMPERATURE', 'TEMPERATURE'
        TIME = 'TIME', 'TIME'
        VOLUME = 'VOLUME', 'VOLUME'

    class System(TextChoices):
        SI = 'SI', 'SI'
        US = 'US', 'US'

    abbr = CharField(max_length=15)
    name = CharField(max_length=63)
    dimension = CharField(max_length=15, choices=Dimension.choices, null=True)
    system = CharField(max_length=2, choices=System.choices, null=True)

    def __str__(self) -> str:
        return f'{self.name} ({self.abbr})'


class Vehicle(BaseAuditable):
    """An individual, uniquely identifiable vehicle."""
    vehicle_year = ForeignKey(
        'VehicleYear', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_year_id: int
    vin = UpperCharField(
        max_length=17, unique=True, validators=[MinLengthValidator(11)]
    )
    # TODO 2023-12-12: VIN Validator based on year + date
    # NHTSA vPIC data could go in a JSON format

    def __str__(self) -> str:
        return f'Vehicle {self.pk}: {self.vin}'


class VehicleMake(BaseAuditable):
    """The make/brand/marque of a vehicle."""
    name = CharField(max_length=255, unique=True, help_text="Make/Brand/Marque")
    manufacturer = ForeignKey(
        Manufacturer, on_delete=SET_NULL,
        null=True,
        **default_related_names(__qualname__)
    )

    def __str__(self) -> str:
        return f'{self.__class__.__name__} {self.pk}: {self.name}'


class VehicleMileage(BaseAuditable):
    """A mileage record for a Vehicle at a given point in time."""
    vehicle = ForeignKey(
        'Vehicle', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_id: int
    odometer_date = DateField(
        validators=[validate_date_not_future],
        help_text="Date on which this odometer reading was captured"
    )
    odometer_miles = PositiveIntegerField(help_text="Odometer reading in miles")
    odometer_time = TimeField(
        null=True, blank=True, help_text="Time of this reading, if available"
    )

    class Meta:
        constraints = [
            # Sanity date/time constraint
            UniqueConstraint(
                fields=('vehicle', 'odometer_date', 'odometer_time'),
                name='unique_vehicle_mileage'
            )
        ]

    @property
    def odometer_datetime(self) -> datetime.datetime:
        return datetime.datetime.combine(self.odometer_date, self.odometer_time)


class VehicleModel(BaseAuditable):
    """The model of a vehicle, e.g., Supra."""
    name = CharField(
        max_length=255,
        help_text="Model name, such as 3000GT, Forte, Supra"
    )
    vehicle_make = ForeignKey(
        VehicleMake, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_make_id: int

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'vehicle_make'),
                name='unique_vehicle_model'
            )
        ]

    def __str__(self) -> str:
        return f'VehicleModel {self.pk}: {self.vehicle_make_id}-{self.name}'


class VehicleService(BaseAuditable):
    """Preventative maintenance or repair.

    Usually encompasses multiple service items.
    """
    date_in = DateField()
    date_out = DateField(null=True, blank=True)
    mileage_in = IntegerField()
    mileage_out = IntegerField()
    vehicle = ForeignKey(
        Vehicle, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_id: int


class VehicleServiceItem(BaseAuditable):  # Line item
    """Individual maintenance items from a service."""
    # TODO: Should have foreign keys for service types, like oil change,
    #  oil filter, tire rotation, since those are standard across vehicles.
    description = CharField(max_length=255)
    vehicle_service = ForeignKey(
        VehicleService, on_delete=CASCADE,
        **default_related_names(__qualname__)
    )
    vehicle_service_id: int


class VehicleTrim(BaseAuditable):
    """An edition/trim of a vehicle model, such as EX, Turbo, Base."""
    name = CharField(max_length=255, help_text="Trim Level, such as EX, GT, SS")
    vehicle_model = ForeignKey(
        VehicleModel, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_model_id: int

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('name', 'vehicle_model'),
                name='unique_vehicle_trim'
            )
        ]

    def __str__(self) -> str:
        return f'VehicleTrim {self.pk}: {self.vehicle_model_id}-{self.name}'


class VehicleYear(BaseAuditable):
    """Year that a Make/Model/Trim was actually produced."""
    vehicle_trim = ForeignKey(
        VehicleTrim, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    vehicle_trim_id: int
    year = IntegerField(
        validators=[MinValueValidator(1886), validate_year_not_future],
        help_text="Production year"
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=('vehicle_trim', 'year'),
                name='unique_vehicle_year'
            )
        ]

    def __str__(self) -> str:
        return f'VehicleYear {self.pk}: {self.vehicle_trim_id}-{self.year}'


class VideoGame(BaseAuditable):
    """
    developer(s) - person or company or other entity
    genre(s)
    language?
    platform: PC, PS4, NES, SNES - not mutually exclusive; m2m
    publisher(s) - usually a company, but could be independently published
    release date - different per platform, port, region, or market (part of m2m)
    tag(s)? Something looser than genre, though not required.
    title

    Could also relate to people:
        voice acting, developers, directors, composers, producers
    Relates to music via soundtracks (songs vs albums is debatable, like movies)
    Like, an "unofficial" OST is kind of an issue for copyright, but not every
    game was published alongside an OST
    Not every game is regionalized right? NTSC / PAL / JP was common for
    consoles. Region # is a thing for media.

    Video Games also are released under different editions
    Sometimes editions are just bundles that include add-ons
    """
    title = CharField(max_length=100)
    # platforms = ManyToManyField()
    series = ForeignKey(
        'VideoGameSeries', on_delete=SET_NULL,
        null=True, blank=True,
        **default_related_names(__qualname__)
    )


class VideoGameAddon(BaseAuditable):
    """DLC, Expansion pack, or other additional components that are optional.

    """
    # release date
    # type, such as DLC, expansion, addon, content, in-game something
    # (or tags may be appropriate)
    name = CharField(max_length=100)
    release_date = DateField(null=True, blank=True)
    video_game = ForeignKey(
        VideoGame, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )


class VideoGameEdition(BaseAuditable):
    name = CharField(max_length=100)
    release_date = DateField(null=True, blank=True)
    video_game = ForeignKey(
        VideoGame, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )


class VideoGamePlatform(BaseAuditable):
    """
    May also be a commodity, asset, or catalog item, but we will probably keep
    this abstracted from the physical consoles or assemblies
    """

    name = CharField(max_length=31)
    short_name = CharField(max_length=15, blank=True)


class VideoGameSeries(BaseAuditable):
    """A grouping of related video games."""
    name = CharField(max_length=63)
    parent_series = ForeignKey(
        'self', on_delete=SET_NULL,
        null=True, blank=True,
        related_name='sub_series'
    )


# class VideoGameXVideoGamePlatform(BaseAuditable):
class VideoGameXVideoGamePlatform:
    """
    This gets closer to the catalog item.

    Example:
        "I bought a [copy] of [game] on [platform]
        "I bought a [key] for [World of Final Fantasy] on [Steam/PC]
        "I bought a [blu-ray] of [World of Final Fantasy] on [PS4]

    TODO 2023-12-12: Console games were regionalized for PAL/NTSC
    """
    release_date = DateField(null=True, blank=True)
    video_game = ForeignKey(
        VideoGame, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    video_game_platform = ForeignKey(
        VideoGamePlatform, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )


class VideoGameEditionXVideoGamePlatform(BaseAuditable):
    release_date = DateField(null=True, blank=True)
    video_game_edition = ForeignKey(
        VideoGameEdition, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    video_game_platform = ForeignKey(
        VideoGamePlatform, on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
