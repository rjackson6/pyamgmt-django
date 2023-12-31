from django_ccbv import DetailView, ListView

from core.models import MusicArtist


class MusicArtistListView(ListView):
    model = MusicArtist
    ordering = ('name',)
    paginate_by = 50
    queryset = MusicArtist.with_related
    template_name = 'core/models/music-artist--list.html'


class MusicArtistDetailView(DetailView):
    model = MusicArtist
    queryset = MusicArtist.with_related
    template_name = 'core/models/music-artist--detail.html'
