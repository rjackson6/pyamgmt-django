from django_ccbv import DetailView, ListView

from core.models import SongPerformance


class SongPerformanceListView(ListView):
    model = SongPerformance
    paginate_by = 50
    template_name = 'core/models/song-performance--list.html'


class SongPerformanceDetailView(DetailView):
    model = SongPerformance
    template_name = 'core/models/song-performance--detail.html'
