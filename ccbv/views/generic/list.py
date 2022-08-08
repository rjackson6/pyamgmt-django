__all__ = ['ListView']

from django.views.generic import list

from ccbv.views.generic.base import ContextMixin, TemplateResponseMixin, View


class MultipleObjectMixin(list.MultipleObjectMixin, ContextMixin):
    pass


class BaseListView(list.BaseListView, MultipleObjectMixin, View):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)


class MultipleObjectTemplateResponseMixin(list.MultipleObjectTemplateResponseMixin, TemplateResponseMixin):
    pass


class ListView(list.ListView, MultipleObjectTemplateResponseMixin, BaseListView):
    pass
