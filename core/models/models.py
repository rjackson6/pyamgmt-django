__all__ = [
    'Account', 'AccountAsset', 'AccountAssetFinancial', 'AccountAssetReal', 'AccountEquity', 'AccountExpense',
    'AccountIncome', 'AccountLiability',
    'Asset', 'AssetDiscrete', 'AssetDiscreteCatalogItem', 'AssetDiscreteVehicle', 'AssetInventory', 'AssetType',
    'CatalogItem', 'CatalogItemDigitalSong', 'CatalogItemMusicAlbum',
    'CatalogItemToInvoiceLineItem', 'CatalogItemToOrderLineItem', 'CatalogItemToPointOfSaleLineItem',
    'Invoice', 'InvoiceLineItem', 'InvoiceLineItemToNonCatalogItem',
    'MediaFormat',
    'MotionPicture',
    'MusicAlbum', 'MusicAlbumArtwork', 'MusicAlbumToMusicArtist', 'MusicAlbumToSongRecording',
    'MusicArtist', 'MusicArtistToPerson', 'MusicArtistToSong', 'MusicArtistToSongRecording',
    'NonCatalogItem',
    'Order', 'OrderLineItem',
    'Party', 'PartyCompany', 'PartyPerson', 'PartyType', 'Payee', 'Person',
    'PointOfSale', 'PointOfSaleDocument', 'PointOfSaleLineItem',
    'Seller', 'Song', 'SongRecording', 'SongToSong',
    'Txn', 'TxnLineItem',
    'Unit',
    'Vehicle', 'VehicleMake', 'VehicleMileage', 'VehicleModel', 'VehicleTrim', 'VehicleYear'
]

from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey,
    TextChoices,
    SET_DEFAULT, SET_NULL,
)

from base.models import BaseAuditable


def get_default_mediaformat_audio():
    return MediaFormat.get_default_audio()


##########
# MODELS #
##########

class Account(BaseAuditable):
    class Subtype(TextChoices):
        ASSET = 'ASSET'  # Checking, Savings, Real, Discrete, Inventory
        LIABILITY = 'LIABILITY'  # Loan, Mortgage, Credit Card
        EQUITY = 'EQUITY'  # Not sure yet
        INCOME = 'INCOME'  # Salary
        EXPENSE = 'EXPENSE'  # Rent, Utilities, Internet, Fees
        OTHER = 'OTHER'  # Not likely to use
    name = CharField(max_length=255, unique=True)
    parent_account = ForeignKey(
        'self', on_delete=SET_NULL, related_name='child_accounts', null=True,
        blank=True)
    subtype = CharField(
        max_length=9, choices=Subtype.choices, default=Subtype.OTHER)

    # objects = managers.AccountManager()

    def __str__(self) -> str:
        return f'{self.name}'

    def clean(self) -> None:
        if self.parent_account == self:
            raise ValidationError("An account may not be its own parent.")

    @property
    def debit_increases(self) -> bool:
        if self.subtype in (self.Subtype.ASSET, self.Subtype.EXPENSE):
            return True
        elif self.subtype in (
            self.Subtype.EQUITY,
            self.Subtype.INCOME,
            self.Subtype.LIABILITY
        ):
            return False


class MediaFormat(BaseAuditable):
    name = CharField(max_length=255, unique=True)

    @classmethod
    def get_default_audio(cls):
        obj, _ = cls.objects.get_or_create(name='Audio')
        return obj.pk
