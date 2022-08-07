from django.views import generic

from pyamgmt.models import *


class AccountListView(generic.ListView):
    model = Account

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        print(context.keys())
        return context


class AccountDetailView(generic.DetailView):
    model = Account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        print(dir(self))
        return context


class AccountCreateView(generic.CreateView):
    model = Account
    fields = '__all__'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        return context


class AccountUpdateView(generic.UpdateView):
    model = Account
    fields = '__all__'
    success_url = '../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        return context


class AccountDeleteView(generic.DeleteView):
    model = Account
    success_url = '../../'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context.keys())
        return context
