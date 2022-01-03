import datetime
import logging

import requests

from django.core.cache import cache
from django.db import transaction
from django.db.models import Case, Count, F, Prefetch, Q, Sum, Value, When
from django.http import HttpResponse
from django.shortcuts import render, redirect

from pyamgmt.forms import *
from pyamgmt.models import *

logger = logging.getLogger(__name__)


def account_list(request):
    """List all records from model Account."""
    context = {}
    q_debits = Sum('txnlineitem__amount', filter=Q(txnlineitem__debit=True))
    q_credits = Sum('txnlineitem__amount', filter=Q(txnlineitem__debit=False))
    qs_account = (
        Account.objects
        .annotate(debits=q_debits)
        .annotate(credits=q_credits)
        .order_by('name')
    )
    print(qs_account.query)
    context.update({'qs_account': qs_account})
    return render(request, 'pyamgmt/models/account_list.html', context)


def account_detail(request, account_pk: int):
    context = {}
    account = Account.objects.prefetch_related('txnlineitem_set__txn__payee').get(pk=account_pk)
    context.update({
        'account': account
    })
    return render(request, 'pyamgmt/models/account_detail.html', context)


def account_form(request, account_pk: int = None):
    context = {}
    instance = None
    if account_pk:
        instance = Account.objects.get(pk=account_pk)
    form = AccountForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        account = form.save()
        if account.subtype == Account.Subtype.ASSET:
            account_asset, _ = AccountAsset.objects.get_or_create(account=account)
        return redirect('pyamgmt:account:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/account_form.html', context)


def accountasset_list(request):
    """List all records from model AccountAsset."""
    context = {}
    qs_accountasset = AccountAsset.objects.select_related('account')
    context.update({'qs_accountasset': qs_accountasset})
    return render(request, 'pyamgmt/models/accountasset_list.html', context)


def accountasset_detail(request, accountasset_pk: int):
    context = {}
    accountasset = AccountAsset.objects.get(pk=accountasset_pk)
    context.update({
        'accountasset': accountasset
    })
    return render(request, 'pyamgmt/models/accountasset_detail.html', context)


@transaction.atomic()
def accountasset_form(request, accountasset_pk: int = None):
    context = {}
    instance = None
    if accountasset_pk:
        instance = AccountAsset.objects.get(pk=accountasset_pk)
    form = AccountAssetForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        account_asset = form.save()
        if account_asset.subtype == AccountAsset.Subtype.FINANCIAL:
            account_asset_financial, _ = AccountAssetFinancial.objects.get_or_create(account_asset=account_asset)
        if account_asset.subtype == AccountAsset.Subtype.REAL:
            account_asset_real, _ = AccountAssetReal.objects.get_or_create(account_asset=account_asset)
        if accountasset_pk:
            return redirect('pyamgmt:accountasset:detail', accountasset_pk=accountasset_pk)
        return redirect('pyamgmt:accountasset:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/accountasset_form.html', context)


def accountassetfinancial_list(request):
    """List all records from model AccountAssetFinancial."""
    context = {}
    qs_accountassetfinancial = (
        AccountAssetFinancial.objects
        .select_related('accountasset__account')
    )
    context.update({'qs_accountassetfinancial': qs_accountassetfinancial})
    return render(request, 'pyamgmt/models/accountassetfinancial_list.html', context)


def accountassetfinancial_detail(request, accountassetfinancial_pk: int):
    context = {}
    accountassetfinancial = (
        AccountAssetFinancial.objects
        .select_related('accountasset__account')
        .get(pk=accountassetfinancial_pk)
    )
    qs_txnlineitem = (
        TxnLineItem.objects
        .filter(account_id=accountassetfinancial_pk)
        .select_related('txn')
        .order_by('-txn__txn_date')
    )
    context.update({
        'accountassetfinancial': accountassetfinancial,
        'qs_txnlineitem': qs_txnlineitem
    })
    return render(request, 'pyamgmt/models/accountassetfinancial_detail.html', context)


@transaction.atomic()
def accountassetfinancial_form(request, accountassetfinancial_pk: int = None):
    context = {}
    instance = None
    accountasset_instance = None
    account_instance = None
    if accountassetfinancial_pk:
        instance = AccountAssetFinancial.objects.get(pk=accountassetfinancial_pk)
        accountasset_instance = instance.account_asset
        account_instance = accountasset_instance.account
    form_accountassetfinancial = AccountAssetFinancialForm(request.POST or None, instance=instance)
    form_accountasset = AccountAssetForm(
        request.POST or None,
        instance=accountasset_instance,
        initial={'subtype': AccountAsset.Subtype.FINANCIAL}
    )
    form_accountasset.fields['subtype'].disabled = True
    form_account = AccountForm(
        request.POST or None,
        instance=account_instance,
        initial={'subtype': Account.Subtype.ASSET}
    )
    form_account.fields['subtype'].disabled = True
    form_account.fields['parent_account'].queryset = (
        form_account.fields['parent_account'].queryset.filter(accountasset__subtype=AccountAsset.Subtype.FINANCIAL)
    )
    if request.method == 'POST' and all(
        [form_account.is_valid(), form_accountasset.is_valid(), form_accountassetfinancial.is_valid()]
    ):
        account = form_account.save()
        accountasset = form_accountasset.save(commit=False)
        accountasset.account = account
        accountasset.save()
        accountassetfinancial = form_accountassetfinancial.save(commit=False)
        accountassetfinancial.accountasset = accountasset
        accountassetfinancial.save()
        if accountassetfinancial_pk:
            return redirect('pyamgmt:accountassetfinancial:detail',
                            accountassetfinancial_pk=accountassetfinancial_pk)
        return redirect('pyamgmt:accountassetfinancial:list')
    context.update({
        'form_account': form_account,
        'form_accountasset': form_accountasset,
        'form_accountassetfinancial': form_accountassetfinancial
    })
    return render(request, 'pyamgmt/models/accountassetfinancial_form.html', context)


