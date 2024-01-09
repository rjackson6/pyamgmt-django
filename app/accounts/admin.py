from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as _UserAdmin

from .models import User


@admin.register(User)
class UserAdmin(_UserAdmin):
    pass
