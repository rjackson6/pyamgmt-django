from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Protocol, Self

from django.apps import apps
from django.db.models.fields.related import RelatedField


def vis_dict_factory(kv_pairs) -> dict:
    m = {'from_': 'from'}
    return {m.get(k, k): v for k, v, in kv_pairs if v is not None}


class MotionPicture(Protocol):
    pk: int
    title: str


class MusicArtist(Protocol):
    pk: int
    name: str


class Person(Protocol):
    pk: int
    preferred_name: str


class Song(Protocol):
    pk: int
    title: str


class VideoGame(Protocol):
    pk: int
    title: str


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
class NodeOptions:
    font: NodeFont | None = None
    mass: int | None = None
    opacity: float | None = None
    physics: bool | None = None
    shape: str | None = None
    value: int | None = None


@dataclass(kw_only=True)
class Node(NodeOptions):
    # TODO 2024-01-07: Enum for these would be easier
    valid_shapes = (
        'ellipse', 'circle', 'database', 'box', 'text',
        'image', 'circularImage', 'diamond', 'dot', 'star', 'triangle',
        'triangleDown', 'hexagon', 'square', 'icon',
        'custom',
    )

    id: str
    label: str
    group: str = ''

    @classmethod
    def from_motion_picture(
            cls, motion_picture: MotionPicture, **kwargs) -> Self:
        return cls(
            id=f'motion_picture-{motion_picture.pk}',
            label=motion_picture.title,
            group='motion_picture',
            **kwargs
        )

    @classmethod
    def from_music_artist(cls, music_artist: MusicArtist, **kwargs) -> Self:
        return cls(
            id=f'music_artist-{music_artist.pk}',
            label=music_artist.name,
            group='music_artist',
            font=NodeFont(size=30),
            **kwargs
        )

    @classmethod
    def from_person(cls, person: Person, **kwargs) -> Self:
        return cls(
            id=f'person-{person.pk}',
            label=person.preferred_name,
            group='person',
            **kwargs
        )

    @classmethod
    def from_song(cls, song: Song, **kwargs) -> Self:
        return cls(
            id=f'song-{song.pk}',
            label=song.title,
            group='song',
            **kwargs
        )

    @classmethod
    def from_video_game(cls, video_game: VideoGame, **kwargs) -> Self:
        return cls(
            id=f'video_game-{video_game.pk}',
            label=video_game.title,
            group='video_game',
            **kwargs
        )


@dataclass(kw_only=True)
class EdgeColor:
    color: str = None
    highlight: str = None
    hover: str = None
    inherit: str = None
    opacity: float = None


@dataclass(kw_only=True)
class EdgeOptions:
    arrows: dict | str | None = None
    chosen: dict | bool | None = None
    color: EdgeColor | None = None
    dashes: list | bool | None = None
    label: str = ''
    length: int | None = None
    physics: bool | None = None
    smooth: dict | bool | None = None
    width: int | None = None


@dataclass
class Edge(EdgeOptions):
    from_: str
    to: str


@dataclass(slots=True)
class VisNetwork:
    # TODO: Just key edges with (from, to) values.
    nodes: dict[str, Node] = field(default_factory=dict)
    edges: list[Edge] = field(default_factory=list)
    _node_set: set[tuple[str, str]] = field(default_factory=set, init=False)
    _edge_set: set[tuple[str, str]] = field(default_factory=set, init=False)

    def extend(
            self,
            network: Self,
            duplicate_edges: bool = False,
            overwrite_nodes: bool = False,
    ) -> None:
        if overwrite_nodes:
            self.nodes.update(network.nodes)
        else:
            network.nodes.update(self.nodes)
            self.nodes = network.nodes
        if duplicate_edges:
            self.edges.extend(network.edges)
        else:
            self.edges.extend(
                x for x in network.edges
                if (x.from_, x.to) not in self._edge_set
            )
        self._node_set.update(network._node_set)
        self._edge_set.update(network._edge_set)

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=vis_dict_factory)

    def to_json(self) -> dict:
        data = {
            k: v for k, v in self.to_dict().items()
            if not k.startswith('_')
        }
        data['nodes'] = list(data['nodes'].values())
        return data


@dataclass(slots=True)
class VisOptions:
    layout: dict = field(default_factory=dict)
    nodes: dict = field(default_factory=dict)
    edges: dict = field(default_factory=dict)
    physics: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.layout:
            self.layout = self.get_default_layout()
        if not self.nodes:
            self.nodes = self.get_default_nodes()
        if not self.edges:
            self.edges = self.get_default_edges()
        if not self.physics:
            self.physics = self.get_default_physics()

    def to_dict(self) -> dict:
        return asdict(self, dict_factory=vis_dict_factory)

    @staticmethod
    def get_default_layout() -> dict:
        return dict(
            improvedLayout=False
        )

    @staticmethod
    def get_default_nodes() -> dict:
        return dict(
            font=dict(size=24),
            opacity=0.8,
            shape='box',
        )

    @staticmethod
    def get_default_edges() -> dict:
        return dict(
            smooth=False
        )

    @staticmethod
    def get_default_physics() -> dict:
        return dict(
            barnesHut=dict(
                gravitationalConstant=-10000,
                springLength=200,
            )
        )


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
        for field_ in fields:
            if isinstance(field_, RelatedField):
                edge_color = None
                length = None
                smooth = None
                if field_.one_to_one:
                    edge_color = EdgeColor(color='CC5555', opacity=0.9)
                elif field_.many_to_many:
                    edge_color = EdgeColor(color='8888FF', opacity=0.6)
                    length = 400
                    smooth = False
                related_model = field_.related_model
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
    x = VisNetwork(nodes, edges)
    return x.to_json()
