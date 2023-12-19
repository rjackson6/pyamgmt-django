from django.contrib import admin

from core import forms
from .models import (
    account, asset, author, book, catalog_item, invoice, manufacturer,
    motion_picture, music_album, music_artist, person, song, txn, vehicle,
    video_game,
)


#########
# Inlines
#########
class MusicAlbumEditionInline(admin.TabularInline):
    model = music_album.MusicAlbumEdition


class MusicAlbumEditionXSongRecordingInline(admin.TabularInline):
    form = forms.admin.MusicAlbumEditionXSongRecordingForm
    model = music_album.MusicAlbumEditionXSongRecording


class MusicAlbumXMusicArtistInline(admin.TabularInline):
    model = music_album.MusicAlbumXMusicArtist


class MusicArtistXPersonInline(admin.TabularInline):
    model = music_artist.MusicArtistXPerson


class MusicArtistXSongRecordingInline(admin.TabularInline):
    form = forms.admin.MusicArtistXSongRecordingForm
    model = music_artist.MusicArtistXSongRecording


class SongRecordingInline(admin.TabularInline):
    model = song.SongRecording


class VideoGameAddonInline(admin.TabularInline):
    model = video_game.VideoGameAddon


class VideoGameEditionInline(admin.TabularInline):
    model = video_game.VideoGameEdition


class VideoGamePlatformRegionInline(admin.TabularInline):
    model = video_game.VideoGamePlatformRegion
    ordering = ('region',)


class VideoGameInline(admin.TabularInline):
    model = video_game.VideoGame
    ordering = ('title',)


###############
# Admin classes
###############
@admin.register(account.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_account', 'subtype')
    list_select_related = ('parent_account',)
    ordering = ('name',)


@admin.register(account.AccountAsset)
class AccountAssetAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'subtype')
    list_select_related = ('account',)


admin.site.register(account.AccountAssetFinancial)


@admin.register(account.AccountAssetReal)
class AccountAssetRealAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)


@admin.register(asset.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('description', 'subtype')


@admin.register(asset.AssetDiscrete)
class AssetDiscrete(admin.ModelAdmin):
    list_display = ('admin_description', 'date_acquired', 'date_withdrawn')


admin.site.register(asset.AssetDiscreteCatalogItem)


@admin.register(asset.AssetDiscreteVehicle)
class AssetDiscreteVehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('asset_discrete__asset', 'vehicle')


admin.site.register(author.Author)

admin.site.register(book.Book)


@admin.register(book.BookEdition)
class BookEditionAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('book',)


admin.site.register(book.BookSeries)


@admin.register(book.BookXMotionPicture)
class BookXMotionPictureAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('book', 'motion_picture',)


admin.site.register(catalog_item.CatalogItem)
admin.site.register(catalog_item.CatalogItemMotionPictureRecording)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(manufacturer.Manufacturer)


@admin.register(motion_picture.MotionPicture)
class MotionPictureAdmin(admin.ModelAdmin):
    ordering = ('title', 'year_produced')


admin.site.register(motion_picture.MotionPictureRecording)
admin.site.register(motion_picture.MotionPictureSeries)


@admin.register(motion_picture.MotionPictureXMusicAlbum)
class MotionPictureXMusicAlbumAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('motion_picture', 'music_album')


admin.site.register(motion_picture.MotionPictureXSong)


@admin.register(music_album.MusicAlbum)
class MusicAlbumAdmin(admin.ModelAdmin):
    inlines = [
        MusicAlbumEditionInline,
        MusicAlbumXMusicArtistInline,
    ]
    list_display = ('title', 'year_produced', 'is_compilation')
    ordering = ('title',)
    search_fields = ('title',)


admin.site.register(music_album.MusicAlbumArtwork)


@admin.register(music_album.MusicAlbumEdition)
class MusicAlbumEditionAdmin(admin.ModelAdmin):
    inlines = [MusicAlbumEditionXSongRecordingInline]
    list_display = ('admin_description',)
    list_select_related = ('music_album',)
    ordering = ('music_album__title', 'name')


@admin.register(music_album.MusicAlbumXMusicArtist)
class MusicAlbumXMusicArtistAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'music_artist')
    ordering = ('music_artist__name', 'music_album__title')


