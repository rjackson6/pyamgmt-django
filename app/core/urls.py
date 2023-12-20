from django.urls import include, path

from . import views

app_name = 'core'

_account_urls = ([
    path('', views.models.MusicAlbumListView.as_view(), name='list')
], app_name)

urlpatterns = [
    path('', views.main.index, name='index'),
    path('models/', include([
        path('account/', views.models.AccountListView.as_view()),
        path('music-album/', include(_account_urls, namespace='music-album')),
        # path('music-album/', views.models.MusicAlbumListView.as_view()),
        path('music-artist/', views.models.MusicArtistListView.as_view()),
        path('vehicle/', views.models.VehicleListView.as_view()),
    ])),
    path('networks/', include([
        path('music-album-x-music-artist/',
             views.networks.MusicArtistNetworkView.as_view()),
        path('music-tags/', views.networks.MusicTagNetworkView.as_view())
    ])),
]
