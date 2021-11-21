from django.apps import apps
from django.shortcuts import render


def home(request):
    """First home page of the module."""
    context = {}
    models = [x.__name__ for x in apps.get_app_config('pyamgmt').get_models()]
    context.update({'models': models})
    return render(request, 'pyamgmt/home.html', context)
