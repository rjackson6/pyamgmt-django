from django.contrib import admin

from ..models import asset


@admin.register(asset.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('description', 'subtype')


@admin.register(asset.AssetDiscrete)
class AssetDiscrete(admin.ModelAdmin):
    list_display = ('admin_description', 'date_acquired', 'date_withdrawn')


@admin.register(asset.AssetDiscreteVehicle)
class AssetDiscreteVehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('asset_discrete__asset', 'vehicle')


admin.site.register(asset.AssetDiscreteXCatalogItem)