def accountassetreal_list(request):
    """List all records from model AccountAssetReal."""
    context = {}
    qs_accountassetreal = (
        AccountAssetReal.objects
        .select_related('accountasset__account')
    )
    context.update({'qs_accountassetreal': qs_accountassetreal})
    return render(request, 'pyamgmt/models/accountassetreal_list.html', context)


def accountassetreal_detail(request, accountassetreal_pk: int):
    context = {}
    accountassetreal = AccountAssetReal.objects.get(pk=accountassetreal_pk)
    context.update({
        'accountassetreal': accountassetreal
    })
    return render(request, 'pyamgmt/models/accountassetreal_detail.html', context)


@transaction.atomic()
def accountassetreal_form(request, accountassetreal_pk: int = None):
    context = {}
    instance = None
    accountasset_instance = None
    account_instance = None
    if accountassetreal_pk:
        instance = AccountAssetReal.objects.get(pk=accountassetreal_pk)
        accountasset_instance = instance.accountasset
        account_instance = accountasset_instance.account
    form_accountassetreal = AccountAssetRealForm(request.POST or None, instance=instance)
    form_accountasset = AccountAssetForm(
        request.POST or None,
        instance=accountasset_instance,
        initial={'subtype': AccountAsset.Subtype.REAL}
    )
    form_accountasset.fields['subtype'].disabled = True
    form_account = AccountForm(
        request.POST or None,
        instance=account_instance,
        initial={'subtype': Account.Subtype.ASSET}
    )
    form_account.fields['parent_account'].queryset = (
        form_account.fields['parent_account'].queryset.filter(accountasset__subtype=AccountAsset.Subtype.REAL)
    )
    form_account.fields['subtype'].disabled = True
    if request.method == 'POST' and all(
        [form_account.is_valid(), form_accountasset.is_valid(), form_accountassetreal.is_valid()]
    ):
        account = form_account.save()
        accountasset = form_accountasset.save(commit=False)
        accountasset.account = account
        accountasset.save()
        accountassetreal = form_accountassetreal.save(commit=False)
        accountassetreal.account_asset = accountasset
        accountassetreal.save()
        if accountassetreal_pk:
            return redirect('pyamgmt:accountassetreal:detail', accountassetreal_pk=accountassetreal_pk)
        return redirect('pyamgmt:accountassetreal:list')
    context.update({
        'form_account': form_account,
        'form_accountasset': form_accountasset,
        'form_accountassetreal': form_accountassetreal
    })
    return render(request, 'pyamgmt/models/accountassetreal_form.html', context)


def accountexpense_list(request):
    """List all records from model AccountExpense."""
    context = {}
    qs_accountexpense = AccountExpense.objects.select_related('account').order_by('account__name').all()
    context.update({'qs_accountexpense': qs_accountexpense})
    return render(request, 'pyamgmt/models/accountexpense_list.html', context)


def accountexpense_detail(request, accountexpense_pk: int):
    context = {}
    accountexpense = AccountExpense.objects.get(pk=accountexpense_pk)
    context.update({
        'accountexpense': accountexpense
    })
    return render(request, 'pyamgmt/models/accountexpense_detail.html', context)


@transaction.atomic()
def accountexpense_form(request, accountexpense_pk: int = None):
    context = {}
    instance = None
    account_instance = None
    if accountexpense_pk:
        instance = AccountExpense.objects.get(pk=accountexpense_pk)
        account_instance = instance.account
    form_accountexpense = AccountExpenseForm(request.POST or None, instance=instance)
    form_account = AccountForm(
        request.POST or None,
        instance=account_instance,
        initial={'subtype': Account.Subtype.EXPENSE}
    )
    form_account.fields['parent_account'].queryset = (
        form_account.fields['parent_account'].queryset.filter(subtype=Account.Subtype.EXPENSE)
    )
    form_account.fields['subtype'].disabled = True
    if request.method == 'POST' and all(
        [form_account.is_valid(), form_accountexpense.is_valid()]
    ):
        account = form_account.save()
        account_expense = form_accountexpense.save(commit=False)
        account_expense.account = account
        account_expense.save()
        if accountexpense_pk:
            return redirect('pyamgmt:accountexpense:detail', accountexpense_pk=accountexpense_pk)
        return redirect('pyamgmt:accountexpense:list')
    context.update({'form_account': form_account, 'form_accountexpense': form_accountexpense})
    return render(request, 'pyamgmt/models/accountexpense_form.html', context)


