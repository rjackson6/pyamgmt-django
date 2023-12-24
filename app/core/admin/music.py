from django.contrib import admin
from django.db.models import Count

from .. import forms
from ..models import music, music_album, music_artist, music_tag
from . import _inlines


@admin.register(music_album.MusicAlbum)
class MusicAlbumAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicAlbumEditionInline,
        _inlines.MusicAlbumXMusicArtistInline,
        _inlines.MusicAlbumXMusicTagInline,
        _inlines.MusicAlbumXPersonInline,
    ]
    list_display = ('title', '_music_artists', 'is_compilation')
    ordering = ('title',)
    search_fields = ('title',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .prefetch_related('music_artists')
        )

    @staticmethod
    def _music_artists(obj) -> str:
        artists = []
        for n, artist in enumerate(obj.music_artists.all()):
            artists.append(artist.name)
            if n > 2:
                artists.append('...')
                break
        artists = ', '.join(artists)
        return artists


admin.site.register(music_album.MusicAlbumArtwork)


@admin.register(music_album.MusicAlbumEdition)
class MusicAlbumEditionAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicAlbumEditionXSongRecordingInline
    ]
    list_display = ('admin_description', 'year_produced')
    list_select_related = ('music_album',)
    ordering = ('music_album__title', 'name')
    search_fields = ('music_album__title', 'name')


@admin.register(music_album.MusicAlbumXMusicArtist)
class MusicAlbumXMusicArtistAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('music_album', 'music_artist')
    ordering = ('music_artist__name', 'music_album__title')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.music_artist.name} : {obj.music_album.title}'


@admin.register(music_album.MusicAlbumXPerson)
class MusicAlbumXPersonAdmin(admin.ModelAdmin):
    inlines = [_inlines.MusicAlbumXPersonXMusicRoleInline]
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'person')


@admin.register(music_album.MusicAlbumXVideoGame)
class MusicAlbumXVideoGameAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'video_game')
    ordering = ('video_game__title', 'music_album__title')


@admin.register(music_artist.MusicArtist)
class MusicArtistAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicAlbumXMusicArtistInline,
        _inlines.MusicArtistActivityInline,
        _inlines.MusicArtistXPersonInline,
    ]
    list_display = (
        'name', 'disambiguator', '_album_count', '_arrangement_count',
        '_people_count', 'website',
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
                Count('people', distinct=True),
            )
        )

    @staticmethod
    def _album_count(obj):
        return obj.music_albums__count

    @staticmethod
    def _arrangement_count(obj):
        return obj.arrangements__count

    @staticmethod
    def _people_count(obj):
        return obj.people__count


@admin.register(music_artist.MusicArtistActivity)
class MusicArtistActivityAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_artist',)
    ordering = ('music_artist__name', 'year_active', 'year_inactive')


@admin.register(music_artist.MusicArtistXPerson)
class MusicArtistXPersonAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonForm
    inlines = [_inlines.MusicArtistXPersonActivityInline]
    list_display = ('admin_description',)
    list_select_related = ('music_artist', 'person')
    ordering = ('music_artist__name', 'person__first_name')
    search_fields = (
        'music_artist__name',
        'person__preferred_name',
    )


@admin.register(music_artist.MusicArtistXPersonActivity)
class MusicArtistXPersonActivityAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonActivityForm
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist_x_person__music_artist',
        'music_artist_x_person__person',
    )


@admin.register(music_artist.MusicArtistXSong)
class MusicArtistXSongAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist',
        'song',
    )


@admin.register(music_artist.MusicArtistXSongPerformance)
class MusicArtistXSongPerformanceAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXSongPerformanceForm
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist',
        'song_performance__song_arrangement',
    )


@admin.register(music.MusicRole)
class MusicRoleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(music_tag.MusicTag)
class MusicTagAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(music.MusicalInstrument)
class MusicalInstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    ordering = ('name',)


@admin.register(music.MusicalInstrumentXPerson)
class MusicalInstrumentXPersonAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('musical_instrument', 'person')
    ordering = ('musical_instrument__name', 'person__last_name')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.musical_instrument.name} : {obj.person.full_name}'
