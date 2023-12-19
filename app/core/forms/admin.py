"""
See docs for omitting the model attribute from admin-only ModelForms:

https://docs.djangoproject.com/en/5.0/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
"""

from django.forms import ModelForm

from .fields import MusicAlbumEditionChoiceField, SongRecordingChoiceField


class MusicAlbumEditionXSongRecordingForm(ModelForm):
    class Meta:
        field_classes = {
            'music_album_edition': MusicAlbumEditionChoiceField,
            'song_recording': SongRecordingChoiceField,
        }


class MusicArtistXSongRecordingForm(ModelForm):
    class Meta:
        field_classes = {
            'song_recording': SongRecordingChoiceField,
        }
