from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView

from pyamgmt.models import MusicAlbumToSongRecording


# class MusicAlbumToSongRecordingView(View):
#     def get(self, request):
#         return HttpResponse('working')


class MusicAlbumToSongRecordingView(TemplateView):
    template_name = 'pyamgmt/models/musicalbumtosongrecording_list.html'
    qs_musicalbumtosongrecording = (
        MusicAlbumToSongRecording.objects
        .select_related('musicalbum', 'songrecording')
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'qs_musicalbumtosongrecording': self.qs_musicalbumtosongrecording
        })
        return context