def accountincome_list(request):
    """List all records from model AccountIncome."""
    context = {}
    qs_accountincome = AccountIncome.objects.select_related('account')
    context.update({'qs_accountincome': qs_accountincome})
    return render(request, 'pyamgmt/models/accountincome_list.html', context)


def accountincome_detail(request, accountincome_pk: int):
    context = {}
    accountincome = AccountIncome.objects.select_related('account').get(pk=accountincome_pk)
    qs_txnlineitem = (
        TxnLineItem.objects
        .filter(account_id=accountincome.pk)
        .select_related('txn')
        .order_by('-txn__txn_date')
    )
    context.update({
        'accountincome': accountincome,
        'qs_txnlineitem': qs_txnlineitem
    })
    return render(request, 'pyamgmt/models/accountincome_detail.html', context)


@transaction.atomic()
def accountincome_form(request, accountincome_pk: int = None):
    context = {}
    instance = None
    account_instance = None
    if accountincome_pk:
        instance = AccountIncome.objects.get(pk=accountincome_pk)
        account_instance = instance.account
    form_accountincome = AccountIncomeForm(request.POST or None, instance=instance)
    form_account = AccountForm(
        request.POST or None, instance=account_instance,
        initial={'subtype': Account.Subtype.INCOME}
    )
    form_account.fields['parent_account'].queryset = (
        form_account.fields['parent_account'].queryset.filter(subtype=Account.Subtype.INCOME)
    )
    form_account.fields['subtype'].disabled = True
    if request.method == 'POST' and all(
        [form_account.is_valid(), form_accountincome.is_valid()]
    ):
        account = form_account.save()
        accountincome = form_accountincome.save(commit=False)
        accountincome.account = account
        accountincome.save()
        if accountincome_pk:
            return redirect('pyamgmt:accountincome:detail', accountincome_pk=accountincome_pk)
        return redirect('pyamgmt:accountincome:list')
    context.update({'form_account': form_account, 'form_accountincome': form_accountincome})
    return render(request, 'pyamgmt/models/accountincome_form.html', context)


def accountliability_list(request):
    """List all records from model AccountLiability."""
    context = {}
    qs_accountliability = AccountLiability.objects.select_related('account')
    context.update({'qs_accountliability': qs_accountliability})
    return render(request, 'pyamgmt/models/accountliability_list.html', context)


def accountliability_detail(request, accountliability_pk: int):
    context = {}
    accountliability = AccountLiability.objects.select_related('account').get(pk=accountliability_pk)
    context.update({
        'accountliability': accountliability
    })
    return render(request, 'pyamgmt/models/accountliability_detail.html', context)


@transaction.atomic()
def accountliability_form(request, accountliability_pk: int = None):
    context = {}
    instance = None
    account_instance = None
    if accountliability_pk:
        instance = AccountLiability.objects.get(pk=accountliability_pk)
        account_instance = instance.account
    form_accountliability = AccountLiabilityForm(request.POST or None, instance=instance)
    form_account = AccountForm(
        request.POST or None, instance=account_instance, initial={'subtype': Account.Subtype.LIABILITY}
    )
    form_account.fields['subtype'].disabled = True
    if request.method == 'POST' and all(
        [form_account.is_valid(), form_accountliability.is_valid()]
    ):
        account = form_account.save()
        accountliability = form_accountliability.save(commit=False)
        accountliability.account = account
        accountliability.save()
        if accountliability_pk:
            return redirect('pyamgmt:accountliability:detail', accountliability_pk=accountliability_pk)
        return redirect('pyamgmt:accountliability:list')
    context.update({'form_account': form_account, 'form_accountliability': form_accountliability})
    return render(request, 'pyamgmt/models/accountliability_form.html', context)


def asset_list(request):
    """List all records from model Asset."""
    context = {}
    qs_asset = Asset.objects.all()
    context.update({'qs_asset': qs_asset})
    return render(request, 'pyamgmt/models/asset_list.html', context)


def asset_detail(request, asset_pk: int):
    context = {}
    asset = Asset.objects.get(pk=asset_pk)
    context.update({
        'asset': asset
    })
    return render(request, 'pyamgmt/models/asset_detail.html', context)


def asset_form(request, asset_pk=None):
    """Supertype. Probably won't include without JavaScript.
    Another method is to not allow adding through this form, and force adding through subtype (multiple forms).
    Another method is JavaScript.
    """
    context = {}
    instance = None
    if asset_pk:
        instance = Asset.objects.get(pk=asset_pk)
    form = AssetForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        # form.save()
        return redirect('pyamgmt:asset:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/asset_form.html', context)


def assetdiscrete_list(request):
    context = {}
    qs_assetdiscrete = AssetDiscrete.objects.select_related('asset')
    context.update({
        'qs_assetdiscrete': qs_assetdiscrete
    })
    return render(request, 'pyamgmt/models/assetdiscrete_list.html', context)


def assetdiscrete_detail(request, assetdiscrete_pk: int):
    context = {}
    assetdiscrete = AssetDiscrete.objects.get(pk=assetdiscrete_pk)
    context.update({
        'assetdiscrete': assetdiscrete
    })
    return render(request, 'pyamgmt/models/assetdiscrete_detail.html', context)


def assetdiscretecatalogitem_list(request):
    context = {}
    return render(request, 'pyamgmt/models/assetdiscretecatalogitem_list.html', context)


