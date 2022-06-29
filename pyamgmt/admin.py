from django.contrib import admin

from pyamgmt import models


# Register your models here.
admin.site.register(models.Account)

admin.site.register(models.AccountAsset)
admin.site.register(models.AccountAssetFinancial)
admin.site.register(models.AccountAssetReal)

admin.site.register(models.Asset)
admin.site.register(models.AssetDiscrete)
admin.site.register(models.AssetDiscreteCatalogItem)
admin.site.register(models.AssetDiscreteVehicle)

admin.site.register(models.MusicAlbum)
admin.site.register(models.MusicAlbumArtwork)

admin.site.register(models.Vehicle)
admin.site.register(models.VehicleMileage)
