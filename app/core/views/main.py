from django.shortcuts import render

from django_ccbv import ListView, TemplateView

from core.models import *


def index(request):
    return render(request, 'core/main.html')


class AccountListView(ListView):
    model = Account
    template_name = 'core/account-list.html'


class TxnRegisterView(TemplateView):
    template_name = 'core/txn-register.html'
