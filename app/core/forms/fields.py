from itertools import islice

from django.forms import ModelChoiceField


class AccountAssetRealChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('account_asset__account')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        return f'{obj.account_asset.account.name}'


class MusicAlbumArtworkChoiceField(ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        return f'[{obj.pk}] {obj.music_album.title}: {obj.short_description}'


class MusicAlbumEditionChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('music_album')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        return f'{obj.music_album.title} ({obj.name})'


class MusicArtistChoiceField(ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        text = f'{obj.name}'
        if obj.disambiguator:
            text += f' [{obj.disambiguator}]'
        return text


class MusicArtistXPersonChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('music_artist', 'person')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        return f'{obj.music_artist.name} : {obj.person.full_name}'


class PersonChoiceField(ModelChoiceField):
    def label_from_instance(self, obj) -> str:
        return obj.preferred_name


class PersonXPhotoChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('person', 'photo')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        return (
            f'[{obj.pk}][{obj.photo.pk}] {obj.photo.short_description}'
        )


class SongChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .prefetch_related('music_artists')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        artists = [x.name for x in islice(obj.music_artists.all(), 0, 3)]
        artists = ', '.join(artists)
        return f'{obj.title} [{artists}]'


class SongPerformanceChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('song_arrangement')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        label = f'{obj.song_arrangement.title}'
        if obj.song_arrangement.is_original:
            label += f' [ORIGINAL]'
        else:
            label += f' [{obj.song_arrangement.description}]'
        if obj.description:
            label += f' ({obj.description})'
        return f'{label} [{obj.performance_type}]'


class SongRecordingChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('song_performance__song_arrangement')
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        label = f'{obj.song_performance.song_arrangement.title}'
        if obj.song_performance.song_arrangement.is_original:
            label += f' [ORIGINAL]'
        else:
            label += f' [{obj.song_performance.song_arrangement.description}]'
        if obj.song_performance.description:
            label += f' [{obj.song_performance.description}]'
        return (
            f'{label} [{obj.song_performance.performance_type}]'
            f' : {obj.duration}'
        )


class VehicleYearChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('vehicle_trim__vehicle_model__vehicle_make')
                .order_by(
                    '-year',
                    'vehicle_trim__vehicle_model__vehicle_make__name',
                    'vehicle_trim__vehicle_model__name',
                    'vehicle_trim__name'
                )
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj) -> str:
        vehicle_year = obj.year
        vehicle_trim = obj.vehicletrim.name
        vehicle_model = obj.vehicletrim.vehiclemodel.name
        vehicle_make = obj.vehicletrim.vehiclemodel.vehiclemake.name
        return f'{vehicle_year} {vehicle_make} {vehicle_model} {vehicle_trim}'
