"""
See docs for omitting the model attribute from admin-only ModelForms:

https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
"""

from functools import partial

from django.forms import ModelForm

from ..models import PersonXPhoto
from .fields import (
    MusicAlbumEditionChoiceField,
    MusicArtistChoiceField,
    MusicArtistXPersonChoiceField,
    PersonChoiceField,
    PersonXPhotoChoiceField,
    SongChoiceField,
    SongPerformanceChoiceField,
    SongRecordingChoiceField,
)


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


def formfield_for_dbfield(db_field, **kwargs):
    print('*** formfield_for_dbfield')
    print(kwargs)
    if db_field.name == 'featured_photo':
        return PersonXPhotoChoiceField(**kwargs)
    return db_field.formfield(**kwargs)


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
