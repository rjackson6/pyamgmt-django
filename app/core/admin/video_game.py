from django.contrib import admin

from ..models import video_game
from . import _inlines


@admin.register(video_game.VideoGame)
class VideoGameAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.VideoGameEditionInline,
        _inlines.VideoGameAddonInline,
        _inlines.PersonXVideoGameInline,
        _inlines.MusicAlbumXVideoGameInline,
    ]
    list_display = ('title', 'series')
    ordering = ('title',)


@admin.register(video_game.VideoGameAddon)
class VideoGameAddonAdmin(admin.ModelAdmin):
    list_display = ('_description', 'release_date')
    list_select_related = ('video_game',)

    @staticmethod
    def _description(obj):
        return f'{obj.video_game.title} : {obj.name}'


@admin.register(video_game.VideoGameEdition)
class VideoGameEditionAdmin(admin.ModelAdmin):
    inlines = [_inlines.VideoGameEditionXVideoGamePlatformInline]
    list_display = ('_description',)
    list_select_related = ('video_game',)

    @staticmethod
    def _description(obj):
        return f'{obj.video_game.title} : {obj.name}'


@admin.register(video_game.VideoGamePlatform)
class VideoGamePlatformAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.VideoGamePlatformRegionInline,
    ]
    ordering = ('name',)


@admin.register(video_game.VideoGamePlatformEdition)
class VideoGamePlatformEditionAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    ordering = ('video_game_platform__name', 'name')

    @staticmethod
    def _description(obj):
        return f'{obj.video_game_platform.name} : {obj.name}'


@admin.register(video_game.VideoGamePlatformRegion)
class VideoGamePlatformRegionAdmin(admin.ModelAdmin):
    list_display = ('_description', 'release_date')
    list_select_related = ('video_game_platform',)
    ordering = ('video_game_platform__name', 'region')

    @staticmethod
    def _description(obj):
        return f'{obj.video_game_platform.name}: {obj.region}'


@admin.register(video_game.VideoGameSeries)
class VideoGameSeriesAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.VideoGameInline,
    ]
    ordering = ('name',)
