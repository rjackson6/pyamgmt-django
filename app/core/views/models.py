from ccbv.views.generic import DetailView, ListView, TemplateView

from core.models import *


class AccountListView(ListView):
    model = Account
    template_name = 'core/models/account--list.html'
