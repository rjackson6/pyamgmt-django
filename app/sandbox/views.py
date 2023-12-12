from functools import partial

from django import forms
from django.shortcuts import render
from django.views.generic import TemplateView

from django_ccbv.views.custom.edit import (
    OneToOneCreateView,
    OneToOneUpdateView,
    FormCollection,
    FormWrapper,
)

from .models import *


class MyFormClass(forms.ModelForm):
    class Meta:
        fields = '__all__'
        model = GeneralTestModel


class SubtypeTemplateView(TemplateView):
    forms = {}

    def get_forms(self):
        return {}

    def get_context_data(self, **kwargs):
        # form_a, form_b, ...
        # form_class(request.POST or None, request.FILES or None, **form_kwargs)
        # forms = {'key/prefix': FormObject}
        return {}

    def post(self, request, **kwargs):
        forms = self.get_forms()
        if all([form.is_valid() for form in self.forms]):
            return
        else:
            return self.render_to_response()


class SomeCustomView:
    form_a = 5000
    dependencies = {
        form_a: None
    }


class TestMultiCreateView(OneToOneCreateView):
    forms = FormCollection(
        abc=FormWrapper(MyFormClass),
        hij=FormWrapper(MyFormClass),
    )
    template_name = 'sandbox/cbv.html'


class TestMultiUpdateView(OneToOneUpdateView):
    pass