def assetdiscretecatalogitem_detail(request, assetdiscretecatalogitem_pk: int):
    context = {}
    assetdiscretecatalogitem = AssetDiscreteCatalogItem.objects.get(pk=assetdiscretecatalogitem_pk)
    context.update({
        'assetdiscretecatalogitem': assetdiscretecatalogitem
    })
    return render(request, 'pyamgmt/models/assetdiscretecatalogitem_detail.html', context)


def assetdiscretevehicle_list(request):
    """List all records from model AssetVehicle."""
    context = {}
    qs_assetdiscretevehicle = (
        AssetDiscreteVehicle.objects
        .select_related('assetdiscrete__asset', 'vehicle')
        .order_by('assetdiscrete__date_withdrawn', '-vehicle__vehicleyear__year')
    )
    context.update({'qs_assetdiscretevehicle': qs_assetdiscretevehicle})
    return render(request, 'pyamgmt/models/assetdiscretevehicle_list.html', context)


def assetdiscretevehicle_detail(request, assetdiscretevehicle_pk: int):
    context = {}
    assetdiscretevehicle = (
        AssetDiscreteVehicle.objects
        .select_related(
            'assetdiscrete',
            'vehicle__vehicleyear__vehicletrim__vehiclemodel__vehiclemake'
        )
        .get(pk=assetdiscretevehicle_pk)
    )
    context.update({
        'assetdiscretevehicle': assetdiscretevehicle
    })
    return render(request, 'pyamgmt/models/assetdiscretevehicle_detail.html', context)


@transaction.atomic
def assetdiscretevehicle_form(request, assetdiscretevehicle_pk=None):
    """Form to add/edit vehicle assets that cascades upwards through the supertypes."""
    context = {}
    assetdiscretevehicle_instance = None
    assetdiscrete_instance = None
    asset_instance = None
    if assetdiscretevehicle_pk:
        assetdiscretevehicle_instance = (
            AssetDiscreteVehicle.objects
            .select_related('assetdiscrete__asset')
            .get(pk=assetdiscretevehicle_pk)
        )
        assetdiscrete_instance = assetdiscretevehicle_instance.assetdiscrete
        asset_instance = assetdiscrete_instance.asset
    form_assetdiscretevehicle = AssetDiscreteVehicleForm(
        request.POST or None, instance=assetdiscretevehicle_instance
    )
    form_assetdiscrete = AssetDiscreteForm(
        request.POST or None, instance=assetdiscrete_instance,
        initial={'subtype': AssetDiscrete.Subtype.VEHICLE}
    )
    form_assetdiscrete.fields['subtype'].disabled = True
    form_asset = AssetForm(
        request.POST or None, instance=asset_instance,
        initial={'subtype': Asset.Subtype.DISCRETE}
    )
    form_asset.fields['subtype'].disabled = True
    if request.method == 'POST' and all(
        [form_assetdiscretevehicle.is_valid(), form_assetdiscrete.is_valid(), form_asset.is_valid()]
    ):
        asset = form_asset.save()
        assetdiscrete = form_assetdiscrete.save(commit=False)
        assetdiscrete.asset = asset
        assetdiscrete.save()
        assetdiscretevehicle = form_assetdiscretevehicle.save(commit=False)
        assetdiscretevehicle.assetdiscrete = assetdiscrete
        assetdiscretevehicle.save()
        if assetdiscretevehicle_pk:
            return redirect('pyamgmt:assetdiscretevehicle:detail',
                            assetdiscretevehicle_pk=assetdiscretevehicle_pk)
        return redirect('pyamgmt:asset-discrete-vehicle:list')
    context.update({
        'form_asset': form_asset,
        'form_assetdiscrete': form_assetdiscrete,
        'form_assetdiscretevehicle': form_assetdiscretevehicle
    })
    return render(request, 'pyamgmt/models/assetdiscretevehicle_form.html', context)


def assetinventory_list(request):
    """List all records from model AssetInventory."""
    context = {}
    qs_assetinventory = AssetInventory.objects.select_related('asset')
    context.update({'qs_assetinventory': qs_assetinventory})
    return render(request, 'pyamgmt/models/assetinventory_list.html', context)


def assetinventory_detail(request, assetinventory_pk: int):
    context = {}
    assetinventory = AssetInventory.objects.get(pk=assetinventory_pk)
    context.update({
        'assetinventory': assetinventory
    })
    return render(request, 'pyamgmt/models/assetinventory_detail.html', context)


def catalogitem_list(request):
    """List all records from CatalogItem."""
    context = {}
    qs_catalogitem = CatalogItem.objects.all()
    context.update({'qs_catalogitem': qs_catalogitem})
    return render(request, 'pyamgmt/models/catalogitem_list.html', context)


def catalogitem_detail(request, catalogitem_pk: int):
    context = {}
    catalogitem = CatalogItem.objects.get(pk=catalogitem_pk)
    context.update({
        'catalogitem': catalogitem
    })
    return render(request, 'pyamgmt/models/catalogitem_detail.html', context)


def catalogitem_form(request, catalogitem_pk: int = None):
    context = {}
    instance = None
    if catalogitem_pk:
        instance = CatalogItem.objects.get(pk=catalogitem_pk)
    form = CatalogItemForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('pyamgmt:catalogitem:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/catalogitem_form.html', context)


