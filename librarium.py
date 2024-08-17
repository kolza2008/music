from sqlalchemy.orm import Session
from sqlalchemy import select
from config import proxies
from lxml import etree
from models import *
import requests
import hashlib
import uuid


def getThumbnailByMBID(mbid):
    req = requests.get(f"https://coverartarchive.org/release-group/{mbid}/front", allow_redirects=False)
    print(req.__dict__)
    req = requests.get(req.headers["Location"], allow_redirects=False)
    return req.headers["Location"]

def getArtist(name):
    with Session(engine) as s:
        req = select(Artist).where(Artist.name == name)
        
        res = s.scalar(req)
        if res is not None:
            return res
        
def getArtistByMBID(mbid, s):
    req = select(Artist).where(Artist.mbid == mbid)
        
    res = s.scalar(req)
    if res is not None:
        return res
        
    response = requests.get(f"https://musicbrainz.org/ws/2/artist/{mbid}", params={"inc": "release-groups"}, proxies=proxies)
    et = etree.fromstring(response.text.encode())

    artist = Artist(
        id = uuid.uuid4().hex,
        mbid = mbid,
        name = et[0][0].text
    )
    s.add(artist)
    s.commit()

    return artist

def getAlbumByName(name, artist, s):
    req = select(Album).where(Album.name == name and Album.artist.name == artist)
        
    res = s.scalar(req)
    if res is not None:
        return res
    
    album = Album(
        id = uuid.uuid4().hex,
        name = name
    )

def importAlbumByName(name, artist, s):
    req = select(Album).where(Album.name == name and Album.artist.name == artist)
        
    res = s.scalar(req)
    if res is not None:
        return res
        
    response = requests.get("https://musicbrainz.org/ws/2/release-group", params={"query": name}, proxies=proxies)
    etgroup = etree.fromstring(response.text.encode())

    releaseID = etgroup[0][0][4][0].get("id")

    req = requests.get(f"https://musicbrainz.org/ws/2/release/{releaseID}", params={"inc": "recordings"}, proxies=proxies)
    et = etree.fromstring(req.text.encode())

    album = Album(
        id = uuid.uuid4().hex,
        mbid = releaseID,
        name = name,
        released_at = etgroup[0][0][1].text,
        thumbnail = getThumbnailByMBID(etgroup[0][0].get("id")),
        artistID = getArtistByMBID(etgroup[0][0][3][0][1].get("id"), s).id
    )
        
    s.add(album)
    s.commit()

    print(et[0][5])

    for i in et[0][5][0][1]:
        for j in iter(i):
            if j.tag == "{http://musicbrainz.org/ns/mmd-2.0#}recording":
                song = Song(
                    id = uuid.uuid4().hex,
                    md5hash = hashlib.md5(f'{j[0].text}+{artist}+{name}'.encode()).hexdigest(),
                    name = j[0].text,
                    author = artist,
                    thumbnail = album.thumbnail,
                    thumbnail1000 = album.thumbnail,
                    albumID = album.id
                )
                s.add(song)
                break
    s.commit()  
    return album
    
def handleTrack(i, s):
    try:
        song = Song(
            id = uuid.uuid4().hex,
            md5hash = hashlib.md5(f'{i["trackCensoredName"]}+{i["artistName"]}+{i["collectionName"]}'.encode()).hexdigest(),
            name = i["trackCensoredName"],
            author = i["artistName"],
            thumbnail = i["artworkUrl100"],
            thumbnail1000 = "",
            albumID = "NULL"
        )
        s.add(song)
        s.commit()
    except Exception as e:
        s.rollback()
        req = select(Song).where(Song.md5hash == hashlib.md5(f'{i["trackCensoredName"]}+{i["artistName"]}+{i["collectionName"]}'.encode()).hexdigest())
        song = s.scalar(req)

    entity = {
        "id": song.id,
        "type": "track",
        "artistID": None,
        "artistName": i["artistName"],
        "albumID": None,
        "albumName": i["collectionName"],
        "trackName": i["trackCensoredName"],
        "thumbnail": i["artworkUrl100"],
        "duration": i["trackTimeMillis"]
    }
    return entity