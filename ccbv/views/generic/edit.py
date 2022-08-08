__all__ = ['CreateView', 'DeleteView', 'FormView', 'UpdateView']

from django.views.generic import edit

from ccbv.views.generic.base import ContextMixin, TemplateResponseMixin, View
from ccbv.views.generic.detail import BaseDetailView, SingleObjectMixin, SingleObjectTemplateResponseMixin


class FormMixin(edit.FormMixin, ContextMixin):
    pass


class ModelFormMixin(edit.ModelFormMixin, SingleObjectMixin):
    pass


class ProcessFormView(edit.ProcessFormView, View):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        return super().post(request, **kwargs)

    def put(self, **kwargs):
        return super().put(**kwargs)


class BaseFormView(edit.BaseFormView, FormMixin, ProcessFormView):
    pass


class FormView(edit.FormView, TemplateResponseMixin, BaseFormView):
    pass


class BaseCreateView(edit.BaseCreateView, ModelFormMixin, ProcessFormView):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class CreateView(edit.CreateView, SingleObjectTemplateResponseMixin, BaseCreateView):
    pass


class BaseUpdateView(edit.BaseUpdateView, ModelFormMixin, ProcessFormView):
    def get(self, request, **kwargs):
        return super().get(request, **kwargs)

    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class UpdateView(edit.UpdateView, SingleObjectTemplateResponseMixin, BaseUpdateView):
    pass


class DeletionMixin(edit.DeletionMixin):
    def delete(self, request, **kwargs):
        return super().delete(request, **kwargs)

    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class BaseDeleteView(edit.BaseDeleteView, DeletionMixin, FormMixin, BaseDetailView):
    def post(self, request, **kwargs):
        return super().post(request, **kwargs)


class DeleteView(edit.DeleteView, SingleObjectTemplateResponseMixin, BaseDeleteView):
    pass
