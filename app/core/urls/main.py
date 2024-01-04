from functools import partial

from django.urls import include, path

from django_base.utils import url_include

from .. import views

app_name = 'core'
make_urls = partial(url_include, app_name=app_name)

_account_urls = make_urls([
    path('', views.models.AccountListView.as_view(), name='list')
])

_music_album_urls = make_urls([
    path('', views.models.MusicAlbumListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.MusicAlbumDetailView.as_view(), name='detail'),
    ])),
])

_music_album_edition_urls = make_urls([
    path('<int:pk>/', include([
        path('',
             views.models.MusicAlbumEditionDetailView.as_view(),
             name='detail')
    ])),
])

_music_artist_urls = make_urls([
    path('', views.models.MusicArtistListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.MusicArtistDetailView.as_view(), name='detail'),
    ])),
])

_person_urls = make_urls([
    path('', views.models.PersonListView.as_view(), name='list'),
    path('<int:pk>/', include([
        path('', views.models.PersonDetailView.as_view(), name='detail'),
    ])),
])

_song_performance_urls = make_urls([
    path('<int:pk>/', include([
        path('',
             views.models.SongPerformanceDetailView.as_view(),
             name='detail')
    ]))
])

_txn_urls = make_urls([
    path('', views.models.TxnListView.as_view(), name='list'),
])

urlpatterns = [
    path('', views.main.index, name='index'),
    path('models/', include([
        path('account/',
             include(_account_urls, namespace='account')),
        path('music-album/',
             include(_music_album_urls, namespace='music-album')),
        path('music-album-edition/',
             include(_music_album_edition_urls,
                     namespace='music-album-edition')),
        path('music-artist/',
             include(_music_artist_urls, namespace='music-artist')),
        path('person/',
             include(_person_urls, namespace='person')),
        path('song-performance/',
             include(_song_performance_urls, namespace='song-performance')),
        path('txn/',
             include(_txn_urls, namespace='txn')),
        path('vehicle/', views.models.VehicleListView.as_view()),
    ])),
    path('music-album-register/',
         views.main.MusicAlbumRegisterView.as_view(),
         name='music-album-register'),
    path('networks/', include([
        path('', views.networks.NetworkIndex.as_view(), name='network-index'),
        path('music-album-x-music-artist/',
             views.networks.MusicArtistDetailedNetworkView.as_view()),
        path('film-games-and-music/',
             views.networks.FilmGamesAndMusicNetworkView.as_view()),
        path('music-artists/', views.networks.MusicArtistNetworkView.as_view()),
        path('music-tags/', views.networks.MusicTagNetworkView.as_view()),
        path('person/', views.networks.PersonRelationView.as_view()),
    ])),
    path('txn-register/', include([
        path('', views.main.AccountListView.as_view(), name='account-list'),
        path('<int:account_pk>/', include([
            path('', views.main.TxnRegisterView.as_view(), name='txn-register')
        ]))
    ]))
]
