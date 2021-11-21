__all__ = [
    'VehicleYearChoiceField'
]


from deform.forms.models import ModelChoiceField


class VehicleYearChoiceField(ModelChoiceField):
    def __init__(self, queryset, **kwargs):
        if queryset is not None:
            queryset = (
                queryset
                .select_related('vehicletrim__vehiclemodel__vehiclemake')
                .order_by(
                    '-year',
                    'vehicletrim__vehiclemodel__vehiclemake__name',
                    'vehicletrim__vehiclemodel__name',
                    'vehicletrim__name'
                )
            )
        super().__init__(queryset, **kwargs)

    def label_from_instance(self, obj):
        vehicleyear = obj.year
        vehicletrim = obj.vehicletrim.name
        vehiclemodel = obj.vehicletrim.vehiclemodel.name
        vehiclemake = obj.vehicletrim.vehiclemodel.vehiclemake.name
        return f'{vehicleyear} {vehiclemake} {vehiclemodel} {vehicletrim}'