import argparse
from pathlib import Path
import sqlite3
import typing

import dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

dotenv.load_dotenv()
sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())


class Playlist(typing.NamedTuple):
    uri: str
    name: str


class Track(typing.NamedTuple):
    uri: str
    name: str
    artist_uri: str
    artist_name: str
    album_uri: str
    album_name: str
    release_date: str


def get_db(db_path: Path) -> sqlite3.Connection:
    db_path.unlink(missing_ok=True)
    db = sqlite3.connect(db_path)
    db.execute("PRAGMA foreign_keys=ON")

    with open("schema.sql") as schema_file:
        db.executescript(schema_file.read())

    return db


def export(spotify_user_uri: str, db_path: Path):
    db = get_db(db_path)

    offset = 0
    while True:
        playlist_page = sp.user_playlists(spotify_user_uri, offset=offset)
        offset += len(playlist_page["items"])

        for raw_playlist in playlist_page["items"]:
            playlist = Playlist(uri=raw_playlist["uri"], name=raw_playlist["name"])
            db.execute("insert into Playlist values (?, ?)", playlist)

        if playlist_page["next"] is None:
            break

    db.commit()

    for playlist_row in db.execute("select * from Playlist"):
        playlist = Playlist(*playlist_row)
        print(f"Fetching tracks for {playlist.name}")

        offset = 0
        while True:
            track_page = sp.playlist_items(playlist_id=playlist.uri, offset=offset)

            for track_index, item in enumerate(track_page["items"]):
                t = item["track"]

                if t["is_local"]:
                    continue

                track = Track(
                    uri=t["uri"],
                    name=t["name"],
                    artist_uri=t["artists"][0]["uri"],
                    artist_name=t["artists"][0]["name"],
                    album_uri=t["album"]["uri"],
                    album_name=t["album"]["name"],
                    release_date=t["album"]["release_date"],
                )

                print(f"    {track.name}")

                question_marks = ", ".join(["?"] * len(track))
                # If a track is present in multiple playlists, it will create a conflict
                db.execute(
                    f"insert or replace into Track values ({question_marks}) on conflict do nothing",
                    track,
                )

                # If a track is in a playlist twice, that will also create a conflict
                db.execute(
                    "insert into TrackPlaylist values (?, ?, ?) on conflict do nothing",
                    (track.uri, playlist.uri, offset + track_index),
                )

            offset += len(track_page["items"])
            if track_page["next"] is None:
                break

        db.commit()

    db.close()


if __name__:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        "--user",
        required=True,
        help="The user for whom to export the playlist. This can be their username or their user id.",
    )
    arg_parser.add_argument(
        "--out",
        type=Path,
        default=Path("export.sqlite3"),
        help="The location to store the exported sqlite3 database. If there is a file at the specified location, it will be deleted. Defaults to 'export.sqlite3'.",
    )

    args = arg_parser.parse_args()
    export(args.user, args.out)
