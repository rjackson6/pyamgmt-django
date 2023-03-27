from django.apps import apps
from django.db.models.fields.related import RelatedField


# noinspection PyProtectedMember
def apps_as_dataset() -> dict:
    """Structures installed app data for use with vis-network."""
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
    data = {'nodes': nodes, 'edges': edges}
    return data
