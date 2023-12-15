from django_ccbv.views.generic import DetailView, ListView, TemplateView

from core.models import *


class AccountListView(ListView):
    model = Account
    template_name = 'core/models/account--list.html'


class MusicAlbumListView(ListView):
    model = MusicAlbum
    ordering = ('title',)
    template_name = 'core/models/music-album--list.html'


class MusicArtistListView(ListView):
    model = MusicArtist
    ordering = ('name',)
    template_name = 'core/models/music-artist--list.html'


class VehicleListView(ListView):
    model = Vehicle
    queryset = (
        Vehicle.objects
        .select_related(
            'vehicle_year__vehicle_trim__vehicle_model__vehicle_make'
        )
    )
    template_name = 'core/models/vehicle--list.html'
