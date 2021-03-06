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
# * user (string): user ID (username)
# * playlists (list of object): list of playlists
#   * playlist_id (string): ID of the playlist ("saved" for saved tracks)
#   * count (number): number of tracks to add from the playlist
with open(sys.argv[1], 'r') as f:
    data = json.load(f)

new_playlist_name = data['new_playlist_name']

# If date_in_name is true, append date at the end of the name of the playlist
if data['date_in_name']:
    new_playlist_name += " — " + time.strftime("%d/%m/%y")

user = data['user']
playlists = data['playlists']

# Create the new playlist and store its ID in a variable
new_playlist_id = sp.user_playlist_create(user, new_playlist_name, public=False)['id']

new_playlist_song_ids = []  # List for the songs of the new playlist

# Iterate over the playlists
for playlist in playlists:
    playlist_id = playlist['playlist_id']
    count = playlist['count']

    # If count < 0, use all songs
    if count < 0:
        count = sp.playlist(playlist_id)['tracks']['total']  # Get number of songs

    offset = 0  # Keep an offset bc requests have a 50/100 track limit
    song_ids = []  # List for the songs from each playlist

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

    # Shuffle tracks, take count and add them to the list of songs of the new playlist
    random.shuffle(song_ids)
    new_playlist_song_ids.extend(song_ids[:count])

# Remove duplicates from the list of songs and shuffle
new_playlist_song_ids = list(dict.fromkeys(new_playlist_song_ids))
random.shuffle(new_playlist_song_ids)

# Add tracks to the new playlist 100 by 100 due to the limit
while len(new_playlist_song_ids) > 0:
    sp.playlist_add_items(new_playlist_id, new_playlist_song_ids[:100])
    new_playlist_song_ids = new_playlist_song_ids[100:]
