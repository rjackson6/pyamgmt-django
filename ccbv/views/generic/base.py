"""Django Class-based View overrides from django.generic.base."""

__all__ = ['ContextMixin', 'RedirectView', 'TemplateResponseMixin', 'TemplateView', 'View']

import logging
from typing import Callable

from django.http import HttpRequest
from django.views.generic import base
from django.utils.decorators import classonlymethod

logger = logging.getLogger("django.request")


class ContextMixin(base.ContextMixin):
    """Almost the same as Django, but doesn't set `view` in context."""
    def get_context_data(self, **kwargs) -> dict:
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


class View(base.View):
    """Forbids the use of *args from views, which as far as I can tell, are only
    passed from unnamed capturing groups in URLs.
    Also got rid of as_view(**init_kwargs), because I will probably never put
    that logic in the URL conf.
    """
    get: Callable
    head: Callable
    request: HttpRequest
    kwargs: dict

    http_method_names = [
        'get',
        'post',
        'put',
        'patch',
        'delete',
        'head',
        'options',
        'trace',
    ]

    # noinspection PyMissingConstructor
    def __init__(self):
        pass

    @classonlymethod
    def as_view(cls):
        def view(request, **kwargs):
            self = cls()
            self.setup(request, **kwargs)
            if not hasattr(self, 'request'):
                raise AttributeError(
                    "%s instance has no 'request' attribute. Did you override "
                    "setup() and forget to call super()?" % cls.__name__
                )
            return self.dispatch(request, **kwargs)

        view.view_class = cls
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__annotations__ = cls.dispatch.__annotations__
        view.__dict__.update(cls.dispatch.__dict__)
        return view

    def setup(self, request, **kwargs) -> None:
        if hasattr(self, 'get') and not hasattr(self, 'head'):
            self.head = self.get
        self.request = request
        self.kwargs = kwargs

    def dispatch(self, request, **kwargs):
        print(f'BaseView.dispatch: ')
        return super().dispatch(request, **kwargs)

    def http_method_not_allowed(self, request, **kwargs):
        return super().http_method_not_allowed(request, **kwargs)

    def options(self, request, **kwargs):
        return super().options(request, **kwargs)


class TemplateResponseMixin(base.TemplateResponseMixin):
    pass


class TemplateView(
    base.TemplateView, TemplateResponseMixin, ContextMixin, View
):
    """Render a template. Pass URL keyword arguments to context.

    Replaces normal .get() method to be keyword-only.
    """
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)


class RedirectView(base.RedirectView, View):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def head(self, request, **kwargs):
        return self.get(request, **kwargs)

    def post(self, request, **kwargs):
        return self.get(request, **kwargs)

    def options(self, request, **kwargs):
        return self.get(request, **kwargs)

    def delete(self, request, **kwargs):
        return self.get(request, **kwargs)

    def put(self, request, **kwargs):
        return self.get(request, **kwargs)

    def patch(self, request, **kwargs):
        return self.get(request, **kwargs)
