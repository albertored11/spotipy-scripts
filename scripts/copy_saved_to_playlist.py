# Script that takes the tracks from your Liked Songs and appends them to the end of a different, existing playlist
# Requires: spotipy
# Usage: python copy_to_playlist.py <dest_playlist_id>
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
# Set SPOTIPY_REDIRECT_URI environment variable (e. g. to http://localhost:9090)

import spotipy
import sys
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) < 2:
    print("Usage: python copy_to_playlist.py <source_playlist_id> <dest_playlist_id>", file=sys.stderr)
    exit(1)

# Define needed scopes:
# * playlist-read-collaborative: to get tracks from collab playlists
# * playlist-read-private: to get tracks from private playlists
# * playlist-modify-private: to create the playlist and add tracks to it
# * user-library-read: to read the Liked playlist and get tracks from it
scope = "playlist-read-collaborative playlist-read-private playlist-modify-private user-library-read"

# Set up auth using Authorization Code Flow
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

dest_playlist_id = sys.argv[1]

offset = 0  # Keep an offset bc requests have a 100 track limit
source_playlist_song_ids = []  # List for the songs from source playlist
dest_playlist_song_ids = []  # List for the songs from destination playlist

# Request tracks from destination playlist
items = sp.playlist_items(dest_playlist_id, limit=100)['items']

# Iterate while getting items from the request
while len(items) > 0:
    for item in items:
        dest_playlist_song_ids.append(item['track']['id'])  # Append the ID of the track

    # Request next 100 items
    offset += 100
    items = sp.playlist_items(dest_playlist_id, limit=100, offset=offset)['items']

offset = 0  # Reset offset

# Request tracks from source Liked playlist
# Note: Liked Playlist has a limit of 50 tracks per request 
items = sp.current_user_saved_tracks(limit=50, offset=0, market="US")['items']

# Iterate while getting items from the request
while len(items) > 0:
    for item in items:
        source_playlist_song_ids.append(item['track']['id'])  # Append the ID of the track

    # Request next 50 items
    offset += 50
    items = sp.current_user_saved_tracks(limit=50, offset=offset, market="US")['items']

# Remove tracks that already are in destination playlist to avoid duplicates
source_playlist_song_ids = [x for x in source_playlist_song_ids if x not in dest_playlist_song_ids]

# Add tracks to the destination playlist 100 by 100 due to the limit
while len(source_playlist_song_ids) > 0:
    sp.playlist_add_items(dest_playlist_id, source_playlist_song_ids[:100])
    source_playlist_song_ids = source_playlist_song_ids[100:]
