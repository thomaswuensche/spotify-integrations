CREATE TABLE spotify_hs_tracks (
    id SERIAL PRIMARY KEY,
    name text,
    artist text,
    added_by_id text,
    added_at timestamp without time zone,
    explicit boolean,
    release_date text,
    release_date_precision text,
    duration_ms integer,
    popularity integer,
    danceability numeric,
    energy numeric,
    valence numeric,
    tempo numeric,
    link text
);

CREATE TABLE spotify_users (
    id text PRIMARY KEY,
    name text NOT NULL
);
