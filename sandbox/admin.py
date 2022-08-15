from django.contrib import admin

from sandbox import models


admin.site.register(models.OneToOneTableBase)
admin.site.register(models.OneToOneTableSubclass)
admin.site.register(models.OneToOneParentLinkBase)
admin.site.register(models.OneToOneParentLinkSubclass)
admin.site.register(models.MultiTableBase)
admin.site.register(models.MultiTableSubclass)
admin.site.register(models.MultiTableWithPtrBase)
admin.site.register(models.MultiTableWithPtrSubclass)
