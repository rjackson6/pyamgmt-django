import datetime
import logging

import requests

from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Case, Count, F, Prefetch, Q, Sum, Value, When
from django.http import HttpResponse  # HttpResponseRedirect
from django.shortcuts import render, redirect
# from django.utils.decorators import method_decorator
# from django.views.decorators.http import require_http_methods

from core.views.base import FormView, MultiFormView, View
from pyamgmt.forms import *
from pyamgmt.models import *

logger = logging.getLogger(__name__)


# V2 notes
# paginate lists as a rule; never as a full result list
#  returning thousands of rows is not sane.
#  search, filter, and paginate is what needs to be built by default
# breadcrumbs
#  defaults can be simplified with includes and attributes, so long as the
#  conventions match. Home -> List -> Detail -> Edit...

class AccountListView(View):
    def get(self, request, **_kwargs):
        q_debits = Sum('txnlineitem__amount', filter=Q(txnlineitem__debit=True))
        q_credits = Sum('txnlineitem__amount', filter=Q(txnlineitem__debit=False))
        qs_account = (
            Account.objects
            .annotate(debits=q_debits)
            .annotate(credits=q_credits)
            .order_by('name'))
        paginator = Paginator(qs_account, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        self.context.update({'qs_account': qs_account, 'page_obj': page_obj})
        return render(request, 'pyamgmt/models/account_list.html', self.context)


class AccountDetailView(View):
    def get(self, request, account_pk: int, **_kwargs):
        account = (
            Account.objects
            .prefetch_related('txnlineitem_set__txn__payee')
            .get(pk=account_pk)
        )
        self.context.update({'account': account})
        return render(request, 'pyamgmt/models/account_detail.html', self.context)


class AccountFormView(FormView):
    def setup(self, request, account_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        if account_pk:
            account = Account.objects.get(pk=account_pk)
        self.form = AccountForm(request.POST or None, instance=account)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/account_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            account = self.form.save()
            if account.subtype == Account.Subtype.ASSET:
                account_asset, _ = AccountAsset.objects.get_or_create(account=account)
            return redirect('pyamgmt:account:list')
        return self.render(request)


class AccountAssetListView(View):
    def get(self, request, **_kwargs):
        qs_accountasset = AccountAsset.objects.select_related('account')
        self.context.update({'qs_accountasset': qs_accountasset})
        return render(request, 'pyamgmt/models/accountasset_list.html', self.context)


class AccountAssetDetailView(View):
    def get(self, request, accountasset_pk: int = None, **_kwargs):
        accountasset = AccountAsset.objects.get(pk=accountasset_pk)
        self.context.update({
            'accountasset': accountasset
        })
        return render(request, 'pyamgmt/models/accountasset_detail.html', self.context)


class AccountAssetFormView(MultiFormView):
    def setup(self, request, accountasset_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        accountasset = None
        if accountasset_pk:
            accountasset = AccountAsset.objects.get(pk=accountasset_pk)
            account = accountasset.account
        self.forms.account = AccountForm(request.POST or None, instance=account)
        self.forms.accountasset = AccountAssetForm(request.POST or None, instance=accountasset)

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, 'pyamgmt/models/accountasset_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountasset = self.forms.accountasset.save(commit=False)
            accountasset.account = account
            accountasset.save()
            match accountasset.subtype:
                case AccountAsset.Subtype.FINANCIAL:
                    accountassetfinancial, _ = AccountAssetFinancial.objects.get_or_create(accountasset=accountasset)
                case AccountAsset.Subtype.REAL:
                    accountassetreal, _ = AccountAssetReal.objects.get_or_create(accountasset=accountasset)
            return redirect('pyamgmt:accountasset:list')
        return self.render(request)


class AccountAssetFinancialListView(View):
    def get(self, request, **_kwargs):
        qs_accountassetfinancial = (
            AccountAssetFinancial.objects
            .select_related('accountasset__account'))
        self.context.update({'qs_accountassetfinancial': qs_accountassetfinancial})
        return render(request, 'pyamgmt/models/accountassetfinancial_list.html', self.context)


class AccountAssetFinancialDetailView(View):
    def get(self, request, accountassetfinancial_pk: int, **_kwargs):
        accountassetfinancial = (
            AccountAssetFinancial.objects
            .select_related('accountasset__account')
            .get(pk=accountassetfinancial_pk))
        qs_txnlineitem = (
            TxnLineItem.objects
            .filter(account_id=accountassetfinancial_pk)
            .select_related('txn')
            .order_by('-txn__txn_date'))
        self.context.update({
            'accountassetfinancial': accountassetfinancial,
            'qs_txnlineitem': qs_txnlineitem
        })
        return render(request, 'pyamgmt/models/accountassetfinancial_detail.html', self.context)


class AccountAssetFinancialFormView(MultiFormView):
    def setup(self, request, accountassetfinancial_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        accountassetfinanancial = None
        accountasset = None
        account = None
        if accountassetfinancial_pk:
            accountassetfinanancial = AccountAssetFinancial.objects.get(pk=accountassetfinancial_pk)
            accountasset = accountassetfinanancial.accountasset
            account = accountasset.account
        self.forms.accountassetfinancial = AccountAssetFinancialForm(
            request.POST or None, instance=accountassetfinanancial)
        # initial={'subtype': AccountAsset.Subtype.FINANCIAL}
        self.forms.accountasset = AccountAssetForm(request.POST or None, instance=accountasset)
        # initial={'subtype': AccountAsset.Subtype.FINANCIAL}
        # form_accountasset.fields['subtype'].disabled = True
        self.forms.account = AccountForm(request.POST or None, instance=account)
        # form_account.fields['subtype'].disabled = True
        # initial={'subtype': Account.Subtype.ASSET}
        # form_account.fields['parent_account'].queryset = (
        #         form_account.fields['parent_account'].queryset.filter(
        #             accountasset__subtype=AccountAsset.Subtype.FINANCIAL)
        #     )

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, 'pyamgmt/models/accountassetfinancial_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountasset = self.forms.accountasset.save(commit=False)
            accountasset.account = account
            accountasset.save()
            accountassetfinancial = self.forms.accountassetfinancial.save(commit=False)
            accountassetfinancial.accountasset = accountasset
            accountassetfinancial.save()
            return redirect('pyamgmt:home')
        return self.render(request)


class AccountAssetRealListView(View):
    def get(self, request, **_kwargs):
        qs_accountassetreal = (
            AccountAssetReal.objects
            .select_related('accountasset__account')
        )
        self.context.update({'qs_accountassetreal': qs_accountassetreal})
        return render(request, 'pyamgmt/models/accountassetreal_list.html', self.context)


class AccountAssetRealDetailView(View):
    def get(self, request, accountassetreal_pk: int, **_kwargs):
        accountassetreal = AccountAssetReal.objects.get(pk=accountassetreal_pk)
        self.context.update({
            'accountassetreal': accountassetreal
        })
        return render(request, 'pyamgmt/models/accountassetreal_detail.html', self.context)


class AccountAssetRealFormView(MultiFormView):
    def setup(self, request, accountassetreal_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        accountasset = None
        accountassetreal = None
        if accountassetreal_pk:
            accountassetreal = AccountAssetReal.objects.get(pk=accountassetreal_pk)
            accountasset = accountassetreal.accountasset
            account = accountasset.account
        self.forms.account = AccountForm(request.POST or None, instance=account)
        self.forms.accountasset = AccountAssetForm(request.POST or None, instance=accountasset)
        self.forms.accountassetreal = AccountAssetRealForm(request.POST or None, instance=accountassetreal)
        # form_account.fields['parent_account'].queryset = (
        #         form_account.fields['parent_account'].queryset.filter(accountasset__subtype=AccountAsset.Subtype.REAL)
        #     )
        # initial={'subtype': Account.Subtype.ASSET}
        # initial={'subtype': AccountAsset.Subtype.REAL}
        # form_accountasset.fields['subtype'].disabled = True

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, 'pyamgmt/models/accountassetreal_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountasset = self.forms.accountasset.save(commit=False)
            accountasset.account = account
            accountasset.save()
            accountassetreal = self.forms.accountassetreal.save(commit=False)
            accountassetreal.accountasset = accountasset
            accountassetreal.save()
            return redirect('pyamgmt:accountassetreal:list')
        return self.render(request)


class AccountExpenseListView(View):
    def get(self, request, **_kwargs):
        qs_accountexpense = AccountExpense.objects.select_related('account').order_by('account__name').all()
        self.context.update({'qs_accountexpense': qs_accountexpense})
        return render(request, 'pyamgmt/models/accountexpense_list.html', self.context)


class AccountExpenseDetailView(View):
    def get(self, request, accountexpense_pk: int, **_kwargs):
        accountexpense = AccountExpense.objects.get(pk=accountexpense_pk)
        self.context.update({
            'accountexpense': accountexpense
        })
        return render(request, 'pyamgmt/models/accountexpense_detail.html', self.context)


class AccountExpenseFormView(MultiFormView):
    def setup(self, request, accountexpense_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        accountexpense = None
        if accountexpense_pk:
            accountexpense = AccountExpense.objects.get(pk=accountexpense_pk)
            account = accountexpense.account
        self.forms.account = AccountForm(request.POST or None, instance=account)
        self.forms.accountexpense = AccountExpenseForm(request.POST or None, instance=accountexpense)

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, 'pyamgmt/models/accountexpense_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountexpense = self.forms.accountexpense.save(commit=False)
            accountexpense.account = account
            accountexpense.save()
            return redirect('pyamgmt:accountexpense:detail', accountexpense=accountexpense.pk)
        return self.render(request)


class AccountIncomeListView(View):
    def get(self, request, **_kwargs):
        qs_accountincome = AccountIncome.objects.select_related('account')
        self.context.update({'qs_accountincome': qs_accountincome})
        return render(request, 'pyamgmt/models/accountincome_list.html', self.context)


class AccountIncomeDetailView(View):
    def get(self, request, accountincome_pk: int, **_kwargs):
        accountincome = AccountIncome.objects.select_related('account').get(pk=accountincome_pk)
        qs_txnlineitem = (
            TxnLineItem.objects
            .filter(account_id=accountincome.pk)
            .select_related('txn')
            .order_by('-txn__txn_date')
        )
        self.context.update({
            'accountincome': accountincome,
            'qs_txnlineitem': qs_txnlineitem
        })
        return render(request, 'pyamgmt/models/accountincome_detail.html', self.context)


class AccountIncomeFormView(MultiFormView):
    def setup(self, request, accountincome_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        accountincome = None
        if accountincome_pk:
            accountincome = AccountIncome.objects.get(pk=accountincome_pk)
            account = accountincome.account
        self.forms.account = AccountForm(request.POST or None, instance=account)
        self.forms.accountincome = AccountIncomeForm(request.POST or None, instance=accountincome)

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, '', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountincome = self.forms.accountincome.save(commit=False)
            accountincome.account = account
            accountincome.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render(request)


class AccountLiabilityListView(View):
    def get(self, request, **_kwargs):
        qs_accountliability = AccountLiability.objects.select_related('account')
        self.context.update({'qs_accountliability': qs_accountliability})
        return render(request, 'pyamgmt/models/accountliability_list.html', self.context)


class AccountLiabilityDetailView(View):
    def get(self, request, accountliability_pk: int, **_kwargs):
        accountliability = AccountLiability.objects.select_related('account').get(pk=accountliability_pk)
        self.context.update({
            'accountliability': accountliability
        })
        return render(request, 'pyamgmt/models/accountliability_detail.html', self.context)


class AccountLiabilityFormView(MultiFormView):
    def setup(self, request, accountliability_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        account = None
        accountliability = None
        if accountliability_pk:
            accountliability = AccountLiability.objects.get(pk=accountliability_pk)
            account = accountliability.account
        self.forms.account = AccountForm(request.POST or None, instance=account)
        self.forms.accountliability = AccountLiabilityForm(request.POST or None, instance=accountliability)

    def render(self, request):
        self.context.update({'forms': forms})
        return render(request, '', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            account = self.forms.account.save()
            accountliability = self.forms.accountliability.save(commit=False)
            accountliability.account = account
            accountliability.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render(request)


class AssetListView(View):
    def get(self, request, **_kwargs):
        qs_asset = Asset.objects.all()
        self.context.update({'qs_asset': qs_asset})
        return render(request, 'pyamgmt/models/asset_list.html', self.context)


class AssetDetailView(View):
    def get(self, request, asset_pk: int, **_kwargs):
        asset = Asset.objects.get(pk=asset_pk)
        self.context.update({
            'asset': asset
        })
        return render(request, 'pyamgmt/models/asset_detail.html', self.context)


class AssetFormView(FormView):
    def setup(self, request, asset_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        asset = None
        if asset_pk:
            asset = Asset.objects.get(pk=asset_pk)
        self.form = AssetForm(request.POST or None, instance=asset)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/asset_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render(request)


class AssetDiscreteListView(View):
    def get(self, request, **_kwargs):
        qs_assetdiscrete = AssetDiscrete.objects.select_related('asset')
        self.context.update({
            'qs_assetdiscrete': qs_assetdiscrete
        })
        return render(request, 'pyamgmt/models/assetdiscrete_list.html', self.context)


class AssetDiscreteDetailView(View):
    def get(self, request, assetdiscrete_pk: int, **_kwargs):
        assetdiscrete = AssetDiscrete.objects.get(pk=assetdiscrete_pk)
        self.context.update({
            'assetdiscrete': assetdiscrete
        })
        return render(request, 'pyamgmt/models/assetdiscrete_detail.html', self.context)


class AssetDiscreteCatalogItemListView(View):
    pass


class AssetDiscreteCatalogItemDetailView(View):
    def get(self, request, assetdiscretecatalogitem_pk: int, **_kwargs):
        assetdiscretecatalogitem = AssetDiscreteCatalogItem.objects.get(pk=assetdiscretecatalogitem_pk)
        self.context.update({
            'assetdiscretecatalogitem': assetdiscretecatalogitem
        })
        return render(request, 'pyamgmt/models/assetdiscretecatalogitem_detail.html', self.context)


class AssetDiscreteVehicleListView(View):
    def get(self, request, **_kwargs):
        qs_assetdiscretevehicle = (
            AssetDiscreteVehicle.objects
            .select_related('assetdiscrete__asset', 'vehicle')
            .order_by('assetdiscrete__date_withdrawn', '-vehicle__vehicleyear__year')
        )
        self.context.update({'qs_assetdiscretevehicle': qs_assetdiscretevehicle})
        return render(request, 'pyamgmt/models/assetdiscretevehicle_list.html', self.context)


class AssetDiscreteVehicleDetailView(View):
    def get(self, request, assetdiscretevehicle_pk: int, **_kwargs):
        assetdiscretevehicle = (
            AssetDiscreteVehicle.objects
            .select_related(
                'assetdiscrete',
                'vehicle__vehicleyear__vehicletrim__vehiclemodel__vehiclemake')
            .get(pk=assetdiscretevehicle_pk)
        )
        self.context.update({
            'assetdiscretevehicle': assetdiscretevehicle
        })
        return render(request, 'pyamgmt/models/assetdiscretevehicle_detail.html', self.context)


class AssetDiscreteVehicleFormView(MultiFormView):
    def setup(self, request, assetdiscretevehicle_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        asset = None
        assetdiscrete = None
        assetdiscretevehicle = None
        if assetdiscretevehicle_pk:
            assetdiscretevehicle = AssetDiscreteVehicle.objects.get(pk=assetdiscretevehicle_pk)
            assetdiscrete = assetdiscretevehicle.assetdiscrete
            asset = assetdiscrete.asset
        self.forms.asset = AssetForm(request.POST or None, instance=asset, subtype=Asset.Subtype.DISCRETE)
        self.forms.assetdiscrete = AssetDiscreteForm(
            request.POST or None, instance=assetdiscrete, subtype=AssetDiscrete.Subtype.VEHICLE
        )
        self.forms.assetdiscretevehicle = AssetDiscreteVehicleForm(request.POST or None, instance=assetdiscretevehicle)

    def render(self, request):
        self.context.update({'forms': self.forms})
        return render(request, 'pyamgmt/models/assetdiscretevehicle_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    @transaction.atomic
    def post(self, request, **_kwargs):
        if self.forms.are_valid():
            asset = self.forms.asset.save()
            assetdiscrete = self.forms.assetdiscrete.save(commit=False)
            assetdiscrete.asset = asset
            assetdiscrete.save()
            assetdiscretevehicle = self.forms.assetdiscretevehicle.save(commit=False)
            assetdiscretevehicle.assetdiscrete = assetdiscrete
            assetdiscretevehicle.save()
            return redirect('pyamgmt:assetdiscretevehicle:detail', assetdiscretevehicle_pk=assetdiscretevehicle.pk)
        return self.render(request)


class AssetInventoryListView(View):
    def get(self, request, **_kwargs):
        qs_assetinventory = AssetInventory.objects.select_related('asset')
        self.context.update({'qs_assetinventory': qs_assetinventory})
        return render(request, 'pyamgmt/models/assetinventory_list.html', self.context)


class AssetInventoryDetailView(View):
    def get(self, request, assetinventory_pk: int, **kwargs):
        assetinventory = AssetInventory.objects.get(pk=assetinventory_pk)
        self.context.update({
            'assetinventory': assetinventory
        })
        return render(request, 'pyamgmt/models/assetinventory_detail.html', self.context)


class CatalogItemListView(View):
    def get(self, request, **_kwargs):
        qs_catalogitem = CatalogItem.objects.all()
        self.context.update({'qs_catalogitem': qs_catalogitem})
        return render(request, 'pyamgmt/models/catalogitem_list.html', self.context)


class CatalogItemDetailView(View):
    def get(self, request, catalogitem_pk: int, **kwargs):
        catalogitem = CatalogItem.objects.get(pk=catalogitem_pk)
        self.context.update({
            'catalogitem': catalogitem
        })
        return render(request, 'pyamgmt/models/catalogitem_detail.html', self.context)


class CatalogItemFormView(FormView):
    def setup(self, request, catalogitem_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        catalogitem = None
        if catalogitem_pk:
            catalogitem = CatalogItem.objects.get(pk=catalogitem_pk)
        self.form = CatalogItemForm(request.POST or None, instance=catalogitem)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/catalogitem_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:catalogitem:list')
        return self.render(request)


class CatalogItemDigitalSongListView(View):
    def get(self, request, **_kwargs):
        qs_catalogitemdigitalsong = CatalogItemDigitalSong.objects.all()
        self.context.update({'qs_catalogitemdigitalsong': qs_catalogitemdigitalsong})
        return render(request, 'pyamgmt/models/catalogitemdigitalsong_list.html', self.context)


class CatalogItemDigitalSongDetailView(View):
    def get(self, request, catalogitemdigitalsong_pk: int, **_kwargs):
        catalogitemdigitalsong = CatalogItemDigitalSong.objects.get(pk=catalogitemdigitalsong_pk)
        self.context.update({'catalogitemdigitalsong': catalogitemdigitalsong})
        return render(request, 'pyamgmt/models/catalogitemdigitalsong_detail.html', self.context)


class CatalogItemDigitalSongFormView(FormView):
    pass


@transaction.atomic
def catalogitemdigitalsong_form(request, catalogitemdigitalsong_pk: int = None):
    context = {}
    instance = None
    if catalogitemdigitalsong_pk:
        instance = CatalogItemDigitalSong.objects.get(pk=catalogitemdigitalsong_pk)
    form = CatalogItemDigitalSongForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('pyamgmt:catalogitemdigitalsong:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/catalogitemdigitalsong_form.html', context)


def catalogitemmusicalbum_list(request):
    """List all records from model CatalogItemMusicAlbum."""
    context = {}
    qs_catalogitemmusicalbum = CatalogItemMusicAlbum.objects.all()
    context.update({'qs_catalogitemmusicalbum': qs_catalogitemmusicalbum})
    return render(request, 'pyamgmt/models/catalogitemmusicalbum_list.html', context)


def catalogitemmusicalbum_detail(request, catalogitemmusicalbum_pk: int):
    context = {}
    catalogitemmusicalbum = CatalogItemMusicAlbum.objects.get(pk=catalogitemmusicalbum_pk)
    context.update({
        'catalogitemmusicalbum': catalogitemmusicalbum
    })
    return render(request, 'pyamgmt/models/catalogitemmusicalbum_detail.html', context)


@transaction.atomic
def catalogitemmusicalbum_form(request, catalog_item_musicalbum_pk: int = None):
    context = {}
    instance = None
    if catalog_item_musicalbum_pk:
        instance = CatalogItemMusicAlbum.objects.get(pk=catalog_item_musicalbum_pk)
    form = CatalogItemMusicAlbumForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if catalog_item_musicalbum_pk:
            return redirect('pyamgmt:catalogitemmusicalbum:detail',
                            catalog_item_musicalbum_pk=catalog_item_musicalbum_pk)
        return redirect('pyamgmt:catalogitemmusicalbum:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/catalogitemmusicalbum_form.html', context)


def catalogitemtopointofsalelineitem_list(request):
    """List all records from model CatalogItemToPointOfSaleLineItem."""
    context = {}
    qs_catalogitemtopointofsalelineitem = CatalogItemToPointOfSaleLineItem.objects.all()
    context.update({'qs_catalogitemtopointofsalelineitem': qs_catalogitemtopointofsalelineitem})
    return render(request, 'pyamgmt/models/catalogitemtopointofsalelineitem_list.html', context)


def catalogitemtopointofsalelineitem_detail(request, catalogitemtopointofsalelineitem_pk: int):
    context = {}
    catalogitemtopointofsalelineitem = (
        CatalogItemToPointOfSaleLineItem.objects
        .select_related(
            'catalogitem',
            'pointofsalelineitem',
            'unit'
        )
        .get(pk=catalogitemtopointofsalelineitem_pk)
    )
    context.update({
        'catalogitemtopointofsalelineitem': catalogitemtopointofsalelineitem
    })
    return render(request, 'pyamgmt/models/catalogitemtopointofsalelineitem_detail.html', context)


def catalogitemtopointofsalelineitem_form(request, catalogitemtopointofsalelineitem_pk: int = None):
    context = {}
    instance = None
    if catalogitemtopointofsalelineitem_pk:
        instance = CatalogItemToPointOfSaleLineItem.objects.get(
            pk=catalogitemtopointofsalelineitem_pk
        )
    form = CatalogItemToPointOfSaleLineItemForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if catalogitemtopointofsalelineitem_pk:
            return redirect(
                'pyamgmt:catalogitemtopointofsalelineitem:detail',
                catalogitemtopointofsalelineitem_pk=catalogitemtopointofsalelineitem_pk
            )
        return redirect('pyamgmt:catalogitemtopointofsalelineitem:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/catalogitemtopointofsalelineitem_form.html', context)


class InvoiceListView(View):
    def get(self, request, **_kwargs):
        qs_invoice = (
            Invoice.objects.all()
        )
        self.context.update({'qs_invoice': qs_invoice})
        return render(request, 'pyamgmt/models/invoice_list.html', self.context)


class MotionPictureListView(View):
    def get(self, request, **_kwargs):
        qs_motionpicture = MotionPicture.objects.all()
        self.context.update({'qs_motionpicture': qs_motionpicture})
        return render(request, 'pyamgmt/models/motionpicture_list.html', self.context)


class MotionPictureFormView(FormView):
    def get(self, _request, **_kwargs):
        return HttpResponse('', status=404)


class MusicAlbumListView(View):
    def get(self, request, **_kwargs):
        qs_musicalbum = (
            MusicAlbum.objects
            .prefetch_related(
                Prefetch('musicartists', queryset=MusicArtist.objects.order_by('name')))
            .order_by('title'))
        paginator = Paginator(qs_musicalbum, 50)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        print(qs_musicalbum.query)
        self.context.update({'qs_musicalbum': qs_musicalbum, 'page_obj': page_obj})
        return render(request, 'pyamgmt/models/musicalbum_list.html', self.context)


class MusicAlbumDetailView(View):
    def get(self, request, musicalbum_pk: int, **kwargs):
        musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
        qs_musicalbumtosongrecording = (
            MusicAlbumToSongRecording.objects
            .filter(musicalbum=musicalbum)
            .select_related('songrecording__song')
            .order_by('disc_number', 'track_number')
        )
        self.context.update({
            'musicalbum': musicalbum,
            'qs_musicalbumtosongrecording': qs_musicalbumtosongrecording
        })
        return render(request, 'pyamgmt/models/musicalbum_detail.html', self.context)


class MusicAlbumFormView(FormView):
    def setup(self, request, musicalbum_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        musicalbum = None
        if musicalbum_pk:
            musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
        self.form = MusicAlbumForm(request.POST or None, instance=musicalbum)

    def render(self, request):
        self.context.update({'form': self.form, 'deform': self.form.as_dict()})
        return render(request, 'pyamgmt/models/musicalbum_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            print(request.POST)
            self.form.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render(request)


def musicalbum_add_song_form(request, musicalbum_pk: int):
    # context = {}
    # musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
    # form = MusicAlbumToSongForm(request.POST or None, musicalbum=musicalbum)
    # if request.method == 'POST' and form.is_valid():
    #     return redirect('pyamgmt:musicalbum:detail', musicalbum_pk=musicalbum_pk)
    # context.update({'form': form})
    # return render(request, 'pyamgmt/models/musicalbum_add_song_form.html', context)
    return HttpResponse('uc')


def musicalbum_addsongs_form(request, musicalbum_pk: int = None):
    """Formset for bulk add. Needs adjustments."""
    # context = {}
    # instance = MusicAlbum.objects.get(pk=musicalbum_pk) if musicalbum_pk else None
    # # formset of M2M model
    # formset = MusicAlbumToSongFormSet(request.POST or None, instance=instance)
    # if request.method == 'POST' and formset.is_valid():
    #     formset.save()
    #     return redirect('pyamgmt:musicalbum:detail', musicalbum_pk=musicalbum_pk)
    # context.update({'formset': formset})
    # return render(request, 'pyamgmt/models/musicalbum_addsongs_form.html', context)
    return HttpResponse('uc')


class MusicAlbumAddSongRecordingFormView(FormView):
    # noinspection PyMethodOverriding
    def setup(self, request, musicalbum_pk: int, **kwargs):
        super().setup(request, **kwargs)
        musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
        self.form = MusicAlbumToSongRecordingForm(request.POST or None, musicalbum=musicalbum)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/musicalbum_add_songrecording_form.html', self.context)

    def get(self, request, **kwargs):
        return

    def post(self, request, **kwargs):
        return


class MusicAlbumToMusicArtistListView(View):
    def get(self, request, **kwargs):
        qs_musicalbumtomusicartist = MusicAlbumToMusicArtist.objects.select_related('musicalbum', 'musicartist')
        self.context.update({'qs_musicalbumtomusicartist': qs_musicalbumtomusicartist})
        return render(request, 'pyamgmt/models/musicalbumtomusicartist_list.html', self.context)


class MusicAlbumToMusicArtistDetailView(View):
    def get(self, request, musicalbumtomusicartist_pk: int, **kwargs):
        musicalbumtomusicartist = MusicAlbumToMusicArtist.objects.get(pk=musicalbumtomusicartist_pk)
        self.context.update({
            'musicalbumtomusicartist': musicalbumtomusicartist
        })
        return render(request, 'pyamgmt/models/musicalbumtomusicartist_detail.html', self.context)


class MusicAlbumToMusicArtistFormView(FormView):
    def setup(self, request, musicalbumtomusicartist_pk: int = None, musicartist_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        musicalbumtomusicartist = None
        musicartist = None
        self.form = MusicAlbumToMusicArtistForm(request.POST or None, instance=musicalbumtomusicartist)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/musicalbumtomusicartist_form.html', self.context)

    def get(self, request, **kwargs):
        return self.render(request)

    def post(self, request, **kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render(request)


class MusicAlbumToSongRecordingListView(View):
    def get(self, request, **kwargs):
        qs_musicalbumtosongrecording = (
            MusicAlbumToSongRecording.objects
            .select_related('musicalbum', 'songrecording__song')
        )
        self.context.update({'qs_musicalbumtosongrecording': qs_musicalbumtosongrecording})
        return render(request, 'pyamgmt/models/musicalbumtosongrecording_list.html', self.context)


class MusicAlbumToSongRecordingDetailView(View):
    def get(self, request, musicalbumtosongrecording_pk: int, **kwargs):
        musicalbumtosongrecording = (
            MusicAlbumToSongRecording.objects
            .select_related('musicalbum', 'songrecording__song')
            .get(pk=musicalbumtosongrecording_pk)
        )
        self.context.update({'musicalbumtosongrecording': musicalbumtosongrecording})
        return render(request, 'pyamgmt/models/musicalbumtosongrecording_detail.html', self.context)


class MusicAlbumToSongRecordingFormView(FormView):
    def musicalbumtosongrecording_form(self, request, musicalbumtosongrecording_pk: int = None):
        return HttpResponse('uc')


# def musicalbumtosong_form(request, musicalbumtosong_pk: int = None):
#     context = {}
#     instance = None
#     if musicalbumtosong_pk:
#         instance = MusicAlbumToSong.objects.get(pk=musicalbumtosong_pk)
#     form = MusicAlbumToSongForm(request.POST or None, instance=instance)
#     if request.method == 'POST' and form.is_valid():
#         form.save()
#         if musicalbumtosong_pk:
#             return redirect('pyamgmt:musicalbumtosong:detail', musicalbumtosong_pk=musicalbumtosong_pk)
#         return redirect('pyamgmt:musicalbumtosong:list')
#     context.update({'form': form})
#     return render(request, 'pyamgmt/models/musicalbumtosong_form.html', context)


class MusicArtistListView(View):
    def get(self, request, **_kwargs):
        qs_musicartist = MusicArtist.objects.order_by('name')
        self.context.update({'qs_musicartist': qs_musicartist})
        return render(request, 'pyamgmt/models/musicartist_list.html', self.context)


class MusicArtistDetailView(View):
    def get(self, request, musicartist_pk: int, **_kwargs):
        musicartist = MusicArtist.objects.get(pk=musicartist_pk)
        qs_musicalbumtomusicartist = (
            MusicAlbumToMusicArtist.objects
            .filter(musicartist=musicartist)
            .select_related('musicalbum')
            .order_by('musicalbum__year_produced')
        )
        qs_musicartisttoperson = (
            MusicArtistToPerson.objects
            .filter(musicartist=musicartist)
            .select_related('musicartist', 'person')
        )
        qs_musicartisttosong = (
            MusicArtistToSong.objects
            .filter(musicartist=musicartist)
            .select_related('musicartist', 'song')
            .order_by('song__title')
        )
        self.context.update({
            'musicartist': musicartist,
            'qs_musicalbumtomusicartist': qs_musicalbumtomusicartist,
            'qs_musicartisttoperson': qs_musicartisttoperson,
            'qs_musicartisttosong': qs_musicartisttosong
        })
        return render(request, 'pyamgmt/models/musicartist_detail.html', self.context)


class MusicArtistFormView(FormView):
    def setup(self, request, musicartist_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        musicartist = None
        if musicartist_pk:
            musicartist = MusicArtist.objects.get(pk=musicartist)
        self.form = MusicArtistForm(request.POST or None, instance=musicartist)

    def render(self):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/musicartist_form.html', self.context)

    def get(self):
        return self.render()

    def post(self):
        if self.form.is_valid():
            self.form.save()
            return redirect()
        return self.render()


def musicartisttoperson_list(request):
    """List all records from model MusicArtistToPerson."""
    context = {}
    qs_musicartisttoperson = MusicArtistToPerson.objects.select_related('musicartist', 'person')
    context.update({'qs_musicartisttoperson': qs_musicartisttoperson})
    return render(request, 'pyamgmt/models/musicartisttoperson_list.html', context)


def musicartisttoperson_detail(request, musicartisttoperson_pk: int):
    context = {}
    musicartisttoperson = MusicArtistToPerson.objects.get(pk=musicartisttoperson_pk)
    context.update({
        'musicartisttoperson': musicartisttoperson
    })
    return render(request, 'pyamgmt/models/musicartisttoperson_detail.html', context)


def musicartisttoperson_form(request, musicartisttoperson_pk: int = None, musicartist_pk: int = None,
                             person_pk: int = None):
    context = {}
    instance = None
    music_artist = None
    if musicartisttoperson_pk:
        instance = MusicArtistToPerson.objects.get(pk=musicartisttoperson_pk)
    if musicartist_pk:
        music_artist = MusicArtist.objects.get(pk=musicartist_pk)
    form = MusicArtistToPersonForm(request.POST or None, instance=instance, music_artist=music_artist)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if musicartisttoperson_pk:
            return redirect('pyamgmt:musicartisttoperson:detail', musicartisttoperson_pk)
        return redirect('pyamgmt:musicartist:detail', musicartist_pk)
    context.update({'form': form})
    return render(request, 'pyamgmt/models/musicartisttoperson_form.html', context)


def musicartisttosong_list(request):
    return HttpResponse('under construction')


def musicartisttosong_detail(request, musicartisttosong_pk: int):
    return HttpResponse('under construction')


def musicartisttosongrecording_list(request):
    return HttpResponse('under construction')


def party_list(request):
    """List all records from model Party."""
    context = {}
    qs_party = Party.objects.all()
    context.update({'qs_party': qs_party})
    return render(request, 'pyamgmt/models/party_list.html', context)


def party_detail(request, party_pk: int):
    context = {}
    party = Party.objects.get(pk=party_pk)
    context.update({
        'party': party
    })
    return render(request, 'pyamgmt/models/party_detail.html', context)


def party_form(request, party_pk: int = None):
    context = {}
    instance = None
    if party_pk:
        instance = Party.objects.get(pk=party_pk)
    form = PartyForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if party_pk:
            return redirect('pyamgmt:party:detail', party_pk=party_pk)
        return redirect('pyamgmt:party:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/party_form.html', context)


def payee_list(request):
    """List all records from model Payee."""
    context = {}
    qs_payee = Payee.objects.order_by('name')
    context.update({'qs_payee': qs_payee})
    return render(request, 'pyamgmt/models/payee_list.html', context)


class PayeeListView(View):
    pass


def payee_detail(request, payee_pk: int):
    context = {}
    payee = Payee.objects.get(pk=payee_pk)
    context.update({
        'payee': payee
    })
    return render(request, 'pyamgmt/models/payee_detail.html', context)


class PayeeDetailView(View):
    pass


def payee_form(request, payee_pk: int = None):
    context = {}
    instance = None
    if payee_pk:
        instance = Payee.objects.get(pk=payee_pk)
    form = PayeeForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if payee_pk:
            return redirect('pyamgmt:payee:detail', payee_pk=payee_pk)
        return redirect('pyamgmt:payee:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/payee_form.html', context)


class PayeeFormView(FormView):
    pass


def person_list(request):
    """List all records from model Person."""
    logger.info(request.GET)
    default_order = ['last_name', 'first_name', 'id']
    context = {}
    order = request.GET.getlist('order', default_order)
    logger.info(Person._meta.get_fields())
    qs_person = Person.objects.order_by(*order)
    context.update({'qs_person': qs_person})
    return render(request, 'pyamgmt/models/person_list.html', context)


class PersonListView(View):
    def get(self, request, **_kwargs):
        default_order = ['last_name', 'first_name', 'id']
        order = request.GET.getlist('order', default_order)
        qs_person = Person.objects.order_by(*order)
        paginator = Paginator(qs_person, 50)
        page_obj = paginator.get_page(request.GET.get('page'))
        self.context.update({
            'qs_person': qs_person,
            'page_obj': page_obj
        })
        return render(request, 'pyamgmt/models/person_list.html', self.context)


def person_detail(request, person_pk: int):
    context = {}
    person = Person.objects.get(pk=person_pk)
    context.update({
        'person': person
    })
    return render(request, 'pyamgmt/models/person_detail.html', context)


class PersonDetailView(View):
    pass


def person_form(request, person_pk: int = None):
    context = {}
    instance = None
    if person_pk:
        instance = Person.objects.get(pk=person_pk)
    form = PersonForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if person_pk:
            return redirect('pyamgmt:person:detail', person_pk=person_pk)
        return redirect('pyamgmt:person:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/person_form.html', context)


class PersonFormView(FormView):
    def setup(self, request, person_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        person = None
        if person_pk:
            person = Person.objects.get(pk=person_pk)
        self.form = PersonForm(request.POST or None, instance=person)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/person_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            _person = self.form.save()
            return redirect('pyamgmt:person:list')
        return self.render(request)


class PointOfSaleListView(View):
    def get(self, request, **_kwargs):
        qs_pointofsale = PointOfSale.objects.all()
        self.context.update({'qs_pointofsale': qs_pointofsale})
        return render(request, 'pyamgmt/models/pointofsale_list.html', self.context)


def pointofsale_detail(request, pointofsale_pk: int):
    context = {}
    pointofsale = PointOfSale.objects.get(pk=pointofsale_pk)
    related_documents = PointOfSaleDocument.objects.filter(pointofsale=pointofsale)
    related_lineitems = PointOfSaleLineItem.objects.filter(pointofsale=pointofsale)
    context.update({
        'pointofsale': pointofsale,
        'related_documents': related_documents,
        'related_lineitems': related_lineitems
    })
    return render(request, 'pyamgmt/models/pointofsale_detail.html', context)


class PointOfSaleDetailView(View):
    def get(self, request, **_kwargs):

        return render(request, 'pyamgmt/models/pointofsale_detail.html', self.context)


def pointofsale_form(request, pointofsale_pk: int = None):
    context = {}
    instance = None
    if pointofsale_pk:
        instance = PointOfSale.objects.get(pk=pointofsale_pk)
    form = PointOfSaleForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if pointofsale_pk:
            return redirect('pyamgmt:pointofsale:detail', pointofsale_pk=pointofsale_pk)
        return redirect('pyamgmt:pointofsale:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/pointofsale_form.html', context)


def pointofsaledocument_list(request):
    """List all records from model PointOfSaleDocument."""
    context = {}
    qs_pointofsaledocument = PointOfSaleDocument.objects.all()
    context.update({'qs_pointofsaledocument': qs_pointofsaledocument})
    return render(request, 'pyamgmt/models/pointofsaledocument_list.html', context)


def pointofsaledocument_detail(request, pointofsaledocument_pk: int):
    context = {}
    pointofsaledocument = PointOfSaleDocument.objects.get(pk=pointofsaledocument_pk)
    print(dir(pointofsaledocument.document))
    context.update({
        'pointofsaledocument': pointofsaledocument
    })
    return render(request, 'pyamgmt/models/pointofsaledocument_detail.html', context)


def pointofsaledocument_form(request, pointofsaledocument_pk: int = None, pointofsale_pk: int = None):
    context = {}
    instance = None
    if pointofsaledocument_pk:
        instance = PointOfSaleDocument.objects.get(pk=pointofsaledocument_pk)
    form = PointOfSaleDocumentForm(
        request.POST or None, request.FILES or None, instance=instance, pointofsale_pk=pointofsale_pk
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        if pointofsaledocument_pk:
            return redirect(
                'pyamgmt:pointofsaledocument:detail', pointofsaledocument_pk=pointofsaledocument_pk
            )
        return redirect('pyamgmt:pointofsaledocument:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/pointofsaledocument_form.html', context)


def pointofsalelineitem_list(request):
    """List all records from model PointOfSaleLineItem."""
    context = {}
    qs_pointofsalelineitem = PointOfSaleLineItem.objects.all()
    context.update({'qs_pointofsalelineitem': qs_pointofsalelineitem})
    return render(request, 'pyamgmt/models/pointofsalelineitem_list.html', context)


def pointofsalelineitem_detail(request, pointofsalelineitem_pk: int):
    context = {}
    pointofsalelineitem = PointOfSaleLineItem.objects.get(pk=pointofsalelineitem_pk)
    context.update({
        'pointofsalelineitem': pointofsalelineitem
    })
    return render(request, 'pyamgmt/models/pointofsalelineitem_detail.html', context)


def pointofsalelineitem_form(request, pointofsalelineitem_pk: int = None, point_of_sale_pk: int = None):
    context = {}
    instance = None
    if pointofsalelineitem_pk:
        instance = PointOfSaleLineItem.objects.get(pk=pointofsalelineitem_pk)
    form = PointOfSaleLineItemForm(request.POST or None, instance=instance, point_of_sale_pk=point_of_sale_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if pointofsalelineitem_pk:
            return redirect(
                'pyamgmt:pointofsalelineitem:detail',
                pointofsalelineitem_pk=pointofsalelineitem_pk
            )
        return redirect('pyamgmt:pointofsalelineitem:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/pointofsalelineitem_form.html', context)


def song_list(request):
    """List all records from model Song."""
    context = {}
    qs_song = (
        Song.objects
        .prefetch_related(
            Prefetch(
                'musicartisttosong_set',
                queryset=(
                    MusicArtistToSong.objects
                    .select_related('musicartist')
                    .order_by('musicartist__name')
                )
            )
        )
        .annotate(Count('songrecording'))
        .order_by('title')
    )
    context.update({'qs_song': qs_song})
    return render(request, 'pyamgmt/models/song_list.html', context)


def song_detail(request, song_pk: int):
    context = {}
    song = Song.objects.get(pk=song_pk)
    # related_albums = MusicAlbumToSong.objects.filter(song=song).select_related('musicalbum')
    related_artists = MusicArtistToSong.objects.filter(song=song).select_related('musicartist')
    related_recordings = SongRecording.objects.filter(song=song)
    related_songs = SongToSong.objects.filter(song_original=song).select_related('song_derivative')
    context.update({
        'song': song,
        # 'related_albums': related_albums,
        'related_artists': related_artists,
        'related_recordings': related_recordings,
        'related_songs': related_songs
    })
    return render(request, 'pyamgmt/models/song_detail.html', context)


class SongFormView(FormView):
    def setup(self, request, song_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        song = None
        if song_pk:
            song = Song.objects.get(pk=song_pk)
        self.form = SongForm(request.POST or None, instance=song)

    def render(self):
        self.context.update({'form': self.form})

    def get(self, _request, **_kwargs):
        return render(self.request, 'pyamgmt/models/song_form.html', self.context)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            if request.POST.get('_addanother'):
                return redirect('pyamgmt:song:add')
            return redirect('pyamgmt:song:list')  # TODO: Back to list OR detail
        return self.render()


class SongRecordingListView(View):
    def get(self, request, **kwargs):
        qs_songrecording = (
            SongRecording.objects
            .select_related('song')
            .prefetch_related('song__musicartisttosong_set__musicartist')  # original artist
        )
        self.context.update({'qs_songrecording': qs_songrecording})
        return render(request, 'pyamgmt/models/songrecording_list.html', self.context)


class SongRecordingDetailView(View):
    def get(self, request, songrecording_pk: int, **kwargs):
        songrecording = SongRecording.objects.select_related('song').get(pk=songrecording_pk)
        related_albums = MusicAlbumToSongRecording.objects.filter(songrecording=songrecording).select_related('musicalbum')
        related_artists = MusicArtistToSongRecording.objects.filter(songrecording=songrecording).select_related('musicartist')
        self.context.update({
            'songrecording': songrecording,
            'related_albums': related_albums,
            'related_artists': related_artists
        })
        return render(request, 'pyamgmt/models/songrecording_detail.html', self.context)


class SongRecordingFormView(FormView):
    def setup(self, request, songrecording_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        songrecording = None
        if songrecording_pk:
            songrecording = SongRecording.objects.get(pk=songrecording_pk)
        self.form = SongRecordingForm(request.POST or None, instance=songrecording)

    def render(self):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/songrecording_form.html', self.context)

    def get(self, request, **kwargs):
        return self.render()

    def post(self, request, **kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect()
        return self.render()


def songtosong_list(request):
    context = {}
    qs_songtosong = SongToSong.objects.all()
    context.update({'qs_songtosong': qs_songtosong})
    return render(request, 'pyamgmt/models/songtosong_list.html', context)


class TxnListView(View):
    def get(self, request, **kwargs):
        q_debits = Sum('line_items__amount', filter=Q(line_items__debit=True))
        q_credits = Sum('line_items__amount', filter=Q(line_items__debit=False))
        qs_txn = (
            Txn.objects
            .select_related('payee')
            .annotate(debits=q_debits)
            .annotate(credits=q_credits)
            .annotate(
                balanced=Case(
                    When(debits=F('credits'), then=Value(True)),
                    default=Value(False)
                )
            )
            .order_by('-txn_date')
        )
        self.context.update({'qs_txn': qs_txn})
        return render(request, 'pyamgmt/models/txn_list.html', self.context)


class TxnDetailView(View):
    def get(self, request, txn_pk: int, **_kwargs):
        txn = Txn.objects.get(pk=txn_pk)
        self.context.update({
            'txn': txn
        })
        return render(request, 'pyamgmt/models/txn_detail.html', self.context)


@transaction.atomic
def txn_form(request, txn_pk=None):
    context = {}
    instance = None
    if txn_pk:
        instance = Txn.objects.get(pk=txn_pk)
    form = TxnForm(request.POST or None, instance=instance)
    formset = TxnLineItemFormSet(request.POST or None, instance=form.instance)
    if request.method == 'POST' and all(
        [form.is_valid(), formset.is_valid()]
    ):
        form.save()
        formset.save()
        if txn_pk:
            return redirect('pyamgmt:txn:detail', txn_pk=txn_pk)
        return redirect('pyamgmt:txn:list')
    context.update({'form': form, 'formset': formset})


# Form + formset
# With default formset behavior, the same multi-form class should work?
class TxnFormView(MultiFormView):
    def setup(self, request, txn_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        txn = None
        if txn_pk:
            txn = Txn.objects.get(pk=txn_pk)
        self.forms.txn = TxnForm(request.POST or None, instance=txn)
        self.forms.txnlineitem = TxnLineItemFormSet()

    def render(self):
        return render(self.request, 'pyamgmt/models/txn_form.html', self.context)

    def get(self, _request, **_kwargs):
        return self.render()

    @transaction.atomic
    def post(self, _request, **_kwargs):
        if self.forms.are_valid():
            return redirect()
        return self.render()


class TxnLineItemListView(View):
    def get(self, request, **kwargs):
        qs_txnlineitem = (
            TxnLineItem.objects
            .select_related('account', 'txn')
        )
        self.context.update({'qs_txnlineitem': qs_txnlineitem})
        return render(request, 'pyamgmt/models/txnlineitem_list.html', self.context)


class TxnLineItemDetailView(View):
    def get(self, request, txnlineitem_pk: int, **_kwargs):
        txnlineitem = (
            TxnLineItem.objects
            .select_related('account', 'txn')
            .get(pk=txnlineitem_pk)
        )
        self.context.update({'txnlineitem': txnlineitem})
        return render(request, 'pyamgmt/models/txnlineitem_detail.html', self.context)


class UnitListView(View):
    def get(self, request, **_kwargs):
        qs_unit = Unit.objects.all()
        self.context.update({'qs_unit': qs_unit})
        return render(request, 'pyamgmt/models/unit_list.html', self.context)


class UnitDetailView(View):
    def get(self, request, unit_pk: int):
        unit = Unit.objects.get(pk=unit_pk)
        self.context.update({
            'unit': unit
        })
        return render(request, 'pyamgmt/models/unit_detail.html', self.context)


class UnitFormView(FormView):
    def setup(self, request, unit_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        unit = None
        if unit_pk:
            unit = Unit.objects.get(pk=unit_pk)
        self.form = UnitForm(request.POST or None, instance=unit)

    def render(self):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/unit_form.html', self.context)

    def get(self, _request, **_kwargs):
        return self.render()

    def post(self, _request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            # if unit_pk:
            #     return redirect('pyamgmt:unit:detail', unit_pk=unit_pk)
            return redirect('pyamgmt:unit:list')
        return self.render()


class VehicleListView(View):
    def get(self, request, **_kwargs):
        pf_vehiclemileage = Prefetch(
            'vehiclemileage_set',
            queryset=VehicleMileage.objects.order_by('-odometer_date', '-odometer_time')
        )
        qs_vehicle = (
            Vehicle.objects
            .select_related('vehicleyear__vehicletrim__vehiclemodel__vehiclemake')
            .prefetch_related(pf_vehiclemileage)
            .order_by(
                '-vehicleyear__year',
                'vehicleyear__vehicletrim__vehiclemodel__vehiclemake__name',
                'vehicleyear__vehicletrim__vehiclemodel__name',
                'vehicleyear__vehicletrim__name',
                'vin')
        )
        self.context.update({'qs_vehicle': qs_vehicle})
        return render(request, 'pyamgmt/models/vehicle_list.html', self.context)


class VehicleDetailView(View):
    def get(self, request, vehicle_pk: int, **_kwargs):
        vehicle = Vehicle.objects.get(pk=vehicle_pk)
        vehiclemileage_records = (
            VehicleMileage.objects
            .filter(vehicle=vehicle)
            .order_by('odometer_date', 'odometer_time')
        )
        chart_data = list(vehiclemileage_records.values('odometer_date', 'odometer_miles'))
        last_record = {}
        average_mileage = []
        for record in chart_data:
            if not last_record:
                last_record = record
                continue
            delta_days = record['odometer_date'] - last_record['odometer_date']
            if delta_days.days == 0:  # TODO: this should be additive
                delta_days = delta_days + datetime.timedelta(days=1)
            delta_mileage = record['odometer_miles'] - last_record['odometer_miles']
            daily_average = delta_mileage / delta_days.days
            average_mileage.append({
                'start_date': last_record['odometer_date'],
                'end_date': record['odometer_date'],
                'delta_mileage': delta_mileage,
                'delta_days': delta_days.total_seconds() * 1000,
                'daily_average': daily_average
            })
            last_record = record
        cache_key = f'Vehicle-{vehicle.vin}-NHTSA'
        nhtsa_api_data = cache.get(cache_key)
        if nhtsa_api_data is None:
            try:
                logger.info('Fetching from NHTSA...')
                response = requests.get(
                    f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinextended/{vehicle.vin}?format=json',
                    timeout=1
                )
                nhtsa_api_data = response.json()
            except Exception as e:
                logger.warning(e)
                nhtsa_api_data = {}
            else:
                logger.info('Caching NHTSA response...')
                cache.set(cache_key, nhtsa_api_data, 60 * 60 * 24 * 7)
        self.context.update({
            'vehicle': vehicle,
            'vehiclemileage_records': vehiclemileage_records,
            'chart_data': chart_data,
            'average_mileage': average_mileage,
            'nhtsa_api_data': nhtsa_api_data
        })
        return render(request, 'pyamgmt/models/vehicle_detail.html', self.context)


class VehicleFormView(FormView):
    def setup(self, request, vehicle_pk: int = None, vehicleyear_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehicle = None
        if vehicle_pk:
            vehicle = Vehicle.objects.get(pk=vehicle_pk)
        self.form = VehicleForm(request.POST or None, instance=vehicle, vehicleyear_pk=vehicleyear_pk)

    def render(self):
        self.context.update({'form': self.form.as_dict()})
        return render(self.request, 'pyamgmt/models/vehicle_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render()

    def post(self, _request, **kwargs):
        if self.form.is_valid():
            self.form.save()
            # if vehicleyear_pk:
            #     return redirect('pyamgmt:vehicleyear:detail', vehicleyear_pk=vehicleyear_pk)
            # if vehicle_pk:
            #     return redirect('pyamgmt:vehicle:detail', vehicle_pk=vehicle_pk)
            return redirect('pyamgmt:vehicle:list')
        return self.render()


class VehicleMakeListView(View):
    def get(self, request):
        qs_vehiclemake = (
            VehicleMake.objects
            .annotate(vehiclemodel_count=Count('vehiclemodel'))
            .order_by('name')
        )
        self.context.update({'qs_vehiclemake': qs_vehiclemake})
        return render(request, 'pyamgmt/models/vehiclemake_list.html', self.context)


class VehicleMakeDetailView(View):
    def get(self, request, vehiclemake_pk: int, **_kwargs):
        vehiclemake = VehicleMake.objects.get(pk=vehiclemake_pk)
        qs_vehiclemodel = VehicleModel.objects.filter(vehiclemake=vehiclemake).order_by('name')
        self.context.update({
            'vehiclemake': vehiclemake,
            'qs_vehiclemodel': qs_vehiclemodel
        })
        return render(request, 'pyamgmt/models/vehiclemake_detail.html', self.context)


class VehicleMakeFormView(FormView):
    def setup(self, request, vehiclemake_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehiclemake = None
        if vehiclemake_pk:
            vehiclemake = VehicleMake.objects.get(pk=vehiclemake_pk)
        self.form = VehicleMakeForm(request.POST or None, instance=vehiclemake)

    def render(self, request):
        self.context.update({'form': self.form})
        # TODO: 'test' form.as_dict()
        self.context.update({'test': self.form.as_dict()})
        return render(request, 'pyamgmt/models/vehiclemake_form.html', self.context)

    def get(self, request):
        return self.render(request)

    def post(self, request):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:vehiclemake:list')
        return self.render(request)


class VehicleMileageListView(View):
    def get(self, request, **kwargs):
        qs_vehiclemileage = VehicleMileage.objects.all()
        self.context.update({'qs_vehiclemileage': qs_vehiclemileage})
        return render(request, 'pyamgmt/models/vehiclemileage_list.html', self.context)


class VehicleMileageDetailView(View):
    def get(self, request, vehiclemileage_pk: int, **kwargs):
        vehiclemileage = VehicleMileage.objects.get(pk=vehiclemileage_pk)
        self.context.update({
            'vehiclemileage': vehiclemileage
        })
        return render(request, 'pyamgmt/models/vehiclemileage_detail.html', self.context)


class VehicleMileageFormView(FormView):
    def setup(self, request, vehiclemileage_pk: int = None, vehicle_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehiclemileage = None
        if vehiclemileage_pk:
            vehiclemileage = VehicleMileage.objects.get(pk=vehiclemileage_pk)
        self.form = VehicleMileageForm(request.POST or None, instance=vehiclemileage, vehicle_pk=vehicle_pk)

    def render(self):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/vehiclemileage_form.html', self.context)

    def get(self, _request, **_kwargs):
        return self.render()

    def post(self, _request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            # if vehiclemileage_pk:
            #     return redirect('pyamgmt:vehiclemileage:detail', vehiclemileage_pk=vehiclemileage_pk)
            # if vehicle_pk:
            #     return redirect('pyamgmt:vehicle:detail', vehicle_pk=vehicle_pk)
            return redirect('pyamgmt:vehiclemileage:list')
        return self.render()


class VehicleModelListView(View):
    def get(self, request, **_kwargs):
        qs_vehiclemodel = (
            VehicleModel.objects
            .select_related('vehiclemake')
            .annotate(vehicletrim_count=Count('vehicletrim'))
            .order_by('vehiclemake__name', 'name')
        )
        self.context.update({'qs_vehiclemodel': qs_vehiclemodel})
        return render(request, 'pyamgmt/models/vehiclemodel_list.html', self.context)


class VehicleModelDetailView(View):
    def get(self, request, vehiclemodel_pk: int, **_kwargs):
        vehiclemodel = VehicleModel.objects.get(pk=vehiclemodel_pk)
        qs_vehicletrim = VehicleTrim.objects.filter(vehiclemodel=vehiclemodel).order_by('name')
        self.context.update({
            'vehiclemodel': vehiclemodel,
            'qs_vehicletrim': qs_vehicletrim
        })
        return render(request, 'pyamgmt/models/vehiclemodel_detail.html', self.context)


class VehicleModelFormView(FormView):
    def setup(self, request, vehiclemodel_pk: int = None, vehiclemake_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehiclemodel = None
        if vehiclemodel_pk:
            vehiclemodel = VehicleModel.objects.get(pk=vehiclemodel_pk)
        self.form = VehicleModelForm(
            request.POST or None, instance=vehiclemodel, vehiclemake_pk=vehiclemake_pk
        )

    def render(self, request):
        self.context.update({'form': self.form})
        return render(request, 'pyamgmt/models/vehiclemodel_form.html', self.context)

    def get(self, request, **kwargs):
        return self.render(request)

    def post(self, request, **kwargs):
        if self.form.is_valid():
            vehiclemodel = self.form.save()
            return redirect('pyamgmt:vehiclemodel:detail', vehiclemodel_pk=vehiclemodel.pk)
        return self.render(request)


class VehicleTrimListView(View):
    def get(self, request, **_kwargs):
        qs_vehicletrim = (
            VehicleTrim.objects
            .select_related('vehiclemodel__vehiclemake')
            .order_by(
                'vehiclemodel__vehiclemake__name',
                'vehiclemodel__name',
                'name')
        )
        self.context.update({'qs_vehicletrim': qs_vehicletrim})
        return render(request, 'pyamgmt/models/vehicletrim_list.html', self.context)


class VehicleTrimDetailView(View):
    def get(self, request, vehicletrim_pk: int, **_kwargs):
        vehicletrim = VehicleTrim.objects.get(pk=vehicletrim_pk)
        qs_vehicleyear = VehicleYear.objects.filter(vehicletrim=vehicletrim).order_by('year')
        self.context.update({
            'vehicletrim': vehicletrim,
            'qs_vehicleyear': qs_vehicleyear
        })
        return render(request, 'pyamgmt/models/vehicletrim_detail.html', self.context)


class VehicleTrimFormView(FormView):
    def setup(self, request, vehicletrim_pk: int = None, vehiclemodel_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehicletrim = None
        if vehicletrim_pk:
            vehicletrim = VehicleTrim.objects.get(pk=vehicletrim_pk)
        self.form = VehicleTrimForm(request.POST or None, instance=vehicletrim, vehiclemodel_pk=vehiclemodel_pk)

    def render(self):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/vehicletrim_form.html', self.context)

    def get(self, _request, **_kwargs):
        return self.render()

    def post(self, _request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:pyamgmt:list')
        return self.render()


class VehicleYearListView(View):
    def get(self, request, **_kwargs):
        qs_vehicleyear = (
            VehicleYear.objects
            .select_related('vehicletrim__vehiclemodel__vehiclemake')
            .order_by(
                'vehicletrim__vehiclemodel__vehiclemake__name',
                'vehicletrim__vehiclemodel__name',
                'vehicletrim__name',
                'year'
            )
        )
        self.context.update({'qs_vehicleyear': qs_vehicleyear})
        return render(request, 'pyamgmt/models/vehicleyear_list.html', self.context)


class VehicleYearDetailView(View):
    def get(self, request, vehicleyear_pk: int, **_kwargs):
        vehicleyear = VehicleYear.objects.get(pk=vehicleyear_pk)
        qs_vehicle = Vehicle.objects.filter(vehicleyear=vehicleyear).order_by('vin')
        self.context.update({
            'vehicleyear': vehicleyear,
            'qs_vehicle': qs_vehicle
        })
        return render(request, 'pyamgmt/models/vehicleyear_detail.html', self.context)


class VehicleYearFormView(FormView):
    def setup(self, request, vehicleyear_pk: int = None, vehicletrim_pk: int = None, **kwargs):
        super().setup(request, **kwargs)
        vehicleyear = None
        if vehicleyear_pk:
            vehicleyear = VehicleYear.objects.get(pk=vehicleyear_pk)
        self.form = VehicleYearForm(request.POST or None, instance=vehicleyear, vehicletrim_pk=vehicletrim_pk)

    def render(self, request):
        self.context.update({'form': self.form})
        return render(self.request, 'pyamgmt/models/vehicleyear_form.html', self.context)

    def get(self, request, **_kwargs):
        return self.render(request)

    def post(self, request, **_kwargs):
        if self.form.is_valid():
            self.form.save()
            return redirect('pyamgmt:vehicleyear:list')
        return self.render(request)
