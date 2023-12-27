from django.contrib import admin

from ..models import person
from . import _inlines


@admin.register(person.Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = [
        _inlines.PersonXPersonRelationInline,
        _inlines.PersonXPersonRelationshipInline,
        _inlines.MusicAlbumXPersonInline,
        _inlines.MusicArtistXPersonInline,
        _inlines.MusicalInstrumentXPersonInline,
    ]
    list_display = (
        'full_name', 'is_living', 'date_of_birth', 'date_of_death', 'age',
        'notes',
    )
    ordering = ('preferred_name', 'first_name', 'last_name',)
    search_fields = ('first_name', 'last_name', 'nickname', 'preferred_name',)
