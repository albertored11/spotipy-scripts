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

* **new_playlist_name (string):** name of the new playlist; set to null if update_playlist is set
* **date_in_name (bool):** if true, append ` — <today's date>` at the end of the name of the playlist, with
`<today's date>` the date of today in DD/MM/YY format.
* **update_playlist (string):** if null, a new playlist is created; else, use the playlist with this ID (all its tracks
  are removed first).
* **user (string):** user ID (username)
* **filler_playlist_id (string):** if null, playlist will be left as is after removing duplicates; else, complete it
  with tracks from the playlist with this ID.
* **playlists (list of object):** list of playlists
  * **playlist_id (string):** ID of the playlist ("saved" for saved tracks)
  * **count (number):** number of tracks to add from the playlist (if it is less than `0`, e.g. `-1`, add all tracks)

Example data file:

```json
{
    "new_playlist_name": "My cool mix",
    "date_in_name": false,
    "update_playlist": null,
    "filler_playlist_id": null,
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

Another example data file:

```json
{
    "new_playlist_name": null,
    "date_in_name": true,
    "update_playlist": "zzzzzzzzzzzzzzzzzzzzzz",
    "filler_playlist_id": "xxxxxxxxxxxxxxxxxxxxxx",
    "user": "myuser2227",
    "playlists": [
        {
            "playlist_id": "xxxxxxxxxxxxxxxxxxxxxx",
            "count": 40
        },
        {
            "playlist_id": "yyyyyyyyyyyyyyyyyyyyyy",
            "count": 60
        }
    ]
}
```

Running the script with that data file would replace all songs from the playlist with ID `zzzzzzzzzzzzzzzzzzzzzz` with
40 randomly chosen songs from the playlist with ID `xxxxxxxxxxxxxxxxxxxxxx` and 60 randomly chosen songs from the
playlist with ID `yyyyyyyyyyyyyyyyyyyyyy`, with the duplicates between playlists removed, and then add songs from the
playlist with ID `xxxxxxxxxxxxxxxxxxxxxx` until it reaches 100 (40 + 60) songs.

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

### [create_year_based_mix](https://github.com/albertored11/spotipy-scripts/blob/main/scripts/create_year_based_mix.py)

This script creates a Spotify playlist with random tracks from an existing playlist, choosing the number of tracks based
on their release date.

It provides an alternative approach to **create_playlist_mix** script. Instead of creating a shuffled playlist from
a certain number of songs from other playlists, it creates a new playlist from an existing one with certain number of
songs within defined ranges of age.

This way, you can easily generate a playlist, for example, from your liked songs, with a bunch of songs released in the
last year and just a few that are older.

The script takes one agrument: the path of a JSON file with the data of the playlists.

Format of the data file:

* **new_playlist_name (string):** name of the new playlist; set to null if update_playlist is set
* **date_in_name (bool):** if true, append ` — <today's date>` at the end of the name of the playlist, with
`<today's date>` the date of today in DD/MM/YY format.
* **update_playlist (string):** if null, a new playlist is created; else, use the playlist with this ID (all its tracks
  are removed first).
* **user (string):** user ID (username)
* **playlist_id (string):** ID of the playlist to take tracks from ("saved" for saved tracks)
* **selection (list of object):** track selection by age (**AGE MUST BE IN ASCENDING ORDER AND THE LAST ONE MUST BE
  NULL**)
  * **age (number):** maximum age of the track (whole years since it was released)
  * **count (number):** number of tracks to add

Example data file:

```json
{
    "new_playlist_name": null,
    "date_in_name": null,
    "update_playlist": "yyyyyyyyyyyyyyyyyyyyyy",
    "user": "myuser2227",
    "playlist_id": "xxxxxxxxxxxxxxxxxxxxxx",
    "selection": [
        {
            "age": 1,
            "count": 45
        },
        {
            "age": 2,
            "count": 25
        },
        {
            "age": 4,
            "count": 12
        },
        {
            "age": 7,
            "count": 8
        },
        {
            "age": 11,
            "count": 6
        },
        {
            "age": null,
            "count": 4
        }
    ]
}
```

Running the script with that data file would replace all songs from the playlist with ID `yyyyyyyyyyyyyyyyyyyyyy` with
45 randomly songs from the playlist with ID `xxxxxxxxxxxxxxxxxxxxxx` and less than 1 year old, 25 songs between 1 and 2
years old, 12 songs between 2 and 4 years old, 8 songs between 4 and 7 years old, 6 songs between 7 and 11 years old and
4 songs older than 11 years.

### [copy_to_playlist](https://github.com/albertored11/spotipy-scripts/blob/main/scripts/copy_to_playlist.py)

This script takes the tracks from a playlist and appends them to the end of a different, existing playlist, avoiding
duplicates.

The reason I wrote this script is to run it every friday to make it copy the tracks from my Release Radar to a playlist
where I keep a history of my Release Radars through the weeks. This way, even if one week I miss the Release Radar and
I don't listen to all the tracks, I can get to keep it in a playlist that doesn't change its contents every week and
listen to them later.

The playlist IDs (source and destination) are read from the first and the second program arguments, respectively:

```bash
python scripts/get_playlist_tracks.py <source_playlist_id> <dest_playlist_id>
```

Running the script would append the tracks from the playlist with ID `<source_playlist_id>` to the end of the playlist
with ID `<dest_playlist_id>`, excepting the ones that already existed in the latter.

#### Automating weekly run

In order to match my particular use case for this script, which I mentioned earlier, some automation is needed to run
the script once a week.

My choice is using a [systemd timer](https://wiki.archlinux.org/title/Systemd/Timers) to run the script every friday at
12:00, but a cron job should also do the work.
