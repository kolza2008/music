from flask import request, Response, send_from_directory, jsonify
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from youtube_import import *
from config import proxies
from librarium import *
from models import *
import requests
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
        fileId = import_track(song.author, song.name, filename=song.id)
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
                songs.append(handleTrack(i, s))
            elif i["wrapperType"] == "collection":
                #album = getAlbumByName(i["collectionName"], i["artistName"], s)
                albums.append(handleAlbum(i, s))
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

        print(song.thumbnail1000)
        if song.thumbnail1000 == "":
            if song.albumID != None:
                song.thumbnail1000 = song.album.thumbnail
        #req = requests.get("https://ya.ru", proxies=proxies) 
    
    res = {
        "id": song.id,
        "name": song.name,
        "author": song.author,
        "thumbnail": song.thumbnail1000
    }

    return jsonify(res)

def getAlbum():
    id_ = request.args.get('id')
    if id_ is None:
        return Response(status=400)
    
    with Session(engine) as s:
        album = s.scalar(select(Album).where(Album.id == id_))

    res = {
        "id": album.id,
        "name": album.name,
        "author": album.artist.name,
        "thumbnail": album.thumbnail,
        "date": album.released_at,
        "songs": [
            {"id": s.id, "name" : s.name} for s in album.songs
        ]
    }

    return jsonify(res)

def register_routes(app):
    app.add_url_rule('/api/trackFileByName', 'downloadTrackExpired', downloadTrack, methods=['GET'])
    app.add_url_rule('/api/trackFile', 'downloadTrack', downloadTrackV2, methods=['GET'])
    app.add_url_rule('/api/search', 'searchEntities', searchTracks, methods=['GET'])
    app.add_url_rule('/api/track', 'getTrack', getTrack, methods=['GET'])
    app.add_url_rule('/api/album', 'getAlbum', getAlbum, methods=['GET'])