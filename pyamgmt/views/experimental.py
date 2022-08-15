"""What I'm trying to do is really just one step removed from the existing
API. The existing API has class attributes on the view class:

View.form_class = None
View.initial = {}

All I'm trying to do is insert a namespace:

View.forms.account.form_class
                  .initial
View.forms.accountasset.form_class
                       .initial

That implies a class attribute named "forms", or a dictionary.
Django Form uses dictionary access for fields, e.g., form.fields['name']
So view.forms['account'] wouldn't be all that unusual as a dictionary.
These circle back to the ideas I've tried, using combinations of dictionaries,
classes, and whatever else.

The most obvious is probably dictionaries.

A helper class or helper function *would* help with the constructor though, and
offer some key safety.

A helper class could have independent methods.

If using helpers, eventually they have to return a FormClass for the view to
instantiate from with request data.

View.forms = {
    'account': {},  -> method -> FormClass -> Form
    'accountasset': {}
}

# forms = (
#     modelform_factory_like(...)  -> FormClass
#     modelform_factory_like(...)
# )

forms = {
    'account': modelform_factory_like(...) -> FormClass
}

forms.account = modelform_factory_like(...) -> FormClass

# Achieved by inner class
View.Forms.account = something

# Without an inner class, would probably need __init__()
# That kind of mixes class and instance attributes, though
View.__init__():
    forms.account = modelform_something()

"""

from django.forms import BaseForm
from django.forms.models import modelform_factory

from ccbv.views import CreateView, DeleteView, DetailView, ListView, UpdateView
from ccbv.views.custom.edit import MultiModelFormView, MultiCreateView, MultiUpdateView

from pyamgmt.forms import *
from pyamgmt.models import *


class AccountAssetFormView(MultiModelFormView):
    template_name = 'pyamgmt/home.html'

    form_def = {
        'accountasset': {
            'prefix': 'account-asset',
            'form_class': AccountAssetForm,
            'initial': {},
            'related': {
                'account': {
                    'prefix': 'account',
                    'form_class': AccountForm,
                    'initial': {},
                }
            }
        },
    }


class AccountAssetCreateView(MultiCreateView):
    model = AccountAsset
    # queryset? Will that work?
    template_name = 'pyamgmt/custom/accountasset_form.html'
    form_def = {
        'account': {
            'prefix': 'account',
            'form_class': AccountForm,
            'initial': {}
        },
        'accountasset': {
            'prefix': 'account-asset',
            'form_class': AccountAssetForm,
            'initial': {},
            # foreign key -> remote
            # can't to the many-side without a formset
            'related': [
                # using from_field-to_otherform?
                {
                    'field': 'account',
                    'to': 'account'
                },
                # using shorthand pair of from:to
                # {'account': 'account'},
            ],
        },
    }


class FormContainer:
    def __init__(self, key, **kwargs):
        self.key = key  # accountasset
        self.forms = []
        # factory pattern? It can't return form instances
        # dictionaries won't conflict
        form = object()


# Form(name='accountasset', form_class=AccountAssetForm, related=[], **form_kwargs)
# Form(ctx_name='accountasset', form_class=AccountAssetForm, related=[], **form_kwargs)
# Form(name='accountasset', form_class=AccountAssetForm, related={}, **form_kwargs)

# Resource -> Dependency
# CentralResource;
# So close. "InlineForm" would mix well with "InlineFormSet"
# Don't know if it's worth the complexity

class BuildForm:
    def __init__(self, form_class, **kwargs):
        self.form_class = form_class
        self.form_kwargs = kwargs


BuildForm(AccountForm)


def form_factory(**kwargs):
    return [BuildForm(kwarg) for kwarg in kwargs]

class Magic:
    def __init__(self, **kwargs):
        # each kwarg is a form?
        self._forms = []
        self.__forms = {}
        self.forms = object()
        for key, form_def in kwargs.items():
            setattr(self.forms, key, form_def)

    def __setattr__(self, name, value):
        if isinstance(value, BaseForm):
            self._forms.append(value)
            self.__forms[name] = value
        super().__setattr__(name, value)

class FormDef:
    def __init__(self, form_class, depends_on=None, **form_kwargs):
        pass


class AccountAssetUpdateView(MultiUpdateView):
    model = AccountAsset
    template_name = 'pyamgmt/custom/accountasset_form.html'
    include = Account

    _forms_c = Magic()
    _forms_c.what = FormDef()
    _forms_c.who = FormDef(AccountAssetForm, depends_on=_forms_c.what)

    _forms = form_factory(
        account={'form_class': AccountForm},
        accountasset={'form_class': AccountAssetForm, 'depends_on': 'account'},
        accountassetreal={'form_class': AccountAssetRealForm}
    )

    _forms_b = Magic(
        account=FormDef(AccountForm),
        accountasset=FormDef(AccountAssetForm, depends_on='account')
    )

    # I think this...is the most straightforward, really.
    # Flat instead of nested. Keys should generally work in avoiding collision.
    # Depends on should be some sort of order. list.insert()?
    # Then keep a reference to the saved objects afterwards.
    forms_b = {
        'account': {'form_class': AccountForm},
        'accountasset': {
            'form_class': AccountAssetForm,
            'depends_on': 'account',
        },
        'accountassetreal': {
            'form_class': AccountAssetRealForm,
            'depends_on': 'accountasset',
        }
    }

    forms = {
        'accountasset': {
            'form_class': AccountAssetForm,
            # 'prefix': 'account-asset',
            'related': {
                'account': {
                    'form_class': AccountForm,
                    # 'prefix': 'account',
                }
            }
        }
    }

    form_def = {
        'account': {
            'prefix': 'account',
            'form_class': AccountForm,
            'initial': {}
        },
        'accountasset': {
            'prefix': 'account-asset',
            'form_class': AccountAssetForm,
            'initial': {},
            # foreign key -> remote
            # can't to the many-side without a formset
            'related': [
                # using from_field-to_otherform?
                {
                    'field': 'account',
                    'to': 'account'
                },
                # using shorthand pair of from:to
                # {'account': 'account'},
            ],
        },
    }
