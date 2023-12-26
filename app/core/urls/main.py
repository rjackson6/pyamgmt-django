from django.urls import include, path

from .. import views

app_name = 'core'

_music_album_urls = ([
    path('', views.models.MusicAlbumListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.MusicAlbumDetailView.as_view(), name='detail'),
    ])),
], app_name)

_music_artist_urls = ([
    path('', views.models.MusicArtistListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.MusicArtistDetailView.as_view(), name='detail'),
    ])),
], app_name)

_person_urls = ([
    path('', views.models.PersonListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.PersonDetailView.as_view(), name='detail'),
    ])),
], app_name)

urlpatterns = [
    path('', views.main.index, name='index'),
    path('models/', include([
        path('account/', views.models.AccountListView.as_view()),
        path('music-album/',
             include(_music_album_urls, namespace='music-album')),
        path('music-artist/',
             include(_music_artist_urls, namespace='music-artist')),
        path('person/',
             include(_person_urls, namespace='person')),
        path('vehicle/', views.models.VehicleListView.as_view()),
    ])),
    path('networks/', include([
        path('music-album-x-music-artist/',
             views.networks.MusicArtistDetailedNetworkView.as_view()),
        path('music-artists/', views.networks.MusicArtistNetworkView.as_view()),
        path('music-tags/', views.networks.MusicTagNetworkView.as_view()),
    ])),
]
