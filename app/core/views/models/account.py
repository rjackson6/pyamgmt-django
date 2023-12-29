from django_ccbv.views.generic import DetailView, ListView

from core.models import *


class AccountListView(ListView):
    model = Account
    queryset = (
        Account.objects
        .prefetch_related('txn_line_item_set')
        .order_by('name')
    )
    template_name = 'core/models/account--list.html'
