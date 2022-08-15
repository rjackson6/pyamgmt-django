from django.views import generic

from pyamgmt.forms import *
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


class AccountAssetListView(generic.ListView):
    model = AccountAsset


class AccountAssetDetailView(generic.DetailView):
    model = AccountAsset


class AccountAssetUpdateView(generic.TemplateView):
    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)

    def forms_valid(self):
        pass

    def post(self, request, *args, **kwargs):
        # forms = []
        # if all([form.is_valid(), form2.is_valid()]):
        pass


# TODO: this is the broken part
#  I think the answer is just...don't.
class AccountAssetUpdateView(generic.UpdateView):
    model = AccountAsset
    # fields = '__all__'
    form_class = AccountAssetForm
    related_form_class = ...

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()  # noqa
        form = self.get_form()
        other_form = ...
        if all([form.is_valid(), other_form.is_valid()]):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):  # + other_form(s)
        self.object = form.save()  # noqa
        # other_object = other_form.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        kwargs['forms'] = {
            'form1': self.get_form()
        }
        return super().get_context_data(**kwargs)
