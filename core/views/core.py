from django.shortcuts import render

from core.views.base import View


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'core/home.html')
