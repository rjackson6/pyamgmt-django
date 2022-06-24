from django.apps import apps
from django.shortcuts import render

from core.views.base import View


class HomeView(View):
    def get(self, request, **kwargs):
        models = [x.__name__ for x in apps.get_app_config('pyamgmt').get_models()]
        self.context.update({'models': models})
        return render(request, 'pyamgmt/home.html', self.context)
