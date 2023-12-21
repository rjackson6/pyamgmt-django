from collections import defaultdict

from django_ccbv.views import TemplateView

from schemaviz import Edge, Node, NodeFont, VisNetwork

from .models import (
    MusicAlbumXMusicArtist,
    MusicAlbumXMusicTag,
    MusicAlbumEditionXSongRecording,
    MusicArtistXPerson,
    MusicArtistXSongPerformance,
)
from ..models import MusicArtistXSong, SongXSong


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


class MusicArtistNetworkView(TemplateView):
    template_name = 'core/music-artist-network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        album_to_artist_map = defaultdict(list)
        artist_to_artist_set = set()
        artist_to_song_arrangement_set = set()
        nodes = {}
        edges = []
        # Artist <-> Person
        qs = MusicArtistXPerson.with_related.all()
        for edge in qs:
            music_artist = edge.music_artist
            person = edge.person
            music_artist_key = f'music_artist-{music_artist.pk}'
            person_key = f'person-{person.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            if person_key not in nodes:
                nodes[person_key] = Node(
                    id=person_key,
                    label=edge.person.full_name,
                    group='person',
                )
            dashes = None
            if edge.is_active is False:
                dashes = True
            edges.append(Edge(
                from_=person_key,
                to=music_artist_key,
                dashes=dashes,
            ))
        # Album <-> Artist
        qs = (
            MusicAlbumXMusicArtist.objects
            .select_related(
                'music_album',
                'music_artist',
            )
        )
        for edge in qs:
            music_album = edge.music_album
            music_artist = edge.music_artist
            music_album_key = f'music_album-{music_album.pk}'
            music_artist_key = f'music_artist-{music_artist.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            album_to_artist_map[music_album_key].append(music_artist_key)
        # Album <-> Song
        qs = (
            MusicAlbumEditionXSongRecording.objects
            .select_related(
                'music_album_edition__music_album',
                'song_recording__song_performance__song_arrangement',
            )
        )
        for edge in qs:
            music_album = edge.music_album_edition.music_album
            song_arrangement = edge.song_recording.song_performance.song_arrangement
            music_album_key = f'music_album-{music_album.pk}'
            song_arrangement_key = f'song_arrangement-{song_arrangement.pk}'
            music_artist_keys = album_to_artist_map.get(music_album_key, [])
            for music_artist_key in music_artist_keys:
                t = music_artist_key, song_arrangement_key
                artist_to_song_arrangement_set.add(t)
        vis_data = VisNetwork(list(nodes.values()), edges)
        context.update({'vis_data': vis_data.to_dict()})
        return context


