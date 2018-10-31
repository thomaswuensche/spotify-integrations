import activeRecords

def whodunit(id):
    if id == "1163268620" :
        return "markus"
    else :
        return "thomas"

def get_and_push_data(item, mysqlcnx, spotify):
    track = item['track']

    name = track['name']
    champ = whodunit(item['added_by']['id'])
    added_at = item['added_at']
    artist_result = spotify.artist(track['artists'][0]['uri'])

    #print(json.dumps(artist_result, indent=4))

    activeTrack = activeRecords.ActiveTrack(name, artist_result, champ, added_at)
    activeTrack.setConnection(mysqlcnx)

    print(activeTrack.toString())
    activeTrack.insert()

    print("***")
