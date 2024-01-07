from collections import defaultdict
import itertools
from typing import Callable

from schemaviz.utils import Edge, Node, VisNetwork

from core.models import (
    MotionPictureXPerson,
    MusicAlbumXMusicArtist,
    MusicAlbumXPerson,
    MusicArtistXPerson,
    MusicArtistXSong,
    MusicArtistXSongPerformance,
    PersonXPersonRelation,
    PersonXPersonRelationship,
    PersonXSong,
    PersonXSongPerformance,
    PersonXVideoGame, MusicAlbumXVideoGame,
)


def resolve_edge_kwargs(
        edge_kwargs: dict | Callable = None,
        edge=None):
    if callable(edge_kwargs):
        return edge_kwargs(edge)
    else:
        return edge_kwargs


def motion_picture_x_person(edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
    nodes = {}
    edges = []
    edge_set = set()
    qs = (
        MotionPictureXPerson.objects
        .select_related('motion_picture', 'person')
    )
    for edge in qs:
        motion_picture = edge.motion_picture
        motion_picture_node = Node.from_motion_picture(motion_picture)
        if motion_picture_node.id not in nodes:
            nodes[motion_picture_node.id] = motion_picture_node
        person = edge.person
        person_node = Node.from_person(person)
        if person_node.id not in nodes:
            nodes[person_node.id] = person_node
        edge_key = (motion_picture_node.id, person_node.id)
        if edge_key not in edge_set:
            kwargs = resolve_edge_kwargs(edge_kwargs, edge)
            edge_set.add(edge_key)
            edges.append(Edge(
                from_=person_node.id,
                to=motion_picture_node.id,
                **kwargs
            ))
    return VisNetwork(nodes, edges)


def music_album_x_music_artist(
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    """Networks where two or more artists worked on an album together."""
    edge_kwargs = edge_kwargs or {}
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
                kwargs = resolve_edge_kwargs(edge_kwargs)
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=node_a.id,
                    to=node_b.id,
                    **kwargs
                ))
    return VisNetwork(nodes, edges)


def music_album_x_person(edge_kwargs: dict = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
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
                    **edge_kwargs
                ))
    return VisNetwork(nodes, edges)


def music_album_x_video_game(
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
    album_to_video_game_map = defaultdict(list)
    nodes = {}
    edges = []
    edge_set = set()
    qs = (
        MusicAlbumXVideoGame.objects
        .select_related('music_album', 'video_game')
    )
    for edge in qs:
        album_to_video_game_map[edge.music_album.pk].append(edge.video_game)
    qs = (
        MusicAlbumXMusicArtist.objects
        .select_related('music_album', 'music_artist')
        .filter(music_album_id__in=album_to_video_game_map.keys())
    )
    for edge in qs:
        music_artist = edge.music_artist
        music_artist_node = Node.from_music_artist(music_artist)
        if music_artist_node.id not in nodes:
            nodes[music_artist_node.id] = music_artist_node
        for video_game in album_to_video_game_map.get(edge.music_album.pk, []):
            video_game_node = Node.from_video_game(video_game)
            if video_game_node.id not in nodes:
                nodes[video_game_node.id] = video_game_node
            edge_key = (music_artist_node.id, video_game_node.id)
            if edge_key not in edge_set:
                kwargs = resolve_edge_kwargs(edge_kwargs, edge)
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=music_artist_node.id,
                    to=video_game_node.id,
                    **kwargs
                ))
    return VisNetwork(nodes, edges)


def music_artist_x_person(
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
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
        edge_key = (person_node.id, music_artist_node.id)
        if edge_key not in edge_set:
            kwargs = resolve_edge_kwargs(edge_kwargs, edge)
            edge_set.add(edge_key)
            edges.append(Edge(
                from_=person_node.id,
                to=music_artist_node.id,
                **kwargs
            ))
    return VisNetwork(nodes, edges)


def person_x_person(
        queryset, edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
    nodes = {}
    edges = []
    edge_set = set()
    for edge in queryset:
        person_a = edge.person_a
        person_a_node = Node.from_person(person_a)
        if person_a_node.id not in nodes:
            nodes[person_a_node.id] = person_a_node
        person_b = edge.person_b
        person_b_node = Node.from_person(person_b)
        if person_b_node.id not in nodes:
            nodes[person_b_node.id] = person_b_node
        edge_key = (person_a_node.id, person_b_node.id)
        if edge_key not in edge_set:
            kwargs = resolve_edge_kwargs(edge_kwargs, edge)
            edges.append(Edge(
                from_=person_a_node.id,
                to=person_b_node.id,
                **kwargs,
            ))
    return VisNetwork(nodes, edges)


def person_x_person_relation(
        queryset=None,
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    if not queryset:
        queryset = (
            PersonXPersonRelation.objects
            .select_related('person_a', 'person_b')
        )
    return person_x_person(queryset, edge_kwargs)


def person_x_person_relationship(
        queryset=None,
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    if not queryset:
        queryset = (
            PersonXPersonRelationship.objects
            .select_related('person_a', 'person_b')
        )
    return person_x_person(queryset, edge_kwargs)


def person_x_song(edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
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
                kwargs = resolve_edge_kwargs(edge_kwargs, edge)
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_node.id,
                    to=music_artist_node.id,
                    **kwargs
                ))
    return VisNetwork(nodes, edges)


def person_x_song_performance(
        edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
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
                kwargs = resolve_edge_kwargs(edge_kwargs, edge)
                edge_set.add(edge_key)
                edges.append(Edge(
                    from_=person_node.id,
                    to=music_artist_node.id,
                    **kwargs
                ))
    return VisNetwork(nodes, edges)


def person_x_video_game(edge_kwargs: dict | Callable = None) -> VisNetwork:
    edge_kwargs = edge_kwargs or {}
    nodes = {}
    edges = []
    edge_set = set()
    qs = (
        PersonXVideoGame.objects
        .select_related('person', 'video_game')
    )
    for edge in qs:
        person = edge.person
        person_node = Node.from_person(person)
        if person_node.id not in nodes:
            nodes[person_node.id] = person_node
        video_game = edge.video_game
        video_game_node = Node.from_video_game(video_game)
        if video_game_node.id not in nodes:
            nodes[video_game_node.id] = video_game_node
        edge_key = (person_node.id, video_game_node.id)
        if edge_key not in edge_set:
            kwargs = resolve_edge_kwargs(edge_kwargs, edge)
            edge_set.add(edge_key)
            edges.append(Edge(
                from_=person_node.id,
                to=video_game_node.id,
                **kwargs
            ))
    return VisNetwork(nodes, edges)
