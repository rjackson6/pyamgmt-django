from collections import defaultdict
import itertools

from schemaviz.utils import Edge, EdgeColor, Node, VisNetwork

from core.models import (
    MusicAlbumXMusicArtist,
    MusicAlbumXPerson,
    MusicArtistXPerson,
    MusicArtistXSong,
    MusicArtistXSongPerformance,
    PersonXSong,
    PersonXSongPerformance,
)


def music_album_x_music_artist() -> VisNetwork:
    """Networks where two or more artists worked on an album together."""
    album_to_artist_map = defaultdict(list)
    nodes = {}
    edges = []
    edge_set = set()
    qs = (
        MusicAlbumXMusicArtist.objects
        .select_related('music_album', 'music_artist')
        .order_by('music_artist_id')
    )
    for edge in qs:
        album_to_artist_map[edge.music_album.pk].append(edge.music_artist)
    for album, artists in album_to_artist_map.items():
        artist_combinations = itertools.combinations(artists, 2)
        for c in artist_combinations:
            artist_a, artist_b = c[0], c[1]
            node_a = Node.from_music_artist(artist_a)
            if node_a.id not in nodes:
                nodes[node_a.id] = node_a
            node_b = Node.from_music_artist(artist_b)
            if node_b.id not in nodes:
                nodes[node_b.id] = node_b
            edge_key = (node_a.id, node_b.id)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=node_a.id,
                    to=node_b.id,
                    width=2,
                ))
    return VisNetwork(nodes, edges)


def music_album_x_person() -> VisNetwork:
    album_to_person_map = defaultdict(list)
    nodes = {}
    edges = []
    edge_set = set()
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
        music_artist_node = Node.from_music_artist(music_artist)
        if music_artist_node.id not in nodes:
            nodes[music_artist_node.id] = music_artist_node
        for person in album_to_person_map.get(edge.music_album.pk, []):
            person_node = Node.from_person(person)
            if person_node.id not in nodes:
                nodes[person_node.id] = person_node
            edge_key = (person_node.id, music_artist_node.id)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_node.id,
                    to=music_artist_node.id,
                    color=EdgeColor(
                        color='66FF66'
                    ),
                    length=600,
                ))
    return VisNetwork(nodes, edges)


def music_artist_x_person() -> VisNetwork:
    nodes = {}
    edges = []
    edge_set = set()
    qs = MusicArtistXPerson.with_related.all()
    for edge in qs:
        music_artist = edge.music_artist
        music_artist_node = Node.from_music_artist(music_artist)
        if music_artist_node.id not in nodes:
            nodes[music_artist_node.id] = music_artist_node
        person = edge.person
        person_node = Node.from_person(person)
        if person_node.id not in nodes:
            nodes[person_node.id] = person_node
        dashes = None
        if edge.is_active is False:
            dashes = True
        edge_key = (person_node.id, music_artist_node.id)
        if edge_key not in edge_set:
            edge_set.add(edge_key)
            edges.append(Edge(
                from_=person_node.id,
                to=music_artist_node.id,
                dashes=dashes,
                width=3,
            ))
    return VisNetwork(nodes, edges)


def person_x_song() -> VisNetwork:
    song_to_person_map = defaultdict(list)
    nodes = {}
    edges = []
    edge_set = set()
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
        music_artist_node = Node.from_music_artist(music_artist)
        if music_artist_node.id not in nodes:
            nodes[music_artist_node.id] = music_artist_node
        for person in song_to_person_map.get(edge.song.pk, []):
            person_node = Node.from_person(person)
            if person_node.id not in nodes:
                nodes[person_node.id] = person_node
            edge_key = (person_node.id, music_artist_node.id)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_node.id,
                    to=music_artist_node.id,
                    color=EdgeColor(
                        color='2266FF'
                    ),
                    length=600,
                ))
    return VisNetwork(nodes, edges)


def person_x_song_performance() -> VisNetwork:
    song_performance_to_person_map = defaultdict(list)
    nodes = {}
    edges = []
    edge_set = set()
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
        music_artist_node = Node.from_music_artist(music_artist)
        if music_artist_node.id not in nodes:
            nodes[music_artist_node.id] = music_artist_node
        persons = song_performance_to_person_map.get(
            edge.song_performance.pk, [])
        for person in persons:
            person_node = Node.from_person(person)
            if person_node.id not in nodes:
                nodes[person_node.id] = person_node
            edge_key = (person_node.id, music_artist_node.id)
            if edge_key not in edge_set:
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_node.id,
                    to=music_artist_node.id,
                    color=EdgeColor(
                        color='6688FF',
                    ),
                ))
    return VisNetwork(nodes, edges)
