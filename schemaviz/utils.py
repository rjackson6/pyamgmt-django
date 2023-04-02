import dataclasses
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict

from django.apps import apps
from django.db.models.fields.related import RelatedField


@dataclass
class Node:
    id: str
    label: str
    group: str = ''
    mass: int = 1
    value: int = 1


@dataclass
class Edge:
    from_: str
    to: str
    label: str = ''


def edge_factory(kv_pairs):
    m = {'from_': 'from'}
    return {m.get(k, k): v for k, v, in kv_pairs}


# noinspection PyProtectedMember
def using_dataclasses():
    nodes = {}  # values() can make the list after the fact, I guess
    edges = []
    tos = Counter()
    for mdl in apps.get_models():
        label = mdl._meta.label
        node = Node(
            id=label,
            label=mdl._meta.object_name,
            group=mdl._meta.app_label
        )
        nodes[label] = node
        fields = mdl._meta.get_fields()
        for field in fields:
            if isinstance(field, RelatedField):
                related_model = field.related_model
                related_label = related_model._meta.label
                edge = Edge(
                    from_=label,
                    to=related_label
                )
                edges.append(edge)
                # Use to_ as the "mass" for the related node
                tos[related_label] += 1
    # Add the counts to the nodes after the keys are populated
    for k, count in tos.items():
        nodes[k].value += count
        nodes[k].mass += count
    return {
        'nodes': [dataclasses.asdict(dc) for dc in nodes.values()],
        'edges': [dataclasses.asdict(dc, dict_factory=edge_factory) for dc in edges],
    }


# noinspection PyProtectedMember
def apps_as_dataset() -> dict:
    """Structures installed app data for use with vis-network."""
    nodes = []  # format {id: '', label: ''}
    edges = []
    node_map = {}
    tos = Counter()
    for mdl in apps.get_models():
        node = {}
        label = mdl._meta.label
        nodes.append({
            'id': label,
            'label': mdl._meta.object_name,
            'group': mdl._meta.app_label,
        })
        node = {'id': label, 'label': mdl._meta.object_name, 'group': mdl._meta.app_label}
        node_map[label] = node
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
                tos[related_label] += 1

    data = {'nodes': nodes, 'edges': edges}
    return data


if __name__ == '__main__':
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyamgmtDjango.settings')
    import django
    django.setup()

    import pprint
    d = using_dataclasses()
    pprint.pp(d)
    pprint.pp(d.get('tos'))
