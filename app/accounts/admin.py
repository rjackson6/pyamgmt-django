from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    User,
    UserXBeer,
)


admin.site.register(User, UserAdmin)


@admin.register(UserXBeer)
class BeerXUserAdmin(admin.ModelAdmin):
    list_display = ('_description', 'has_tried', 'worthy')

    @staticmethod
    def _description(obj):
        return f'{obj.user}: {obj.beer.name}'
