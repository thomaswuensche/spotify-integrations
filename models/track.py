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

    def __init__(self, result_item):
        self.id = result_item['track']['id']
        self.name = result_item['track']['name']
        self.artist = result_item['track']['artists'][0]['name']
        self.explicit = result_item['track']['explicit']
        self.release_date = result_item['track']['album']['release_date']
        self.release_date_precision = result_item['track']['album']['release_date_precision']
        self.duration_ms = result_item['track']['duration_ms']
        self.popularity = result_item['track']['popularity']
        self.link = result_item['track']['external_urls']['spotify']

    def set_audio_features(self, audio_features):
        self.danceability = audio_features['danceability']
        self.energy = audio_features['energy']
        self.valence = audio_features['valence']
        self.tempo = audio_features['tempo']