def catalogitemdigitalsong_list(request):
    """List all records from CatalogItemDigitalSong."""
    context = {}
    qs_catalogitemdigitalsong = CatalogItemDigitalSong.objects.all()
    context.update({'qs_catalogitemdigitalsong': qs_catalogitemdigitalsong})
    return render(request, 'pyamgmt/models/catalogitemdigitalsong_list.html', context)


def catalogitemdigitalsong_detail(request, catalogitemdigitalsong_pk: int):
    context = {}
    catalogitemdigitalsong = CatalogItemDigitalSong.objects.get(pk=catalogitemdigitalsong_pk)
    context.update({
        'catalogitemdigitalsong': catalogitemdigitalsong
    })
    return render(request, 'pyamgmt/models/catalogitemdigitalsong_detail.html', context)


@transaction.atomic()
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


@transaction.atomic()
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


def invoice_list(request):
    context = {}
    qs_invoice = (
        Invoice.objects.all()
    )
    context.update({'qs_invoice': qs_invoice})
    return render(request, 'pyamgmt/models/invoice_list.html', context)


def motionpicture_list(request):
    context = {}
    qs_motionpicture = MotionPicture.objects.all()
    context.update({'qs_motionpicture': qs_motionpicture})
    return render(request, 'pyamgmt/models/motionpicture_list.html', context)


def motionpicture_form(request):
    context = {}
    return HttpResponse('uc')


def musicalbum_list(request):
    """List all records from model MusicAlbum."""
    context = {}
    qs_musicalbum = (
        MusicAlbum.objects
        .prefetch_related(
            Prefetch('musicartists', queryset=MusicArtist.objects.order_by('name'))
        )
        .order_by('title')
    )
    print(qs_musicalbum.query)
    context.update({'qs_musicalbum': qs_musicalbum})
    return render(request, 'pyamgmt/models/musicalbum_list.html', context)


def musicalbum_detail(request, musicalbum_pk: int):
    context = {}
    musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
    qs_musicalbumtosongrecording = (
        MusicAlbumToSongRecording.objects
        .filter(musicalbum=musicalbum)
        .select_related('songrecording__song')
        .order_by('disc_number', 'track_number')
    )
    context.update({
        'musicalbum': musicalbum,
        'qs_musicalbumtosongrecording': qs_musicalbumtosongrecording
    })
    return render(request, 'pyamgmt/models/musicalbum_detail.html', context)


def musicalbum_form(request, musicalbum_pk: int = None):
    context = {}
    instance = None
    if musicalbum_pk:
        instance = MusicAlbum.objects.get(pk=musicalbum_pk)
    form = MusicAlbumForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        print(request.POST)
        form.save()
        if musicalbum_pk:
            return redirect('pyamgmt:musicalbum:detail', musicalbum_pk=musicalbum_pk)
        return redirect('pyamgmt:musicalbum:list')
    context.update({'form': form})
    context.update({'deform': form.as_dict()})
    return render(request, 'pyamgmt/models/musicalbum_form.html', context)


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


def musicalbum_add_songrecording_form(request, musicalbum_pk: int):
    context = {}
    musicalbum = MusicAlbum.objects.get(pk=musicalbum_pk)
    form = MusicAlbumToSongRecordingForm(request.POST or None, musicalbum=musicalbum)
    context.update({
        'form': form,
        'musicalbum': musicalbum
    })
    return render(request, 'pyamgmt/models/musicalbum_add_songrecording_form.html', context)


def musicalbumtomusicartist_list(request):
    """List all records from model MusicAlbumToMusicArtist."""
    context = {}
    qs_musicalbumtomusicartist = MusicAlbumToMusicArtist.objects.select_related('musicalbum', 'musicartist')
    context.update({'qs_musicalbumtomusicartist': qs_musicalbumtomusicartist})
    return render(request, 'pyamgmt/models/musicalbumtomusicartist_list.html', context)


def musicalbumtomusicartist_detail(request, musicalbumtomusicartist_pk: int):
    context = {}
    musicalbumtomusicartist = MusicAlbumToMusicArtist.objects.get(pk=musicalbumtomusicartist_pk)
    context.update({
        'musicalbumtomusicartist': musicalbumtomusicartist
    })
    return render(request, 'pyamgmt/models/musicalbumtomusicartist_detail.html', context)


def musicalbumtomusicartist_form(request, musicalbumtomusicartist_pk: int = None, musicartist_pk: int = None):
    context = {}
    instance = None
    initial = None
    if musicalbumtomusicartist_pk:
        instance = MusicAlbumToMusicArtist.objects.get(pk=musicalbumtomusicartist_pk)
    if musicartist_pk:
        music_artist = MusicArtist.objects.get(pk=musicartist_pk)
        initial = {'music_artist': music_artist}
    form = MusicAlbumToMusicArtistForm(request.POST or None, instance=instance, initial=initial)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if musicalbumtomusicartist_pk:
            return redirect('pyamgmt:musicalbumtomusicartist:detail',
                            musicalbumtomusicartist_pk=musicalbumtomusicartist_pk)
        if musicartist_pk:
            return redirect('pyamgmt:musicartist:detail', musicartist_pk=musicartist_pk)
        return redirect('pyamgmt:music-album-to-music-artist:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/musicalbumtomusicartist_form.html', context)


