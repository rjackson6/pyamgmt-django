from django.contrib import admin

from ..forms.admin import AssetForm, AssetDiscreteXCatalogItemForm
from ..models import asset


@admin.register(asset.Asset)
class AssetAdmin(admin.ModelAdmin):
    form = AssetForm
    list_display = ('description', 'subtype')


@admin.register(asset.AssetDiscrete)
class AssetDiscrete(admin.ModelAdmin):
    list_display = ('_description', 'date_acquired', 'date_withdrawn')
    list_select_related = ('asset',)

    @staticmethod
    def _description(obj) -> str:
        return obj.asset.description


@admin.register(asset.AssetDiscreteVehicle)
class AssetDiscreteVehicleAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('asset_discrete__asset', 'vehicle')

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.asset_discrete.asset.description}'
            f' : {obj.vehicle.vin}'
        )


@admin.register(asset.AssetDiscreteXCatalogItem)
class AssetDiscreteXCatalogItemAdmin(admin.ModelAdmin):
    form = AssetDiscreteXCatalogItemForm
    list_display = ('_description',)
    list_select_related = ('asset_discrete__asset',)

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.asset_discrete.asset.description}'
            f' : {obj.catalog_item}'
        )


@admin.register(asset.AssetInventory)
class AssetInventoryAdmin(admin.ModelAdmin):
    list_display = ('_description', 'catalog_item', 'quantity',)
    list_select_related = ('asset', 'catalog_item')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.asset.description}'
