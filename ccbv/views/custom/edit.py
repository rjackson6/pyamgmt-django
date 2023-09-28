"""
2023-04-24: Revisiting the supertype / subtype forms

This is the primary usecase that I want to support with a class-based view.
Native ones get most of the way there, but I want to be able to include multiple
model forms in the same class.

I don't think this needs to apply to foreign key relationships. Those are better
with formsets (specifically, inline formsets).

Rather, the "is-a" relationship is what I want to edit in the same view.

I guess there could be a case where I want to display multiple model forms that
are creating or modifying one record each. I'm not sure how to do that
intuitively.

For supertype/subtype, there are a few things going for me:
- primary key
  - The OneToOneField on the subtype will point to the parent class.
  - This can also infer dependency for saving.
  - That field can be excluded from display, but should be included in the save
  method.
  - I would still have to tell the class about which ModelForms to use.

BaseCreateView(ModelFormMixin, ProcessFormView):
- object
- get()
- post()

ModelFormMixin(FormMixin, SingleObjectMixin):
- object             -- still singular; one object that 'is-a' subtype
- fields             ** not usable
- get_form_class()   ** get_form_classes()
- get_form_kwargs()  ** get_form_kwargses?
- get_success_url()
- form_valid()       ** forms_valid()

ProcessFormView(View):
- get()
- post()
- put()

FormMixin(ContextMixin):
- initial         ** not usable; needs per-form
- form_class      ** form_classes
- success_url     -- ok
- prefix          ** not usable; each form needs a prefix
--
- get_initial()       ** not usable
- get_prefix()        ** not usable
- get_form_class()    **
- get_form()          ** get_forms()
- get_form_kwargs()   **
- get_success_url()   ** ok
- form_valid          ** forms_valid()
- form_invalid        ** forms_invalid(); any form
- get_context_data()  ** I think this needs to be altered, {'forms': []}

SingleObjectMixin(ContextMixin):
- model                -- ok
- queryset             -- ok
- slug_field           -- ok
- context_object_name  -- ok
- slug_url_kwarg       -- ok
- pk_url_kwarg         -- ok
- query_pk_and_slug    -- ok
- get_object()         -- ok, I think
- get_queryset()
- get_slug_field()
- get_context_object_name()
- get_context_data()   -- ok, I think


Based on this, the classes that need adjustments are:
- FormMixin
- ModelFormMixin
- ProcessFormView
- BaseCreateView

"""

import logging
import typing

from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.views.generic.base import ContextMixin, View
from django.views.generic.detail import (
    SingleObjectMixin, SingleObjectTemplateResponseMixin
)
from django.views.generic.edit import ProcessFormView

logger = logging.getLogger(__name__)


# Yes, I think.
class FormWrapper:
    """Wraps a Form class to defer instantiation until needed by the View."""
    # TODO: dependencies / related_fields
    def __init__(self, form_class, *, prefix=None, initial=None, **kwargs):
        logger.info('FormWrapper.__init__()')
        self.form_class = form_class
        self.prefix = prefix
        self.initial = initial or {}
        self.kwargs = kwargs

    def __call__(self, prefix=None, **kwargs):
        """Returns an instance of form_class with the stored arguments."""
        logger.info('FormWrapper.__call__()')
        return self.form_class(
            prefix=prefix or self.prefix,
            initial=self.initial,
            **self.kwargs,
            **kwargs
        )


class FormCollection:
    """"""
    do_not_call_in_templates = True

    def __init__(self, related_fields=None, **kwargs):
        logger.info('FormCollection.__init__()')
        # since I'm trying to use kwargs as key: form definitions, the Forms
        # should collect under an attribute
        # related_fields has some kind of definition for attribute + saving
        self.forms = {}
        self.related_fields = related_fields or {}
        self._form_wrappers = {}
        for k, v in kwargs.items():
            if isinstance(v, FormWrapper):
                self._form_wrappers[k] = v

    def __call__(self, **kwargs):
        """Instantiate Forms, using the stored keys as prefixes."""
        logger.info('FormCollection.__call__()')
        for k, wrapper in self._form_wrappers.items():
            self.forms[k] = wrapper(prefix=k, **kwargs)
        return self

    def __getitem__(self, item):
        return self.forms[item]

    def __iter__(self):
        yield from self.forms.values()

    def are_valid(self):
        logger.info('FormCollection.are_valid()')
        return all([f for f in self.forms])


