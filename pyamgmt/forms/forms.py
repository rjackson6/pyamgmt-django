__all__ = [
    'AccountForm', 'AccountAssetForm', 'AccountAssetFinancialForm', 'AccountAssetRealForm', 'AccountExpenseForm',
    'AccountIncomeForm', 'AccountLiabilityForm',
    'AssetForm', 'AssetFormVehicle', 'AssetDiscreteForm', 'AssetDiscreteVehicleForm',
    'CatalogueItemForm', 'CatalogueItemDigitalSongForm', 'CatalogueItemMusicAlbumForm',
    'CatalogueItemToPointOfSaleLineItemForm',
    'MusicAlbumForm', 'MusicAlbumToMusicArtistForm', 'MusicAlbumToSongForm', 'MusicArtistForm',
    'MusicArtistToPersonForm',
    'PartyForm', 'PayeeForm', 'PersonForm', 'PointOfSaleForm', 'PointOfSaleDocumentForm', 'PointOfSaleLineItemForm',
    'SongForm',
    'TxnForm',
    'UnitForm',
    'VehicleForm', 'VehicleMakeForm', 'VehicleMileageForm', 'VehicleModelForm', 'VehicleTrimForm', 'VehicleYearForm',
    # FormSets
    'MusicAlbumToSongFormSet',
    'TxnLineItemFormSet'
]

from django import forms

from deform.forms import ModelForm, inlineformset_factory

from pyamgmt.forms.fields import *
from pyamgmt.models import *

BASE_AUDITABLE_FIELDS = ('timestamp_created', 'timestamp_modified')


class AccountForm(ModelForm):
    prefix = 'account'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if hasattr(self.instance, 'id'):  # hasattr(self, 'instance') and...
            self.fields['parent_account'].queryset = Account.objects.exclude(id=self.instance.id)

    class Meta:
        model = Account
        exclude = BASE_AUDITABLE_FIELDS


class AccountAssetForm(ModelForm):
    """Used in conjunction with supertype form."""
    prefix = 'account-asset'

    class Meta:
        model = AccountAsset
        exclude = BASE_AUDITABLE_FIELDS + ('account',)


class AccountAssetFinancialForm(ModelForm):
    """Used in conjunction with supertype form."""
    prefix = 'account-asset-financial'

    class Meta:
        model = AccountAssetFinancial
        exclude = BASE_AUDITABLE_FIELDS + ('accountasset',)


class AssetModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f'{obj.description}'


class AccountAssetRealForm(ModelForm):
    """Used in conjuction with supertype form."""
    prefix = 'account-asset-real'

    def __init__(self, *args, **kwargs):
        # Override the queryset on Asset
        super().__init__(*args, **kwargs)
        self.fields['asset'].queryset = Asset.objects.filter(subtype=Asset.Subtype.DISCRETE)

    class Meta:
        model = AccountAssetReal
        exclude = BASE_AUDITABLE_FIELDS + ('accountasset',)
        field_classes = {
            'asset': AssetModelChoiceField
        }


