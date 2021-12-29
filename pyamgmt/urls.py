from django.urls import include, path

import pyamgmt.views

app_name = 'pyamgmt'

_account_urls = ([
    path('', pyamgmt.views.models.account_list, name='list'),
    path('add/', pyamgmt.views.models.account_form, name='add'),
    path('<int:account_pk>/', include([
        path('', pyamgmt.views.models.account_detail, name='detail'),
        path('edit/', pyamgmt.views.models.account_form, name='edit')
    ]))
], 'pyamgmt')

_accountasset_urls = ([
    path('', pyamgmt.views.models.accountasset_list, name='list'),
    path('add/', pyamgmt.views.models.accountasset_form, name='add'),
    path('<int:accountasset_pk>/', include([
        path('', pyamgmt.views.models.accountasset_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountasset_form, name='edit')
    ]))
], 'pyamgmt')

_accountassetfinancial_urls = ([
    path('', pyamgmt.views.models.accountassetfinancial_list, name='list'),
    path('add/', pyamgmt.views.models.accountassetfinancial_form, name='add'),
    path('<int:accountassetfinancial_pk>/', include([
        path('', pyamgmt.views.models.accountassetfinancial_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountassetfinancial_form, name='edit')
    ]))
], 'pyamgmt')

_accountassetreal_urls = ([
    path('', pyamgmt.views.models.accountassetreal_list, name='list'),
    path('add/', pyamgmt.views.models.accountassetreal_form, name='add'),
    path('<int:accountassetreal_pk>/', include([
        path('', pyamgmt.views.models.accountassetreal_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountassetreal_form, name='edit')
    ]))
], 'pyamgmt')

_accountexpense_urls = ([
    path('', pyamgmt.views.models.accountexpense_list, name='list'),
    path('add/', pyamgmt.views.models.accountexpense_form, name='add'),
    path('<int:accountexpense_pk>/', include([
        path('', pyamgmt.views.models.accountexpense_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountexpense_form, name='edit')
    ]))
], 'pyamgmt')

_accountincome_urls = ([
    path('', pyamgmt.views.models.accountincome_list, name='list'),
    path('add/', pyamgmt.views.models.accountincome_form, name='add'),
    path('<int:accountincome_pk>/', include([
        path('', pyamgmt.views.models.accountincome_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountincome_form, name='edit')
    ]))
], 'pyamgmt')

_accountliability_urls = ([
    path('', pyamgmt.views.models.accountliability_list, name='list'),
    path('add/', pyamgmt.views.models.accountliability_form, name='add'),
    path('<int:accountliability_pk>/', include([
        path('', pyamgmt.views.models.accountliability_detail, name='detail'),
        path('edit/', pyamgmt.views.models.accountliability_form, name='edit')
    ]))
], 'pyamgmt')

_asset_urls = ([
    path('', pyamgmt.views.models.asset_list, name='list'),
    # path('add/', pyamgmt.views.models.asset_form, name='add'),
    path('<int:asset_pk>/', include([
        path('', pyamgmt.views.models.asset_detail, name='detail'),
        # path('edit/', pyamgmt.views.models.asset_form, name='edit')
    ]))
], 'pyamgmt')

_assetdiscrete_urls = ([
    path('', pyamgmt.views.models.assetdiscrete_list, name='list'),
    path('<int:assetdiscrete_pk>/', include([
        path('', pyamgmt.views.models.assetdiscrete_detail, name='detail')
    ]))
], 'pyamgmt')

_assetdiscretevehicle_urls = ([
    path('', pyamgmt.views.models.assetdiscretevehicle_list, name='list'),
    path('add/', pyamgmt.views.models.assetdiscretevehicle_form, name='add'),
    path('<int:assetdiscretevehicle_pk>/', include([
        path('', pyamgmt.views.models.assetdiscretevehicle_detail, name='detail'),
        path('edit/', pyamgmt.views.models.assetdiscretevehicle_form, name='edit')
    ]))
], 'pyamgmt')

_assetinventory_urls = ([
    path('', pyamgmt.views.models.assetinventory_list, name='list'),
    # path('add/', pyamgmt.views.models.asset_inventory_form, name='add'),
    path('<int:assetinventory_pk>/', include([
        # path('', pyamgmt.views.models.asset_inventory_detail, name='detail'),
        # path('edit/', pyamgmt.views.models.asset_inventory_form, name='edit')
    ]))
], 'pyamgmt')

