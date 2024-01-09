from django_ccbv.views import TemplateView

from schemaviz import (
    BarnesHutOptions,
    Edge,
    EdgeColor,
    Node,
    NodeFont,
    NodeOptions,
    PhysicsOptions,
    VisNetwork,
    VisOptions,
)

from ..models import (
    MusicAlbumXMusicTag,
)
from ..utils import network


class NetworkIndex(TemplateView):
    template_name = 'core/network-index.html'


class MusicNetworkView(TemplateView):
    """Explores several edges of interest.

    Motion Picture <-> Music Album;
    Music Album <-> Music Artist;
    Music Album <-> Person;
    Music Album <-> Video Game;
    Music Artist <-> Person;
    """
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return context


class FilmGamesAndMusicNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        vis_data = network.person_to_motion_picture()
        vis_data.extend(network.person_to_music_artist())
        vis_data.extend(network.music_artist_via_music_album())
        vis_data.extend(
            network.person_to_music_artist_via_music_album())
        vis_data.extend(network.music_album_x_video_game())
        vis_data.extend(network.person_to_music_artist_via_song())
        vis_data.extend(network.person_to_music_artist_via_song_performance())
        vis_data.extend(network.person_to_video_game())

        vis_options = VisOptions(
            nodes=NodeOptions(
                font=NodeFont(
                    color='white',
                    size=20,
                ),
                opacity=0.8,
                shape='dot',
                value=1,
            ),
            physics=PhysicsOptions(
                barnesHut=BarnesHutOptions(
                    gravitationalConstant=-5000,
                )
            )
        )
        context.update({
            'vis_data': vis_data.to_json(),
            'vis_options': vis_options.to_dict()
        })
        return context


class MusicArtistNetworkView(TemplateView):
    """Explores edges that relate Music Artists to people.

    Factors out specific albums and songs from display to reduce rendering.
    """
    template_name = 'core/network.html'

    @staticmethod
    def get_music_artist_x_person_edge_kwargs(edge) -> dict:
        dashes = None
        width = 3
        if edge.is_active is False:
            dashes = True
            width = 1
        return {
            'dashes': dashes,
            'width': width,
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        vis_data = network.person_to_music_artist(
            edge_kwargs=self.get_music_artist_x_person_edge_kwargs
        )
        vis_data.extend(network.music_artist_via_music_album(
            edge_kwargs={
                'width': 2,
            }
        ))
        vis_data.extend(network.person_to_music_artist_via_music_album(
            edge_kwargs={
                'color': EdgeColor(color='66FF66'),
            }
        ))
        vis_data.extend(network.person_to_music_artist_via_song(
            edge_kwargs={
                'color': EdgeColor(color='2266FF'),
            }
        ))
        vis_data.extend(network.person_to_music_artist_via_song_performance(
            edge_kwargs={
                'color': EdgeColor(color='6688FF'),
            }
        ))
        vis_options = VisOptions(
            nodes=NodeOptions(
                font=NodeFont(
                    color='white',
                    size=20,
                ),
                opacity=0.8,
                shape='dot',
                value=1,
            ),
        )
        context.update({
            'vis_data': vis_data.to_json(),
            'vis_options': vis_options.to_dict(),
        })
        return context


class MusicTagNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        vn = VisNetwork()
        qs = (
            MusicAlbumXMusicTag.objects
            .select_related('music_album', 'music_tag')
        )
        for edge in qs:
            music_album = edge.music_album
            music_tag = edge.music_tag
            music_album_key = f'music_album-{music_album.pk}'
            music_tag_key = music_tag.name
            if music_album_key not in vn.nodes:
                vn.nodes[music_album_key] = Node(
                    id=music_album_key,
                    label=music_album.title,
                    group='music_album',
                )
            if music_tag_key not in vn.nodes:
                vn.nodes[music_tag_key] = Node(
                    id=music_tag_key,
                    label=music_tag.name,
                    group='music_tag',
                )
            vn.edges[(music_album_key, music_tag_key)].append(Edge(
                from_=music_album_key,
                to=music_tag_key,
            ))
        context.update({
            'vis_data': vn.to_json(),
        })
        return context


class PersonRelationView(TemplateView):
    template_name = 'core/network.html'

    @staticmethod
    def get_person_x_person_relation_edge_kwargs(edge) -> dict:
        color = EdgeColor(color='#4488FF')
        width = 3
        length = None
        if edge.relation in edge.Relation.get_sibling_members():
            color = EdgeColor(color='#BB0000')
            width = 2
            length = 600
        return {
            'color': color,
            'length': length,
            'width': width,
        }

    @staticmethod
    def get_person_x_person_relationship_edge_kwargs(edge) -> dict:
        color = EdgeColor(color='#00FF00')
        width = 1
        length = None
        if edge.relationship in edge.Relationship.get_partner_members():
            color = EdgeColor(color='#FF00FF')
            width = 3
            length = None
        return {
            'color': color,
            'width': width,
            'length': length,
        }

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        vis_data = network.person_x_person_relation(
            edge_kwargs=self.get_person_x_person_relation_edge_kwargs)
        vis_data.extend(
            network.person_x_person_relationship(
                edge_kwargs=self.get_person_x_person_relationship_edge_kwargs
            ), allow_duplicate_edges=True)
        context['vis_data'] = vis_data.to_json()
        return context


class SongNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return context
