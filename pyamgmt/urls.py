from django.urls import include, path

import pyamgmt.views

app_name = 'pyamgmt'

_account_urls = ([
    path('', pyamgmt.views.models.AccountListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountFormView.as_view(), name='add'),
    path('<int:account_pk>/', include([
        path('', pyamgmt.views.models.AccountDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountFormView.as_view(), name='edit'),
        path('delete/', pyamgmt.views.models.AccountDeleteView.as_view(), name='delete'),
    ]))
], app_name)

_accountasset_urls = ([
    path('', pyamgmt.views.models.AccountAssetListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountAssetFormView.as_view(), name='add'),
    path('<int:accountasset_pk>/', include([
        path('', pyamgmt.views.models.AccountAssetDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountAssetFormView.as_view(), name='edit')
    ]))
], app_name)

_accountassetfinancial_urls = ([
    path('', pyamgmt.views.models.AccountAssetFinancialListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountAssetFinancialFormView.as_view(), name='add'),
    path('<int:accountassetfinancial_pk>/', include([
        path('', pyamgmt.views.models.AccountAssetFinancialDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountAssetFinancialFormView.as_view(), name='edit')
    ]))
], app_name)

_accountassetreal_urls = ([
    path('', pyamgmt.views.models.AccountAssetRealListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountAssetRealFormView.as_view(), name='add'),
    path('<int:accountassetreal_pk>/', include([
        path('', pyamgmt.views.models.AccountAssetRealDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountAssetRealFormView.as_view(), name='edit')
    ]))
], app_name)

_accountexpense_urls = ([
    path('', pyamgmt.views.models.AccountExpenseListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountExpenseFormView.as_view(), name='add'),
    path('<int:accountexpense_pk>/', include([
        path('', pyamgmt.views.models.AccountExpenseDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountExpenseFormView.as_view(), name='edit')
    ]))
], app_name)

_accountincome_urls = ([
    path('', pyamgmt.views.models.AccountIncomeListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountIncomeFormView.as_view(), name='add'),
    path('<int:accountincome_pk>/', include([
        path('', pyamgmt.views.models.AccountIncomeDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountIncomeFormView.as_view(), name='edit')
    ]))
], app_name)

_accountliability_urls = ([
    path('', pyamgmt.views.models.AccountLiabilityListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AccountLiabilityFormView.as_view(), name='add'),
    path('<int:accountliability_pk>/', include([
        path('', pyamgmt.views.models.AccountLiabilityDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AccountLiabilityFormView.as_view(), name='edit')
    ]))
], app_name)

_asset_urls = ([
    path('', pyamgmt.views.models.AssetListView.as_view(), name='list'),
    # path('add/', pyamgmt.views.models.asset_form, name='add'),
    path('<int:asset_pk>/', include([
        path('', pyamgmt.views.models.AssetDetailView.as_view(), name='detail'),
        # path('edit/', pyamgmt.views.models.asset_form, name='edit')
    ]))
], app_name)

_assetdiscrete_urls = ([
    path('', pyamgmt.views.models.AssetDiscreteListView.as_view(), name='list'),
    path('<int:assetdiscrete_pk>/', include([
        path('', pyamgmt.views.models.AssetDiscreteDetailView.as_view(), name='detail')
    ]))
], app_name)

_assetdiscretevehicle_urls = ([
    path('', pyamgmt.views.models.AssetDiscreteVehicleListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.AssetDiscreteVehicleFormView.as_view(), name='add'),
    path('<int:assetdiscretevehicle_pk>/', include([
        path('', pyamgmt.views.models.AssetDiscreteVehicleDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.AssetDiscreteVehicleFormView.as_view(), name='edit')
    ]))
], app_name)

_assetinventory_urls = ([
    path('', pyamgmt.views.models.AssetInventoryListView.as_view(), name='list'),
    # path('add/', pyamgmt.views.models.asset_inventory_form, name='add'),
    path('<int:assetinventory_pk>/', include([
        # path('', pyamgmt.views.models.asset_inventory_detail, name='detail'),
        # path('edit/', pyamgmt.views.models.asset_inventory_form, name='edit')
    ]))
], app_name)

