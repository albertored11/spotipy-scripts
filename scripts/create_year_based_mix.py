# Script that creates a Spotify playlist with random tracks from an existing playlist, choosing the number of tracks
# based on their release date
# Requires: spotipy
# Usage: python create_year_based_mix.py data.json rd_cache.csv
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
# Set SPOTIPY_REDIRECT_URI environment variable (e. g. to http://localhost:9090)

import spotipy
import random
import time
import json
import sys
import os
import common
from datetime import date
from dateutil.relativedelta import relativedelta
from spotipy.oauth2 import SpotifyOAuth

def main():
    if len(sys.argv) < 3:
        print("Usage: python create_year_based_mix.py data.json rd_cache.csv", file=sys.stderr)
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
    # * new_playlist_name (string): name of the new playlist; set to null if update_playlist is set
    # * date_in_name (bool): if true, append — <today's date> at the end of the name of the playlist, with
    #   <today's date> the date of today in DD/MM/YY format.
    # * update_playlist (string): if null, a new playlist is created; else, use the playlist with this ID (all its
    #   tracks are removed first).
    # * user (string): user ID (username)
    # * playlist_id (string): ID of the playlist to take tracks from ("saved" for saved tracks)
    # * selection (list of object): track selection by age (AGE MUST BE IN ASCENDING ORDER AND THE LAST ONE MUST BE
    #   NULL)
    #   * age (number): maximum age of the track (whole years since it was released)
    #   * count (number): number of tracks to add
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    new_playlist_name = data['new_playlist_name']
    update_playlist = data['update_playlist']
    user = data['user']
    playlist_id = data['playlist_id']
    selection = data['selection']

    rd_cache_file = sys.argv[2]

    # Create cache file if it does not exist
    if not os.path.exists(rd_cache_file):
        os.mknod(rd_cache_file)

    existing_playlist_song_ids = []  # List for the songs of the existing playlist

    # If update_playlist is null, create the new playlist and store its ID in a variable, else store the existing
    # playlist ID and get all its tracks
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
            for collection in items:
                existing_playlist_song_ids.append(collection['track']['id'])  # Append the ID of the track

            # Request next 100 items
            offset += 100
            items = sp.playlist_items(new_playlist_id, limit=100, offset=offset)['items']

    new_playlist_song_ids = []  # List for the songs of the new playlist
    year_collections = dict()  # Dictionary to organize songs by age

    # Populate year_collections (key: maximum age; value: dict with count and a list of song IDs)
    for collection in selection:
        year_collections[str(collection['age'])] = dict(count = collection['count'], song_ids = [])

    # Get list of tracks from playlist
    tracks = common.get_tracks_from_playlist(sp, playlist_id)

    # Iterate over tracks
    for track in tracks:
        release_date = common.actual_track_release_date(sp, track, rd_cache_file)  # Release date

        # If no hyphens in release date, it is just the year, so add July 1st (mid-year)
        if '-' not in release_date:
            release_date += "-07-01"

        # Get age of the track in whole years
        age = relativedelta(date.today(), date.fromisoformat(release_date)).years

        # Put track in its corresponding collection
        for collection in selection:
            threshold = collection['age']  # Maximum age for the tracks in the collection

            if threshold is None or age < threshold:
                year_collections[str(threshold)]['song_ids'].append(str(track['id']))
                break

    # Shuffle tracks and add count to list of songs
    for collection in year_collections:
        song_ids = year_collections[collection]['song_ids']
        count = year_collections[collection]['count']

        random.shuffle(song_ids)
        new_playlist_song_ids.extend(song_ids[:count])

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
