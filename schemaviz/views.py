from django.apps import apps

from ccbv.views import TemplateView


class MainView(TemplateView):
    template_name = 'schemaviz/main.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # get_models returns a list of classes
        # auto-created / swapped models False by default
        get_models = apps.get_models()

        # With get_models and access to the related objects by class, it should
        # be possible to build a network of the relations
        from django.db.models.fields.related import RelatedField
        from django.db.models.fields.reverse_related import ForeignObjectRel
        # TODO: A standard node/edge format would be ideal
        d = {}
        for mdl in get_models:
            label = mdl._meta.label  # noqa
            if label not in d:
                d[label] = {'to': [], 'from': []}
            fields = mdl._meta.get_fields()  # noqa
            for field in fields:
                related_model = None
                direction = None
                if isinstance(field, RelatedField):
                    # ForeignKey, which points to another model from this one
                    # Direction is "up" or "to"
                    related_model = field.related_model._meta.label  # noqa
                    direction = 'to'
                elif isinstance(field, ForeignObjectRel):
                    # Field from another model points to this model
                    # Direction is "down" or "from"
                    related_model = field.related_model._meta.label  # noqa
                    direction = 'from'
                if related_model:
                    # print(f'related_model found: {related_model}')
                    if related_model not in d:
                        d[related_model] = {'to': [], 'from': []}
                    d[label][direction].append(related_model)

        context.update({
            'd': d,
        })
        return context
