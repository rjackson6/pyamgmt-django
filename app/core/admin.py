from django.contrib import admin

from .models import account, asset, catalog_item, models


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

admin.site.register(models.Invoice)
admin.site.register(models.InvoiceLineItem)

admin.site.register(models.MotionPicture)
admin.site.register(models.MusicAlbum)
admin.site.register(models.MusicAlbumArtwork)
admin.site.register(models.MusicArtist)

admin.site.register(models.Txn)
admin.site.register(models.TxnLineItem)

admin.site.register(models.Vehicle)
admin.site.register(models.VehicleMake)
admin.site.register(models.VehicleMileage)
admin.site.register(models.VehicleModel)
admin.site.register(models.VehicleService)
admin.site.register(models.VehicleServiceItem)
admin.site.register(models.VehicleTrim)
admin.site.register(models.VehicleYear)
admin.site.register(models.VideoGame)
admin.site.register(models.VideoGamePlatform)