_catalogitem_urls = ([
    path('', pyamgmt.views.models.catalogitem_list, name='list'),
    path('add/', pyamgmt.views.models.catalogitem_form, name='add'),
    path('<int:catalogitem_pk>/', include([
        path('', pyamgmt.views.models.catalogitem_detail, name='detail'),
        path('edit/', pyamgmt.views.models.catalogitem_form, name='edit')
    ]))
], 'pyamgmt')

_catalogitemdigitalsong_urls = ([
    path('', pyamgmt.views.models.catalogitemdigitalsong_list, name='list'),
    path('add/', pyamgmt.views.models.catalogitemdigitalsong_form, name='add'),
    path('<int:catalogitemdigitalsong_pk>/', include([
        path('', pyamgmt.views.models.catalogitemdigitalsong_detail,
             name='detail'),
        path('edit/', pyamgmt.views.models.catalogitemdigitalsong_form, name='edit')
    ]))
], 'pyamgmt')

_catalogitemmusicalbum_urls = ([
    path('', pyamgmt.views.models.catalogitemmusicalbum_list, name='list'),
    path('add/', pyamgmt.views.models.catalogitemmusicalbum_form, name='add'),
    path('<int:catalogitemmusicalbum_pk>/', include([
        path('', pyamgmt.views.models.catalogitemmusicalbum_detail, name='detail'),
        path('edit/', pyamgmt.views.models.catalogitemmusicalbum_form, name='edit')
    ]))
], 'pyamgmt')

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
], 'pyamgmt')

_invoice_urls = ([
    path('', pyamgmt.views.models.invoice_list, name='list')
], 'pyamgmt')

_motionpicture_urls = ([
    path('', pyamgmt.views.models.motionpicture_list, name='list')
], 'pyamgmt')

_musicalbum_urls = ([
    path('', pyamgmt.views.models.musicalbum_list, name='list'),
    path('add/', pyamgmt.views.models.musicalbum_form, name='add'),
    path('<int:musicalbum_pk>/', include([
        path('', pyamgmt.views.models.musicalbum_detail, name='detail'),
        path('edit/', pyamgmt.views.models.musicalbum_form, name='edit'),
        path('add-song/', pyamgmt.views.models.musicalbum_add_song_form, name='add-song'),
        path('add-songs/', pyamgmt.views.models.musicalbum_addsongs_form, name='add-songs')
    ]))
], 'pyamgmt')

_musicalbumtomusicartist_urls = ([
    path('', pyamgmt.views.models.musicalbumtomusicartist_list, name='list'),
    path('add/', pyamgmt.views.models.musicalbumtomusicartist_form, name='add'),
    path('<int:musicalbumtomusicartist_pk>/', include([
        path('', pyamgmt.views.models.musicalbumtomusicartist_detail,
             name='detail'),
        path('edit/', pyamgmt.views.models.musicalbumtomusicartist_form, name='edit')
    ]))
], 'pyamgmt')

_musicalbumtosongrecording_urls = ([
    path('', pyamgmt.views.models.musicalbumtosongrecording_list, name='list')
], 'pyamgmt')

_musicartist_urls = ([
    path('', pyamgmt.views.models.musicartist_list, name='list'),
    path('add/', pyamgmt.views.models.musicartist_form, name='add'),
    path('<int:musicartist_pk>/', include([
        path('', pyamgmt.views.models.musicartist_detail, name='detail'),
        path('edit/', pyamgmt.views.models.musicartist_form, name='edit'),
        path('add-music-album/', pyamgmt.views.models.musicalbumtomusicartist_form,
             name='add'),
        path('add-person/', pyamgmt.views.models.musicartisttoperson_form, name='add-person')
    ]))
], 'pyamgmt')

_musicartisttoperson_urls = ([
    path('', pyamgmt.views.models.musicartisttoperson_list, name='list'),
    path('add/', pyamgmt.views.models.musicartisttoperson_form, name='add'),
    path('<int:musicartisttoperson_pk>/', include([
        path('', pyamgmt.views.models.musicartisttoperson_detail, name='detail'),
        path('edit/', pyamgmt.views.models.musicartisttoperson_form, name='edit')
    ]))
], 'pyamgmt')

