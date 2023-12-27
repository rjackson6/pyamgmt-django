from io import BytesIO
import os
from PIL import Image, ImageOps

from django.core.files import File
from django.db.models import CharField, ImageField, TextField

from django_base.models import BaseAuditable


class Photo(BaseAuditable):
    short_description = CharField(max_length=255, blank=True)
    description = TextField(blank=True)
    image = ImageField()
    # TODO: SHA hash
    # TODO: Thumbnail field
    thumbnail = ImageField(null=True, blank=True)

    def save(self, *args, **kwargs) -> None:
        size = (100, 100)
        name, ext = os.path.splitext(self.image.name)
        ext = ext.lower()
        new_file = BytesIO()
        with Image.open(self.image) as im:
            # t = ImageOps.contain(im, size)
            t = ImageOps.pad(im, size, color='#000')
            t.save(new_file, 'JPEG')
        self.thumbnail.save('where_am_i.jpg', File(new_file), save=False)
        super().save(*args, **kwargs)
