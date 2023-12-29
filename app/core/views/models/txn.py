from django.db.models import Count

from django_ccbv import ListView

from core.models import *


class TxnListView(ListView):
    model = Txn
    queryset = (
        Txn.objects
        .select_related('payee')
        .prefetch_related('line_items__account')
        .annotate(line_item_count=Count('line_items'))
        .order_by('-txn_date')
    )
    template_name = 'core/models/txn--list.html'
