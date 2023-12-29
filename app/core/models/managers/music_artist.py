from django.db.models import Manager, Prefetch


class MusicArtistManager(Manager):
    def get_queryset(self):
        from ..music_artist import MusicArtistActivity
        from ..person import Person

        return (
            super().get_queryset()
            .prefetch_related(
                Prefetch(
                    'music_artist_activity_set',
                    queryset=(
                        MusicArtistActivity.objects
                        .order_by('-year_inactive', '-year_active')
                    )
                ),
                Prefetch(
                    'personnel',
                    queryset=(
                        Person.objects
                        .prefetch_related(
                            'music_artist_x_person_set'
                            '__music_artist_x_person_activity_set'
                        )
                        .filter(
                            music_artist_x_person__music_artist_x_person_activity__year_inactive__isnull=True,
                        )
                        .distinct()
                        .order_by('preferred_name',)
                    ),
                    to_attr='active_members',
                )
            )
        )


class MusicArtistXPersonManager(Manager):
    def get_queryset(self):
        from ..music_artist import (
            MusicArtistActivity, MusicArtistXPersonActivity
        )

        return (
            super().get_queryset()
            .select_related('music_artist', 'person')
            .prefetch_related(
                Prefetch(
                    'music_artist__music_artist_activity_set',
                    queryset=(
                        MusicArtistActivity.objects
                        .order_by('-year_inactive')
                    )
                ),
                Prefetch(
                    'music_artist_x_person_activity_set',
                    queryset=(
                        MusicArtistXPersonActivity.objects
                        .order_by('-year_active')
                    )
                )
            )
        )
