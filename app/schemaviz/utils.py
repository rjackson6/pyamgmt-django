from collections import Counter
from dataclasses import asdict, dataclass, field

from django.apps import apps
from django.db.models.fields.related import RelatedField


@dataclass(kw_only=True)
class NodeFont:
    color: str | None = None
    size: int | None = None
    face: str | None = None
    background: str | None = None
    strokeWidth: int | None = None
    align: str | None = None
    vadjust: int | None = None
    multi: bool | str | None = None


@dataclass(kw_only=True)
class Node:
    valid_shapes = (
        'ellipse', 'circle', 'database', 'box', 'text',
        'image', 'circularImage', 'diamond', 'dot', 'star', 'triangle',
        'triangleDown', 'hexagon', 'square', 'icon',
        'custom',
    )

    id: str
    label: str
    group: str = ''
    mass: int = 1  # "count" would help generalize
    physics: bool | None = None
    shape: str | None = None
    value: int = 1
    font: NodeFont | None = None


@dataclass(kw_only=True)
class EdgeColor:
    color: str = None
    highlight: str = None
    hover: str = None
    inherit: str = None
    opacity: float = None


@dataclass(kw_only=True)
class Edge:
    from_: str
    to: str
    color: EdgeColor | None = None
    dashes: list | bool | None = None
    label: str = ''
    length: int | None = None
    physics: bool | None = None
    smooth: dict | bool | None = None


@dataclass(slots=True)
class VisNetwork:
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=self.dict_factory)

    @staticmethod
    def dict_factory(kv_pairs):
        m = {'from_': 'from'}
        return {m.get(k, k): v for k, v, in kv_pairs if v is not None}


# noinspection PyProtectedMember
def apps_dataset() -> dict:
    nodes = {}
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
                edge_color = None
                length = None
                smooth = None
                if field.one_to_one:
                    edge_color = EdgeColor(color='CC5555', opacity=0.9)
                elif field.many_to_many:
                    edge_color = EdgeColor(color='8888FF', opacity=0.6)
                    length = 400
                    smooth = False
                related_model = field.related_model
                related_label = related_model._meta.label
                edge = Edge(
                    from_=label,
                    to=related_label,
                    color=edge_color,
                    length=length,
                    smooth=smooth,
                )
                edges.append(edge)
                # Use to_ as the "mass" for the related node
                tos[related_label] += 1
    # Add the counts to the nodes after the keys are populated
    for k, count in tos.items():
        nodes[k].value += count
        nodes[k].mass += count
    x = VisNetwork(list(nodes.values()), edges)
    return x.to_dict()
