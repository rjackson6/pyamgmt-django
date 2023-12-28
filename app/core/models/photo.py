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
        for size in self.ImageSize:
            file_to_save = self.image_full
            resize = False
            w, h = size.value
            if width > w or height > h:
                resize = True
            with Image.open(self.image_full) as image_full:
                size_name = size.name.lower()
                if resize:
                    new_image = BytesIO()
                    t = ImageOps.contain(image_full, size.value)
                    t.save(new_image, ext)
                    file_to_save = new_image
            field = getattr(self, f'image_{size_name}')
            field.save(
                f'{name}--{size_name}.{ext}',
                File(file_to_save),
                save=False
            )
        super().save(*args, **kwargs)
