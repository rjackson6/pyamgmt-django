"""
See docs for omitting the model attribute from admin-only ModelForms:

https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
"""

from django.forms import ModelForm

from ..models import PersonXPhoto, MusicAlbumArtwork
from .fields import (
    AccountAssetChoiceField,
    AccountAssetRealChoiceField,
    AssetDiscreteChoiceField,
    MusicAlbumArtworkChoiceField,
    MusicAlbumEditionChoiceField,
    MusicArtistChoiceField,
    MusicArtistXPersonChoiceField,
    PersonChoiceField,
    PersonXPhotoChoiceField,
    SongPerformanceChoiceField,
    SongRecordingChoiceField,
)


class AccountAssetRealForm(ModelForm):
    class Meta:
        field_classes = {
            'account_asset': AccountAssetChoiceField,
        }


class AccountAssetRealXAssetDiscreteForm(ModelForm):
    class Meta:
        field_classes = {
            'account_asset_real': AccountAssetRealChoiceField,
            'asset_discrete': AssetDiscreteChoiceField,
        }


class AssetForm(ModelForm):
    class Meta:
        field_classes = {
            'account_asset_real': AccountAssetRealChoiceField
        }


class MusicAlbumForm(ModelForm):
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        if instance:
            self.fields['cover_artwork'].queryset = (
                MusicAlbumArtwork.objects
                .select_related('music_album')
                .filter(music_album=instance)
            )

    class Meta:
        field_classes = {
            'cover_artwork': MusicAlbumArtworkChoiceField,
        }


class MusicAlbumProductionForm(ModelForm):
    class Meta:
        field_classes = {
            'music_album_edition': MusicAlbumEditionChoiceField,
        }


class MusicAlbumEditionXSongRecordingForm(ModelForm):
    class Meta:
        field_classes = {
            'music_album_edition': MusicAlbumEditionChoiceField,
            'song_recording': SongRecordingChoiceField,
        }


class MusicArtistXPersonForm(ModelForm):
    class Meta:
        field_classes = {
            'music_artist': MusicArtistChoiceField,
            'person': PersonChoiceField,
        }


class MusicArtistXPersonActivityForm(ModelForm):
    class Meta:
        field_classes = {
            'music_artist_x_person': MusicArtistXPersonChoiceField,
        }


class MusicArtistXSongPerformanceForm(ModelForm):
    class Meta:
        field_classes = {
            'song_performance': SongPerformanceChoiceField,
        }


class PersonForm(ModelForm):
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)
        if instance:
            self.fields['featured_photo'].queryset = (
                PersonXPhoto.objects
                .select_related('person', 'photo')
                .filter(person=instance)
            )

    class Meta:
        field_classes = {
            'featured_photo': PersonXPhotoChoiceField
        }


class PersonXPhotoForm(ModelForm):
    class Meta:
        field_classes = {
            'person': PersonChoiceField
        }


class SongRecordingForm(ModelForm):
    class Meta:
        field_classes = {
            'song_performance': SongPerformanceChoiceField,
        }
