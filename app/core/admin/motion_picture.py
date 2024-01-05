from django.contrib import admin

from ..models import motion_picture
from . import _inlines


@admin.register(motion_picture.MotionPicture)
class MotionPictureAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MotionPictureXPersonInline,
        _inlines.MotionPictureXMusicAlbumInline,
    ]
    list_display = ('title', 'disambiguator', 'year_produced',)
    ordering = ('title', 'year_produced',)
    search_fields = ('title',)


admin.site.register(motion_picture.MotionPictureRecording)


@admin.register(motion_picture.MotionPictureSeries)
class MotionPictureSeriesAdmin(admin.ModelAdmin):
    # inlines = [
    #     _inlines.MotionPictureInline,
    # ]
    list_display = ('name',)
    ordering = ('name',)


@admin.register(motion_picture.MotionPictureXMusicAlbum)
class MotionPictureXMusicAlbumAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('motion_picture', 'music_album')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.motion_picture.title} : {obj.music_album.title}'


admin.site.register(motion_picture.MotionPictureXSong)
