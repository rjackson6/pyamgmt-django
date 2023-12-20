"""
See docs for omitting the model attribute from admin-only ModelForms:

https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
"""

from django.forms import ModelForm

from .fields import (
    MusicAlbumEditionChoiceField,
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


class MusicArtistXSongPerformanceForm(ModelForm):
    class Meta:
        field_classes = {
            'song_performance': SongPerformanceChoiceField,
        }


class SongRecordingForm(ModelForm):
    class Meta:
        field_classes = {
            'song_performance': SongPerformanceChoiceField,
        }


class SongXSongForm(ModelForm):
    class Meta:
        field_classes = {
            'song_archetype': SongChoiceField,
            'song_derivative': SongChoiceField,
        }
