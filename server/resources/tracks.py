from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

tracks_bp = Blueprint('tracks', __name__, url_prefix="/artists/<artist_id>/albums/<album_id>")
db = db()

def is_valid_length(length_sec):
    try:
        float(length_sec)
        return True
    except ValueError:
        return False

def id_error():
    return jsonify(
        {
            "error": "Artist ID, album ID and track ID must be an integer."
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
            "error": "There is no track associated with given album."
        }
    ), NOT_FOUND

def no_data():
    return jsonify(
        {
            "error": "Unsopported format of request."
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
                       SELECT track.id, track.album_id, track.name, track.length_sec FROM TRACK AS track
                       JOIN ALBUM as album
                       ON track.album_id = album.id
                       JOIN ARTIST as artist
                       ON album.artist_id = artist.id
                       WHERE artist.id = {artist_id} AND album.id = {album_id};
                       ''')
        tracks = cursor.fetchall()

        if not tracks:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "message": "There is no track in the given album."
                }
            ), OK

        cursor.close()
        connection.close()
        return jsonify(tracks), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>', methods=['GET'])
def get_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

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
                       SELECT track.id, track.album_id, track.name, track.length_sec FROM TRACK AS track
                       JOIN ALBUM as album
                       ON track.album_id = album.id
                       JOIN ARTIST as artist
                       ON album.artist_id = artist.id
                       WHERE artist.id = {artist_id} AND album.id = {album_id} AND track.id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()

        cursor.close()
        connection.close()

        return jsonify(track), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks', methods=['POST'])
def add_track(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        name = data.get('name')
        length_sec = data.get('length_sec')

        if not name:
            return jsonify(
                {
                    "error": "\"name\" field of the track must be provided."
                }
            ), BAD_REQUEST
        if not length_sec:
            return jsonify(
                {
                    "error": "\"length_sec\" field of the track must be provided."
                }
            ), BAD_REQUEST
        
        if not is_valid_length(length_sec):
            return jsonify(
                {
                    "error": "\"length_sec\" field must be float."
                }
            ), BAD_REQUEST
        
        # The database stores 3 digits after comma
        length_sec = round(length_sec, 3)

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
        
        cursor.execute('''
                       INSERT INTO TRACK (album_id, name, length_sec) 
                       VALUES (%s, %s, %s);
                       ''', (album_id, name, length_sec))
        cursor.commit()

        cursor.close()
        connection.close()

        track_id = cursor.lastrowid

        return jsonify(
            {
                "message": "Track added successfully.",
                "track": {
                    "album_id": album_id,
                    "id": track_id,
                    "name": name,
                    "length_sec": length_sec
                }
            }
        ), CREATED
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>', methods=['PUT'])
def update_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        name = data.get('name')
        length_sec = data.get('length_sec')

        if not name:
            return jsonify(
                {
                    "error": "\"name\" field of the track must be provided."
                }
            ), BAD_REQUEST
        if not length_sec:
            return jsonify(
                {
                    "error": "\"length_sec\" field of the track must be provided."
                }
            ), BAD_REQUEST
        
        if not is_valid_length(length_sec):
            return jsonify(
                {
                    "error": "\"length_sec\" field must be float."
                }
            ), BAD_REQUEST
        
        # The database stores 3 digits after comma
        length_sec = round(length_sec, 3)

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
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id} AND artist.id = {artist_id} AND track.id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute(f'''
                       UPDATE TRACK 
                       SET name = "{name}", length_sec = "{length_sec}"
                       WHERE id = {track_id};
                       ''')
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track updated successfully.",
                "track": {
                    "album_id": album_id,
                    "id": track_id,
                    "name": name,
                    "length_sec": length_sec
                }
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()


@tracks_bp.route('/tracks/<track_id>', methods=['PATCH'])
def modify_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        name = data.get('name')
        length_sec = data.get('length_sec')
        
        if not name and not length_sec:
            return jsonify(
                {
                    "error": "No modifiable field has been specified. Modifiable fields are: \"name\", \"length_sec\"."
                }
            ), BAD_REQUEST

        if length_sec:
            if not is_valid_length(length_sec):
                return jsonify(
                    {
                        "error": "\"length_sec\" field must be float."
                    }
                ), BAD_REQUEST
            # The database stores 3 digits after comma
            length_sec = round(length_sec, 3)

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
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id} AND artist.id = {artist_id} AND track.id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute(f'''
                       UPDATE TRACK 
                       SET {f"name = \"{name}\"," if name else ""} 
                           {f"length_sec = \"{length_sec}\"" if length_sec else ""}
                       WHERE id = {track_id};
                       ''')
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track updated successfully.",
                "track": {
                    "album_id": album_id,
                    "id": track_id,
                    "name": name,
                    "length_sec": length_sec
                }
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>', methods=['DELETE'])
def delete_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)
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
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id} AND artist.id = {artist_id} AND track.id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute(f'''
                       DELETE FROM TRACK
                       WHERE id = {track_id};
                       ''')
        connection.commit()
        
        return jsonify(
            {
                "message": "Track deleted successfully."
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()
