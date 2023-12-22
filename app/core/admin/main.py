from django.contrib import admin
from django.db.models import Count

from . import inlines
from .. import forms
from ..models import (
    account, asset, author, beer, book, catalog_item, city, config, invoice,
    manufacturer, motion_picture, music, music_album, music_artist, music_tag,
    person, song, txn, vehicle, video_game,
)


@admin.register(account.Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_account', 'subtype')
    list_select_related = ('parent_account',)
    ordering = ('name',)


@admin.register(account.AccountAsset)
class AccountAssetAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'subtype')
    list_select_related = ('account',)


admin.site.register(account.AccountAssetFinancial)


@admin.register(account.AccountAssetReal)
class AccountAssetRealAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)


@admin.register(asset.Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ('description', 'subtype')


@admin.register(asset.AssetDiscrete)
class AssetDiscrete(admin.ModelAdmin):
    list_display = ('admin_description', 'date_acquired', 'date_withdrawn')


admin.site.register(asset.AssetDiscreteCatalogItem)


@admin.register(asset.AssetDiscreteVehicle)
class AssetDiscreteVehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('asset_discrete__asset', 'vehicle')


admin.site.register(author.Author)

admin.site.register(beer.Beer)


@admin.register(beer.BeerStyle)
class BeerStyleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(beer.Brewery)
class BreweryAdmin(admin.ModelAdmin):
    ordering = ('name',)


admin.site.register(book.Book)


@admin.register(book.BookEdition)
class BookEditionAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('book',)


admin.site.register(book.BookSeries)


@admin.register(book.BookXMotionPicture)
class BookXMotionPictureAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('book', 'motion_picture',)


admin.site.register(catalog_item.CatalogItem)
admin.site.register(catalog_item.CatalogItemMotionPictureRecording)

admin.site.register(city.USCity)

admin.site.register(config.Config)

admin.site.register(invoice.Invoice)
admin.site.register(invoice.InvoiceLineItem)

admin.site.register(manufacturer.Manufacturer)


@admin.register(motion_picture.MotionPicture)
class MotionPictureAdmin(admin.ModelAdmin):
    inlines = [inlines.MotionPictureXMusicAlbumInline]
    ordering = ('title', 'year_produced')


admin.site.register(motion_picture.MotionPictureRecording)
admin.site.register(motion_picture.MotionPictureSeries)


@admin.register(motion_picture.MotionPictureXMusicAlbum)
class MotionPictureXMusicAlbumAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('motion_picture', 'music_album')


admin.site.register(motion_picture.MotionPictureXSong)


@admin.register(music_album.MusicAlbum)
class MusicAlbumAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicAlbumEditionInline,
        inlines.MusicAlbumXMusicArtistInline,
        inlines.MusicAlbumXMusicTagInline,
        inlines.MusicAlbumXPersonInline,
    ]
    list_display = ('title', 'is_compilation')
    ordering = ('title',)
    search_fields = ('title',)


admin.site.register(music_album.MusicAlbumArtwork)


@admin.register(music_album.MusicAlbumEdition)
class MusicAlbumEditionAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicAlbumEditionXSongRecordingInline
    ]
    list_display = ('admin_description', 'year_produced')
    list_select_related = ('music_album',)
    ordering = ('music_album__title', 'name')
    search_fields = ('music_album__title', 'name')


@admin.register(music_album.MusicRole)
class MusicRoleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(music_album.MusicAlbumXMusicArtist)
class MusicAlbumXMusicArtistAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('music_album', 'music_artist')
    ordering = ('music_artist__name', 'music_album__title')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.music_artist.name} : {obj.music_album.title}'


@admin.register(music_album.MusicAlbumXPerson)
class MusicAlbumXPersonAdmin(admin.ModelAdmin):
    inlines = [inlines.MusicAlbumXPersonRoleInline]
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'person')


@admin.register(music_album.MusicAlbumXVideoGame)
class MusicAlbumXVideoGameAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_album', 'video_game')
    ordering = ('video_game__title', 'music_album__title')


