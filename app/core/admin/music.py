from django.contrib import admin

from ..models import music, music_tag


@admin.register(music.MusicRole)
class MusicRoleAdmin(admin.ModelAdmin):
    ordering = ('name',)


@admin.register(music_tag.MusicTag)
class MusicTagAdmin(admin.ModelAdmin):
    ordering = ('name',)


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
