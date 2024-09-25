# Script that prints all tracks from a Spotify playlist
# Requires: spotipy
# Usage: python create_playlist_mix.py <playlist_id>
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables

import spotipy
import sys
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

if len(sys.argv) < 2:
    print("Usage: python create_playlist_mix.py <playlist_id>", file=sys.stderr)
    exit(1)

playlist_id = sys.argv[1]  # Read playlist ID from first program argument

# If playlist_id is "saved", request saved tracks; otherwise, request tracks from the corresponding playlist
if playlist_id == "saved":
    # Define needed scopes:
    # * user-library-read: to get tracks from library (liked songs)
    scope = "user-library-read"

    # Set up auth using Authorization Code Flow
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    liked_songs = sp.current_user_saved_tracks(limit=50)  # Request first 50 items
    items = liked_songs['items']  # Load items

    track_total = liked_songs['total']  # Number of saved tracks

    # Print "Liked Songs" and number of tracks
    print("Liked Songs — " + str(track_total) + " tracks\n")
else:
    # Set up auth using Client Credentials Flow
    auth_manager = SpotifyClientCredentials()
    sp = spotipy.Spotify(auth_manager=auth_manager)

    playlist = sp.playlist(playlist_id)  # Load playlist info
    items = sp.playlist_items(playlist_id, limit=100)['items']  # Request first 100 items

    track_total = playlist['tracks']['total']  # Number of tracks in the playlist

    # Print playlist name and number of tracks
    print(playlist['name'] + " — " + str(track_total) + " tracks\n")

offset = 0  # Keep an offset bc requests have a 100 track limit
count = 0
# Iterate while getting items from the request
while len(items) > 0:
    for item in items:
        track = item['track']
        artists = track['artists']
        count += 1
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

    # Request next 50/100 items
    if playlist_id == "saved":
        offset += 50
        items = liked_songs = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
    else:
        offset += 100
        items = sp.playlist_items(playlist_id, limit=100, offset=offset)['items']


print(count);
