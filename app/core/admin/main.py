from django.contrib import admin

from ..models import (
    author, beer, book, catalog_item, city, config, invoice,
    manufacturer, motion_picture, photo, txn, vehicle, video_game,
)
from . import _inlines


admin.site.register(author.Author)

admin.site.register(beer.Beer)


@admin.register(beer.BeerStyle)
class BeerStyleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(beer.Brewery)
class BreweryAdmin(admin.ModelAdmin):
    ordering = ('name',)


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

admin.site.register(city.USCity)

admin.site.register(config.Config)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(manufacturer.Manufacturer)


@admin.register(motion_picture.MotionPicture)
class MotionPictureAdmin(admin.ModelAdmin):
    inlines = [_inlines.MotionPictureXMusicAlbumInline]
    ordering = ('title', 'year_produced')


admin.site.register(motion_picture.MotionPictureRecording)
admin.site.register(motion_picture.MotionPictureSeries)


@admin.register(motion_picture.MotionPictureXMusicAlbum)
class MotionPictureXMusicAlbumAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('motion_picture', 'music_album')


admin.site.register(motion_picture.MotionPictureXSong)

admin.site.register(photo.Photo)

admin.site.register(txn.Txn)


@admin.register(txn.TxnLineItem)
class TxnLineItemAdmin(admin.ModelAdmin):
    list_display = ('_txn_date', '_account', 'debit', '_debit_sign', 'amount')
    list_display_links = ('_account',)
    ordering = ('-txn__txn_date',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .select_related('account', 'txn')
        )

    @staticmethod
    def _account(obj):
        return obj.account.name

    @staticmethod
    def _debit_sign(obj) -> str:
        polarity = obj.polarity()
        if polarity == 1:
            return '+'
        elif polarity == -1:
            return '-'

    @staticmethod
    def _txn_date(obj):
        return obj.txn.txn_date


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
        _inlines.VideoGameEditionInline,
        _inlines.VideoGameAddonInline,
        _inlines.MusicAlbumXVideoGameInline,
    ]
    list_display = ('title', 'series')
    ordering = ('title',)


@admin.register(video_game.VideoGameAddon)
class VideoGameAddonAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'release_date')
    list_select_related = ('video_game',)


@admin.register(video_game.VideoGameEdition)
class VideoGameEditionAdmin(admin.ModelAdmin):
    inlines = [_inlines.VideoGameEditionXVideoGamePlatformInline]
    list_display = ('admin_description',)
    list_select_related = ('video_game',)


@admin.register(video_game.VideoGamePlatform)
class VideoGamePlatformAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.VideoGamePlatformRegionInline,
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
        _inlines.VideoGameInline,
    ]
    ordering = ('name',)
