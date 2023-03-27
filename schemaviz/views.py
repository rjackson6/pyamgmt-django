from django.apps import apps

from ccbv.views import TemplateView


class MainView(TemplateView):
    template_name = 'schemaviz/main.html'

    # noinspection PyProtectedMember
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        # With get_models and access to the related objects by class, it should
        # be possible to build a network of the relations
        from django.db.models.fields.related import RelatedField
        # Using vis.js node/edge format
        nodes = []  # format {id: '', label: ''}
        edges = []
        for mdl in apps.get_models():
            label = mdl._meta.label
            nodes.append({
                'id': label,
                'label': mdl._meta.object_name,
                'group': mdl._meta.app_label,
            })
            fields = mdl._meta.get_fields()
            for field in fields:
                if isinstance(field, RelatedField):
                    related_model = field.related_model
                    related_label = related_model._meta.label
                    edges.append({
                        'from': label,
                        'to': related_label,
                        # 'label': field.name,
                    })
        # TODO: Post-processing into vis "groups" might be nice
        #  Simple group could be "app_name"
        data = {'nodes': nodes, 'edges': edges}

        context.update({
            'vis_data': data,
        })
        return context
