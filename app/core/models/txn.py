from decimal import Decimal

from django.db.models import (
    BooleanField, DateField, ForeignKey, TextField,
    PROTECT,
    Sum,
)

from django_base.models import BaseAuditable
from django_base.utils import default_related_names

from . import _querysets
from ._fields import CurrencyField


class Txn(BaseAuditable):
    """A (financial) transaction.

    Should have properties for "total debit" and "total credit" derived from its
    line items, and those values should be equal.
    """

    payee_id: int

    memo = TextField(null=True, blank=True)
    payee = ForeignKey(
        'Payee', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    ref_total = CurrencyField(
        null=True, blank=True,
        verbose_name="Reference Total",
        help_text="Total transaction amount reflected on statement."
    )
    txn_date = DateField()

    objects = _querysets.TxnQuerySet.as_manager()

    @property
    def _is_balanced(self) -> bool:
        return self._total_debits == self._total_credits

    @property
    def _total_credits(self) -> Decimal:
        qs = (
            self.line_items.filter(debit=False)
            .aggregate(
                total_credits=Sum('amount')
            )
        )
        return qs['total_credits'] or 0

    @property
    def _total_debits(self) -> Decimal:
        qs = (
            self.line_items.filter(debit=True)
            .aggregate(
                total_debits=Sum('amount')
            )
        )
        return qs['total_debits'] or 0


class TxnLineItem(BaseAuditable):
    """A line item of a Transaction.

    To support double-entry style accounting, this is where different accounts
    are related to individual debits/credits, and the outer "Transaction" groups
    them together as a total.
    Every transaction should have at least two line items representing the
    "from" and "to" accounts.
    """

    account_id: int
    txn_id: int

    account = ForeignKey(
        'Account', on_delete=PROTECT,
        **default_related_names(__qualname__)
    )
    amount = CurrencyField()
    debit = BooleanField(default=False)
    memo = TextField(null=True, blank=True)
    txn = ForeignKey(
        Txn, on_delete=PROTECT,
        related_name='line_items'
    )

    def __str__(self) -> str:
        return f'TxnLineItem {self.pk}: {self.txn_id}'

    @property
    def entry(self):
        return 'Debit' if self.debit else 'Credit'

    def polarity(self):
        return self.account.debit_polarity(self.debit)

    def value(self) -> Decimal:
        return round(self.polarity() * self.amount, 2)
