from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

tracks_bp = Blueprint('tracks', __name__, url_prefix="/artists/<artist_id>/albums/<album_id>")
db = db()

def id_error():
    return jsonify(
        {
            "error": "The IDs of track, "
        }
    ), BAD_REQUEST

def internal_error():
    return jsonify(
        {
            "error": "An internal error occurred."
        }
    ), INTERNAL_SERVER_ERROR

def no_artist():
    return jsonify(
        {
            "error": "There is no artist associated with given ID."
        }
    ), NOT_FOUND

def no_album():
    return jsonify(
        {
            "error": "There is no album associated with given artist."
        }
    ), NOT_FOUND

def no_track():
    return jsonify(
        {
            "error": "There is no track associated with given album"
        }
    ), NOT_FOUND

def no_data():
    return jsonify(
        {
            "error": "Unsopported format of request"
        }
    ), BAD_REQUEST

@tracks_bp.route('/tracks', methods=['GET'])
def get_tracks(artist_id, album_id):
    try:
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'''
                       SELECT * FROM ARTIST
                       WHERE id = {artist_id};
                       ''')
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute(f'''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id} AND artist.id = {artist_id};
                       ''')
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()

        cursor.execute(f'''
                       SELECT track.id, track.name FROM TRACK AS track
                       JOIN ALBUM as album
                       ON track.album_id = album.id
                       JOIN ARTIST as artist
                       ON album.artist_id = artist.id
                       WHERE artist.id = {artist_id} AND album.id = {album_id};
                       ''')
        results = cursor.fetchall()

        if not results:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "message": "There is no track in the given album."
                }
            ), OK

        cursor.close()
        connection.close()
        return jsonify(results), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()