class MultipleFormMixin(ContextMixin):
    """Provide a way to show and handle multiple forms in a request."""
    # get_initial
    # get_prefix
    # get_form_class
    forms: FormCollection
    request: HttpRequest

    def get_forms(self):
        logger.info('MultipleFormMixin.get_forms()')
        # Should return instantiated forms
        # original is: return form_class(**self.get_form_kwargs())
        return self.forms(**self.get_form_kwargs())

    def get_form_kwargs(self) -> dict:
        logger.info('MultipleFormMixin.get_form_kwargs()')
        # initial, prefix, data, files
        # initial + prefix are no longer needed
        # data + files should be harmless to share with all forms, although
        # there's room for magic if I need to parse through the POST and FILES
        # data
        # TODO: One problem here is specifying kwargs for a particular form, and
        #  not the others.
        #  I think overriding `get_forms` would work if customization is needed
        #  to this degree.
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs

    def get_success_url(self) -> str:
        # returns a string of class attribute
        ...

    def forms_valid(self, forms) -> HttpResponse:
        # returns an http response (redirect)
        ...
        return HttpResponse('We are valid!')

    def forms_invalid(self, forms) -> HttpResponse:
        # returns render
        ...
        return HttpResponse('We are <i>*not*</i> valid!')

    def get_context_data(self, **kwargs) -> dict:
        logger.info('MultipleFormMixin.get_context_data()')
        # adds "forms" to context
        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms()
        return super().get_context_data(**kwargs)


class OneToOneModelFormMixin(MultipleFormMixin, SingleObjectMixin):
    object: typing.Any

    # fields
    # get_form_class
    def get_form_kwargs(self):
        logger.info('OneToOneModelFormMixin.get_form_kwargs()')
        # needed for "instance", if updating existing records
        kwargs = super().get_form_kwargs()
        # if hasattr(self, "object"): kwargs.update({"instance": self.object})
        # TODO: instance mapping
        #  This would also need some introspection like the related fields
        #  Starting from a central object, the object.attribute needs to supply
        #  that instance to the form, or None if it doesn't exist (but should)
        print(self.forms)  # FormCollection object
        print(self.object)  # SingleObjectMixin, I think
        # We need to know which one "this" object is
        # And we need to know which form applies to "this" instance
        # I could assume that the first form is "this" object, or use special
        # key to indicate that a form maps to the view's "object"
        return kwargs

    def get_success_url(self) -> str:
        # this just checks for get_absolute_url() if success_url isn't defined
        ...

    def forms_valid(self, forms):
        logger.info('OneToOneModelFormMixin.forms_valid()')
        # save behavior; self.object = form.save()
        # with forms, it needs to know about the save order, as well as any
        # inter-related attributes between multiple forms
        ...
        return HttpResponse('ModelForms are, incredibly, valid!')


# Done
class ProcessMultiFormView(ProcessFormView):
    get_forms: typing.Callable
    forms_valid: typing.Callable
    forms_invalid: typing.Callable

    def post(self, request, *args, **kwargs):
        forms = self.get_forms()
        if forms.are_valid():
            return self.forms_valid(forms)
        else:
            return self.forms_invalid(forms)


class BaseOneToOneCreateView(OneToOneModelFormMixin, ProcessMultiFormView):
    object: None

    def get(self, request, **kwargs):
        self.object = None
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        self.object = None
        return super().post(request, **kwargs)


class OneToOneCreateView(
    SingleObjectTemplateResponseMixin, BaseOneToOneCreateView
):
    template_name_suffix = '--form'


class BaseOneToOneUpdateView(OneToOneModelFormMixin, ProcessMultiFormView):
    object: None

    def get(self, request, **kwargs):
        self.object = self.get_object()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        self.object = self.get_object()
        return super().post(request, **kwargs)


class OneToOneUpdateView(
    SingleObjectTemplateResponseMixin, BaseOneToOneUpdateView
):
    template_name_suffix = '--form'
