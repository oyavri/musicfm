from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

artists_bp = Blueprint('artists', __name__)
db = db()

def id_error():
    return jsonify(
        {
            "error": "Artist ID must be an integer."
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
            "error": "There is no such artist with given ID."
        }
    ), NOT_FOUND

def no_data():
    return jsonify(
        {
            "error": "Unsopported format of request."
        }
    ), BAD_REQUEST


@artists_bp.route('/artists', methods=['GET'])
def get_artists():
    try:
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'''
                       SELECT * FROM ARTIST;
                       ''')
        users = cursor.fetchall()

        if not users:
            return jsonify(
                {
                    "message": "There is no artist in the database."
                }
            ), OK

        cursor.close()
        connection.close()
        return jsonify(users), OK
    
    except:
        return internal_error()

@artists_bp.route('/artists/<artist_id>', methods=['GET'])
def get_artist(artist_id):
    try:
        artist_id = int(artist_id)

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
        
        cursor.close()
        connection.close()
        return jsonify(artist), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@artists_bp.route('/artists', methods=['POST'])
def add_artist():
    try:
        data = request.get_json()

        if not data:
            return no_data()

        name = data.get('name')
        short_info = data.get('short_info')

        if not name:
            return jsonify(
                {
                    "error": "\"name\" field of the artist must be provided."
                }
            ), BAD_REQUEST
        if not short_info:
            return jsonify(
                {
                    "error": "\"short_info\" field of the artist must be provided."
                }
            ), BAD_REQUEST
        
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute('''
                       INSERT INTO ARTIST (name, short_info) 
                       VALUES (%s, %s);
                       ''', (name, short_info))
        connection.commit()

        cursor.close()
        connection.close()

        artist_id = cursor.lastrowid

        return jsonify(
            {
                "message": "Artist added successfully.", 
                "artist": {
                    "id": artist_id,
                    "name": name,
                    "short_info": short_info
                }
            }
        ), CREATED
    
    except:
        return internal_error()
    
@artists_bp.route('/artists/<artist_id>', methods=['PUT'])
def update_artist(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return no_data()

        name = data.get('name')
        short_info = data.get('short_info')

        if not name:
            return jsonify({"error": "\"name\" field of the artist must be provided."}), BAD_REQUEST
        if not short_info:
            return jsonify({"error": "\"short_info\" field of the artist must be provided."}), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST 
                       WHERE id={artist_id};
                       ''')
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute(f'''
                       UPDATE ARTIST 
                       SET name = "{name}", short_info = "{short_info}" 
                       WHERE id = {artist_id};
                       ''')
        connection.commit()

        cursor.close()
        connection.close()
        return jsonify(
            {
                "message": "Artist updated successfully.", 
                "artist": {
                    "id": artist_id,
                    "name": name, 
                    "short_info": short_info
                }
            }
        ), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@artists_bp.route('/artists/<artist_id>', methods=['PATCH'])
def modify_artist(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return no_data()

        name = data.get('name')
        short_info = data.get('short_info')

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST 
                       WHERE id={artist_id};
                       ''')
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        if not name and not short_info:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "No modifiable field has been specified. Modifiable fields are: \"name\", \"short_info\"."
                }
            ), BAD_REQUEST
        
        cursor.execute(f'''
                        UPDATE ARTIST 
                        SET {f"name = \"{name}\"," if name else ""}
                            {f"short_info = \"{short_info}\"" if short_info else ""} 
                        WHERE id = {artist_id};
                        ''')
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Artist updated successfully.", 
                "artist": {
                    "id": artist_id,
                    "name": name, 
                    "short_info": short_info
                }
            }
        ), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@artists_bp.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist_id = int(artist_id)

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'''
                       SELECT * FROM ARTIST 
                       WHERE id={artist_id};
                       ''')
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute(f'''
                       DELETE FROM ARTIST 
                       WHERE id = {artist_id};
                       ''')
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Artist deleted successfully."
            }
        ), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()
