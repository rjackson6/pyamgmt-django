from django.core.validators import MinLengthValidator
from django.db.models import (
    CASCADE, CharField, ForeignKey, JSONField, OneToOneField, SET_DEFAULT,
    TextChoices
)

from django_base.models import BaseAuditable
from django_base.models.fields import UpperCharField
from django_base.utils import default_related_names, pascal_case_to_snake_case
from django_base.validators import validate_alphanumeric, validate_digit

from core.models.models import get_default_media_format_audio
from core.validators import validate_isbn, validate_isbn_13_check_digit


class CatalogItem(BaseAuditable):
    """An item with unique registries in other global systems.

    Can generally be ordered, purchased, re-sold, and accumulated as a discrete
    asset or inventory.
    Does not include concepts like labor hours, services, or warranties.
    """
    class Subtype(TextChoices):
        DIGITAL_SONG = 'DIGITAL_SONG', 'DIGITAL_SONG'
        MUSIC_ALBUM = 'MUSIC_ALBUM', 'MUSIC_ALBUM'
    asin = UpperCharField(
        max_length=10, unique=True, null=True, blank=True,
        validators=[MinLengthValidator(10), validate_alphanumeric],
        verbose_name="ASIN",
        help_text="Amazon Standard Identification Number"
    )
    ean_13 = CharField(
        max_length=13, unique=True, null=True, blank=True,
        validators=[MinLengthValidator(13), validate_digit],
        verbose_name="EAN-13",
        help_text="European Article Number"
    )
    eav = JSONField(null=True, blank=True)
    # isbn is also part of gsin / gs1 spec now, apparently
    isbn = CharField(
        max_length=10, unique=True, null=True, blank=True,
        validators=[MinLengthValidator(10), validate_isbn],
        verbose_name="ISBN",
        help_text="International Standard Book Number"
    )
    isbn_13 = CharField(
        max_length=13, unique=True, null=True, blank=True,
        validators=[
            MinLengthValidator(13),
            validate_digit,
            validate_isbn_13_check_digit
        ]
    )
    ismn = CharField(
        max_length=13, unique=True, null=True, blank=True,
        validators=[MinLengthValidator(13)],
        verbose_name="ISMN",
        help_text="International Standard Music Number"
    )
    name = CharField(max_length=255)
    subtype = CharField(
        max_length=31, choices=Subtype.choices, null=True, blank=True
    )
    upc_a = CharField(
        max_length=12, unique=True, null=True, blank=True,
        validators=[MinLengthValidator(12), validate_digit]
    )


class CatalogItemDigitalSong(BaseAuditable):
    """Digital songs.

    Unlike Music albums, can be distributed individually absent of other medium.
    - Even if a song is released as a "Single", that "Single" still requires a
      medium for physical distribution, which makes it a "Single Album"
    """
    catalog_item = OneToOneField(
        CatalogItem, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    catalog_item_id: int


class CatalogItemMusicAlbumProduction(BaseAuditable):
    """A produced Music Album distributed in a particular format."""
    catalog_item = OneToOneField(
        CatalogItem, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    catalog_item_id: int
    # Does
    media_format = ForeignKey(
        'MediaFormat', on_delete=SET_DEFAULT,
        default=get_default_media_format_audio,
        **default_related_names(__qualname__)
    )
    media_format_id: int
    # music_album_production = ForeignKey('MusicAlbumProduction')
