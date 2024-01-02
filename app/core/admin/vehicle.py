from django.contrib import admin

from ..models import vehicle


@admin.register(vehicle.Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('admin_description',)
    list_select_related = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make',
    )
    ordering = (
        'vehicle_year__vehicle_trim__vehicle_model__vehicle_make__name',
        'vehicle_year__vehicle_trim__vehicle_model__name',
        'vehicle_year__vehicle_trim__name',
        'vehicle_year',
        'vin'
    )


admin.site.register(vehicle.VehicleMake)
admin.site.register(vehicle.VehicleMileage)
admin.site.register(vehicle.VehicleModel)
admin.site.register(vehicle.VehicleService)
admin.site.register(vehicle.VehicleServiceItem)
admin.site.register(vehicle.VehicleTrim)
admin.site.register(vehicle.VehicleYear)
