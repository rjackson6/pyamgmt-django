from django.db.models import CharField

from django_base.models import BaseAuditable


class MediaFormat(BaseAuditable):
    name = CharField(max_length=255, unique=True)

    @classmethod
    def get_default_audio(cls) -> int:
        obj, _ = cls.objects.get_or_create(name='Audio')
        return obj.pk
