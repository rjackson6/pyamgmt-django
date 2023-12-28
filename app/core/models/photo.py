import enum
from io import BytesIO
import os
from PIL import Image, ImageOps

from django.core.files import File
from django.db.models import CharField, ImageField, TextField

from django_base.models import BaseAuditable


class Photo(BaseAuditable):

    class ImageSize(enum.Enum):
        THUMBNAIL = (100, 100)
        SMALL = (250, 250)
        MEDIUM = (640, 640)
        LARGE = (1280, 1280)

    short_description = CharField(max_length=255, blank=True)
    description = TextField(blank=True)
    image_full = ImageField()
    # TODO: SHA hash
    # TODO: Thumbnail field
    image_thumbnail = ImageField(null=True, blank=True, editable=False)
    image_small = ImageField(null=True, blank=True, editable=False)
    image_medium = ImageField(null=True, blank=True, editable=False)
    image_large = ImageField(null=True, blank=True, editable=False)

    def __str__(self) -> str:
        return self.short_description

    def save(self, *args, **kwargs) -> None:
        width, height = self.image_full.width, self.image_full.height
        name, ext = os.path.splitext(self.image_full.name)
        ext = ext[1:].lower()
        if ext == 'jpg':
            ext = 'jpeg'
        resizes = []
        for size in self.ImageSize:
            w, h = size.value
            if width > w or height > h:
                resizes.append(size)
        if resizes:
            with Image.open(self.image_full) as image_full:
                for size in resizes:
                    size_name = size.name.lower()
                    new_image = BytesIO()
                    t = ImageOps.contain(image_full, size.value)
                    t.save(new_image, ext)
                    field = getattr(self, f'image_{size_name}')
                    field.save(
                        f'{name}--{size_name}.{ext}',
                        File(new_image),
                        save=False
                    )
        super().save(*args, **kwargs)
