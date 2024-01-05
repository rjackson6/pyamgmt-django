from django.db.models import Prefetch

from django_ccbv.views.generic import DetailView, ListView

from core.models import *


class MusicAlbumListView(ListView):
    model = MusicAlbum
    ordering = ('title',)
    paginate_by = 50
    queryset = MusicAlbum.objects.prefetch_related('music_artists')
    template_name = 'core/models/music-album--list.html'


class MusicAlbumDetailView(DetailView):
    model = MusicAlbum
    queryset = (
        MusicAlbum.objects
        .prefetch_related('music_artists', 'personnel')
    )
    template_name = 'core/models/music-album--detail.html'


class MusicAlbumEditionDetailView(DetailView):
    model = MusicAlbumEdition
    template_name = 'core/models/music-album-edition--detail.html'


class PersonListView(ListView):
    model = Person
    ordering = ('preferred_name',)
    paginate_by = 50
    template_name = 'core/models/person--list.html'


class PersonDetailView(DetailView):
    model = Person
    queryset = (
        Person.objects
        .select_related('featured_photo__photo')
        .prefetch_related(
            Prefetch(
                'music_albums',
                queryset=MusicAlbum.objects.order_by('title')
            ),
            Prefetch(
                'music_artists',
                queryset=MusicArtist.objects.order_by('name')
            )
        )
    )
    template_name = 'core/models/person--detail.html'


class VehicleListView(ListView):
    model = Vehicle
    queryset = (
        Vehicle.objects
        .select_related(
            'vehicle_year__vehicle_trim__vehicle_model__vehicle_make'
        )
    )
    template_name = 'core/models/vehicle--list.html'
