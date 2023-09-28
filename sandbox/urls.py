from django.urls import path

from . import views


urlpatterns = [
    path('', views.TestMultiCreateView.as_view())
]
