from django_ccbv import DetailView, ListView

from core.models import MusicArtist


class MusicArtistListView(ListView):
    model = MusicArtist
    ordering = ('name',)
    queryset = MusicArtist.with_related
    template_name = 'core/models/music-artist--list.html'


class MusicArtistDetailView(DetailView):
    model = MusicArtist
    template_name = 'core/models/music-artist--detail.html'
