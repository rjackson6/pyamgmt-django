from django.core.exceptions import ValidationError
from django.db.models import (
    CharField, ForeignKey, OneToOneField,
    TextChoices,
    CASCADE, PROTECT, SET_NULL,
    Manager,
)

from django_base.models.models import BaseAuditable
from django_base.utils import default_related_names, pascal_case_to_snake_case

from . import _managers


# region Account
class Account(BaseAuditable):
    """Double-entry style account.

    If money goes into it or comes out of it, literally or figuratively, it may
    be tracked as an account.
    Assets, Expenses, Dividends, Losses:
        increased by debit; decreased by credit
    Liabilities, Income, Capital, Revenue, Gains, Equity:
        decreased by debit; increased by credit
    """

    class Subtype(TextChoices):
        ASSET = 'ASSET'  # Checking, Savings, Real, Discrete, Inventory
        LIABILITY = 'LIABILITY'  # Loan, Mortgage, Credit Card
        EQUITY = 'EQUITY'  # Not sure yet
        INCOME = 'INCOME'  # Salary
        EXPENSE = 'EXPENSE'  # Rent, Utilities, Internet, Fees
        OTHER = 'OTHER'  # Not likely to use
    name = CharField(max_length=255, unique=True)
    parent_account = ForeignKey(
        'self',
        on_delete=SET_NULL,
        related_name='child_accounts',
        null=True,
        blank=True
    )
    subtype = CharField(
        max_length=9, choices=Subtype.choices, default=Subtype.OTHER
    )

    objects = _managers.AccountManager()
    assets = _managers.AccountManagerAsset()
    liabilities = _managers.AccountManagerLiability()
    equities = _managers.AccountManagerEquity()
    incomes = _managers.AccountManagerIncome()
    expenses = _managers.AccountManagerExpense()

    def __str__(self) -> str:
        return f'{self.name}'

    def clean(self) -> None:
        if self.parent_account == self:
            raise ValidationError("An account may not be its own parent.")

    @property
    def balance(self) -> int:
        return 0

    def debit_polarity(self, debit: bool) -> int:
        if self.debit_increases is debit:
            return 1
        else:
            return -1

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


# region AccountAsset
class AccountAsset(BaseAuditable):
    """An asset account.

    Examples: a bank checking account, or a physical item with value.
    """

    class Subtype(TextChoices):
        FINANCIAL = 'FINANCIAL', 'FINANCIAL'
        REAL = 'REAL', 'REAL'
        OTHER = 'OTHER', 'OTHER'

    account = OneToOneField(
        Account, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_id: int
    subtype = CharField(
        max_length=31, choices=Subtype.choices, default=Subtype.OTHER
    )

    objects = Manager()
    financials = _managers.AccountAssetManagerFinancial()
    real = _managers.AccountAssetManagerReal()


class AccountAssetFinancial(BaseAuditable):
    """An asset which is monetary.

    Examples: a cash or checking account.
    """
    account_asset = OneToOneField(
        AccountAsset, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_asset_id: int
    account_number = CharField(max_length=63, null=True, blank=True)
    institution = None  # TODO 2023-12-12


class AccountAssetReal(BaseAuditable):
    """A real asset.

    Examples: a vehicle, or real estate.
    Implies inherent value, and may be subject to depreciation.
    """
    account_asset = OneToOneField(
        AccountAsset, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_asset_id: int
    # TODO 2023-12-12: Decide if I want `limit_choices_to=` here. If so, needs a
    #  callback.
    asset = ForeignKey(
        'Asset',
        on_delete=SET_NULL,
        null=True,
        blank=True,
        **default_related_names(__qualname__)
    )
    asset_id: int
# endregion AccountAsset


class AccountEquity(BaseAuditable):
    """A business model included for completeness

    Examples: Common Stock, Paid-In Capital.
    """
    account = OneToOneField(
        Account, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_id: int


class AccountExpense(BaseAuditable):
    """An expense account.

    Examples: Utilities, Rent, or Fuel.
    """
    account = OneToOneField(
        Account, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_id: int


class AccountIncome(BaseAuditable):
    """An income account.

    Examples: Salary, dividends
    """
    account = OneToOneField(
        Account, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_id: int


class AccountLiability(BaseAuditable):
    """A liability account.

    Examples: a loan, mortgage, or credit card
    Notes:
        Secured vs Unsecured
        Revolving vs Non-Revolving
        - Credit card is Unsecured, Revolving
        - Mortgage is Secured, Non-Revolving
        - Car Loan is Secured, Non-Revolving
        - HELOC is Secured (by equity)
            - somewhat revolving? Open term with a limit?
    """
    class Subtype(TextChoices):
        SECURED = 'SECURED', 'SECURED'
        OTHER = 'OTHER', 'OTHER'
    account = OneToOneField(
        Account, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_id: int
    account_number = CharField(max_length=63, null=True, blank=True)
    lender = None  # TODO 2023-12-12
    subtype = CharField(
        max_length=15, choices=Subtype.choices, default=Subtype.OTHER
    )


class AccountLiabilitySecured(BaseAuditable):
    """A liability account that is held against an asset."""
    account_liability = OneToOneField(
        AccountLiability, on_delete=CASCADE, primary_key=True,
        related_name=pascal_case_to_snake_case(__qualname__)
    )
    account_liability_id: int
    asset = ForeignKey(
        'Asset', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    asset_id: int
# endregion Account
