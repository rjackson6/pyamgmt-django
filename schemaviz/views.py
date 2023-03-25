from django.apps import apps

from ccbv.views import TemplateView


class MainView(TemplateView):
    template_name = 'schemaviz/main.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        all_models = dict(apps.all_models)
        get_models = apps.get_models()
        context.update({
            'all_models': all_models,
            'get_models': get_models,
        })
        return context
