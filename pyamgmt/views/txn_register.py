from django.shortcuts import render

from core.views.base import View

from pyamgmt.models import *


class TxnRegister(View):
    def get(self, request, **kwargs):
        txns = (
            Txn.objects
            .select_related('payee')
            .prefetch_related('line_items__account')
            .order_by('-txn_date')
        )
        self.context.update({'txns': txns})
        return render(request, 'pyamgmt/main/txn_register.html', self.context)
