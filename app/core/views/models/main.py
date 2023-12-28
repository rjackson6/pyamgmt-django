from django_ccbv.views.generic import DetailView, ListView

from core.models import *


class AccountListView(ListView):
    model = Account
    template_name = 'core/models/account--list.html'


class MusicAlbumListView(ListView):
    model = MusicAlbum
    ordering = ('title',)
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
    template_name = 'core/models/person--list.html'


class PersonDetailView(DetailView):
    model = Person
    queryset = (
        Person.objects
        .select_related('featured_photo__photo')
    )
    template_name = 'core/models/person--detail.html'


class SongPerformanceDetailView(DetailView):
    model = SongPerformance
    template_name = 'core/models/song-performance--detail.html'


class VehicleListView(ListView):
    model = Vehicle
    queryset = (
        Vehicle.objects
        .select_related(
            'vehicle_year__vehicle_trim__vehicle_model__vehicle_make'
        )
    )
    template_name = 'core/models/vehicle--list.html'
