class ActiveTrack():

    name = ""
    artist = None
    champ = ""
    added_at = ""

    def __init__(self, name, artist, champ, added_at):
        self.name = name
        self.artist = artist
        self.champ = champ
        self.added_at = added_at

    def getGenres(self):
        return self.artist['genres']

    def getArtistName(self):
        return self.artist['name']

    def toString(self):
        return self.name + " : " + self.getArtistName() + " : " + self.champ + " : " + self.added_at