_catalogitem_urls = ([
    path('', pyamgmt.views.models.CatalogItemListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.CatalogItemFormView.as_view(), name='add'),
    path('<int:catalogitem_pk>/', include([
        path('', pyamgmt.views.models.CatalogItemDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.CatalogItemFormView.as_view(), name='edit')
    ]))
], app_name)

_catalogitemdigitalsong_urls = ([
    path('', pyamgmt.views.models.CatalogItemDigitalSongListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.catalogitemdigitalsong_form, name='add'),
    path('<int:catalogitemdigitalsong_pk>/', include([
        path('', pyamgmt.views.models.CatalogItemDigitalSongDetailView.as_view(),
             name='detail'),
        path('edit/', pyamgmt.views.models.catalogitemdigitalsong_form, name='edit')
    ]))
], app_name)

_catalogitemmusicalbum_urls = ([
    path('', pyamgmt.views.models.catalogitemmusicalbum_list, name='list'),
    path('add/', pyamgmt.views.models.catalogitemmusicalbum_form, name='add'),
    path('<int:catalogitemmusicalbum_pk>/', include([
        path('', pyamgmt.views.models.catalogitemmusicalbum_detail, name='detail'),
        path('edit/', pyamgmt.views.models.catalogitemmusicalbum_form, name='edit')
    ]))
], app_name)

_catalogitemtopointofsalelineitem_urls = ([
    path('', pyamgmt.views.models.catalogitemtopointofsalelineitem_list, name='list'),
    path('add/', pyamgmt.views.models.catalogitemtopointofsalelineitem_form,
         name='add'),
    path('<int:catalogitemtopointofsalelineitem_pk>/', include([
        path('', pyamgmt.views.models.catalogitemtopointofsalelineitem_detail,
             name='detail'),
        path('edit/', pyamgmt.views.models.catalogitemtopointofsalelineitem_form,
             name='edit')
    ]))
], app_name)

_invoice_urls = ([
    path('', pyamgmt.views.models.InvoiceListView.as_view(), name='list')
], app_name)

_motionpicture_urls = ([
    path('', pyamgmt.views.models.MotionPictureListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.MotionPictureFormView.as_view(), name='add')
], app_name)

_musicalbum_urls = ([
    path('', pyamgmt.views.models.MusicAlbumListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.MusicAlbumFormView.as_view(), name='add'),
    path('<int:musicalbum_pk>/', include([
        path('', pyamgmt.views.models.MusicAlbumDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.MusicAlbumFormView.as_view(), name='edit'),
        path('add-song-recording/', pyamgmt.views.models.MusicAlbumAddSongRecordingFormView.as_view(),
             name='add-songrecording'),
    ]))
], app_name)

_musicalbumtomusicartist_urls = ([
    path('', pyamgmt.views.models.MusicAlbumToMusicArtistListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.MusicAlbumToMusicArtistFormView.as_view(), name='add'),
    path('<int:musicalbumtomusicartist_pk>/', include([
        path('', pyamgmt.views.models.MusicAlbumToMusicArtistDetailView.as_view(),
             name='detail'),
        path('edit/', pyamgmt.views.models.MusicAlbumToMusicArtistFormView.as_view(), name='edit')
    ]))
], app_name)

_musicalbumtosongrecording_urls = ([
    path('', pyamgmt.views.models.MusicAlbumToSongRecordingListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.MusicAlbumToSongRecordingFormView.as_view(), name='add'),
    path('<int:musicalbumtosongrecording_pk>/', include([
        path('', pyamgmt.views.models.MusicAlbumToSongRecordingDetailView.as_view(), name='detail')
    ]))
], app_name)

_musicartist_urls = ([
    path('', pyamgmt.views.models.MusicArtistListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.MusicArtistFormView.as_view(), name='add'),
    path('<int:musicartist_pk>/', include([
        path('', pyamgmt.views.models.MusicArtistDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.MusicArtistFormView.as_view(), name='edit'),
        path('add-music-album/', pyamgmt.views.models.MusicAlbumToMusicArtistFormView.as_view(),
             name='add-musicalbum'),
        path('add-person/', pyamgmt.views.models.musicartisttoperson_form, name='add-person')
    ]))
], app_name)

