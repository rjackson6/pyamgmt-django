__all__ = []

from django.core.exceptions import ImproperlyConfigured
from django.forms import Form
from django.http import HttpResponseRedirect

from ccbv.views.generic.base import ContextMixin, TemplateResponseMixin, View
from ccbv.views.generic.detail import BaseDetailView, SingleObjectMixin, SingleObjectTemplateResponseMixin


class Forms:
    """A container object for Django Form instances."""
    def __init__(self):
        self._forms = []

    def __iter__(self):
        yield from self._forms


class __MultiFormMixin(ContextMixin):
    """This is yet another attempt at my conventions for transparent multiple
    form handling.
    """

    # The thing is: would I mix regular forms and model forms?
    #  Maybe for a search form. But probably not?
    #  And this links *all* forms with validation logic
    #  So, no, I don't think I would use these outside of model forms.

    # get_context_data <- get_form <- get_form_class <- get_form_kwargs <- get_initial
    #                                                                   <- get_prefix

    # get_context_data <- get_form[s] <- get_form_class[es] <- get_form[s]_kwargs

    # def get_forms(self):
    #     form_kwargs = self.get_form_kwargs()
    #     form_instances = {}
    #     for key, form_def in self.form_def.items():
    #         form_class = form_def['form_class']
    #         form = form_class(
    #             **form_kwargs,
    #             prefix=form_def.get('prefix'),
    #             initial=form_def.get('initial', None)
    #         )
    #         form_instances[key] = form
    #     return form_instances

    def get_form(self, form_class, prefix: str, initial: dict = None, **kwargs):
        return form_class(**kwargs, prefix=prefix, initial=initial)

    def get_forms(self):
        form_kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            form_kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        form_instances = {}
        for key, form_def in self.form_def.items():
            form = self.get_form(
                **form_kwargs,
                form_class=form_def['form_class'],
                prefix=form_def['prefix'],
                initial=form_def.get('initial', None)
            )
            form_instances[key] = form
        return form_instances

    def get_form_kwargs(self):
        # kind of hacky
        kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        return kwargs


class MultiFormMixin(ContextMixin):
    """MRO"""


class MultiModelFormMixin(MultiFormMixin, SingleObjectMixin):
    success_url = None
    forms = {}

    def get_context_data(self, **kwargs) -> dict:
        if 'forms' not in kwargs:
            kwargs['forms'] = self.get_forms()
            # {'form1': ModelForm(), 'form2': ModelForm()
        return super().get_context_data(**kwargs)

    def get_forms(self):
        forms = self.forms.copy()
        forms_b = self.forms_b.copy()

    def get_form(self): pass

    def get_form_kwargs(self): pass

    def get_success_url(self):
        if not self.success_url:
            raise ImproperlyConfigured("No URL to redirect to. Provide a success_url.")
        return str(self.success_url)  # may be lazy

    def forms_valid(self, forms):
        # all forms valid; start with the dependencies?
        # how to generalize...
        # iterator/generator. If the forms save in order, then it's fine
        # the attribute matters for access
        for form in forms:
            # structure needs to be reverse dependencies, or something like that
            obj = form.save()
            for related_obj in obj.related:
                attr = ''
                setattr(related_obj, attr, obj)  # sets the model instance attr
                related_obj.save()
                # for related in ...
                #  I may have reinvented the nested serializer
            pass
        model1 = form.save()
        model2 = form.save(commit=False)
        attr = ''
        setattr(model2, attr, model1)
        model2.save()
        model3 = form.save(commit=False)
        setattr(model3, attr, model2)
        model3.save()
        model4 = form.save(commit=False)
        setattr(model4, attr, model2)
        model4.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        return self.render_to_response(self.get_context_data(forms=forms))


