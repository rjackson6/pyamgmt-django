from collections import defaultdict
from itertools import combinations

from django_ccbv.views import TemplateView

from schemaviz import Edge, EdgeColor, Node, NodeFont, VisNetwork

from ..models import (
    MusicAlbumXMusicArtist,
    MusicAlbumXMusicTag,
    MusicAlbumXPerson,
    MusicAlbumEditionXSongRecording,
    MusicArtistXPerson,
    MusicArtistXSong,
    MusicArtistXSongPerformance,
    PersonXSong,
    PersonXSongPerformance,
)


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
    """Explores edges that relate Music Artists to people.

    Factors out specific albums and songs from display to reduce rendering.
    """
    template_name = 'core/music-artist-network.html'

    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        nodes = {}
        edges = []
        edge_set = set()
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
            edge_key = (person_key, music_artist_key)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_key,
                    to=music_artist_key,
                    dashes=dashes,
                    width=3,
                ))
        # MusicAlbum - Artist traversal
        # These artists should link to each other.
        album_to_artist_map = defaultdict(list)
        qs = (
            MusicAlbumXMusicArtist.objects
            .select_related('music_album', 'music_artist')
            .order_by('music_artist_id')
        )
        for edge in qs:
            album_to_artist_map[edge.music_album.pk].append(edge.music_artist)
        for album, artists in album_to_artist_map.items():
            # These are combinations between the artists
            artist_combinations = combinations(artists, 2)
            for artist_a, artist_b in artist_combinations:
                key_a = f'music_artist-{artist_a.pk}'
                key_b = f'music_artist-{artist_b.pk}'
                edge_key = (key_a, key_b)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(Edge(
                        from_=key_a,
                        to=key_b,
                        width=2,
                    ))
        # MusicAlbum - Person traversal
        album_to_person_map = defaultdict(list)
        qs = (
            MusicAlbumXPerson.objects
            .select_related('music_album', 'person')
            .order_by('person_id')
        )
        for edge in qs:
            album_to_person_map[edge.music_album.pk].append(edge.person)
        qs = (
            MusicAlbumXMusicArtist.objects
            .select_related('music_album', 'music_artist')
            .filter(music_album_id__in=album_to_person_map.keys())
        )
        for edge in qs:
            music_artist = edge.music_artist
            music_artist_key = f'music_artist-{music_artist.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            for person in album_to_person_map.get(edge.music_album.pk, []):
                person_key = f'person-{person.pk}'
                if person_key not in nodes:
                    nodes[person_key] = Node(
                        id=person_key,
                        label=person.full_name,
                        group='person'
                    )
                edge_key = (person_key, music_artist_key)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(Edge(
                        from_=person_key,
                        to=music_artist_key,
                        color=EdgeColor(
                            color='66FF66'
                        ),
                        length=600,
                    ))
        # Song traversal
        song_to_person_map = defaultdict(list)
        qs = (
            PersonXSong.objects
            .select_related('person', 'song')
        )
        for edge in qs:
            song_to_person_map[edge.song.pk].append(edge.person)
        qs = (
            MusicArtistXSong.objects
            .select_related('music_artist', 'song')
            .filter(song_id__in=song_to_person_map.keys())
        )
        for edge in qs:
            music_artist = edge.music_artist
            music_artist_key = f'music_artist-{music_artist.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            for person in song_to_person_map.get(edge.song.pk, []):
                person_key = f'person-{person.pk}'
                if person_key not in nodes:
                    nodes[person_key] = Node(
                        id=person_key,
                        label=person.full_name,
                        group='person'
                    )
                edge_key = (person_key, music_artist_key)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(Edge(
                        from_=person_key,
                        to=music_artist_key,
                        color=EdgeColor(
                            color='2266FF'
                        ),
                        length=600,
                    ))
        # SongPerformance traversal
        song_performance_to_person_map = defaultdict(list)
        qs = (
            PersonXSongPerformance.objects
            .select_related('person', 'song_performance')
        )
        for edge in qs:
            (
                song_performance_to_person_map[edge.song_performance.pk]
                .append(edge.person)
            )
        qs = (
            MusicArtistXSongPerformance.objects
            .select_related('music_artist', 'song_performance')
            .filter(
                song_performance_id__in=song_performance_to_person_map.keys()
            )
        )
        for edge in qs:
            music_artist = edge.music_artist
            music_artist_key = f'music_artist-{music_artist.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            persons = song_performance_to_person_map.get(
                edge.song_performance.pk, [])
            for person in persons:
                person_key = f'person-{person.pk}'
                if person_key not in nodes:
                    nodes[person_key] = Node(
                        id=person_key,
                        label=person.full_name,
                        group='person'
                    )
                edge_key = (person_key, music_artist_key)
                if edge_key not in edge_set:
                    edge_set.add(edge_key)
                    edges.append(Edge(
                        from_=person_key,
                        to=music_artist_key,
                        color=EdgeColor(
                            color='6688FF',
                        ),
                    ))
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
