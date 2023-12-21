from django.contrib import admin

from .. import forms
from .. import models


class MusicAlbumEditionInline(admin.TabularInline):
    model = models.MusicAlbumEdition
    extra = 1


class MusicAlbumEditionXSongRecordingInline(admin.TabularInline):
    form = forms.admin.MusicAlbumEditionXSongRecordingForm
    model = models.MusicAlbumEditionXSongRecording


class MusicAlbumXMusicArtistInline(admin.TabularInline):
    model = models.MusicAlbumXMusicArtist
    extra = 1


class MusicAlbumXMusicTagInline(admin.TabularInline):
    model = models.MusicAlbumXMusicTag
    extra = 2


class MusicAlbumXPersonInline(admin.TabularInline):
    model = models.MusicAlbumXPerson
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related('music_album', 'person')
        )


class MusicArtistActivityInline(admin.TabularInline):
    model = models.MusicArtistActivity
    extra = 1


class MusicArtistXPersonInline(admin.TabularInline):
    model = models.MusicArtistXPerson
    extra = 2

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related('music_artist', 'person')
        )


class MusicArtistXPersonActivityInline(admin.TabularInline):
    model = models.MusicArtistXPersonActivity
    extra = 1


class MusicArtistXSongInline(admin.TabularInline):
    model = models.MusicArtistXSong
    extra = 1


class MusicArtistXSongArrangementInline(admin.TabularInline):
    model = models.MusicArtistXSongArrangement
    extra = 1


class MusicArtistXSongPerformanceInline(admin.TabularInline):
    form = forms.admin.MusicArtistXSongPerformanceForm
    model = models.MusicArtistXSongPerformance
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs.select_related('music_artist', 'song_performance')
            .order_by('music_artist__name')
        )


class MusicalInstrumentXPersonInline(admin.TabularInline):
    model = models.MusicalInstrumentXPerson


class PersonXSongPerformanceInline(admin.TabularInline):
    model = models.PersonXSongPerformance
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('person', 'song_performance__song_arrangement')


class SongArrangementInline(admin.TabularInline):
    model = models.SongArrangement
    extra = 1


class SongPerformanceInline(admin.TabularInline):
    model = models.SongPerformance
    extra = 1


class SongRecordingInline(admin.TabularInline):
    model = models.SongRecording
    extra = 1

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('song_performance__song_arrangement')


class SongXSongArrangementInline(admin.TabularInline):
    model = models.SongXSongArrangement
    extra = 1


class VideoGameAddonInline(admin.TabularInline):
    model = models.VideoGameAddon


class VideoGameEditionInline(admin.TabularInline):
    model = models.VideoGameEdition


class VideoGamePlatformRegionInline(admin.TabularInline):
    model = models.VideoGamePlatformRegion
    ordering = ('region',)


class VideoGameInline(admin.TabularInline):
    model = models.VideoGame
    ordering = ('title',)