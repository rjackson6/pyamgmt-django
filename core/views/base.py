import logging

from django.http import (
    HttpResponse,
    HttpResponseNotAllowed,
)
from django.utils.decorators import classonlymethod

logger = logging.getLogger("django.request")


class BaseView:
    """Forbids the use of *args from views, which as far as I can tell, are only
     passed from unnamed capturing groups in URLs.
    """

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **initkwargs):
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError(
                    "The method name %s is not accepted as a keyword argument "
                    "to %s()." % (key, cls.__name__)
                )
            if not hasattr(cls, key):
                raise TypeError(
                    "%s() received an invalid keyword %r. as_view "
                    "only accepts arguments that are already "
                    "attributes of the class." % (cls.__name__, key)
                )

        def view(request, **kwargs):
            self = cls(**initkwargs)
            self.setup(request, **kwargs)
            if not hasattr(self, "request"):
                raise AttributeError(
                    "%s instance has no 'request' attribute. Did you override "
                    "setup() and forget to call super()?" % cls.__name__
                )
            return self.dispatch(request, **kwargs)

        view.view_class = cls
        view.view_initkwargs = initkwargs
        view.__doc__ = cls.__doc__
        view.__module__ = cls.__module__
        view.__annotations__ = cls.dispatch.__annotations__
        view.__dict__.update(cls.dispatch.__dict__)
        return view

    def setup(self, request, **kwargs):
        if hasattr(self, "get") and not hasattr(self, "head"):
            self.head = self.get  # noqa
        self.request = request  # noqa
        self.kwargs = kwargs  # noqa

    def dispatch(self, request, **kwargs):
        if request.method.lower() in self.http_method_names:
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
            extra={"status_code": 405, "request": request},
        )
        return HttpResponseNotAllowed(self._allowed_methods())

    def options(self, _request, **_kwargs):
        response = HttpResponse()
        response.headers["Allow"] = ", ".join(self._allowed_methods())
        response.headers["Content-Length"] = "0"
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]


class View(BaseView):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = None

    def setup(self, request, **kwargs):
        super().setup(request, **kwargs)
        self.context = {}
