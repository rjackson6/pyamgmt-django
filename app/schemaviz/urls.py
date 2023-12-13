from django.urls import path

from schemaviz import views

app_name = 'schemaviz'

urlpatterns = [
    path('', views.MainView.as_view()),
]
