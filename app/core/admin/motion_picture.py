from django.contrib import admin

from ..models import motion_picture
from . import _inlines


@admin.register(motion_picture.MotionPicture)
class MotionPictureAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.MotionPictureXPersonInline,
        _inlines.MotionPictureXMusicAlbumInline,
    ]
    ordering = ('title', 'year_produced')


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
    list_display = ('admin_description',)
    list_select_related = ('motion_picture', 'music_album')


admin.site.register(motion_picture.MotionPictureXSong)
