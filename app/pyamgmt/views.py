from django.shortcuts import render


def root(request, *args, **kwargs):
    return render(request, 'home.html')
