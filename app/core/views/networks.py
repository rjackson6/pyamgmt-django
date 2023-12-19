from django_ccbv.views import TemplateView

from schemaviz import Edge, Node, NodeFont, VisNetwork

from .models import (
    MusicAlbumXMusicArtist,
    MusicAlbumEditionXSongRecording,
    MusicArtistXPerson,
    MusicArtistXSongRecording,
)


class MusicArtistNetworkView(TemplateView):
    template_name = 'core/music-artist-network.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        nodes = {}
        edges = []
        # Album <-> Artist relationships
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
                dashes=True,
            ))
        # Artist <-> Person
        qs = (
            MusicArtistXPerson.objects
            .select_related('music_artist', 'person')
        )
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
            edges.append(Edge(
                from_=person_key,
                to=music_artist_key,
            ))
        # Album[Edition] <-> Recording
        # Not worried about the specific edition; rolling up to the album
        # is fine here.
        qs = (
            MusicAlbumEditionXSongRecording.objects
            .select_related(
                'music_album_edition__music_album',
                'song_recording__song',
            )
        )
        for edge in qs:
            music_album = edge.music_album_edition.music_album
            song_recording = edge.song_recording
            music_album_key = f'music_album-{music_album.pk}'
            song_recording_key = f'song_recording-{song_recording.pk}'
            if music_album_key not in nodes:
                nodes[music_album_key] = Node(
                    id=music_album_key,
                    label=music_album.title,
                    group='music_album',
                )
            if song_recording_key not in nodes:
                nodes[song_recording_key] = Node(
                    id=song_recording_key,
                    label=song_recording.song.title,
                    group='song_recording',
                )
            edges.append(Edge(
                from_=music_album_key,
                to=song_recording_key,
                dashes=True,
            ))
        # Artist <-> Recording
        qs = (
            MusicArtistXSongRecording.objects
            .select_related('music_artist', 'song_recording')
        )
        for edge in qs:
            music_artist = edge.music_artist
            song_recording = edge.song_recording
            music_artist_key = f'music_artist-{music_artist.pk}'
            song_recording_key = f'song_recording-{song_recording.pk}'
            if music_artist_key not in nodes:
                nodes[music_artist_key] = Node(
                    id=music_artist_key,
                    label=music_artist.name,
                    group='music_artist',
                    font=NodeFont(size=30),
                )
            if song_recording_key not in nodes:
                nodes[song_recording_key] = Node(
                    id=song_recording_key,
                    label=song_recording.song.title,
                    group='song_recording',
                )
            edges.append(Edge(
                from_=music_artist_key,
                to=song_recording_key,
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
