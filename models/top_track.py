from .track import Track

class TopTrack(Track):

    @staticmethod
    def bulk_insert(db, tracks):
        super(__class__, __class__).bulk_insert(db, tracks)
        db.bulk_insert('tracks_top', tracks)

    def __init__(self, track, date, rank, time_range):
        super().__init__(track)
        self.date = date
        self.rank = rank
        self.time_range = time_range
