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


class PersonListView(ListView):
    model = Person
    template_name = 'core/models/person--list.html'


class PersonDetailView(DetailView):
    model = Person
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