_musicartisttoperson_urls = ([
    path('', pyamgmt.views.models.musicartisttoperson_list, name='list'),
    path('add/', pyamgmt.views.models.musicartisttoperson_form, name='add'),
    path('<int:musicartisttoperson_pk>/', include([
        path('', pyamgmt.views.models.musicartisttoperson_detail, name='detail'),
        path('edit/', pyamgmt.views.models.musicartisttoperson_form, name='edit')
    ]))
], app_name)

_musicartisttosong_urls = ([
    path('', pyamgmt.views.models.musicartisttosong_list, name='list'),
    # path('add/')
    path('<int:musicartisttosong_pk>/', include([
        path('', pyamgmt.views.models.musicartisttosong_detail, name='detail')
    ]))
], app_name)

_musicartisttosongrecording_urls = ([
    path('', pyamgmt.views.models.musicartisttosongrecording_list, name='list')
], app_name)

_party_urls = ([
    path('', pyamgmt.views.models.party_list, name='list'),
    path('add/', pyamgmt.views.models.party_form, name='add'),
    path('<int:party_pk>/', include([
        path('', pyamgmt.views.models.party_detail, name='detail'),
        path('edit/', pyamgmt.views.models.party_form, name='edit')
    ]))
], app_name)

_payee_urls = ([
    path('', pyamgmt.views.models.payee_list, name='list'),
    path('add/', pyamgmt.views.models.payee_form, name='add'),
    path('<int:payee_pk>/', include([
        path('', pyamgmt.views.models.payee_detail, name='detail'),
        path('edit/', pyamgmt.views.models.payee_form, name='edit')
    ]))
], app_name)

_person_urls = ([
    path('', pyamgmt.views.models.PersonListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.PersonFormView.as_view(), name='add'),
    path('<int:person_pk>/', include([
        path('', pyamgmt.views.models.person_detail, name='detail'),
        path('edit/', pyamgmt.views.models.PersonFormView.as_view(), name='edit')
    ]))
], app_name)

_pointofsale_urls = ([
    path('', pyamgmt.views.models.PointOfSaleListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.pointofsale_form, name='add'),
    path('<int:pointofsale_pk>/', include([
        path('', pyamgmt.views.models.pointofsale_detail, name='detail'),
        path('add-point-of-sale-document/', pyamgmt.views.models.pointofsaledocument_form,
             name='add-pointofsaledocument'),
        path('add-point-of-sale-line-item/', pyamgmt.views.models.pointofsalelineitem_form,
             name='add-pointofsalelineitem'),
        path('edit/', pyamgmt.views.models.pointofsale_form, name='edit')
    ]))
], app_name)

_pointofsaledocument_urls = ([
    path('', pyamgmt.views.models.pointofsaledocument_list, name='list'),
    path('add/', pyamgmt.views.models.pointofsaledocument_form, name='add'),
    path('<int:pointofsaledocument_pk>/', include([
        path('', pyamgmt.views.models.pointofsaledocument_detail, name='detail'),
        path('edit/', pyamgmt.views.models.pointofsaledocument_form, name='edit')
    ]))
], app_name)

_pointofsalelineitem_urls = ([
    path('', pyamgmt.views.models.pointofsalelineitem_list, name='list'),
    path('add/', pyamgmt.views.models.pointofsalelineitem_form, name='add'),
    path('<int:pointofsalelineitem_pk>/', include([
        path('', pyamgmt.views.models.pointofsalelineitem_detail, name='detail'),
        path('edit/', pyamgmt.views.models.pointofsalelineitem_form, name='edit')
    ]))
], app_name)

_song_urls = ([
    path('', pyamgmt.views.models.song_list, name='list'),
    path('add/', pyamgmt.views.models.SongFormView.as_view(), name='add'),
    path('<int:song_pk>/', include([
        path('', pyamgmt.views.models.song_detail, name='detail'),
        path('edit/', pyamgmt.views.models.SongFormView.as_view(), name='edit')
    ]))
], app_name)

_songrecording_urls = ([
    path('', pyamgmt.views.models.SongRecordingListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.SongRecordingFormView.as_view(), name='add'),
    path('<int:songrecording_pk>/', include([
        path('', pyamgmt.views.models.SongRecordingDetailView.as_view(), name='detail')
    ]))
], app_name)

