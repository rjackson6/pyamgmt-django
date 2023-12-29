from django.contrib import admin
from django.utils.html import format_html

from ..forms.admin import PersonForm
from ..models import person
from . import _inlines


@admin.register(person.Person)
class PersonAdmin(admin.ModelAdmin):
    form = PersonForm
    inlines = [
        _inlines.PersonXPhotoInline,
        _inlines.PersonXPersonRelationInline,
        _inlines.PersonXPersonRelationshipInline,
        _inlines.MusicAlbumXPersonInline,
        _inlines.MusicArtistXPersonInline,
        _inlines.MusicalInstrumentXPersonInline,
    ]
    list_display = (
        'image_tag', 'preferred_name', 'full_name', 'is_living',
        'date_of_birth', 'date_of_death', 'age', 'notes',
    )
    list_display_links = ('preferred_name', 'full_name',)
    list_select_related = ('featured_photo__photo',)
    ordering = ('preferred_name', 'first_name', 'last_name',)
    search_fields = ('first_name', 'last_name', 'nickname', 'preferred_name',)

    @staticmethod
    def image_tag(obj):
        if not obj.featured_photo:
            return ''
        return format_html(
            '<img src="{}" alt="{}">',
            obj.featured_photo.photo.image_thumbnail.url,
            obj.preferred_name
        )


@admin.register(person.PersonXPhoto)
class PersonXPhoto(admin.ModelAdmin):
    pass
