from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.main.index, name='index'),
    path('models/', include([
        path('account/', views.models.AccountListView.as_view()),
        path('music-album/', views.models.MusicAlbumListView.as_view()),
        path('music-artist/', views.models.MusicArtistListView.as_view()),
        path('vehicle/', views.models.VehicleListView.as_view()),
    ]))
]