def musicalbumtosongrecording_list(request):
    """"""
    context = {}
    qs_musicalbumtosongrecording = (
        MusicAlbumToSongRecording.objects
        .select_related('musicalbum', 'songrecording__song')
    )
    context.update({'qs_musicalbumtosongrecording': qs_musicalbumtosongrecording})
    return render(request, 'pyamgmt/models/musicalbumtosongrecording_list.html', context)


def musicalbumtosongrecording_detail(request, musicalbumtosongrecording_pk: int):
    context = {}
    musicalbumtosongrecording = (
        MusicAlbumToSongRecording.objects
        .select_related('musicalbum', 'songrecording__song')
        .get(pk=musicalbumtosongrecording_pk)
    )
    context.update({'musicalbumtosongrecording': musicalbumtosongrecording})
    return render(request, 'pyamgmt/models/musicalbumtosongrecording_detail.html', context)


def musicalbumtosongrecording_form(request, musicalbumtosongrecording_pk: int = None):
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


def musicartist_list(request):
    """List all records from model MusicArtist."""
    context = {}
    qs_musicartist = MusicArtist.objects.order_by('name')
    context.update({'qs_musicartist': qs_musicartist})
    return render(request, 'pyamgmt/models/musicartist_list.html', context)


def musicartist_detail(request, musicartist_pk: int):
    context = {}
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
    context.update({
        'musicartist': musicartist,
        'qs_musicalbumtomusicartist': qs_musicalbumtomusicartist,
        'qs_musicartisttoperson': qs_musicartisttoperson,
        'qs_musicartisttosong': qs_musicartisttosong
    })
    return render(request, 'pyamgmt/models/musicartist_detail.html', context)


def musicartist_form(request, musicartist_pk=None):
    context = {}
    instance = None
    if musicartist_pk:
        instance = MusicArtist.objects.get(pk=musicartist_pk)
    form = MusicArtistForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if musicartist_pk:
            return redirect('pyamgmt:musicartist:detail', musicartist_pk)
        return redirect('pyamgmt:musicartist:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/musicartist_form.html', context)


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


def payee_detail(request, payee_pk: int):
    context = {}
    payee = Payee.objects.get(pk=payee_pk)
    context.update({
        'payee': payee
    })
    return render(request, 'pyamgmt/models/payee_detail.html', context)


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


def person_detail(request, person_pk: int):
    context = {}
    person = Person.objects.get(pk=person_pk)
    context.update({
        'person': person
    })
    return render(request, 'pyamgmt/models/person_detail.html', context)


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


def pointofsale_list(request):
    """List all records from model PointOfSale."""
    context = {}
    qs_pointofsale = PointOfSale.objects.all()
    context.update({'qs_pointofsale': qs_pointofsale})
    return render(request, 'pyamgmt/models/pointofsale_list.html', context)


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


def song_form(request, song_pk: int = None):
    context = {}
    instance = None
    if song_pk:
        instance = Song.objects.get(pk=song_pk)
    form = SongForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if request.POST.get('_addanother'):
            return redirect('pyamgmt:song:add')
        if song_pk:
            return redirect('pyamgmt:song:detail', song_pk=song_pk)
        return redirect('pyamgmt:song:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/song_form.html', context)


def songrecording_list(request):
    context = {}
    qs_songrecording = (
        SongRecording.objects
        .select_related('song')
        .prefetch_related('song__musicartisttosong_set__musicartist')  # original artist
    )
    context.update({'qs_songrecording': qs_songrecording})
    return render(request, 'pyamgmt/models/songrecording_list.html', context)


def songrecording_detail(request, songrecording_pk: int):
    context = {}
    songrecording = SongRecording.objects.select_related('song').get(pk=songrecording_pk)
    related_albums = MusicAlbumToSongRecording.objects.filter(songrecording=songrecording).select_related('musicalbum')
    related_artists = MusicArtistToSongRecording.objects.filter(songrecording=songrecording).select_related('musicartist')
    context.update({
        'songrecording': songrecording,
        'related_albums': related_albums,
        'related_artists': related_artists
    })
    return render(request, 'pyamgmt/models/songrecording_detail.html', context)


def songrecording_form(request, songrecording_pk: int = None):
    context = {}
    instance = None
    if songrecording_pk:
        instance = SongRecording.objects.get(pk=songrecording_pk)
    form = SongRecordingForm(request.POST or None, instance=instance)
    context.update({
        'form': form
    })
    return render(request, 'pyamgmt/models/songrecording_form.html', context)


def songtosong_list(request):
    """"""
    context = {}
    qs_songtosong = SongToSong.objects.all()
    context.update({'qs_songtosong': qs_songtosong})
    return render(request, 'pyamgmt/models/songtosong_list.html', context)


def txn_list(request):
    """List all records from model Txn."""
    context = {}
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
    context.update({'qs_txn': qs_txn})
    return render(request, 'pyamgmt/models/txn_list.html', context)


def txn_detail(request, txn_pk: int):
    context = {}
    txn = Txn.objects.get(pk=txn_pk)
    context.update({
        'txn': txn
    })
    return render(request, 'pyamgmt/models/txn_detail.html', context)


