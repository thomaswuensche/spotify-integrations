class Track():

    @classmethod
    def bulk_insert(cls, db, tracks):
        tracks_deduped = cls.dedupe_tracks(tracks)
        db.bulk_insert('tracks', tracks_deduped)

    @classmethod
    def dedupe_tracks(cls, tracks):
        tracks_deduped = []
        for track in tracks:
            if not track.id in [track.id for track in tracks_deduped]:
                tracks_deduped.append(track)

        return tracks_deduped

    def __init__(self, track):
        self.id = track['id']
        self.name = track['name']
        self.artist = track['artists'][0]['name']
        self.explicit = track['explicit']
        self.release_date = track['album']['release_date']
        self.release_date_precision = track['album']['release_date_precision']
        self.duration_ms = track['duration_ms']
        self.popularity = track['popularity']
        self.link = track['external_urls']['spotify']

    def set_audio_features(self, audio_features):
        self.danceability = audio_features['danceability']
        self.energy = audio_features['energy']
        self.valence = audio_features['valence']
        self.tempo = audio_features['tempo']
