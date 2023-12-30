from django.db.models import Case, Prefetch, When
from django.shortcuts import render

from django_ccbv import ListView, TemplateView

from core.models import Account, Txn, TxnLineItem


def index(request):
    return render(request, 'core/main.html')


class AccountListView(ListView):
    model = Account
    queryset = (
        Account.objects
        .annotate_balance()
        .annotate(
            financial=Case(
                When(account_asset__account_asset_financial__isnull=False,
                     then=True)
            )
        )
        .order_by('financial', 'subtype', 'name')
    )
    template_name = 'core/account-list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['financial_accounts'] = (x for x in self.object_list if x.financial)
        context['other_accounts'] = (x for x in self.object_list if not x.financial)
        return context


class TxnRegisterView(TemplateView):
    template_name = 'core/txn-register.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        account = (
            Account.objects.get(pk=kwargs['account_pk'])
        )
        # Still have to do a prefetch related
        txns = (
            Txn.objects
            .filter(line_items__account=account)
            .prefetch_related(
                Prefetch(
                    'line_items',
                    queryset=(
                        TxnLineItem.objects
                        .select_related('account')
                    )
                )
            )
            .select_related('payee')
            .order_by('-txn_date')
        )
        line_items = (
            TxnLineItem.objects
            .filter(account=account)
            .select_related('account', 'txn__payee')
            .order_by('-txn__txn_date')
        )
        context.update(dict(
            account=account,
            txns=txns,
            line_items=line_items,
        ))
        return context