@transaction.atomic()
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
    return render(request, 'pyamgmt/models/txn_form.html', context)


def txnlineitem_list(request):
    return HttpResponse('')


def txnlineitem_detail(request, txnlineitem_pk: int):
    context = {}
    txnlineitem = (
        TxnLineItem.objects
        .select_related('account', 'txn')
        .get(pk=txnlineitem_pk)
    )
    context.update({'txnlineitem': txnlineitem})
    return render(request, 'pyamgmt/models/txnlineitem_detail.html', context)


def unit_list(request):
    """List all records from model Unit."""
    context = {}
    qs_unit = Unit.objects.all()
    context.update({'qs_unit': qs_unit})
    return render(request, 'pyamgmt/models/unit_list.html', context)


def unit_detail(request, unit_pk: int):
    context = {}
    unit = Unit.objects.get(pk=unit_pk)
    context.update({
        'unit': unit
    })
    return render(request, 'pyamgmt/models/unit_detail.html', context)


def unit_form(request, unit_pk: int = None):
    context = {}
    instance = None
    if unit_pk:
        instance = Unit.objects.get(pk=unit_pk)
    form = UnitForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if unit_pk:
            return redirect('pyamgmt:unit:detail', unit_pk=unit_pk)
        return redirect('pyamgmt:unit:list')
    context.update({'form': form})
    print(render(request, 'pyamgmt/models/unit_form.html', context).content)
    return render(request, 'pyamgmt/models/unit_form.html', context)


def vehicle_list(request):
    """List all records from model Vehicle."""
    context = {}
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
            'vin'
        )
    )
    context.update({'qs_vehicle': qs_vehicle})
    return render(request, 'pyamgmt/models/vehicle_list.html', context)


def vehicle_detail(request, vehicle_pk: int):
    context = {}
    vehicle = Vehicle.objects.get(pk=vehicle_pk)
    vehiclemileage_records = VehicleMileage.objects.filter(vehicle=vehicle).order_by('odometer_date', 'odometer_time')
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
            cache.set(cache_key, nhtsa_api_data, 60 * 60 * 24)
    context.update({
        'vehicle': vehicle,
        'vehiclemileage_records': vehiclemileage_records,
        'chart_data': chart_data,
        'average_mileage': average_mileage,
        'nhtsa_api_data': nhtsa_api_data
    })
    return render(request, 'pyamgmt/models/vehicle_detail.html', context)


