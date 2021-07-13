from datetime import datetime
from .track import Track

class HSTrack(Track):

    @staticmethod
    def bulk_insert(db, tracks):
        super(__class__, __class__).bulk_insert(db, tracks)
        db.bulk_insert('tracks_hs', tracks)

    def __init__(self, result_item):
        super().__init__(result_item['track'])
        self.added_by = result_item['added_by']['id']
        self.added_at = datetime.strptime(result_item['added_at'], '%Y-%m-%dT%H:%M:%SZ')