_songtosong_urls = ([
    path('', pyamgmt.views.models.songtosong_list, name='list')
], app_name)

_txn_urls = ([
    path('', pyamgmt.views.models.TxnListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.txn_form, name='add'),
    path('<int:txn_pk>/', include([
        path('', pyamgmt.views.models.TxnDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.txn_form, name='edit')
    ]))
], app_name)

_txnlineitem_urls = ([
    path('', pyamgmt.views.models.TxnLineItemListView.as_view(), name='list'),
    path('<int:txnlineitem_pk>/', include([
        path('', pyamgmt.views.models.TxnLineItemDetailView.as_view(), name='detail')
    ]))
], app_name)

_unit_urls = ([
    path('', pyamgmt.views.models.UnitListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.UnitFormView.as_view(), name='add'),
    path('<int:unit_pk>/', include([
        path('', pyamgmt.views.models.UnitDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.UnitFormView.as_view(), name='edit')
    ]))
], app_name)

_vehicle_urls = ([
    path('', pyamgmt.views.models.VehicleListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleFormView.as_view(), name='add'),
    path('<int:vehicle_pk>/', include([
        path('', pyamgmt.views.models.VehicleDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleFormView.as_view(), name='edit'),
        path('add-vehicle-mileage/', pyamgmt.views.models.VehicleMileageFormView.as_view(), name='add-vehiclemileage')
    ]))
], app_name)

_vehiclemake_urls = ([
    path('', pyamgmt.views.models.VehicleMakeListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleMakeFormView.as_view(), name='add'),
    path('<int:vehiclemake_pk>/', include([
        path('', pyamgmt.views.models.VehicleMakeDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleMakeFormView.as_view(), name='edit'),
        path('add-vehicle-model/', pyamgmt.views.models.VehicleModelFormView.as_view(), name='add-vehiclemodel')
    ]))
], app_name)

_vehiclemileage_urls = ([
    path('', pyamgmt.views.models.VehicleMileageListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleMileageFormView.as_view(), name='add'),
    path('<int:vehiclemileage_pk>/', include([
        path('', pyamgmt.views.models.VehicleMileageDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleMileageFormView.as_view(), name='edit')
    ]))
], app_name)

_vehiclemodel_urls = ([
    path('', pyamgmt.views.models.VehicleModelListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleModelFormView.as_view(), name='add'),
    path('<int:vehiclemodel_pk>/', include([
        path('', pyamgmt.views.models.VehicleModelDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleModelFormView.as_view(), name='edit'),
        path('add-vehicle-trim/', pyamgmt.views.models.VehicleTrimFormView.as_view(), name='add-vehicletrim')
    ]))
], app_name)

_vehicletrim_urls = ([
    path('', pyamgmt.views.models.VehicleTrimListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleTrimFormView.as_view(), name='add'),
    path('<int:vehicletrim_pk>/', include([
        path('', pyamgmt.views.models.VehicleTrimDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleTrimFormView.as_view(), name='edit'),
        path('add-vehicle-year/', pyamgmt.views.models.VehicleYearFormView.as_view(), name='add-vehicleyear')
    ]))
], app_name)

_vehicleyear_urls = ([
    path('', pyamgmt.views.models.VehicleYearListView.as_view(), name='list'),
    path('add/', pyamgmt.views.models.VehicleYearFormView.as_view(), name='add'),
    path('<int:vehicleyear_pk>/', include([
        path('', pyamgmt.views.models.VehicleYearDetailView.as_view(), name='detail'),
        path('edit/', pyamgmt.views.models.VehicleYearFormView.as_view(), name='edit'),
        path('add-vehicle/', pyamgmt.views.models.VehicleFormView.as_view(), name='add-vehicle')
    ]))
], app_name)