class AccountAssetRealSubtypeForm(ModelForm):
    """Used only for subclassing an existing AccountAsset record."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['account_asset'].queryset = AccountAsset.objects.exclude(subtype=AccountAsset.Subtype.FINANCIAL)

    class Meta:
        model = AccountAssetReal
        exclude = BASE_AUDITABLE_FIELDS


class AccountExpenseForm(ModelForm):
    """Used in conjunction with supertype form."""
    prefix = 'account-expense'

    class Meta:
        model = AccountExpense
        exclude = BASE_AUDITABLE_FIELDS + ('account',)


class AccountIncomeForm(ModelForm):
    """Used in conjunction with supertype form."""
    prefix = 'account-income'

    class Meta:
        model = AccountIncome
        exclude = BASE_AUDITABLE_FIELDS + ('account',)


class AccountLiabilityForm(ModelForm):
    """Used in conjunction with supertype form."""
    prefix = 'account-liability'

    class Meta:
        model = AccountLiability
        exclude = BASE_AUDITABLE_FIELDS + ('account',)


class AssetForm(ModelForm):
    prefix = 'asset'

    class Meta:
        model = Asset
        exclude = BASE_AUDITABLE_FIELDS


class AssetFormVehicle(ModelForm):
    # Could use keyword arguments instead and re-use the form
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['subtype'] = Asset.Subtype.VEHICLE
        self.fields['subtype'].disabled = True

    class Meta:
        model = Asset
        exclude = BASE_AUDITABLE_FIELDS


class AssetDiscreteForm(ModelForm):
    prefix = 'asset-discrete'

    class Meta:
        model = AssetDiscrete
        exclude = BASE_AUDITABLE_FIELDS + ('asset',)


class AssetDiscreteCatalogueItemForm(ModelForm):
    prefix = 'asset-discrete-catalogue-item'

    class Meta:
        model = AssetDiscreteCatalogueItem
        exclude = BASE_AUDITABLE_FIELDS + ('assetdiscrete',)


class AssetDiscreteVehicleForm(ModelForm):
    prefix = 'asset-discrete-vehicle'

    class Meta:
        model = AssetDiscreteVehicle
        exclude = BASE_AUDITABLE_FIELDS + ('assetdiscrete',)


class CatalogueItemForm(ModelForm):
    class Meta:
        model = CatalogueItem
        exclude = BASE_AUDITABLE_FIELDS


class CatalogueItemDigitalSongForm(ModelForm):
    class Meta:
        model = CatalogueItemDigitalSong
        exclude = BASE_AUDITABLE_FIELDS


class CatalogueItemMusicAlbumForm(ModelForm):
    class Meta:
        model = CatalogueItemMusicAlbum
        exclude = BASE_AUDITABLE_FIELDS


class CatalogueItemToPointOfSaleLineItemForm(ModelForm):
    class Meta:
        model = CatalogueItemToPointOfSaleLineItem
        exclude = BASE_AUDITABLE_FIELDS


class MusicAlbumForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['musicartists'].queryset = MusicArtist.objects.order_by('name')

    class Meta:
        model = MusicAlbum
        exclude = BASE_AUDITABLE_FIELDS + ('songs',)


class MusicAlbumToMusicArtistForm(ModelForm):
    def __init__(self, *args, **kwargs):
        musicartist = kwargs.pop('musicartist', None)
        super().__init__(*args, **kwargs)
        if musicartist in self.initial:
            self.initial['musicartist'] = musicartist
            self.fields['musicartist'].disabled = True

    class Meta:
        model = MusicAlbumToMusicArtist
        exclude = BASE_AUDITABLE_FIELDS


class MusicAlbumToSongForm(ModelForm):
    pass
    # def __init__(self, *args, **kwargs):
    #     musicalbum = kwargs.pop('musicalbum', None)
    #     # song = kwargs.pop('song', None)  # If coming from other model
    #     super().__init__(*args, **kwargs)
    #     if musicalbum is not None:
    #         self.initial['musicalbum'] = musicalbum
    #         self.fields['musicalbum'].disabled = True
    #
    # class Meta:
    #     model = MusicAlbumToSong
    #     exclude = BASE_AUDITABLE_FIELDS


MusicAlbumToSongFormSet = None
# inlineformset_factory(
#     MusicAlbum,
#     MusicAlbumToSong,
#     fields='__all__'
# )


class MusicArtistForm(ModelForm):
    class Meta:
        model = MusicArtist
        exclude = BASE_AUDITABLE_FIELDS + ('songs',)


class MusicArtistToPersonForm(ModelForm):
    # TODO: Should probably be a formset, too
    def __init__(self, *args, **kwargs):
        music_artist = kwargs.pop('music_artist')
        super().__init__(*args, **kwargs)
        if music_artist:
            self.initial['music_artist'] = music_artist
            self.fields['music_artist'].disabled = True

    class Meta:
        model = MusicArtistToPerson
        exclude = BASE_AUDITABLE_FIELDS


class PartyForm(ModelForm):
    class Meta:
        model = Party
        exclude = BASE_AUDITABLE_FIELDS


class PayeeForm(ModelForm):
    class Meta:
        model = Payee
        exclude = BASE_AUDITABLE_FIELDS


class PersonForm(ModelForm):
    class Meta:
        model = Person
        exclude = BASE_AUDITABLE_FIELDS


class PointOfSaleForm(ModelForm):
    class Meta:
        model = PointOfSale
        exclude = BASE_AUDITABLE_FIELDS


class PointOfSaleDocumentForm(ModelForm):
    def __init__(self, *args, **kwargs):
        point_of_sale_id = kwargs.pop('point_of_sale_id')
        super().__init__(*args, **kwargs)
        if point_of_sale_id:
            point_of_sale = PointOfSale.objects.get(id=point_of_sale_id)
            self.initial['point_of_sale'] = point_of_sale
            self.fields['point_of_sale'].disabled = True

    class Meta:
        model = PointOfSaleDocument
        exclude = BASE_AUDITABLE_FIELDS


class PointOfSaleLineItemForm(ModelForm):
    def __init__(self, *args, **kwargs):
        point_of_sale_id = kwargs.pop('point_of_sale_id')
        super().__init__(*args, **kwargs)
        if point_of_sale_id:
            point_of_sale = PointOfSale.objects.get(id=point_of_sale_id)
            self.initial['point_of_sale'] = point_of_sale
            self.fields['point_of_sale'].disabled = True

    class Meta:
        model = PointOfSaleLineItem
        exclude = BASE_AUDITABLE_FIELDS


class SongForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['musicartists'].queryset = MusicArtist.objects.order_by('name')

    class Meta:
        model = Song
        exclude = BASE_AUDITABLE_FIELDS


class TxnForm(ModelForm):
    class Meta:
        model = Txn
        exclude = BASE_AUDITABLE_FIELDS


TxnLineItemFormSet = forms.inlineformset_factory(
    Txn,
    TxnLineItem,
    fields='__all__',
    extra=2
)


class UnitForm(ModelForm):
    class Meta:
        model = Unit
        exclude = BASE_AUDITABLE_FIELDS


class VehicleForm(ModelForm):
    def __init__(self, *args, **kwargs):
        vehicleyear_pk = kwargs.pop('vehicleyear_pk')
        super().__init__(*args, **kwargs)
        if vehicleyear_pk:
            vehicleyear = VehicleYear.objects.get(pk=vehicleyear_pk)
            self.initial['vehicleyear'] = vehicleyear
            self.fields['vehicleyear'].disabled = True

    class Meta:
        model = Vehicle
        exclude = BASE_AUDITABLE_FIELDS
        field_classes = {
            'vehicleyear': VehicleYearChoiceField
        }


class VehicleMakeForm(ModelForm):
    class Meta:
        model = VehicleMake
        exclude = BASE_AUDITABLE_FIELDS


class VehicleMileageForm(ModelForm):  # forms.ModelForm
    def __init__(self, *args, **kwargs):
        vehicle_pk = kwargs.pop('vehicle_pk')
        super().__init__(*args, **kwargs)
        if vehicle_pk:
            vehicle = Vehicle.objects.get(id=vehicle_pk)
            self.initial['vehicle'] = vehicle
            self.fields['vehicle'].disabled = True

    class Meta:
        model = VehicleMileage
        exclude = BASE_AUDITABLE_FIELDS


class VehicleModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        vehiclemake_pk = kwargs.pop('vehiclemake_pk')
        super().__init__(*args, **kwargs)
        if vehiclemake_pk:
            vehiclemake = VehicleMake.objects.get(id=vehiclemake_pk)
            self.initial['vehiclemake'] = vehiclemake
            self.fields['vehiclemake'].disabled = True

    class Meta:
        model = VehicleModel
        exclude = BASE_AUDITABLE_FIELDS


class VehicleTrimForm(ModelForm):
    def __init__(self, *args, **kwargs):
        vehiclemodel_pk = kwargs.pop('vehiclemodel_pk')
        super().__init__(*args, **kwargs)
        if vehiclemodel_pk:
            vehiclemodel = VehicleModel.objects.get(pk=vehiclemodel_pk)
            self.initial['vehiclemodel'] = vehiclemodel
            self.fields['vehiclemodel'].disabled = True

    class Meta:
        model = VehicleTrim
        exclude = BASE_AUDITABLE_FIELDS


class VehicleYearForm(ModelForm):
    def __init__(self, *args, **kwargs):
        vehicletrim_pk = kwargs.pop('vehicletrim_pk')
        super().__init__(*args, **kwargs)
        if vehicletrim_pk:
            vehicletrim = VehicleTrim.objects.get(id=vehicletrim_pk)
            self.initial['vehicletrim'] = vehicletrim
            self.fields['vehicletrim'].disabled = True

    class Meta:
        model = VehicleYear
        exclude = BASE_AUDITABLE_FIELDS
