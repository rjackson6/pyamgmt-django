import enum
import hashlib

from django.db.models import (
    CharField, ImageField, PositiveSmallIntegerField, TextField,
    ManyToManyField,
)

from django_base.models import BaseAuditable

from ._utils import resize_image


class Photo(BaseAuditable):

    class ImageSize(enum.Enum):
        THUMBNAIL = (100, 100)
        SMALL = (250, 250)
        MEDIUM = (640, 640)
        LARGE = (1280, 1280)

    short_description = CharField(max_length=255, blank=True)
    description = TextField(blank=True)
    year_taken = PositiveSmallIntegerField(null=True, blank=True)
    attribution = CharField(max_length=255, blank=True)
    # TODO: The following fields could probably be a mixin, but I'm not sure
    #  about overriding the save method
    image_full = ImageField()
    image_full_sha256 = CharField(
        max_length=64, unique=True, null=True, editable=False,
    )
    image_large = ImageField(null=True, blank=True, editable=False)
    image_medium = ImageField(null=True, blank=True, editable=False)
    image_small = ImageField(null=True, blank=True, editable=False)
    image_thumbnail = ImageField(null=True, blank=True, editable=False)

    people = ManyToManyField(
        'Person', through='PersonXPhoto',
        related_name='+', blank=True,
    )

    def __str__(self) -> str:
        return self.short_description

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
