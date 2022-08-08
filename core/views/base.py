__all__ = [
    'View',
    'FormView', 'MultiFormView',
]

import copy
import logging
from typing import Callable

from django.core.paginator import Paginator
from django.db.models.query import QuerySet
import django.forms
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.utils.decorators import classonlymethod

import ccbv.views

logger = logging.getLogger("django.request")


# Local Custom Classes
class View(ccbv.views.View):
    def __init__(self):
        super().__init__()
        self.context = {}

    # def get_context_data(self, **kwargs):
    #     return kwargs


class FormView(View):
    def __init__(self):
        super().__init__()
        self.form = None


class Forms:
    def __init__(self):
        self._forms = []

    def are_valid(self):
        return all([form.is_valid() for form in self._forms])

    def __setattr__(self, key, value):
        if isinstance(value, django.forms.BaseForm):
            self._forms.append(value)
        super().__setattr__(key, value)


class MultiFormView(View):
    def __init__(self):
        super().__init__()
        self.forms = Forms()


class ModelView(View):
    pass


class ModelDetailView(ModelView):
    pass
    # content_type = None
    # context_object_name = None
    # extra_context = None
    # model = None
    # pk_url_kwarg = 'pk'
    # query_and_pk_slug = False
    # queryset = None
    # response_class = TemplateResponse
    # slug_field = 'slug'
    # slug_url_kwarg = 'slug'
    # template_engine = None
    # template_name = None
    # template_name_suffix = '_list'

    # get()
    # get_context_data = generic.detail.SingleObjectMixin.get_context_data
    # get_context_object_name = generic.detail.SingleObjectMixin.get_context_object_name
    # get_queryset = generic.detail.SingleObjectMixin.get_queryset
    # get_slug_field = generic.detail.SingleObjectMixin.get_slug_field
    # get_template_names()
    # render_to_response()


class ModelListView(ModelView):
    pass
    # allow_empty = True
    # content_type = None
    # context_object_name = None
    # extra_context = None
    # model = None
    # ordering = None
    # page_kwarg = "page"
    # paginate_by = None  # int
    # paginate_orphans = 0
    # paginator_class = Paginator
    # queryset = None
    # response_class = TemplateResponse
    # template_engine = None
    # template_name = None
    # template_name_suffix = '_list'

    # get = generic.list.BaseListView.get
    # get_allow_empty = generic.list.MultipleObjectMixin.get_allow_empty
    # get_context_data = generic.list.MultipleObjectMixin.get_context_data
    # get_context_object_name = generic.list.MultipleObjectMixin.get_context_object_name
    # get_ordering = generic.list.MultipleObjectMixin.get_ordering
    # get_paginate_by = generic.list.MultipleObjectMixin.get_paginate_by
    # get_paginate_orphans = generic.list.MultipleObjectMixin.get_paginate_orphans
    # get_paginator = generic.list.MultipleObjectMixin.get_paginator
    # get_queryset = generic.list.MultipleObjectMixin.get_queryset
    # get_template_names = generic.list.MultipleObjectTemplateResponseMixin.get_template_names
    # paginate_queryset = generic.list.MultipleObjectMixin.paginate_queryset
    # render_to_response = generic.base.TemplateResponseMixin.render_to_response


class ModelFormView(ModelView):
    def __init__(self):
        super().__init__()
        self.form = None


class ModelMultiFormView(ModelView):
    def __init__(self):
        super().__init__()
        self.forms = Forms()
