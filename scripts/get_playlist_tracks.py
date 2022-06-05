# Script that prints all tracks from a Spotify playlist
# Requires: spotipy
# Usage: python create_playlist_mix.py <playlist_id>
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables

import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials

# Set up auth using Client Credentials Flow
auth_manager = SpotifyClientCredentials()
sp = spotipy.Spotify(auth_manager=auth_manager)

playlist_id = sys.argv[1]

playlist = sp.playlist(playlist_id)  # Load playlist info
items = sp.playlist_items(playlist_id, limit=100)['items']  # Request first 100 items

track_total = playlist['tracks']['total']  # Number of tracks in the playlist
offset = 0  # Keep an offset bc requests have a 100 track limit

# Print playlist name and number of tracks
print(playlist['name'] + " — " + str(track_total) + " tracks\n")

# Iterate while getting items from the request
while len(items) > 0:
    for item in items:
        track = item['track']
        artists = track['artists']

        # If just one artist, print its name
        if len(artists) == 1:
            print(artists[0]['name'] + " — ", end="")
        # If more than one artist, separate them with commas
        else:
            for artist in artists[:-1]:
                print(artist['name'], end=", ")

            print(artists[len(artists) - 1]['name'] + " — ", end="")

        # Print track name
        print(track['name'])

    # Increment offset in 100 (max limit)
    offset += 100

    # Request next 100 items
    items = sp.playlist_items(playlist_id, limit=100, offset=offset)['items']