urlpatterns = [
    path('', pyamgmt.views.main.HomeView.as_view(), name='home'),
    path('account/', include(_account_urls, namespace='account')),
    path('account-asset/', include(_accountasset_urls, namespace='accountasset')),
    path('account-asset-financial/', include(_accountassetfinancial_urls, namespace='accountassetfinancial')),
    path('account-asset-real/', include(_accountassetreal_urls, namespace='accountassetreal')),
    path('account-expense/', include(_accountexpense_urls, namespace='accountexpense')),
    path('account-income/', include(_accountincome_urls, namespace='accountincome')),
    path('account-liability/', include(_accountliability_urls, namespace='accountliability')),
    path('asset/', include(_asset_urls, namespace='asset')),
    path('asset-discrete/', include(_assetdiscrete_urls, namespace='assetdiscrete')),
    path('asset-discrete-vehicle/', include(_assetdiscretevehicle_urls, namespace='assetdiscretevehicle')),
    path('asset-inventory/', include(_assetinventory_urls, namespace='assetinventory')),
    path('catalog-item/', include(_catalogitem_urls, namespace='catalogitem')),
    path('catalog-item-digital-song/', include(_catalogitemdigitalsong_urls, namespace='catalogitemdigitalsong')),
    path('catalog-item-music-album/', include(_catalogitemmusicalbum_urls, namespace='catalogitemmusicalbum')),
    path('catalog-item-to-point-of-sale-line-item/', include(
        _catalogitemtopointofsalelineitem_urls, namespace='catalogitemtopointofsalelineitem'
    )),
    path('invoice/', include(_invoice_urls, namespace='invoice')),
    path('motion-picture/', include(_motionpicture_urls, namespace='motionpicture')),
    path('music-album/', include(_musicalbum_urls, namespace='musicalbum')),
    path('music-album-to-music-artist/', include(_musicalbumtomusicartist_urls, namespace='musicalbumtomusicartist')),
    path('music-album-to-song-recording/', include(
        _musicalbumtosongrecording_urls, namespace='musicalbumtosongrecording'
    )),
    path('music-artist/', include(_musicartist_urls, namespace='musicartist')),
    path('music-artist-to-person/', include(_musicartisttoperson_urls, namespace='musicartisttoperson')),
    path('music-artist-to-song/', include(_musicartisttosong_urls, namespace='musicartisttosong')),
    path('party/', include(_party_urls, namespace='party')),
    path('payee/', include(_payee_urls, namespace='payee')),
    path('person/', include(_person_urls, namespace='person')),
    path('point-of-sale/', include(_pointofsale_urls, namespace='pointofsale')),
    path('point-of-sale-document/', include(_pointofsaledocument_urls, namespace='pointofsaledocument')),
    path('point-of-sale-line-item/', include(_pointofsalelineitem_urls, namespace='pointofsalelineitem')),
    path('song/', include(_song_urls, namespace='song')),
    path('song-recording/', include(_songrecording_urls, namespace='songrecording')),
    path('song-to-song/', include(_songtosong_urls, namespace='songtosong')),
    path('txn/', include(_txn_urls, namespace='txn')),
    path('txnlineitem/', include(_txnlineitem_urls, namespace='txnlineitem')),
    path('unit/', include(_unit_urls, namespace='unit')),
    path('vehicle/', include(_vehicle_urls, namespace='vehicle')),
    path('vehicle-make/', include(_vehiclemake_urls, namespace='vehiclemake')),
    path('vehicle-mileage/', include(_vehiclemileage_urls, namespace='vehiclemileage')),
    path('vehicle-model/', include(_vehiclemodel_urls, namespace='vehiclemodel')),
    path('vehicle-trim/', include(_vehicletrim_urls, namespace='vehicletrim')),
    path('vehicle-year/', include(_vehicleyear_urls, namespace='vehicleyear')),
    # Alternate Generic URLs
    path('generic/', include([
        path('account/', include([
            path('', pyamgmt.views.generic.AccountListView.as_view()),
            path('add/', pyamgmt.views.generic.AccountCreateView.as_view()),
            path('<int:pk>/', include([
                path('', pyamgmt.views.generic.AccountDetailView.as_view()),
                path('edit/', pyamgmt.views.generic.AccountUpdateView.as_view()),
                path('delete/', pyamgmt.views.generic.AccountDeleteView.as_view()),
            ])),
        ])),
    ])),
    # Specialized URLs
    path('experimental/', pyamgmt.views.experimental.current, name='experimental'),
    path('txn-register/', pyamgmt.views.txn_register.TxnRegister.as_view(), name='txn-register')
]
