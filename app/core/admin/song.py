from django.contrib import admin
from django.db.models import Count

from .. import forms
from ..models import song
from . import _inlines


@admin.register(song.SongDisambiguator)
class SongDisambiguatorAdmin(admin.ModelAdmin):
    pass


@admin.register(song.Song)
class SongAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicArtistXSongInline,
        _inlines.PersonXSongInline,
        _inlines.SongXSongArrangementInline,
    ]
    list_display = (
        '_description',
        'disambiguator',
        '_arrangement_count',
    )
    ordering = ('title',)
    search_fields = ('title',)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('music_artists')
            .annotate(Count('arrangements'))
        )

    @staticmethod
    def _description(obj) -> str:
        artists = []
        for n, artist in enumerate(obj.music_artists.all()):
            artists.append(artist.name)
            if n > 2:
                artists.append('...')
                break
        artists = ', '.join(artists)
        return f'{obj.title} [{artists}]'

    @staticmethod
    def _arrangement_count(obj) -> int:
        return obj.arrangements__count


@admin.register(song.SongArrangement)
class SongArrangementAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.SongPerformanceInline,
        _inlines.SongXSongArrangementInline,
        _inlines.MusicArtistXSongArrangementInline,
        _inlines.PersonXSongArrangementInline,
    ]
    list_display = (
        'title', 'disambiguator', 'is_original', 'description',
        '_performance_count',
    )
    ordering = ('title', '-is_original', 'description')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('song_performance_set')
            .annotate(Count('song_performance'))
        )

    @staticmethod
    def _performance_count(obj) -> int:
        return obj.song_performance__count


@admin.register(song.SongPerformance)
class SongPerformanceAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicArtistXSongPerformanceInline,
        _inlines.PersonXSongPerformanceInline,
        _inlines.SongRecordingInline,
    ]
    list_display = (
        '_description', 'performance_type',
    )
    list_select_related = ('song_arrangement',)
    ordering = ('song_arrangement__title',)

    @staticmethod
    def _description(obj) -> str:
        text = f'{obj.song_arrangement.title}'
        if obj.song_arrangement.disambiguator:
            text += f' [{obj.song_arrangement.disambiguator}]'
        if obj.song_arrangement.description:
            text += f' [{obj.song_arrangement.description}]'
        if obj.description:
            text += f' - {obj.description}'
        return text


@admin.register(song.SongRecording)
class SongRecordingAdmin(admin.ModelAdmin):
    form = forms.admin.SongRecordingForm
    inlines = [_inlines.MusicAlbumEditionXSongRecordingInline]
    list_display = (
        '_description', 'duration',
    )
    list_select_related = ('song_performance__song_arrangement',)
    ordering = ('song_performance__song_arrangement__title',)

    @staticmethod
    def _description(obj) -> str:
        text = f'{obj.song_performance.song_arrangement.title}'
        if obj.song_performance.description:
            text += f' - {obj.song_performance.description}'
        return text
