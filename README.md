# Spotify Playlist Export

This Python tool allows you to save the metadata of all your Spotify playlists into a local sqlite3 database.

## Caveats

Some known limitations of this tool:

1. If a song is present twice in a playlist, it will only be saved once.
1. Songs that only exist locally (e.g., don't exist in Spotify) will be skipped over.

## Dependencies

* Python >= 3.9
* Spotify API app credentials - this should include a client id and client secret.

## Quickstart

After having cloned the repo and `cd`ed inside, run:

```
$ python3 -m venv venv
$ . venv/bin/activate
$ pip install -r requirements.txt
$ cp example.env .env
```

Then, open `.env` in a text editor and add your credentials.
Finally, you can export your playlists with:

```
$ python spotify_playlist_export.py --user $YOUR_USER_NAME_OR_ID
```

To get more information on the possible parameters, you can run:

```
$ python spotify_playlist_export.py --help
```