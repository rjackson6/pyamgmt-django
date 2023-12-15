from django.contrib import admin

from .models import (
    account, asset, catalog_item, invoice, models, motion_picture, music_album,
    music_artist, txn, vehicle, video_game,
)


# Account and subtypes
admin.site.register(account.Account)
admin.site.register(account.AccountAsset)
admin.site.register(account.AccountAssetFinancial)
admin.site.register(account.AccountAssetReal)
# Asset and subtypes
admin.site.register(asset.Asset)
admin.site.register(asset.AssetDiscrete)
admin.site.register(asset.AssetDiscreteCatalogItem)
admin.site.register(asset.AssetDiscreteVehicle)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(motion_picture.MotionPicture)
admin.site.register(music_album.MusicAlbum)
admin.site.register(music_album.MusicAlbumArtwork)
admin.site.register(music_artist.MusicArtist)

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
admin.site.register(video_game.VideoGamePlatform)