def vehicle_form(request, vehicle_pk: int = None, vehicleyear_pk: int = None):
    context = {}
    instance = None
    if vehicle_pk:
        instance = Vehicle.objects.get(pk=vehicle_pk)
    form = VehicleForm(request.POST or None, instance=instance, vehicleyear_pk=vehicleyear_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if vehicleyear_pk:
            return redirect('pyamgmt:vehicleyear:detail', vehicleyear_pk=vehicleyear_pk)
        if vehicle_pk:
            return redirect('pyamgmt:vehicle:detail', vehicle_pk=vehicle_pk)
        return redirect('pyamgmt:vehicle:list')
    # context.update({'form': form})
    context.update({'form': form.as_dict()})
    return render(request, 'pyamgmt/models/vehicle_form.html', context)


def vehiclemake_list(request):
    """List all records from model VehicleMake."""
    context = {}
    qs_vehiclemake = (
        VehicleMake.objects
        .annotate(vehiclemodel_count=Count('vehiclemodel'))
        .order_by('name')
    )
    context.update({'qs_vehiclemake': qs_vehiclemake})
    return render(request, 'pyamgmt/models/vehiclemake_list.html', context)


def vehiclemake_detail(request, vehiclemake_pk: int):
    context = {}
    vehiclemake = VehicleMake.objects.get(pk=vehiclemake_pk)
    qs_vehiclemodel = VehicleModel.objects.filter(vehiclemake=vehiclemake).order_by('name')
    context.update({
        'vehiclemake': vehiclemake,
        'qs_vehiclemodel': qs_vehiclemodel
    })
    return render(request, 'pyamgmt/models/vehiclemake_detail.html', context)


def vehiclemake_form(request, vehiclemake_pk: int = None):
    context = {}
    instance = None
    if vehiclemake_pk:
        instance = VehicleMake.objects.get(pk=vehiclemake_pk)
    form = VehicleMakeForm(request.POST or None, instance=instance)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('pyamgmt:vehiclemake:list')
    context.update({'form': form})
    context.update({'test': form.as_dict()})
    return render(request, 'pyamgmt/models/vehiclemake_form.html', context)


def vehiclemileage_list(request):
    """List all records from model VehicleMileage."""
    context = {}
    qs_vehiclemileage = VehicleMileage.objects.all()
    context.update({'qs_vehiclemileage': qs_vehiclemileage})
    return render(request, 'pyamgmt/models/vehiclemileage_list.html', context)


def vehiclemileage_detail(request, vehiclemileage_pk: int):
    context = {}
    vehiclemileage = VehicleMileage.objects.get(pk=vehiclemileage_pk)
    context.update({
        'vehiclemileage': vehiclemileage
    })
    return render(request, 'pyamgmt/models/vehiclemileage_detail.html', context)


def vehiclemileage_form(request, vehiclemileage_pk: int = None, vehicle_pk: int = None):
    context = {}
    instance = None
    if vehiclemileage_pk:
        instance = VehicleMileage.objects.get(pk=vehiclemileage_pk)
    form = VehicleMileageForm(request.POST or None, instance=instance, vehicle_pk=vehicle_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if vehiclemileage_pk:
            return redirect('pyamgmt:vehiclemileage:detail', vehiclemileage_pk=vehiclemileage_pk)
        if vehicle_pk:
            return redirect('pyamgmt:vehicle:detail', vehicle_pk=vehicle_pk)
        return redirect('pyamgmt:vehiclemileage:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/vehiclemileage_form.html', context)


def vehiclemodel_list(request):
    """List all records from model VehicleModel."""
    context = {}
    qs_vehiclemodel = (
        VehicleModel.objects
        .select_related('vehiclemake')
        .annotate(vehicletrim_count=Count('vehicletrim'))
        .order_by('vehiclemake__name', 'name')
    )
    context.update({'qs_vehiclemodel': qs_vehiclemodel})
    return render(request, 'pyamgmt/models/vehiclemodel_list.html', context)


def vehiclemodel_detail(request, vehiclemodel_pk: int):
    context = {}
    vehiclemodel = VehicleModel.objects.get(pk=vehiclemodel_pk)
    qs_vehicletrim = VehicleTrim.objects.filter(vehiclemodel=vehiclemodel).order_by('name')
    context.update({
        'vehiclemodel': vehiclemodel,
        'qs_vehicletrim': qs_vehicletrim
    })
    return render(request, 'pyamgmt/models/vehiclemodel_detail.html', context)


def vehiclemodel_form(request, vehiclemodel_pk: int = None, vehiclemake_pk: int = None):
    context = {}
    instance = None
    if vehiclemodel_pk:
        instance = VehicleModel.objects.get(pk=vehiclemodel_pk)
    form = VehicleModelForm(request.POST or None, instance=instance, vehiclemake_pk=vehiclemake_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if vehiclemake_pk:
            return redirect('pyamgmt:vehiclemake:detail', vehiclemake_pk=vehiclemake_pk)
        return redirect('pyamgmt:vehiclemodel:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/vehiclemodel_form.html', context)


def vehicletrim_list(request):
    """List all records from model VehicleTrim."""
    context = {}
    qs_vehicletrim = (
        VehicleTrim.objects
        .select_related('vehiclemodel__vehiclemake')
        .order_by(
            'vehiclemodel__vehiclemake__name',
            'vehiclemodel__name',
            'name'
        )
    )
    context.update({'qs_vehicletrim': qs_vehicletrim})
    return render(request, 'pyamgmt/models/vehicletrim_list.html', context)


def vehicletrim_detail(request, vehicletrim_pk: int):
    context = {}
    vehicletrim = VehicleTrim.objects.get(pk=vehicletrim_pk)
    qs_vehicleyear = VehicleYear.objects.filter(vehicletrim=vehicletrim).order_by('year')
    context.update({
        'vehicletrim': vehicletrim,
        'qs_vehicleyear': qs_vehicleyear
    })
    return render(request, 'pyamgmt/models/vehicletrim_detail.html', context)


def vehicletrim_form(request, vehicletrim_pk: int = None, vehiclemodel_pk: int = None):
    context = {}
    instance = None
    if vehicletrim_pk:
        instance = VehicleTrim.objects.get(pk=vehicletrim_pk)
    form = VehicleTrimForm(request.POST or None, instance=instance, vehiclemodel_pk=vehiclemodel_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if vehiclemodel_pk:
            return redirect('pyamgmt:vehiclemodel:detail', vehiclemodel_pk=vehiclemodel_pk)
        if vehicletrim_pk:
            return redirect('pyamgmt:vehicletrim:detail', vehicletrim_pk=vehicletrim_pk)
        return redirect('pyamgmt:vehicletrim:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/vehicletrim_form.html', context)


def vehicleyear_list(request):
    """List all records from model VehicleYear."""
    context = {}
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
    context.update({'qs_vehicleyear': qs_vehicleyear})
    return render(request, 'pyamgmt/models/vehicleyear_list.html', context)


def vehicleyear_detail(request, vehicleyear_pk: int):
    context = {}
    vehicleyear = VehicleYear.objects.get(pk=vehicleyear_pk)
    qs_vehicle = Vehicle.objects.filter(vehicleyear=vehicleyear).order_by('vin')
    context.update({
        'vehicleyear': vehicleyear,
        'qs_vehicle': qs_vehicle
    })
    return render(request, 'pyamgmt/models/vehicleyear_detail.html', context)


def vehicleyear_form(request, vehicleyear_pk: int = None, vehicletrim_pk: int = None):
    context = {}
    instance = None
    if vehicleyear_pk:
        instance = VehicleYear.objects.get(pk=vehicleyear_pk)
    form = VehicleYearForm(request.POST or None, instance=instance, vehicletrim_pk=vehicletrim_pk)
    if request.method == 'POST' and form.is_valid():
        form.save()
        if vehicletrim_pk:
            return redirect('pyamgmt:vehicletrim:detail', vehicletrim_pk=vehicletrim_pk)
        return redirect('pyamgmt:vehicleyear:list')
    context.update({'form': form})
    return render(request, 'pyamgmt/models/vehicleyear_form.html', context)
