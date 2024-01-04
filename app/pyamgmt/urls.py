from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.core.handlers.wsgi import WSGIRequest
from django.urls import include, path
from django.views.decorators.csrf import csrf_exempt

import debug_toolbar

from . import views

admin.site.site_header = 'PyAMgmt Admin'

urlpatterns = [
    path('', views.root, name='root'),
    path('admin/', admin.site.urls),
    # path('beer/', include('core.urls.beer', namespace='beer')),
    path('beer/', include('core.urls.beer')),
    path('pyamgmt/', include('core.urls.main')),
    path('schemaviz/', include('schemaviz.urls')),
    path('sandbox/', include('sandbox.urls')),
]


@csrf_exempt
def reverse_proxy(request: WSGIRequest):
    import requests
    from django.http.response import HttpResponse

    request_path = request.get_full_path()
    url = f"http://localhost:1234/{request_path}"
    requestor = getattr(requests, request.method.lower())
    proxied_response = requestor(url, data=request.body, files=request.FILES)
    response = HttpResponse(
        proxied_response.content,
        content_type=proxied_response.headers.get('content-type')
    )
    for header_key, header_value in proxied_response.headers.items():
        response[header_key] = header_value
    return response


if settings.DEBUG is True:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
        # path('assets/', reverse_proxy),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
