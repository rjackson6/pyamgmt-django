from django.contrib import admin

from ..models import account


@admin.register(account.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_account', 'subtype')
    list_select_related = ('parent_account',)
    ordering = ('name',)


@admin.register(account.AccountAsset)
class AccountAssetAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'subtype')
    list_select_related = ('account',)


admin.site.register(account.AccountAssetFinancial)


@admin.register(account.AccountAssetReal)
class AccountAssetRealAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