class __MultiModelFormMixin(__MultiFormMixin, SingleObjectMixin):
    # TODO: This may or may not be SingleObject in our use case.
    #  There's a subtype use. There's maybe a related model use.
    #  E.g.: Single primary key + scope (Account vs. AccountAsset)
    #  E.g.: Single primary key + Single Object + Related (FormSet?)
    #  Would we ever try to attempt two separate models?
    #    Probably not. It doesn't make sense as an API.
    #    So let's say, single object is like "Central Object". "Main Object".
    #  Related through attribute could...be the key here?
    #  Kind of like an inline formset.
    #  At least if editing multiple instances.
    #  That's how they would pass through.

    #  TODO: As a rule, I think disallow some of the magic.
    #   and eventually rename this to something like
    #   "ModelFormWithRelatedObjects"

    # fields -> doesn't make sense, unless using a dictionary between the model classes
    # models -> doesn't make sense, since a form_class will be required
    # NO modelform_factory. Just write a form class.
    # form_class is the earliest return from the original method, anyway

    # instance(s) need to be set though.
    # TODO: There needs to be a related-by definition
    #  form1: "central" object; gets instance
    #  form2: "related_on = form1.field"
    #  form3: "related_on = form2.field"

    # TODO: This is where instance= gets set
    # def get_form_kwargs(self):
    #     kwargs = super().get_form_kwargs()  # data, files

    def get_forms(self):
        form_kwargs = {}
        if self.request.method in ('POST', 'PUT'):
            form_kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        form_instances = {}
        for key, form_def in self.form_def.items():
            form_kwargs = form_kwargs.copy()
            form_class = form_def['form_class']
            if hasattr(self, 'object') and isinstance(self.object, form_class.Meta.model):
                # This is the target object of SingleObjectMixin
                form_kwargs.update({'instance': self.object})
            # This won't work until an instance has been determined
            # TODO: Either split the def (form_def, related_forms)
            #       OR make order of definition required (assume first form is
            #       resource target)
            #       OR, single form_def with a key for "related"
            elif related := form_def.get('related', None):
                for i in related:
                    field = i['field']
                    to = i['to']

            form = self.get_form(
                **form_kwargs,
                form_class=form_class,
                prefix=form_def['prefix'],
                initial=form_def.get('initial', None)
            )
            form_instances[key] = form
        return form_instances

    def get_success_url(self) -> str:
        if self.success_url:
            url = self.success_url.format(**self.object.__dict__)
        else:
            try:
                url = self.object.get_absolute_url()
            except AttributeError:
                raise ImproperlyConfigured(
                    "No URL to redirect to. Either provide success_url or"
                    " define a get_absolute_url method on the Model."
                )
        return url

    def forms_valid(self, forms):
        for index, form in enumerate(forms):
            if not index:
                self.object = form.save()
            else:
                form.save()  # throw away the other objects?
        return super().forms_valid(forms)


class ProcessMultiFormView(View):
    def get(self, request, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, **kwargs):
        forms = self.get_forms()
        # if forms.are_valid():
        if all([form.is_valid() for form in forms]):
            return self.forms_valid()
        else:
            return self.forms_invalid()

    def put(self, request, **kwargs):
        return self.post(**kwargs)


class BaseMultiModelFormView(MultiModelFormMixin, ProcessMultiFormView):
    pass


class MultiModelFormView(TemplateResponseMixin, BaseMultiModelFormView):
    pass


class BaseMultiCreateView(MultiModelFormMixin, ProcessMultiFormView):
    def get(self, request, **kwargs):
        self.object = None
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        self.object = None
        return super().get(request, **kwargs)


class MultiCreateView(SingleObjectTemplateResponseMixin, BaseMultiCreateView):
    template_name_suffix = '_form'


class BaseMultiUpdateView(MultiModelFormMixin, ProcessMultiFormView):
    def get(self, request, **kwargs):
        self.object = self.get_object()
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        self.object = self.get_object()
        return super().get(request, **kwargs)


class MultiUpdateView(SingleObjectTemplateResponseMixin, BaseMultiUpdateView):
    template_name_suffix = '_form'


class MultiDeletionMixin:
    """For what we're doing...it would be chained deletion, right?
    Deletion from subclass to superclass.
    """
    success_url = None

    def delete(self, request, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()  # TODO
        return HttpResponseRedirect(success_url)

    def post(self, request, **kwargs):
        return self.delete(request, **kwargs)

    def get_success_url(self):
        if self.success_url:
            return self.success_url.format(**self.object.__dict__)
        else:
            raise ImproperlyConfigured(
                "No URL to redirect to. Provide a success_url"
            )


class BaseMultiDeleteView(MultiDeletionMixin, MultiFormMixin, BaseDetailView):
    form_class = Form

    def post(self, request, **kwargs):
        self.object = self.get_object()
        form = self.get_form()  # Our "confirm delete" form
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.delete()  # TODO
        return HttpResponseRedirect(success_url)


class DeleteView(SingleObjectTemplateResponseMixin, BaseMultiDeleteView):
    template_name_suffix = "_confirm_delete"
