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

Some scripts have hardcoded variables that must be set. Review the code of the script you want to run and set them
accordingly.

Then run the script:

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

There is a `playlist_id` hardcoded variable that has to be set to the ID of the playlist.

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

(TODO)
