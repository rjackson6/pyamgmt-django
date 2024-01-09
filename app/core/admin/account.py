from django.contrib import admin

from ..models import account


@admin.register(account.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_account', 'subtype')
    list_select_related = ('parent_account',)
    ordering = ('name',)


@admin.register(account.AccountAsset)
class AccountAssetAdmin(admin.ModelAdmin):
    list_display = ('_description', 'subtype')
    list_select_related = ('account',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account.name


admin.site.register(account.AccountAssetFinancial)


@admin.register(account.AccountAssetReal)
class AccountAssetRealAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('account_asset__acount',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account_asset.account.name