class MusicArtistDetailedNetworkView(TemplateView):
    template_name = 'core/music-artist-network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        album_to_artist_map = defaultdict(list)
        artist_to_song_arrangement_set = set()
        nodes = {}
        edges = []
        # Generalizing this would need a from_attr, to_attr, and a handler
        # for connected foreign keys, as well as labels and keys.
        # Artist <-> Person
        qs = MusicArtistXPerson.with_related.all()
        for edge in qs:
            music_artist = edge.music_artist
            person = edge.person
            music_artist_key = f'music_artist-{music_artist.pk}'
            person_key = f'person-{person.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            if person_key not in nodes:
                nodes[person_key] = Node(
                    id=person_key,
                    label=edge.person.full_name,
                    group='person',
                )
            dashes = None
            if edge.is_active is False:
                dashes = True
            edges.append(Edge(
                from_=person_key,
                to=music_artist_key,
                dashes=dashes,
                length=600,
            ))
        # Album <-> Artist
        qs = (
            MusicAlbumXMusicArtist.objects
            .select_related(
                'music_album',
                'music_artist',
            )
        )
        for edge in qs:
            music_album = edge.music_album
            music_artist = edge.music_artist
            music_album_key = f'music_album-{music_album.pk}'
            music_artist_key = f'music_artist-{music_artist.pk}'
            if music_album_key not in nodes:
                nodes[music_album_key] = Node(
                    id=music_album_key,
                    label=music_album.title,
                    group='music_album',
                )
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            edges.append(Edge(
                from_=music_album_key,
                to=music_artist_key,
            ))
            album_to_artist_map[music_album_key].append(music_artist_key)
        # Album <-> Song
        # If Artist connects through a song, ignore additional edges
        # later on
        qs = (
            MusicAlbumEditionXSongRecording.objects
            .select_related(
                'music_album_edition__music_album',
                'song_recording__song_performance__song_arrangement',
            )
        )
        for edge in qs:
            music_album = edge.music_album_edition.music_album
            song_arrangement = edge.song_recording.song_performance.song_arrangement
            music_album_key = f'music_album-{music_album.pk}'
            song_arrangement_key = f'song_arrangement-{song_arrangement.pk}'
            if music_album_key not in nodes:
                nodes[music_album_key] = Node(
                    id=music_album_key,
                    label=music_album.title,
                    group='music_album',
                )
            if song_arrangement_key not in nodes:
                nodes[song_arrangement_key] = Node(
                    id=song_arrangement_key,
                    label=song_arrangement.title,
                    group='song',
                )
            edges.append(Edge(
                from_=music_album_key,
                to=song_arrangement_key,
            ))
            # music_artist_key = album_to_artist_map.get(music_album_key, None)
            music_artist_keys = album_to_artist_map.get(music_album_key, [])
            for music_artist_key in music_artist_keys:
                t = music_artist_key, song_arrangement_key
                artist_to_song_arrangement_set.add(t)
        # Artist <-> Song
        qs = (
            MusicArtistXSongPerformance.objects
            .select_related(
                'music_artist', 'song_performance__song_arrangement'
            )
        )
        for edge in qs:
            music_artist = edge.music_artist
            song_arrangement = edge.song_performance.song_arrangement
            music_artist_key = f'music_artist-{music_artist.pk}'
            song_arrangement_key = f'song_arrangement-{song_arrangement.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            if song_arrangement_key not in nodes:
                nodes[song_arrangement_key] = Node(
                    id=song_arrangement_key,
                    label=song_arrangement.title,
                    group='song',
                )
            t = music_artist_key, song_arrangement_key
            if t not in artist_to_song_arrangement_set:
                edges.append(Edge(
                    from_=music_artist_key,
                    to=song_arrangement_key,
                ))
                artist_to_song_arrangement_set.add(t)
        # Artist <-> Song
        qs = (
            MusicArtistXSong.objects
            .select_related('music_artist', 'song')
        )
        for edge in qs:
            music_artist = edge.music_artist
            song = edge.song
            music_artist_key = f'music_artist-{music_artist.pk}'
            song_key = f'song-{song.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            if song_key not in nodes:
                nodes[song_key] = Node(
                    id=song_key,
                    label=song.title,
                    group='song',
                )
            t = music_artist_key, song_key
            if t not in artist_to_song_arrangement_set:
                edges.append(Edge(
                    from_=music_artist_key,
                    to=song_key,
                ))
                artist_to_song_arrangement_set.add(t)
        # Song <-> Song
        qs = (
            SongXSong.objects
            .select_related('song_archetype', 'song_derivative')
        )
        for edge in qs:
            a = edge.song_archetype
            d = edge.song_derivative
            for x in (a, d):
                song_key = f'song-{x.pk}'
                if song_key not in nodes:
                    nodes[song_key] = Node(
                        id=song_key,
                        label=x.title,
                        group='song',
                    )
            edges.append(Edge(
                from_=f'song-{a.pk}',
                to=f'song-{d.pk}',
            ))
        vis_data = VisNetwork(list(nodes.values()), edges)
        context.update({
            'vis_data': vis_data.to_dict(),
        })
        return context


class MusicTagNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        qs = (
            MusicAlbumXMusicTag.objects
            .select_related('music_album', 'music_tag')
        )
        nodes = {}
        edges = []
        for edge in qs:
            music_album = edge.music_album
            music_tag = edge.music_tag
            music_album_key = f'music_album-{music_album.pk}'
            music_tag_key = music_tag.name
            if music_album_key not in nodes:
                nodes[music_album_key] = Node(
                    id=music_album_key,
                    label=music_album.title,
                    group='music_album',
                )
            if music_tag_key not in nodes:
                nodes[music_tag_key] = Node(
                    id=music_tag_key,
                    label=music_tag.name,
                    group='music_tag',
                )
            edges.append(Edge(
                from_=music_album_key,
                to=music_tag_key,
            ))
        vis_data = VisNetwork(list(nodes.values()), edges)
        context.update({
            'vis_data': vis_data.to_dict(),
        })
        return context


class SongNetworkView(TemplateView):
    template_name = 'core/network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        return context