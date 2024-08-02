from flask import request, Response, send_from_directory, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from youtube_import import *
from models import *
import requests
import hashlib
import pprint
import uuid


def downloadTrack():
    try:
        author = request.args.get('author')
        track = request.args.get('name')
    
        fileId = import_track(author, track)

        return send_from_directory(config.PATH + "/download", fileId+".mp3")
    except Exception as ex:
        return Response(status=500, response=f"youtube raised error: {str(ex)}")
    
def downloadTrackV2():
    try:
        id_ = request.args.get('id')
    except:
        return Response(status=400)

    with Session(engine) as s:
        song = s.scalar(select(Song).where(Song.id == id_))
    
    try:
        fileId = import_track(song.author, song.name)
        return send_from_directory(config.PATH + "/download", fileId+".mp3")
    except Exception as ex:
        return Response(status=500, response=f"youtube raised error: {str(ex)}")
    
def searchTracks():
    try:
        data = request.args['d']
    except KeyError:
        return Response(status=400)
    
    r = requests.get("https://itunes.apple.com/search", params={'term': data, 'country': 'RU', 'entity': 'musicArtist,musicTrack,album'})
    res = r.json()

    artists = []
    albums = []
    songs = []

    with Session(engine) as s:
        for i in res["results"]:
            if i["wrapperType"] == "track":
                try:
                    song = Song(
                        id = uuid.uuid4().hex,
                        md5hash = hashlib.md5(f'{i["trackCensoredName"]}+{i["artistName"]}+{i["collectionName"]}'.encode()).hexdigest(),
                        name = i["trackCensoredName"],
                        author = i["artistName"],
                        thumbnail = i["artworkUrl100"]
                    )
                    s.add(song)
                    s.commit()
                except:
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
                songs.append(entity)
            elif i["wrapperType"] == "collection":
                entity = {
                    "id": None,
                    "type": "album",
                    "artistID": None,
                    "artistName": i["artistName"],
                    "name": i["collectionName"],
                    "thumbnail": i["artworkUrl100"]
                }
                albums.append(entity)
            elif i["wrapperType"] == "artist":
                entity = {
                    "id": None,
                    "type": "artist",
                    "name": i["artistName"],
                }
                artists.append(entity)
            else:
                print(i["wrapperType"])
        
    return jsonify([*artists, *albums, *songs])

def getTrack():
    id_ = request.args.get('id')
    if id_ is None:
        return Response(status=400)
    
    with Session(engine) as s:
        song = s.scalar(select(Song).where(Song.id == id_))
    
    res = {
        "id": song.id,
        "name": song.name,
        "author": song.author
    }

    return jsonify(res)

def register_routes(app):
    app.add_url_rule('/api/trackFileByName', 'downloadTrackExpired', downloadTrack, methods=['GET'])
    app.add_url_rule('/api/trackFile', 'downloadTrack', downloadTrackV2, methods=['GET'])
    app.add_url_rule('/api/search', 'searchEntities', searchTracks, methods=['GET'])
    app.add_url_rule('/api/track', 'getTrack', getTrack, methods=['GET'])