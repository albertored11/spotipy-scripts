# Script that keeps songs from a playlist that doesn't exceed a maximum age in another playlist
# Requires: spotipy
# Usage: python latest_music.py data.json
# Set SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET environment variables
# Set SPOTIPY_REDIRECT_URI environment variable (e. g. to http://localhost:9090)

import spotipy
import json
import sys
import common
from datetime import date
from dateutil.relativedelta import relativedelta
from spotipy.oauth2 import SpotifyOAuth

# Get age in months from a date
def age_in_months(release_date):
    # If no hyphens in release date, it is just the year, so add July 1st (mid-year)
    if '-' not in release_date:
        release_date += "-07-01"

    # Get age of the track in whole months
    age = relativedelta(date.today(), date.fromisoformat(release_date))
    return age.months + 12 * age.years

def main():
    if len(sys.argv) < 2:
        print("Usage: python latest_music.py data.json", file=sys.stderr)
        exit(1)

    # Define needed scopes:
    # * playlist-read-collaborative: to get tracks from collab playlists
    # * playlist-read-private: to get tracks from private playlists
    # * playlist-modify-private: to add tracks to the playlist
    # * user-library-read: to get tracks from library (liked songs)
    scope = "playlist-read-collaborative playlist-read-private playlist-modify-private user-library-read"

    # Set up auth using Authorization Code Flow
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, open_browser=False))

    # Load data from JSON file. Format:
    # * update_playlist (string): save tracks in the playlist with this ID
    # * user (string): user ID (username)
    # * playlist_id (string): ID of the playlist to take tracks from ("saved" for saved tracks)
    # * max_months (number): maximum age (in months) of the track (whole months since it was released)
    with open(sys.argv[1], 'r') as f:
        data = json.load(f)

    playlist_id = data['playlist_id']
    update_playlist = data['update_playlist']
    max_months = data['max_months']

    # Tracks in the source and the target playlists
    source_playlist_tracks = common.get_tracks_from_playlist(sp, playlist_id)
    target_playlist_tracks = common.get_tracks_from_playlist(sp, update_playlist)

    # Track IDs in the target playlist
    target_playlist_track_ids = [t['id'] for t in target_playlist_tracks]

    # For every track in the source playlist, check if it already is in the target playlist
    for track in source_playlist_tracks:
        if track['id'] not in target_playlist_track_ids:
            release_date = track['album']['release_date']
            months = age_in_months(release_date)

            # Add track if it doesn't exceed maximum age
            if months < max_months:
                target_playlist_tracks_aux = common.get_tracks_from_playlist(sp, update_playlist)
                pos = None

                # Calculate position in list to keep a descending order (most recent first)
                for i in range(len(target_playlist_tracks_aux)):
                    track0 = target_playlist_tracks_aux[i]
                    track0_release_date = track0['album']['release_date']

                    if release_date > track0_release_date:
                        pos = i
                        break

                sp.playlist_add_items(update_playlist, [track['id']], position=pos)

    # For every track in the target playlist
    for track in target_playlist_tracks:
        release_date = track['album']['release_date']
        months = age_in_months(release_date)

        # Remove track if it exceeds maximum age now
        if months >= max_months:
            sp.playlist_remove_all_occurrences_of_items(update_playlist, [track['id']])

if __name__ == '__main__':
    main()