_musicartisttosong_urls = ([
    path('', pyamgmt.views.models.musicartisttosong_list, name='list'),
    # path('add/')
    path('<int:musicartisttosong_pk>/', include([
        path('', pyamgmt.views.models.musicartisttosong_detail, name='detail')
    ]))
], 'pyamgmt')

_musicartisttosongrecording_urls = ([
    path('', pyamgmt.views.models.musicartisttosongrecording_list, name='list')
], 'pyamgmt')

_party_urls = ([
    path('', pyamgmt.views.models.party_list, name='list'),
    path('add/', pyamgmt.views.models.party_form, name='add'),
    path('<int:party_pk>/', include([
        path('', pyamgmt.views.models.party_detail, name='detail'),
        path('edit/', pyamgmt.views.models.party_form, name='edit')
    ]))
], 'pyamgmt')

_payee_urls = ([
    path('', pyamgmt.views.models.payee_list, name='list'),
    path('add/', pyamgmt.views.models.payee_form, name='add'),
    path('<int:payee_pk>/', include([
        path('', pyamgmt.views.models.payee_detail, name='detail'),
        path('edit/', pyamgmt.views.models.payee_form, name='edit')
    ]))
], 'pyamgmt')

_person_urls = ([
    path('', pyamgmt.views.models.person_list, name='list'),
    path('add/', pyamgmt.views.models.person_form, name='add'),
    path('<int:person_pk>/', include([
        path('', pyamgmt.views.models.person_detail, name='detail'),
        path('edit/', pyamgmt.views.models.person_form, name='edit')
    ]))
], 'pyamgmt')

_pointofsale_urls = ([
    path('', pyamgmt.views.models.pointofsale_list, name='list'),
    path('add/', pyamgmt.views.models.pointofsale_form, name='add'),
    path('<int:pointofsale_pk>/', include([
        path('', pyamgmt.views.models.pointofsale_detail, name='detail'),
        path('add-point-of-sale-document/', pyamgmt.views.models.pointofsaledocument_form,
             name='add-pointofsaledocument'),
        path('add-point-of-sale-line-item/', pyamgmt.views.models.pointofsalelineitem_form,
             name='add-pointofsalelineitem'),
        path('edit/', pyamgmt.views.models.pointofsale_form, name='edit')
    ]))
], 'pyamgmt')

_pointofsaledocument_urls = ([
    path('', pyamgmt.views.models.pointofsaledocument_list, name='list'),
    path('add/', pyamgmt.views.models.pointofsaledocument_form, name='add'),
    path('<int:pointofsaledocument_pk>/', include([
        path('', pyamgmt.views.models.pointofsaledocument_detail, name='detail'),
        path('edit/', pyamgmt.views.models.pointofsaledocument_form, name='edit')
    ]))
], 'pyamgmt')

_pointofsalelineitem_urls = ([
    path('', pyamgmt.views.models.pointofsalelineitem_list, name='list'),
    path('add/', pyamgmt.views.models.pointofsalelineitem_form, name='add'),
    path('<int:pointofsalelineitem_pk>/', include([
        path('', pyamgmt.views.models.pointofsalelineitem_detail, name='detail'),
        path('edit/', pyamgmt.views.models.pointofsalelineitem_form, name='edit')
    ]))
], 'pyamgmt')

_song_urls = ([
    path('', pyamgmt.views.models.song_list, name='list'),
    path('add/', pyamgmt.views.models.song_form, name='add'),
    path('<int:song_pk>/', include([
        path('', pyamgmt.views.models.song_detail, name='detail'),
        path('edit/', pyamgmt.views.models.song_form, name='edit')
    ]))
], 'pyamgmt')

_songrecording_urls = ([
    path('', pyamgmt.views.models.songrecording_list, name='list'),
    path('<int:songrecording_pk>/', include([
        path('', pyamgmt.views.models.songrecording_detail, name='detail')
    ]))
], 'pyamgmt')

_songtosong_urls = ([
    path('', pyamgmt.views.models.songtosong_list, name='list')
], 'pyamgmt')

