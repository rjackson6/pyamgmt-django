from django.contrib import admin
from django.db.models import Count

from .. import forms
from ..models import music_artist
from . import _inlines


@admin.register(music_artist.MusicArtist)
class MusicArtistAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicAlbumXMusicArtistInline,
        _inlines.MusicArtistActivityInline,
        _inlines.MusicArtistXPersonInline,
    ]
    list_display = (
        'name', 'disambiguator', '_album_count', '_arrangement_count',
        '_personnel_count', 'website',
    )
    ordering = ('name',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .annotate(
                Count('arrangements', distinct=True),
                Count('music_albums', distinct=True),
                Count('personnel', distinct=True),
            )
        )

    @staticmethod
    def _album_count(obj):
        return obj.music_albums__count

    @staticmethod
    def _arrangement_count(obj):
        return obj.arrangements__count

    @staticmethod
    def _personnel_count(obj):
        return obj.personnel__count


@admin.register(music_artist.MusicArtistActivity)
class MusicArtistActivityAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('music_artist',)
    ordering = ('music_artist__name', 'year_active', 'year_inactive')
    search_fields = ('music_artist__name',)

    @staticmethod
    def _description(obj) -> str:
        text = f'{obj.music_artist.name} : {obj.year_active}'
        if obj.year_inactive:
            text += f' - {obj.year_inactive}'
        else:
            text += f' - Present'
        return text


@admin.register(music_artist.MusicArtistXPerson)
class MusicArtistXPersonAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonForm
    inlines = [
        _inlines.MusicArtistXPersonActivityInline,
    ]
    list_display = ('_description',)
    list_select_related = ('music_artist', 'person')
    ordering = ('music_artist__name', 'person__first_name')
    search_fields = (
        'music_artist__name',
        'person__preferred_name',
    )

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.music_artist.name} : {obj.person.full_name}'
        )


@admin.register(music_artist.MusicArtistXPersonActivity)
class MusicArtistXPersonActivityAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonActivityForm
    list_display = ('_description',)
    list_select_related = (
        'music_artist_x_person__music_artist',
        'music_artist_x_person__person',
    )

    @staticmethod
    def _description(obj) -> str:
        text = (
            f'{obj.music_artist_x_person.music_artist.name}'
            f' : {obj.music_artist_x_person.person.full_name}'
            f' : {obj.year_active}'
        )
        if obj.year_inactive:
            text += f'-{obj.year_inactive}'
        return text


@admin.register(music_artist.MusicArtistXSong)
class MusicArtistXSongAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = (
        'music_artist',
        'song',
    )

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.music_artist.name}: {obj.song.title}'


@admin.register(music_artist.MusicArtistXSongPerformance)
class MusicArtistXSongPerformanceAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXSongPerformanceForm
    list_display = ('_description', 'comments')
    list_select_related = (
        'music_artist',
        'song_performance__song_arrangement',
    )
    ordering = (
        'music_artist__name',
        'song_performance__song_arrangement__title',
    )

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.music_artist.name}'
            f' : {obj.song_performance.song_arrangement.title}'
        )
