__all__ = [
    'BaseDetailView',
    'DetailView',
    'SingleObjectMixin',
    'SingleObjectTemplateResponseMixin'
]

from django.views.generic import detail

from ccbv.views.generic.base import ContextMixin, TemplateResponseMixin, View


class SingleObjectMixin(detail.SingleObjectMixin, ContextMixin):
    pass


class BaseDetailView(detail.BaseDetailView, SingleObjectMixin, View):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)


class SingleObjectTemplateResponseMixin(detail.SingleObjectTemplateResponseMixin, TemplateResponseMixin):
    pass


class DetailView(detail.DetailView, SingleObjectTemplateResponseMixin, BaseDetailView):
    pass
