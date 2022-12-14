# Script that creates a Spotify playlist with random tracks from other playlists
# If there are duplicates in the resulting playlist, they are removed
# Requires: spotipy
# Usage: python create_playlist_mix.py data.json
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
# Set SPOTIPY_REDIRECT_URI environment variable (e. g. to http://localhost:9090)

import spotipy
import random
import time
import json
import sys
from spotipy.oauth2 import SpotifyOAuth

def get_tracks_from_playlist(sp, playlist_id):
    """
    Given a spotipy Spotify instance and a playlist ID, returns a list containing the IDs of every track in that
    playlist.
    """

    offset = 0  # Keep an offset bc requests have a 50/100 track limit
    song_ids = []  # List for the songs from the playlist

    # If playlist_id is "saved", request saved tracks; otherwise, request tracks from the corresponding playlist
    if playlist_id == "saved":
        items = sp.current_user_saved_tracks(limit=50)['items']  # Max limit for saved tracks = 50
    else:
        items = sp.playlist_items(playlist_id, limit=100)['items']  # Max limit for playlists = 100

    # Iterate while getting items from the request
    while len(items) > 0:
        for item in items:
            song_ids.append(item['track']['id'])  # Append the ID of the track

        # Request next 50/100 items
        if playlist_id == "saved":
            offset += 50
            items = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        else:
            offset += 100
            items = sp.playlist_items(playlist_id, limit=100, offset=offset)['items']

    # Return list with all song IDs
    return song_ids

def get_random_tracks_from_playlist(sp, playlist_id, count):
    """
    Given a spotipy Spotify instance, a playlist ID and a number, returns a list containing that number of IDs of
    randomly selected tracks from that playlist.
    """

    song_ids = get_tracks_from_playlist(sp, playlist_id)

    # TODO: this does not work with saved songs
    # If count < 0, use all songs
    if count < 0:
        count = sp.playlist(playlist_id)['tracks']['total']  # Get number of songs

    # Shuffle tracks, take count and return them
    random.shuffle(song_ids)
    return song_ids[:count]

def main():
    if len(sys.argv) < 2:
        print("Usage: python create_playlist_mix.py data.json", file=sys.stderr)
        exit(1)

    # Define needed scopes:
    # * playlist-read-collaborative: to get tracks from collab playlists
    # * playlist-read-private: to get tracks from private playlists
    # * playlist-modify-private: to create the playlist and add tracks to it
    # * user-library-read: to get tracks from library (liked songs)
    scope = "playlist-read-collaborative playlist-read-private playlist-modify-private user-library-read"

    # Set up auth using Authorization Code Flow
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # Load data from JSON file. Format:
    # * new_playlist_name (string): name of the new playlist (leave blank for default)
    # * date_in_name (bool): if true, append — <today's date> at the end of the name of the playlist, with <today's date>
    #   the date of today in DD/MM/YY format.
    # * update_playlist (string): if null, a new playlist is created; else, use the playlist with this ID (all its tracks
    #   are removed first).
    # * user (string): user ID (username)
    # * playlists (list of object): list of playlists
    #   * playlist_id (string): ID of the playlist ("saved" for saved tracks)
    #   * count (number): number of tracks to add from the playlist
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    new_playlist_name = data['new_playlist_name']
    user = data['user']
    playlists = data['playlists']
    update_playlist = data['update_playlist']
    filler_playlist_id = data['filler_playlist_id']

    existing_playlist_song_ids = []  # List for the songs of the existing playlist

    # If update_playlist is null, create the new playlist and store its ID in a variable, else store the existing playlist
    # ID and get all its tracks
    if update_playlist is None:
        # If date_in_name is true, append date at the end of the name of the playlist
        if data['date_in_name']:
            new_playlist_name += " — " + time.strftime("%d/%m/%y")

        new_playlist_id = sp.user_playlist_create(user, new_playlist_name, public=False)['id']
    else:
        new_playlist_id = update_playlist

        offset = 0  # Keep an offset bc requests have a 100 track limit

        items = sp.playlist_items(new_playlist_id, limit=100)['items']  # Max limit for playlists = 100

        # Iterate while getting items from the request
        while len(items) > 0:
            for item in items:
                existing_playlist_song_ids.append(item['track']['id'])  # Append the ID of the track

            # Request next 100 items
            offset += 100
            items = sp.playlist_items(new_playlist_id, limit=100, offset=offset)['items']

    new_playlist_song_ids = []  # List for the songs of the new playlist
    total_count = 0  # Eventually, number of songs that should be selected in total across all playlists

    # Iterate over the playlists
    for playlist in playlists:
        playlist_id = playlist['playlist_id']
        count = playlist['count']

        total_count += count

        # Add shuffled tracks to the list of songs of the new playlist
        new_playlist_song_ids.extend(get_random_tracks_from_playlist(sp, playlist_id, count))

    # Remove duplicates from the list of songs
    new_playlist_song_ids = list(dict.fromkeys(new_playlist_song_ids))

    # If a filler playlist ID is specified, add random tracks from it
    if filler_playlist_id is not None:
        # Get all tracks from the filler playlist
        filler_playlist_song_ids = get_tracks_from_playlist(sp, filler_playlist_id)

        # While the desired number of tracks has not been achieved and there are tracks remaining from filler playlist,
        # keep adding new ones
        while len(new_playlist_song_ids) < total_count and not all(elem in new_playlist_song_ids for elem in filler_playlist_song_ids):
            # Number of tracks to take: difference between desired number and current number
            count = total_count - len(new_playlist_song_ids)

            # Add newly selected tracks and remove duplicates
            new_playlist_song_ids.extend(get_random_tracks_from_playlist(sp, filler_playlist_id, count))
            new_playlist_song_ids = list(dict.fromkeys(new_playlist_song_ids))

    # Shuffle list of songs
    random.shuffle(new_playlist_song_ids)

    # If update_playlist is not null, remove all its tracks 100 by 100 due to the limit
    if update_playlist is not None:
        while len(existing_playlist_song_ids) > 0:
            sp.playlist_remove_all_occurrences_of_items(new_playlist_id, existing_playlist_song_ids[:100])
            existing_playlist_song_ids = existing_playlist_song_ids[100:]

    # Add tracks to the new playlist 100 by 100 due to the limit
    while len(new_playlist_song_ids) > 0:
        sp.playlist_add_items(new_playlist_id, new_playlist_song_ids[:100])
        new_playlist_song_ids = new_playlist_song_ids[100:]

if __name__ == '__main__':
    main()
