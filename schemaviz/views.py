from django.apps import apps
from django.shortcuts import render


class MainView(View):
    def get(self, request, **kwargs):
        all_models = dict(apps.all_models)  # can't use default dict in templates
        get_models = apps.get_models()
        self.context.update({
            'all_models': all_models,
            'get_models': get_models,
        })
        return render(request, 'schemaviz/main.html', self.context)
