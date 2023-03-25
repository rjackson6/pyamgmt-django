from django.contrib import admin

from .models import models


# Account and subtypes
admin.site.register(models.Account)
admin.site.register(models.AccountAsset)
admin.site.register(models.AccountAssetFinancial)
admin.site.register(models.AccountAssetReal)
# Asset and subtypes
admin.site.register(models.Asset)
admin.site.register(models.AssetDiscrete)
admin.site.register(models.AssetDiscreteCatalogItem)
admin.site.register(models.AssetDiscreteVehicle)

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
