from flask import Blueprint, jsonify, request, app
from database import db
from datetime import datetime

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

albums_bp = Blueprint('albums', __name__, url_prefix="/artists/<artist_id>")
db = db()

def is_valid_date(date):
    try:
        datetime.strptime(date, '%Y-%m-%d')
        return True
    except ValueError:
        return False

def no_artist():
    return jsonify(
            {
                "error": "There is no artist with given artist ID."
            }
        ), NOT_FOUND
    
def no_album():
    return jsonify(
                    {
                        "error": "There is no such album associated with given artist ID."
                    }
                ), NOT_FOUND

def id_error():
    return jsonify(
                {
                    "error": "Artist ID and album ID must be an integer."
                }
            ), BAD_REQUEST

def internal_error():
    return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR

def no_data():
    return jsonify(
                    {
                        "error": "Unsupported format of request."
                    }
                ), BAD_REQUEST


@albums_bp.route('/albums', methods=['GET'])
def get_albums(artist_id):
    try:
        artist_id = int(artist_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT album.id as album_id, album.artist_id, album.name, album.type, album.release_date 
                       FROM ALBUM AS album 
                       JOIN ARTIST AS artist 
                       ON album.artist_id = artist.id 
                       WHERE artist_id = %s;
                       ''', (artist_id))
        albums = cursor.fetchall()

        if not albums:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "message": "There is no album of given artist."
                }
            ), OK

        cursor.close()
        connection.close()
        return jsonify(albums), OK
    except ValueError:
        return jsonify(
                {
                    "error": "Artist ID must be an integer."
                }
            ), BAD_REQUEST
    except:
        return internal_error()



@albums_bp.route('/albums/<album_id>', methods=['GET'])
def get_album(artist_id, album_id): 
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST 
                       WHERE id = %s;
                       ''', (artist_id))
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT album.id as album_id, album.artist_id, album.name, album.type, album.release_date 
                       FROM ALBUM AS album 
                       JOIN ARTIST AS artist 
                       ON album.artist_id = artist.id 
                       WHERE album.artist_id = %s and album.id = %s;
                       ''', (artist_id, album_id))
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.close()
        connection.close()
        return jsonify(album), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()
    


@albums_bp.route('/albums', methods=['POST'])
def add_album(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return no_data()
    
        name = data.get('name')
        album_type = data.get('type')
        release_date = data.get('release_date')

        if not name:
            return jsonify(
                    {
                        "error": "\"name\" field of the album must be provided."
                    }
                ), BAD_REQUEST
        if not album_type:
            return jsonify(
                    {
                        "error": "\"type\" field of the album must be provided."
                    }
                ), BAD_REQUEST
        if not release_date:
            return jsonify(
                    {
                        "error": "\"release_date\" field of the album must be provided."
                    }
                ), BAD_REQUEST

        if not is_valid_date(release_date):
            return jsonify(
                    {
                        "error": "\"release_date\" field must be in the format of \"YYYY-MM-DD\""
                    }
                ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST 
                       WHERE id = %s;
                       ''', (artist_id))
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       INSERT INTO ALBUM (artist_id, name, `type`, release_date)
                       VALUES (%s, %s, %s, %s);
                       ''', (artist_id, name, album_type, release_date))
        connection.commit()

        cursor.close()
        connection.close()

        album_id = cursor.lastrowid

        return jsonify(
                {
                    "message": "Album added successfully.", 
                    "album": { 
                        "artist_id": artist_id, 
                        "id": album_id, 
                        "name": name, 
                        "type": album_type,
                        "release_date": release_date
                    }
                }
            ), CREATED
    except ValueError:
        return id_error()
    except:
        return internal_error()


@albums_bp.route('/albums/<album_id>', methods=['PUT'])
def update_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        data = request.get_json()        
        if not data:
            return no_data()

        name = data.get('name')
        album_type = data.get('type')
        release_date = data.get('release_date')

        if not name:
            return jsonify(
                    {
                        "error": "\"name\" field of the album must be provided."
                    }
                ), BAD_REQUEST
        if not album_type:
            return jsonify(
                    {
                        "error": "\"type\" field of the album must be provided."
                    }
                ), BAD_REQUEST
        if not release_date:
            return jsonify(
                    {
                        "error": "\"release_date\" field of the album must be provided."
                    }
                ), BAD_REQUEST
        
        if not is_valid_date(release_date):
            return jsonify(
                    {
                        "error": "\"release_date\" field must be in the format of \"YYYY-MM-DD\""
                    }
                ), BAD_REQUEST
        
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST 
                       WHERE id = %s;
                       ''', (artist_id))
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * 
                       FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s;
                       ''', (album_id))
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()

        cursor.execute('''
                       UPDATE ALBUM
                       SET name = %s, `type` = %s, release_date = %s
                       WHERE id = %s;
                       ''', (name, album_type, release_date, album_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
                {
                    "message": "Album updated successfully.", 
                    "album": { 
                        "artist_id": artist_id, 
                        "id": album_id, 
                        "name": name, 
                        "type": album_type,
                        "release_date": release_date
                    }
                }
            ), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()
    


@albums_bp.route('/albums/<album_id>', methods=['PATCH'])
def modify_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        data = request.get_json()        
        if not data:
            return no_data()

        name = data.get('name')
        album_type = data.get('type')
        release_date = data.get('release_date')

        if not name and not album_type and not release_date:
            return jsonify(
                    {
                        "error": "No modifiable field has been specified. Modifiable fields are: \"name\", \"type\" and \"release_date\"."
                    }
                ), BAD_REQUEST

        if not is_valid_date(release_date):
            return jsonify(
                    {
                        "error": "\"release_date\" field must be in the format of \"YYYY-MM-DD\"."
                    }
                ), BAD_REQUEST
        
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST 
                       WHERE id = %s;
                       ''', (artist_id))
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
    
        cursor.execute('''
                       SELECT * 
                       FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s;
                       ''', (album_id))
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()

        set_clauses = []
        params = []

        if name:
            set_clauses.append("name = %s")
            params.append(name)
        if album_type:
            set_clauses.append("`type` = %s")
            params.append(album_type)
        if release_date:
            set_clauses.append("release_date = %s")
            params.append(release_date)

        set_clause = ", ".join(set_clauses)
        params.append(album_id)

        cursor.execute('''
                       UPDATE ALBUM 
                       SET {}
                       WHERE id = %s;
                       '''.format(set_clause), params)
        connection.commit()
        
        cursor.close()
        connection.close()
        
        return jsonify(
                {
                    "message": "Album updated successfully.", 
                    "album": { 
                        "artist_id": artist_id, 
                        "id": album_id, 
                        "name": name, 
                        "type": album_type, 
                        "release_date": release_date
                    }
                }
            ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()
    
@albums_bp.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        # this check of existance of artist and existance of album of given artist 
        # has been all around the api, should be a function. 
        cursor.execute('''
                       SELECT * FROM ARTIST 
                       WHERE id = %s;
                       ''', (artist_id))
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
    
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s;
                       ''', (album_id))
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       DELETE FROM ALBUM
                       WHERE id = %s;
                       ''', (album_id))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
                {
                    "message": "Album deleted successfully.", 
                }
            ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()
