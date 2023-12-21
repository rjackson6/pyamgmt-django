from django.urls import path

from .. import views


urlpatterns = [
    path('', views.beer.BeerNetworkView.as_view(), name='beer')
]