@admin.register(music_artist.MusicArtist)
class MusicArtistAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicAlbumXMusicArtistInline,
        inlines.MusicArtistActivityInline,
        inlines.MusicArtistXPersonInline,
    ]
    list_display = (
        'name', '_album_count', '_arrangement_count', '_people_count',
        'website',
    )
    ordering = ('name',)
    search_fields = ('name',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return (
            qs
            .annotate(
                Count('arrangements', distinct=True),
                Count('music_albums', distinct=True),
                Count('people', distinct=True),
            )
        )

    @staticmethod
    def _album_count(obj):
        return obj.music_albums__count

    @staticmethod
    def _arrangement_count(obj):
        return obj.arrangements__count

    @staticmethod
    def _people_count(obj):
        return obj.people__count


@admin.register(music_artist.MusicArtistActivity)
class MusicArtistActivityAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = ('music_artist',)
    ordering = ('music_artist__name', 'year_active', 'year_inactive')


@admin.register(music_artist.MusicArtistXPerson)
class MusicArtistXPersonAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonForm
    inlines = [inlines.MusicArtistXPersonActivityInline]
    list_display = ('admin_description',)
    list_select_related = ('music_artist', 'person')
    ordering = ('music_artist__name', 'person__first_name')
    search_fields = (
        'music_artist__name',
        'person__preferred_name',
    )


@admin.register(music_artist.MusicArtistXPersonActivity)
class MusicArtistXPersonActivityAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXPersonActivityForm
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist_x_person__music_artist',
        'music_artist_x_person__person',
    )


@admin.register(music_artist.MusicArtistXSong)
class MusicArtistXSongAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist',
        'song',
    )


@admin.register(music_artist.MusicArtistXSongPerformance)
class MusicArtistXSongPerformanceAdmin(admin.ModelAdmin):
    form = forms.admin.MusicArtistXSongPerformanceForm
    list_display = ('admin_description',)
    list_select_related = (
        'music_artist',
        'song_performance__song_arrangement',
    )


admin.site.register(music_tag.MusicTag)


@admin.register(music.MusicalInstrument)
class MusicalInstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'section')
    ordering = ('name',)


@admin.register(music.MusicalInstrumentXPerson)
class MusicalInstrumentXPersonAdmin(admin.ModelAdmin):
    list_display = ('_description',)
    list_select_related = ('musical_instrument', 'person')
    ordering = ('musical_instrument__name', 'person__last_name')

    @staticmethod
    def _description(obj) -> str:
        return f'{obj.musical_instrument.name} : {obj.person.full_name}'


@admin.register(person.Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicAlbumXPersonInline,
        inlines.MusicArtistXPersonInline,
        inlines.MusicalInstrumentXPersonInline,
    ]
    list_display = (
        'full_name', 'is_living', 'date_of_birth', 'date_of_death', 'age',
        'notes',
    )
    ordering = ('last_name', 'first_name')
    search_fields = ('first_name', 'last_name')


@admin.register(song.SongDisambiguator)
class SongDisambiguatorAdmin(admin.ModelAdmin):
    pass


@admin.register(song.Song)
class SongAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicArtistXSongInline,
        inlines.PersonXSongInline,
        inlines.SongXSongArrangementInline,
    ]
    list_display = (
        '_description',
        'disambiguator',
        '_arrangement_count',
    )
    ordering = ('title',)
    search_fields = ('title',)

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('music_artists')
            .annotate(Count('arrangements'))
        )

    @staticmethod
    def _description(obj) -> str:
        artists = []
        for n, artist in enumerate(obj.music_artists.all()):
            artists.append(artist.name)
            if n > 2:
                artists.append(', ...')
                break
        artists = ', '.join(artists)
        return f'{obj.title} [{artists}]'

    @staticmethod
    def _arrangement_count(obj) -> int:
        return obj.arrangements__count


