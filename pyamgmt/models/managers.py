from django.db.models import Manager


class MusicArtistToPersonManager(Manager):
    def get_queryset(self):
        return super().get_queryset().select_related('musicartist', 'person')
