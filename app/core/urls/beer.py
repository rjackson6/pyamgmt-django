from django.urls import path

from .. import views

app_name = 'core-beer'

urlpatterns = [
    path('', views.beer.BeerNetworkView.as_view(), name='network')
]