@admin.register(song.SongArrangement)
class SongArrangementAdmin(admin.ModelAdmin):
    inlines = [
        inlines.SongXSongArrangementInline,
        inlines.MusicArtistXSongArrangementInline,
        inlines.PersonXSongArrangementInline,
        inlines.SongPerformanceInline,
    ]
    list_display = (
        'title', 'disambiguator', '_performance_count', 'is_original',
        'description'
    )
    ordering = ('title', '-is_original', 'description')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .prefetch_related('song_performance_set')
            .annotate(Count('song_performance'))
        )

    @staticmethod
    def _performance_count(obj) -> int:
        return obj.song_performance__count


@admin.register(song.SongPerformance)
class SongPerformanceAdmin(admin.ModelAdmin):
    inlines = [
        inlines.MusicArtistXSongPerformanceInline,
        inlines.PersonXSongPerformanceInline,
        inlines.SongRecordingInline,
    ]
    list_display = (
        '_description', 'performance_type',
    )
    list_select_related = ('song_arrangement',)
    ordering = ('song_arrangement__title',)

    @staticmethod
    def _description(obj) -> str:
        text = f'{obj.song_arrangement.title}'
        if obj.song_arrangement.disambiguator:
            text += f' [{obj.song_arrangement.disambiguator}]'
        if obj.song_arrangement.description:
            text += f' [{obj.song_arrangement.description}]'
        if obj.description:
            text += f' - {obj.description}'
        return text


@admin.register(song.SongRecording)
class SongRecordingAdmin(admin.ModelAdmin):
    form = forms.admin.SongRecordingForm
    inlines = [inlines.MusicAlbumEditionXSongRecordingInline]
    list_display = (
        '_description', 'duration',
    )
    list_select_related = ('song_performance__song_arrangement',)
    ordering = ('song_performance__song_arrangement__title',)

    @staticmethod
    def _description(obj) -> str:
        text = f'{obj.song_performance.song_arrangement.title}'
        if obj.song_performance.description:
            text += f' - {obj.song_performance.description}'
        return text


admin.site.register(txn.Txn)
admin.site.register(txn.TxnLineItem)


@admin.register(vehicle.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make',
    )
    ordering = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make__name',
        'vehicle_year__vehicle_trim__vehicle_model__name',
        'vehicle_year__vehicle_trim__name',
        'vehicle_year',
        'vin'
    )


admin.site.register(vehicle.VehicleMake)
admin.site.register(vehicle.VehicleMileage)
admin.site.register(vehicle.VehicleModel)
admin.site.register(vehicle.VehicleService)
admin.site.register(vehicle.VehicleServiceItem)
admin.site.register(vehicle.VehicleTrim)
admin.site.register(vehicle.VehicleYear)


@admin.register(video_game.VideoGame)
class VideoGameAdmin(admin.ModelAdmin):
    inlines = [
        inlines.VideoGameEditionInline,
        inlines.VideoGameAddonInline,
        inlines.MusicAlbumXVideoGameInline,
    ]
    list_display = ('title', 'series')
    ordering = ('title',)


@admin.register(video_game.VideoGameAddon)
class VideoGameAddonAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'release_date')
    list_select_related = ('video_game',)


@admin.register(video_game.VideoGameEdition)
class VideoGameEditionAdmin(admin.ModelAdmin):
    inlines = [inlines.VideoGameEditionXVideoGamePlatformInline]
    list_display = ('admin_description',)
    list_select_related = ('video_game',)


@admin.register(video_game.VideoGamePlatform)
class VideoGamePlatformAdmin(admin.ModelAdmin):
    inlines = [
        inlines.VideoGamePlatformRegionInline,
    ]
    ordering = ('name',)


@admin.register(video_game.VideoGamePlatformEdition)
class VideoGamePlatformEditionAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    ordering = ('video_game_platform__name', 'name')


@admin.register(video_game.VideoGamePlatformRegion)
class VideoGamePlatformRegionAdmin(admin.ModelAdmin):
    list_display = ('admin_description', 'release_date')
    list_select_related = ('video_game_platform',)
    ordering = ('video_game_platform__name', 'region')


@admin.register(video_game.VideoGameSeries)
class VideoGameSeriesAdmin(admin.ModelAdmin):
    inlines = [
        inlines.VideoGameInline,
    ]
    ordering = ('name',)
