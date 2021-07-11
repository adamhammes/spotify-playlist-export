create table Playlist (
    uri text not null primary key,
    name text not null
);

create table Track (
    uri text not null primary key,
    name text not null,
    artist_uri text not null,
    artist_name text not null,
    album_uri text not null,
    album_name text not null,
    release_date text not null
);

create table TrackPlaylist (
    track_uri text not null references Track(uri),
    playlist_uri text not null references Playlist(uri),
    track_index integer not null,

    primary key (track_uri, playlist_uri)
);
