from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .. import forms
from ..models import music_album
from . import _inlines


@admin.register(music_album.MusicAlbum)
class MusicAlbumAdmin(admin.ModelAdmin):
    form = forms.admin.MusicAlbumForm
    inlines = [
        _inlines.MusicAlbumArtworkInline,
        _inlines.MusicAlbumEditionInline,
        _inlines.MusicAlbumXMusicArtistInline,
        _inlines.MusicAlbumXMusicTagInline,
        _inlines.MusicAlbumXPersonInline,
    ]
    list_display = (
        'image_tag', 'title', '_music_artists', '_edition_count',
        'is_compilation',
    )
    list_display_links = ('title',)
    ordering = ('title',)
    search_fields = ('title', 'music_artists__name')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .prefetch_related('music_artists')
            .annotate(
                Count('music_album_edition', distinct=True),
            )
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

    @staticmethod
    def _edition_count(obj) -> int:
        return obj.music_album_edition__count

    @staticmethod
    def image_tag(obj: music_album.MusicAlbum) -> str:
        if not obj.cover_artwork:
            return ''
        return format_html(
            '<img src="{}" alt="{}">',
            obj.cover_artwork.image_thumbnail.url,
            obj.cover_artwork.short_description
        )


admin.site.register(music_album.MusicAlbumArtwork)


@admin.register(music_album.MusicAlbumEdition)
class MusicAlbumEditionAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MusicAlbumEditionXSongRecordingInline
    ]
    list_display = ('_description', 'year_produced')
    list_select_related = ('music_album',)
    ordering = ('music_album__title', 'name')
    search_fields = ('music_album__title', 'name')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.music_album.title} [{obj.name}]'


@admin.register(music_album.MusicAlbumProduction)
class MusicAlbumProductionAdmin(admin.ModelAdmin):
    form = forms.admin.MusicAlbumProductionForm
    list_display = ('_description', 'media_format')
    list_select_related = ('music_album_edition__music_album',)

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.music_album_edition.music_album.title}'
            f' [{obj.music_album_edition.name}]'
        )


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
    list_display = ('_description',)
    list_select_related = ('music_album', 'person')
    
    @staticmethod
    def _description(obj) -> str:
        return f'{obj.music_album.title} : {obj.person.full_name}'


@admin.register(music_album.MusicAlbumXVideoGame)
class MusicAlbumXVideoGameAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('music_album', 'video_game')
    ordering = ('video_game__title', 'music_album__title')
    
    @staticmethod
    def _description(obj) -> str:
        return f'{obj.video_game.title} : {obj.music_album.title}'