@admin.register(music_album.MusicAlbumXVideoGame)
class MusicAlbumXVideoGameAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'video_game')


@admin.register(music_artist.MusicArtist)
class MusicArtistAdmin(admin.ModelAdmin):
    inlines = [
        MusicAlbumXMusicArtistInline,
        MusicArtistXPersonInline,
    ]
    list_display = ('name', 'website')
    ordering = ('name',)
    search_fields = ('name',)


@admin.register(music_artist.MusicArtistActivity)
class MusicArtistActivityAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_artist',)
    ordering = ('music_artist__name', 'year_active', 'year_inactive')


@admin.register(music_artist.MusicArtistXPerson)
class MusicArtistXPersonAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_artist', 'person')
    ordering = ('music_artist__name', 'person__first_name')


@admin.register(music_artist.MusicArtistXPersonActivity)
class MusicArtistXPersonActivityAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist_x_person__music_artist',
        'music_artist_x_person__person'
    )


@admin.register(music_artist.MusicArtistXSongRecording)
class MusicArtistXSongRecordingAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXSongRecordingForm
    list_display = ('admin_description',)
    list_select_related = ('music_artist', 'song_recording__song')


@admin.register(person.Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'is_living', 'date_of_birth', 'date_of_death', 'age',
        'notes',
    )
    ordering = ('last_name', 'first_name')
    search_fields = ('first_name', 'last_name')


@admin.register(song.Song)
class SongAdmin(admin.ModelAdmin):
    inlines = [
        SongRecordingInline
    ]
    ordering = ('title',)


@admin.register(song.SongRecording)
class SongRecordingAdmin(admin.ModelAdmin):
    inlines = [
        MusicAlbumEditionXSongRecordingInline,
        MusicArtistXSongRecordingInline,
    ]
    list_display = (
        'admin_description', 'recording_type',
    )
    list_select_related = ('song',)
    ordering = ('song__title',)


admin.site.register(song.SongXSong)

admin.site.register(txn.Txn)
admin.site.register(txn.TxnLineItem)


@admin.register(vehicle.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make',
    )
    ordering = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make__name',
        'vehicle_year__vehicle_trim__vehicle_model__name',
        'vehicle_year__vehicle_trim__name',
        'vehicle_year',
        'vin'
    )


admin.site.register(vehicle.VehicleMake)
admin.site.register(vehicle.VehicleMileage)
admin.site.register(vehicle.VehicleModel)
admin.site.register(vehicle.VehicleService)
admin.site.register(vehicle.VehicleServiceItem)
admin.site.register(vehicle.VehicleTrim)
admin.site.register(vehicle.VehicleYear)


@admin.register(video_game.VideoGame)
class VideoGameAdmin(admin.ModelAdmin):
    inlines = [
        VideoGameEditionInline,
        VideoGameAddonInline,
    ]
    ordering = ('title',)


@admin.register(video_game.VideoGameAddon)
class VideoGameAddonAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'release_date')
    list_select_related = ('video_game',)


admin.site.register(video_game.VideoGameEdition)


@admin.register(video_game.VideoGamePlatform)
class VideoGamePlatformAdmin(admin.ModelAdmin):
    inlines = [
        VideoGamePlatformRegionInline,
    ]
    ordering = ('name',)


@admin.register(video_game.VideoGamePlatformEdition)
class VideoGamePlatformEditionAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    ordering = ('video_game_platform__name', 'name')


@admin.register(video_game.VideoGamePlatformRegion)
class VideoGamePlatformRegionAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'release_date')
    list_select_related = ('video_game_platform',)
    ordering = ('video_game_platform__name', 'region')


@admin.register(video_game.VideoGameSeries)
class VideoGameSeriesAdmin(admin.ModelAdmin):
    inlines = [
        VideoGameInline,
    ]
    ordering = ('name',)
