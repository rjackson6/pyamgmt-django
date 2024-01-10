from django.contrib import admin

from .. import forms
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


@admin.register(account.AccountAssetFinancial)
class AccountAssetFinancialAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('account_asset__account',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account_asset.account.name


@admin.register(account.AccountAssetReal)
class AccountAssetRealAdmin(admin.ModelAdmin):
    form = forms.admin.AccountAssetRealForm
    list_display = ('_description',)
    list_select_related = ('account_asset__account',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account_asset.account.name


@admin.register(account.AccountAssetRealXAssetDiscrete)
class AccountAssetRealXAssetDiscreteAdmin(admin.ModelAdmin):
    form = forms.admin.AccountAssetRealXAssetDiscreteForm
    list_display = ('_description',)
    list_select_related = (
        'account_asset_real__account_asset__account',
        'asset_discrete__asset',
    )

    @staticmethod
    def _description(obj) -> str:
        return (
            f'{obj.account_asset_real.account_asset.account.name}'
            f' : {obj.asset_discrete.asset.description}'
        )


admin.site.register(account.AccountEquity)


@admin.register(account.AccountExpense)
class AccountExpenseAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('account',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account.name


@admin.register(account.AccountIncome)
class AccountIncomeAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('account',)

    @staticmethod
    def _description(obj) -> str:
        return obj.account.name


admin.site.register(account.AccountLiability)
admin.site.register(account.AccountLiabilitySecured)
