from django.db.models import Prefetch
from django.views.generic.base import TemplateView

from pyamgmt.models import MusicAlbumToSongRecording, MusicArtistToSong, Song


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


class SongListView(TemplateView):
    template_name = 'pyamgmt/models/song_list.html'
    qs_song = (
        Song.objects
        .prefetch_related(
            Prefetch(
                'musicartisttosong_set',
                queryset=(
                    MusicArtistToSong.objects
                    .select_related('musicartist')
                    .order_by('musicartist__name')
                )
            )
        )
        .order_by('title')
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({'qs_song': self.qs_song})
        return context
