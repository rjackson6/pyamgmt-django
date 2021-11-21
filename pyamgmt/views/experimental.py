from django.shortcuts import render


def current(request):
    """Test an iFrame loading a sub-form or something."""
    context = {}
    return render(request, 'pyamgmt/experimental/iframe.html', context)
