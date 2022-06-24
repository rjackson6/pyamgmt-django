__all__ = [
    'View',
    'FormView', 'MultiFormView',
]

import logging
from typing import Callable

import django.forms
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseNotAllowed,
)
from django.utils.decorators import classonlymethod

logger = logging.getLogger("django.request")


class BaseView:
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
        if hasattr(self, 'handle'):
            handler = self.handle
        elif request.method.lower() in self.http_method_names:
            handler = getattr(
                self, request.method.lower(), self.http_method_not_allowed
            )
        else:
            handler = self.http_method_not_allowed
        return handler(request, **kwargs)

    def http_method_not_allowed(self, request, **_kwargs):
        logger.warning(
            "Method Not Allowed (%s): %s",
            request.method,
            request.path,
            extra={'status_code': 405, 'request': request},
        )
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self, _request, **_kwargs):
        response = HttpResponse()
        response.headers['Allow'] = ', '.join(self._allowed_methods())
        response.headers['Content-Length'] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class View(BaseView):
    def __init__(self):
        self.context = None

    def setup(self, request, **kwargs):
        super().setup(request, **kwargs)
        self.context = {}


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
