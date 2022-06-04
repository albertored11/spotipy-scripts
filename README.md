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

### Preparing the environment

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