_txn_urls = ([
    path('', pyamgmt.views.models.txn_list, name='list'),
    path('add/', pyamgmt.views.models.txn_form, name='add'),
    path('<int:txn_pk>/', include([
        path('', pyamgmt.views.models.txn_detail, name='detail'),
        path('edit/', pyamgmt.views.models.txn_form, name='edit')
    ]))
], 'pyamgmt')

_txnlineitem_urls = ([
    path('', pyamgmt.views.models.txnlineitem_list, name='list'),
    path('<int:txnlineitem_pk>/', include([
        path('', pyamgmt.views.models.txnlineitem_detail, name='detail')
    ]))
], 'pyamgmt')

_unit_urls = ([
    path('', pyamgmt.views.models.unit_list, name='list'),
    path('add/', pyamgmt.views.models.unit_form, name='add'),
    path('<int:unit_pk>/', include([
        path('', pyamgmt.views.models.unit_detail, name='detail'),
        path('edit/', pyamgmt.views.models.unit_form, name='edit')
    ]))
], 'pyamgmt')

_vehicle_urls = ([
    path('', pyamgmt.views.models.vehicle_list, name='list'),
    path('add/', pyamgmt.views.models.vehicle_form, name='add'),
    path('<int:vehicle_pk>/', include([
        path('', pyamgmt.views.models.vehicle_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehicle_form, name='edit'),
        path('add-vehicle-mileage/', pyamgmt.views.models.vehiclemileage_form, name='add-vehiclemileage')
    ]))
], 'pyamgmt')

_vehiclemake_urls = ([
    path('', pyamgmt.views.models.vehiclemake_list, name='list'),
    path('add/', pyamgmt.views.models.vehiclemake_form, name='add'),
    path('<int:vehiclemake_pk>/', include([
        path('', pyamgmt.views.models.vehiclemake_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehiclemake_form, name='edit'),
        path('add-vehicle-model/', pyamgmt.views.models.vehiclemodel_form, name='add-vehiclemodel')
    ]))
], 'pyamgmt')

_vehiclemileage_urls = ([
    path('', pyamgmt.views.models.vehiclemileage_list, name='list'),
    path('add/', pyamgmt.views.models.vehiclemileage_form, name='add'),
    path('<int:vehiclemileage_pk>/', include([
        path('', pyamgmt.views.models.vehiclemileage_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehiclemileage_form, name='edit')
    ]))
], 'pyamgmt')

_vehiclemodel_urls = ([
    path('', pyamgmt.views.models.vehiclemodel_list, name='list'),
    path('add/', pyamgmt.views.models.vehiclemodel_form, name='add'),
    path('<int:vehiclemodel_pk>/', include([
        path('', pyamgmt.views.models.vehiclemodel_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehiclemodel_form, name='edit'),
        path('add-vehicle-trim/', pyamgmt.views.models.vehicletrim_form, name='add-vehicletrim')
    ]))
], 'pyamgmt')

_vehicletrim_urls = ([
    path('', pyamgmt.views.models.vehicletrim_list, name='list'),
    path('add/', pyamgmt.views.models.vehicletrim_form, name='add'),
    path('<int:vehicletrim_pk>/', include([
        path('', pyamgmt.views.models.vehicletrim_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehicletrim_form, name='edit'),
        path('add-vehicle-year/', pyamgmt.views.models.vehicleyear_form, name='add-vehicleyear')
    ]))
], 'pyamgmt')

_vehicleyear_urls = ([
    path('', pyamgmt.views.models.vehicleyear_list, name='list'),
    path('add/', pyamgmt.views.models.vehicleyear_form, name='add'),
    path('<int:vehicleyear_pk>/', include([
        path('', pyamgmt.views.models.vehicleyear_detail, name='detail'),
        path('edit/', pyamgmt.views.models.vehicleyear_form, name='edit'),
        path('add-vehicle/', pyamgmt.views.models.vehicle_form, name='add-vehicle')
    ]))
], 'pyamgmt')

urlpatterns = [
    path('', pyamgmt.views.general.home, name='home'),
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
    # Specialized URLs
    path('experimental/', pyamgmt.views.experimental.current, name='experimental'),
    path('txn-register/', pyamgmt.views.txn_register.txn_register, name='txn-register')
]
