# Script that adds music from one or more playlists to another one, keeping a history to avoid readding tracks
# Requires: spotipy
# Usage: python update_playlist_with_new_music.py data.json
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
# Set SPOTIPY_REDIRECT_URI environment variable (e. g. to http://localhost:9090)

import spotipy
import json
import sys
import common
from spotipy.oauth2 import SpotifyOAuth

def main():
    if len(sys.argv) < 2:
        print("Usage: python update_playlist_with_new_music.py data.json", file=sys.stderr)
        exit(1)

    # Define needed scopes:
    # * playlist-read-collaborative: to get tracks from collab playlists
    # * playlist-read-private: to get tracks from private playlists
    # * playlist-modify-private: to add tracks to the playlist
    # * playlist-modify-public: to add tracks to the playlist
    # * user-library-read: to get tracks from library (liked tracks)
    scope = "playlist-read-collaborative playlist-read-private playlist-modify-private playlist-modify-public user-library-read"

    # Set up auth using Authorization Code Flow
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))

    # Load data from JSON file. Format:
    # * target_playlist_id (string): ID of the playlist to add the tracks to
    # * history_playlist_id (string): ID of the playlist where the history of tracks added to target playlist is kept
    # * source_playlsit_ids (list of string): list of IDs of playlists to get new tracks from
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    target_playlist_id = data['target_playlist_id']
    history_playlist_id = data['history_playlist_id']
    source_playlist_ids = data['source_playlist_ids']

    history_playlist_track_isrcs = []  # List for the current tracks of the history playlist
    target_playlist_track_ids = []  # List for the new tracks of the target playlist

    offset = 0  # Keep an offset bc requests have a 100 track limit

    items = sp.playlist_items(history_playlist_id, limit=100)['items']  # Max limit for playlists = 100

    # Iterate while getting items from the request
    while len(items) > 0:
        for item in items:
            history_playlist_track_isrcs.append(item['track']['external_ids']['isrc'])  # Append the ISRC of the track

        # Request next 100 items
        offset += 100
        items = sp.playlist_items(history_playlist_id, limit=100, offset=offset)['items']

    # Iterate over source playlists
    for playlist_id in source_playlist_ids:
        tracks = common.get_tracks_from_playlist(sp, playlist_id)

        for track in tracks:
            isrc = track['external_ids']['isrc']
            track_id = track['id']

            if isrc not in history_playlist_track_isrcs:
                target_playlist_track_ids.append(common.get_oldest_track_id(sp, track_id))
                history_playlist_track_isrcs.append(isrc)

    # Add tracks to the new playlist 100 by 100 due to the limit
    while len(target_playlist_track_ids) > 0:
        sp.playlist_add_items(target_playlist_id, target_playlist_track_ids[:100])
        sp.playlist_add_items(history_playlist_id, target_playlist_track_ids[:100])
        target_playlist_track_ids = target_playlist_track_ids[100:]


if __name__ == '__main__':
    main()
