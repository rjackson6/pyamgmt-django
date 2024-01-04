from collections import deque
from io import BytesIO
import os
from typing import Iterable

from PIL import Image, ImageOps

from django.db.models import QuerySet
from django.db.models.fields.files import ImageFieldFile


# TODO 2023-12-12: This should be a utils.function
#  I guess it could take a list of callbacks, too? Then other functions could
#  be applied to each record as they are traversed.
#  Alternatively, and for cases where depth calculation isn't required, just
#  keep a flat list of references and do the extra work somewhere else
#  The reason why "depth" is specific is because it's part of the memo, and the
#  only part that's directly connected to the traversal
#  Since this mutates the given list and objects, the return could be the flat
#  version.
def calculate_depth(
        data_list: list[dict],
        key: str,
        depth_key: str = 'depth',
) -> list:
    """"""

    queue = deque([(id(x), x, 1) for x in data_list])
    memo = set()
    while queue:
        id_, account, depth = queue.popleft()
        if id_ in memo:
            continue
        memo.add(id_)
        account[depth_key] = depth
        queue.extend((id(x), x, depth + 1) for x in account[key])
    return data_list


def resize_image(image_field: ImageFieldFile, sizes: Iterable) -> dict:
    """Given an image and an iterable of tuple dimensions, resize the
    image to the given size constraints.
    """

    data = {}
    image_width, image_height = image_field.width, image_field.height
    name, ext = os.path.splitext(image_field.name)
    ext = ext[1:].lower()
    if ext == 'jpg':
        ext = 'jpeg'
    for size in sizes:
        file_to_save = image_field
        resize = False
        width, height = size.value
        if image_width > width or image_height > height:
            resize = True
        with Image.open(image_field) as image:
            size_name = size.name.lower()
            if resize:
                new_image = BytesIO()
                t = ImageOps.contain(image, size.value)
                t.save(new_image, ext)
                file_to_save = new_image
        field_name = f'image_{size_name}'
        file_name = f'{name}--{size_name}.{ext}'
        data[field_name] = file_name, file_to_save
    return data


def traverse_depth(
        data_list: list[dict],
        key: str,
        depth_key: str = 'depth',
) -> list:
    """Updates dictionaries with depth and returns the flattened list."""

    all_ = []
    queue = deque([(id(x), x, 1) for x in data_list])
    memo = set()
    while queue:
        id_, account, depth = queue.popleft()
        if id_ in memo:
            continue
        memo.add(id_)
        all_.append(account)
        account[depth_key] = depth
        queue.extend((id(x), x, depth + 1) for x in account[key])
    return all_


def hierarchy(foreign_key: str, *values):
    # values / extra values for queryset
    # queryset object; values
    # could I use values_list? or in_bulk()?
    qs: QuerySet
    qs = QuerySet()
    data = []
    data_map = {}
    deferred = deque()
    if qs:
        for record in qs.iterator():
            record['descendents'] = []
    return

