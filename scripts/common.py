import random
import csv

def get_tracks_from_playlist(sp, playlist_id):
    """
    Given a spotipy Spotify instance and a playlist ID, returns a list containing every track in that playlist.
    """

    offset = 0  # Keep an offset bc requests have a 50/100 track limit
    songs = []  # List for the songs from the playlist

    # If playlist_id is "saved", request saved tracks; otherwise, request tracks from the corresponding playlist
    if playlist_id == "saved":
        items = sp.current_user_saved_tracks(limit=50)['items']  # Max limit for saved tracks = 50
    else:
        items = sp.playlist_items(playlist_id, limit=100)['items']  # Max limit for playlists = 100

    # Iterate while getting items from the request
    while len(items) > 0:
        for item in items:
            songs.append(item['track'])  # Append track

        # Request next 50/100 items
        if playlist_id == "saved":
            offset += 50
            items = sp.current_user_saved_tracks(limit=50, offset=offset)['items']
        else:
            offset += 100
            items = sp.playlist_items(playlist_id, limit=100, offset=offset)['items']

    # Return list with all songs
    return songs

def get_random_tracks_from_playlist(sp, playlist_id, count):
    """
    Given a spotipy Spotify instance, a playlist ID and a number, returns a list containing that number of IDs of
    randomly selected tracks from that playlist.
    """

    song_ids = []

    for song in get_tracks_from_playlist(sp, playlist_id):
        song_ids.append(song['id'])

    # TODO: this does not work with saved songs
    # If count < 0, use all songs
    if count < 0:
        count = sp.playlist(playlist_id)['tracks']['total']  # Get number of songs

    # Shuffle tracks, take count and return them
    random.shuffle(song_ids)
    return song_ids[:count]

def actual_track_release_date(sp, track, rd_cache_file):
    """
    Given a spotipy Spotify instance, a track object and the path to a cache file, returns the actual release date of
    the track; this is, the release date of the album, single... where it first appeared
    """
    # Open cache file for reading
    with open(rd_cache_file, "r") as f:
        reader = csv.reader(f)  # Create CSV reader

        isrc = track['external_ids']['isrc']  # Get track ISRC

        # Find ISRC in the cache file and return release date if found
        for row in reader:
            if row[0] == isrc:
                return row[1]

    # If ISRC wasn't found, open cache file for appending to add it
    with open(rd_cache_file, "a") as f:
        writer = csv.writer(f)  # Create CSV writer

        track_rd = track['album']['release_date']  # Release date of the album associated to the track
        releases = sp.search("isrc:" + isrc)['tracks']['items']  # Find all releases of the track using its ISRC
        release_dates = [release['album']['release_date'] for release in releases]  # List of all release dates

        # If the list release dates is not empty, take the older one; else, use track_rd
        if release_dates:
            rd = min(release_dates)
        else:
            rd = track_rd

        # Save ISRC and release date to the cache file
        writer.writerow([isrc, rd])

        return rd
