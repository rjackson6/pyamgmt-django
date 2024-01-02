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
    inlines = [
        _inlines.MotionPictureXPersonInline,
        _inlines.MotionPictureXMusicAlbumInline,
    ]
    ordering = ('title', 'year_produced')


admin.site.register(motion_picture.MotionPictureRecording)
admin.site.register(motion_picture.MotionPictureSeries)


@admin.register(motion_picture.MotionPictureXMusicAlbum)
class MotionPictureXMusicAlbumAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('motion_picture', 'music_album')


admin.site.register(motion_picture.MotionPictureXSong)


@admin.register(photo.Photo)
class PhotoAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.PersonXPhotoInline,
    ]


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
