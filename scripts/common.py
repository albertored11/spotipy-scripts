import random

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
