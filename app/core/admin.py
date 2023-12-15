from django.contrib import admin

from .models import (
    account, asset, catalog_item, invoice, models, motion_picture, music_album,
    music_artist, song, txn, vehicle, video_game,
)


@admin.register(account.Account)
class AccountAdmin(admin.ModelAdmin):
    ordering = ('name',)


admin.site.register(account.AccountAsset)
admin.site.register(account.AccountAssetFinancial)
admin.site.register(account.AccountAssetReal)

admin.site.register(asset.Asset)
admin.site.register(asset.AssetDiscrete)
admin.site.register(asset.AssetDiscreteCatalogItem)
admin.site.register(asset.AssetDiscreteVehicle)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(motion_picture.MotionPicture)


@admin.register(music_album.MusicAlbum)
class MusicAlbumAdmin(admin.ModelAdmin):
    ordering = ('title',)


admin.site.register(music_album.MusicAlbumArtwork)

admin.site.register(music_artist.MusicArtist)

admin.site.register(song.Song)
admin.site.register(song.SongRecording)
admin.site.register(song.SongXSong)

admin.site.register(txn.Txn)
admin.site.register(txn.TxnLineItem)

admin.site.register(vehicle.Vehicle)
admin.site.register(vehicle.VehicleMake)
admin.site.register(vehicle.VehicleMileage)
admin.site.register(vehicle.VehicleModel)
admin.site.register(vehicle.VehicleService)
admin.site.register(vehicle.VehicleServiceItem)
admin.site.register(vehicle.VehicleTrim)
admin.site.register(vehicle.VehicleYear)

admin.site.register(video_game.VideoGame)
admin.site.register(video_game.VideoGameAddon)
admin.site.register(video_game.VideoGameEdition)
admin.site.register(video_game.VideoGamePlatform)
admin.site.register(video_game.VideoGameSeries)
