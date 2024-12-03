from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

artists_bp = Blueprint('artists', __name__)
db = db()

@artists_bp.route('/artists', methods=['GET'])
def get_artists():
    try:
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT * FROM ARTIST")
        results = cursor.fetchall()

        cursor.close()
        connection.close()
        return jsonify(results), OK
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR

@artists_bp.route('/artists/<artist_id>', methods=['GET'])
def get_artist(artist_id):
    try:
        artist_id = int(artist_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'SELECT * FROM ARTIST WHERE id = {artist_id}')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Artist not found."}), NOT_FOUND
        
        cursor.close()
        connection.close()
        return jsonify(result), OK
    except ValueError:
        return jsonify({"error": "Artist id must be an integer"}), BAD_REQUEST
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR

@artists_bp.route('/artists', methods=['POST'])
def add_artist():
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "Unsopported format of request"}), BAD_REQUEST

        name = data.get('name')
        short_info = data.get('short_info')

        if not name:
            return jsonify({"error": "\"name\" field of the artist must be provided."}), BAD_REQUEST
        if not short_info:
            short_info = ""
        
        connection = db.connect()
        cursor = connection.cursor()
        
        cursor.execute(f'INSERT INTO ARTIST (name, short_info) VALUES ("{name}", "{short_info}")')
        connection.commit()

        cursor.close()
        connection.close()
        
        return jsonify({"message": "Artist added successfully.", "name": name, "short_info": short_info}), CREATED
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR
    
@artists_bp.route('/artists/<artist_id>', methods=['PUT'])
def update_artist(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "Unsopported format of request"}), BAD_REQUEST

        name = data.get('name')
        short_info = data.get('short_info')

        if not name:
            return jsonify({"error": "Name of the artist cannot be null"}), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'SELECT * FROM ARTIST WHERE id={artist_id}')
        results = cursor.fetchone()

        if results is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Artist not found."}), NOT_FOUND

        cursor.execute(f'UPDATE ARTIST SET name = "{name}", short_info = "{short_info}" WHERE id = {artist_id}')
        connection.commit()

        cursor.close()
        connection.close()
        return jsonify({"message": "Artist updated successfully.", "name": name, "short_info": short_info}), OK
    except ValueError:
        return jsonify({"error": "Artist id must be an integer"}), BAD_REQUEST
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR

@artists_bp.route('/artists/<artist_id>', methods=['PATCH'])
def modify_artist(artist_id):
    try:
        artist_id = int(artist_id)

        data = request.get_json()
        if not data:
            return jsonify({"error": "Unsopported format of request"}), BAD_REQUEST

        name = data.get('name')
        short_info = data.get('short_info')

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'SELECT * FROM ARTIST WHERE id={artist_id}')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Artist not found."}), NOT_FOUND
        
        # Update either one of them or both of them
        if name:
            cursor.execute(f'UPDATE ARTIST SET name = "{name}" WHERE id = {artist_id}')
        elif short_info:
            cursor.execute(f'UPDATE ARTIST SET short_info = {short_info} WHERE id = {artist_id}')
        else:
            cursor.execute(f'UPDATE ARTIST SET name = "{name}", short_info = "{short_info}" WHERE id = {artist_id}')

        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Artist updated successfully.", "name": name, "short_info": short_info}), OK
    except ValueError:
        return jsonify({"error": "Artist id must be an integer"}), BAD_REQUEST
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR

@artists_bp.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist_id = int(artist_id)

        connection = db.connect()
        cursor = connection.cursor()

        cursor.execute(f'SELECT * FROM ARTIST WHERE id={artist_id}')
        result = cursor.fetchone()

        if result is None:
            cursor.close()
            connection.close()
            return jsonify({"error": "Artist not found."}), NOT_FOUND
        
        cursor.execute(f'DELETE FROM ARTIST WHERE id = {artist_id}')
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Artist deleted successfully."}), OK
    except ValueError:
        return jsonify({"error": "Artist id must be an integer"}), BAD_REQUEST
    except:
        return jsonify({"error": "An internal error occurred."}), INTERNAL_SERVER_ERROR
