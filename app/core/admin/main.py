from django.contrib import admin

from ..models import (
    author, beer, book, catalog_item, city, config, invoice,
    manufacturer, photo, txn,
)
from . import _inlines


admin.site.register(author.Author)


@admin.register(beer.Beer)
class BeerAdmin(admin.ModelAdmin):
    list_display = ('name', 'style', 'brewery',)
    list_select_related = ('brewery', 'style')
    ordering = ('name',)


@admin.register(beer.BeerStyle)
class BeerStyleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(beer.BeerXUser)
class BeerXUserAdmin(admin.ModelAdmin):
    list_display = ('_description', 'has_tried', 'approved')

    @staticmethod
    def _description(obj):
        return f'{obj.user}: {obj.beer.name}'


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
    list_display = ('_description',)
    list_select_related = ('book', 'motion_picture',)

    @staticmethod
    def _description(obj):
        return f'{obj.book.title} : {obj.motion_picture.title}'


admin.site.register(catalog_item.CatalogItem)
admin.site.register(catalog_item.CatalogItemMotionPictureRecording)

admin.site.register(city.USCity)

admin.site.register(config.Config)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(manufacturer.Manufacturer)


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
