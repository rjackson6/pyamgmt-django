# Generated by Django 5.0 on 2023-12-24 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_remove_songarrangement_unique_song_arrangement_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='motionpicture',
            name='songs',
            field=models.ManyToManyField(blank=True, related_name='+', through='core.MotionPictureXSong', to='core.song'),
        ),
        migrations.AlterField(
            model_name='songperformance',
            name='music_artists',
            field=models.ManyToManyField(blank=True, related_name='+', through='core.MusicArtistXSongPerformance', to='core.musicartist'),
        ),
        migrations.AlterField(
            model_name='songperformance',
            name='personnel',
            field=models.ManyToManyField(blank=True, related_name='+', through='core.PersonXSongPerformance', to='core.person'),
        ),
        migrations.AlterField(
            model_name='songrecording',
            name='music_album_editions',
            field=models.ManyToManyField(blank=True, related_name='+', through='core.MusicAlbumEditionXSongRecording', to='core.musicalbumedition'),
        ),
    ]