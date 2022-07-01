# spotipy-scripts

Collection of Python scripts that access the [Spotify API](https://developer.spotify.com/documentation/web-api/) using
[spotipy](https://github.com/plamere/spotipy).

## Usage

### Register a Spotify app

In order to use the Spotify API, a registered Spotify app is needed. If you don't have one or if you want to use a new
one, follow [these steps](https://developer.spotify.com/documentation/general/guides/authorization/app-settings/) to
create an app and get a client ID and a client secret.

Authorization Code Flow is used by some scripts. You will need to define a redirect URI in the app settings for this
authentication method to work. I suggest using `http://localhost:9090`.

### Prepare the environment

The scripts are written in Python and use the spotipy library, so first of all Python must be installed.

There are several options to install spotipy. My choice is creating a virtual environment using
[virtualenv](https://virtualenv.pypa.io/en/latest/) and installing it via pip.

First, clone the repository and cd into it:

```bash
git clone https://github.com/albertored11/spotipy-scripts.git
cd spotipy-scripts
```

Create a Python virtual environment and activate it (optional):

```bash
virtualenv venv
source venv/bin/activate # for bash/zsh
```

Then install spotipy:

```bash
pip install spotipy
```

Now, some environment variables need to be defined to access the API through spotipy:

```bash
export SPOTIPY_CLIENT_ID="<app_client_id>"
export SPOTIPY_CLIENT_SECRET="<app_client_id>"
export SPOTIPY_REDIRECT_URI="http://localhost:9090" # replace with the redirect URI you chose
```

### Run a script

To run the script:

```bash
python scripts/<script_name>.py
```

## Scripts

### [get_playlist_tracks](https://github.com/albertored11/spotipy-scripts/blob/main/scripts/get_playlist_tracks.py)

This script prints all tracks from a Spotify playlist. It supports playlists with a number of songs that exceeds the API
limit (100 songs), making multiple requests.

In the first line, it shows the name of the playlist and the number of songs. Then, after a blank line, it shows one
song per line, with the list of artists sepparated with commas and the name of the song.

This is the first script I wrote as I started tinkering with spotipy, and it probably doesn't have much practical use.

The playlist ID is read from the first program argument:

```bash
python scripts/get_playlist_tracks.py <playlist_id>
```

Example output:

```
EDM — 1740 tracks

Edward Maya, Vika Jigulina — Stereo Love - Radio Edit
David Guetta — When Love Takes Over (feat. Kelly Rowland)
Flo Rida — Club Can't Handle Me (feat. David Guetta) - From the Step Up 3D Soundtrack
Guru Josh Project — Infinity 2008 - Klaas Vocal Edit
Stromae — Alors On Danse - Radio Edit
...
<output omitted>
...
Tchami, Marten Hørger — The Calling
Alok, Bastille — Run Into Trouble
Jax Jones, Martin Solveig, GRACEY, Europa — Lonely Heart
```

### [create_playlist_mix](https://github.com/albertored11/spotipy-scripts/blob/main/scripts/create_playlist_mix.py)

This script creates a Spotify playlist with random tracks from other playlists.

This is the main reason I stared tinkering with the Spotify API. In my Spotify account, I have playlists with recently
released music, and sometimes I like to shuffle those playlists when I don't want to think about what exact songs I want
to listen to. Other times, I prefer to shuffle all my liked songs, which not only include recent music, but also songs
from several years ago. And sometimes I want a mix of these two: a bunch of recent songs, and some good oldies.

Before writing this script, I used to manually create playlists which I called "Shuffle mixes". I would shuffle a couple
of playlists with recent music, I would take a number of songs from them, and then I would do the same with my liked
songs. That used to take me some time, so I decided to automate the process, and the result is this script!

The script takes one agrument: the path of a JSON file with the data of the playlists.

Format of the data file:

* **new_playlist_name (string):** name of the new playlist (leave blank for default: "Shuffle mix — <today's date>")
* **user (string):** user ID (username)
* **playlists (list of object):** list of playlists
  * **playlist_id (string):** ID of the playlist ("saved" for saved tracks)
  * **count (number):** number of tracks to add from the playlist (if it is less than `0`, e.g. `-1`, add all tracks)

Example data file:

```json
{
    "new_playlist_name": "My cool mix",
    "user": "myuser2227",
    "playlists": [
        {
            "playlist_id": "saved",
            "count": 40
        },
        {
            "playlist_id": "xxxxxxxxxxxxxxxxxxxxxx",
            "count": 25
        },
        {
            "playlist_id": "yyyyyyyyyyyyyyyyyyyyyy",
            "count": 35
        }
    ]
}
```

Running the script with that data file would create a playlist named "My cool mix", which would contain 40 randomly
chosen songs from myuser2227's liked songs, 25 randomly chosen songs from the playlist with ID `xxxxxxxxxxxxxxxxxxxxxx`
and 35 randomly chosen songs from the playlist with ID `yyyyyyyyyyyyyyyyyyyyyy`, with the duplicates between playlists
removed.

#### More use cases

Another possible and simpler use case for this script could be shuffling a single playlist. This could be useful if you
want to shuffle the songs of a playlist and save that new order in a different playlist.

The advantage compared to using the shuffle mode is that this way the order is kept, so even if you leave the playlist
unfinished listening, you can come back whenever you want and make sure you listen to every song in the playlist, but in
a random order.

Example data file for this use case:

```json
{
    "new_playlist_name": "My shuffled playlist",
    "user": "myuser2227",
    "playlists": [
        {
            "playlist_id": "yyyyyyyyyyyyyyyyyyyyyy",
            "count": -1
        }
    ]
}
```

Running the script with that data file would create a playlist named "My shuffled playlist", which would contain every
song from the playlist with ID `xxxxxxxxxxxxxxxxxxxxxx`, but in a random order.
