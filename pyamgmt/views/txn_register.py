from django.shortcuts import render

from pyamgmt.models import *


def txn_register(request):
    context = {}
    txns = (
        Txn.objects
        .select_related('payee')
        .prefetch_related('line_items__account')
        .order_by('-txn_date')
    )
    context.update({'txns': txns})
    return render(request, 'pyamgmt/main/txn_register.html', context)
