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
    


@albums_bp.route('/albums', methods=['GET'])
def get_albums(artist_id):
    try:
        artist_id = int(artist_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'''
                       SELECT album.id as album_id, album.artist_id, album.name, album.type, album.release_date 
                       FROM ALBUM AS album 
                       JOIN ARTIST AS artist 
                       ON album.artist_id = artist.id 
                       WHERE artist_id = {artist_id};
                       ''')
        results = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify(results), OK
    except ValueError:
        return jsonify(
                {
                    "error": "Artist id must be an integer."
                }
            ), BAD_REQUEST
    except:
        return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR




@albums_bp.route('/albums/<album_id>', methods=['GET'])
def get_album(artist_id, album_id): 
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'''
                        SELECT album.id as album_id, album.artist_id, album.name, album.type, album.release_date 
                        FROM ALBUM AS album 
                        JOIN ARTIST AS artist 
                        ON album.artist_id = artist.id 
                        WHERE album.artist_id = {artist_id} and album.id = {album_id};
                        ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "Album not found"
                    }
                ), NOT_FOUND
        
        cursor.close()
        connection.close()
        return jsonify(result), OK
    except ValueError:
        return jsonify(
                {
                    "error": "Artist id and album id must be an integer."
                }
            ), BAD_REQUEST
    except:
        return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR
    


@albums_bp.route('/albums', methods=['POST'])
def add_album(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return jsonify(
                    {
                        "error": "Unsupported format of request."
                    }
                ), BAD_REQUEST
    
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
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST WHERE id = {artist_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no artist with given id."
                    }
                ), BAD_REQUEST

        cursor.execute('''
                       INSERT INTO ALBUM (artist_id, name, `type`, release_date)
                       VALUES (%s, %s, %s, %s);
                       ''', (artist_id, name, album_type, release_date))
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
                {
                    "message": "Album added successfully.", 
                    "album": { 
                        "artist_id": artist_id, 
                        "id": cursor.lastrowid, 
                        "name": name, 
                        "type": album_type,
                        "release_date": release_date
                    }
                }
            ), CREATED
    except ValueError:
        return jsonify(
                {
                    "error": "Artist id must be an integer."
                }
            ), BAD_REQUEST
    except Exception as e:
        return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR
    


@albums_bp.route('/albums/<album_id>', methods=['PUT'])
def update_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        data = request.get_json()        
        if not data:
            return jsonify(
                    {
                        "error": "Unsupported format of request."
                    }
                ), BAD_REQUEST

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
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST WHERE id = {artist_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no artist with given artist id."
                    }
                ), BAD_REQUEST

        cursor.execute(f'''
                       SELECT * 
                       FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no such album associated with given artist id."
                    }
                ), BAD_REQUEST

        cursor.execute(f'''
                       UPDATE ALBUM
                       SET name = "{name}", `type` = "{album_type}", release_date = "{release_date}"
                       WHERE id = {album_id};
                       ''')
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
        return jsonify(
                {
                    "error": "Artist id and album id must be an integer."
                }
            ), BAD_REQUEST
    except Exception as e:
        return jsonify(
                {
                    "error": f"An internal error occurred. {e}"
                }
            ), INTERNAL_SERVER_ERROR
    


@albums_bp.route('/albums/<album_id>', methods=['PATCH'])
def modify_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        data = request.get_json()        
        if not data:
            return jsonify(
                    {
                        "error": "Unsupported format of request."
                    }
                ), BAD_REQUEST

        name = data.get('name')
        album_type = data.get('type')
        release_date = data.get('release_date')

        if not is_valid_date(release_date):
            return jsonify(
                    {
                        "error": "\"release_date\" field must be in the format of \"YYYY-MM-DD\""
                    }
                ), BAD_REQUEST
        
        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST WHERE id = {artist_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no artist with given artist id."
                    }
                ), BAD_REQUEST
    
        cursor.execute(f'''
                       SELECT * 
                       FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no such album associated with given artist id."
                    }
                ), BAD_REQUEST
        
        if not name and not album_type and not release_date:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "No modifiable field has been specified. Modifiable fields are: \"name\", \"type\" and \"release_date\"."
                    }
                ), BAD_REQUEST
        
        cursor.execute(f'''
                        UPDATE ALBUM
                        SET {f"name = \"{name}\"," if name else ""} 
                            {f"`type` = \"{album_type}\"," if album_type else ""} 
                            {f"release_date = \"{release_date}\"" if release_date else ""}
                        WHERE id = {album_id};
                        ''')

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
        return jsonify(
                {
                    "error": "Artist id and album id must be an integer."
                }
            ), BAD_REQUEST
    except:
        return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR
    
@albums_bp.route('/albums/<album_id>', methods=['DELETE'])
def delete_album(artist_id, album_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)

        connection = db.connect()
        cursor = connection.cursor()

        # this check of existance of artist and existance of album of given artist 
        # has been all around the api, should be a function. 
        cursor.execute(f'''
                       SELECT * FROM ARTIST WHERE id = {artist_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no artist with given artist id."
                    }
                ), NOT_FOUND
    
        cursor.execute(f'''
                       SELECT * 
                       FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = {album_id};
                       ''')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify(
                    {
                        "error": "There is no such album associated with given artist id."
                    }
                ), NOT_FOUND
        
        cursor.execute(f'''
                       DELETE FROM ALBUM
                       WHERE id = {album_id};
                       ''')

    except ValueError:
        return jsonify(
                {
                    "error": "Artist id and album id must be an integer."
                }
            ), BAD_REQUEST
    except:
        return jsonify(
                {
                    "error": "An internal error occurred."
                }
            ), INTERNAL_SERVER_ERROR
