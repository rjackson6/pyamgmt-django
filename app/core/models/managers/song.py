from django.db.models import Manager


class SongArrangementOriginalsManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(original=True)
