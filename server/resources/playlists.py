from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

playlists_bp = Blueprint('playlists', __name__, url_prefix="/users/<user_id>")
db = db()

def id_error():
    return jsonify(
        {
            "error": "User ID and playlist ID must be an integer."
        }
    ), BAD_REQUEST

def id_error_without_playlist():
    return jsonify(
        {
            "error": "User ID must be an integer."
        }
    ), BAD_REQUEST

def id_error_with_track_id():
    return jsonify(
            {
                "error": "User ID, playlist ID, and track ID must be an integer."
            }
        ), BAD_REQUEST

def internal_error():
    return jsonify(
        {
            "error": "An internal error occurred."
        }
    ), INTERNAL_SERVER_ERROR

def no_user():
    return jsonify(
        {
            "error": "There is no such user with given ID."
        }
    ), NOT_FOUND

def no_track():
    return jsonify(
        {
            "error": "There is no such track with given ID."
        }
    ), NOT_FOUND

def no_playlist():
    return jsonify(
        {
            "error": "There is no playlist associated with given user ID."
        }
    ), NOT_FOUND

def not_in_playlist():
    return jsonify(
        {
            "error": "There is no such track in the given playlist."
        }
    ), NOT_FOUND

def no_data():
    return jsonify(
        {
            "error": "Unsupported format of request."
        }
    ), BAD_REQUEST

@playlists_bp.route('/playlists', methods=['POST'])
def create_playlist(user_id):
    try:
        user_id = int(user_id)

        data = request.get_json()
        if not data:
            return no_data()

        playlist_name = data.get('name')
        if not playlist_name:
            return jsonify(
                {
                    "error": "Playlist name must be provided"
                }
            ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
                       SELECT id FROM USER 
                       WHERE id = %s;
                       """, [user_id])
        user = cursor.fetchone()

        if not user:
            cursor.close()
            connection.close()
            return no_user()

        cursor.execute("""
                       INSERT INTO PLAYLIST (name, user_id) 
                       VALUES (%s, %s);
                       """, [playlist_name, user_id])
        connection.commit()

        playlist_id = cursor.lastrowid

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Playlist created successfully",
                "playlist": {
                    "id": playlist_id, 
                    "name": playlist_name
                }
            }
        ), OK
    except ValueError:
        return id_error_without_playlist()
    except:
        return internal_error()
    
@playlists_bp.route('/playlists/<playlist_id>', methods=['DELETE'])
def delete_playlist(user_id, playlist_id):
    try:
        user_id = int(user_id)
        playlist_id = int(playlist_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        # Validate that the playlist exists and belongs to the user
        cursor.execute("""
                       SELECT id FROM PLAYLIST 
                       WHERE id = %s AND user_id = %s;
                       """, [playlist_id, user_id]
        )
        playlist = cursor.fetchone()

        if not playlist:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "Playlist not found or does not belong to the user"
                }
            ), NOT_FOUND

        cursor.execute("""
                       DELETE FROM PLAYLIST 
                       WHERE id = %s;
                       """, [playlist_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Playlist deleted successfully"
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()


@playlists_bp.route('/playlists', methods=['GET'])
def get_playlists(user_id):
    try:
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM USER
                       WHERE id = %s;
                       ''', [user_id])
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()

        cursor.execute('''
                       SELECT id, `name` FROM PLAYLIST
                       WHERE user_id = %s;
                       ''', [user_id])
        playlists = cursor.fetchall()
        if not playlists:
            cursor.close()
            connection.close()
            return jsonify([]), OK
        
        cursor.close()
        connection.close()
        return jsonify(playlists), OK
    except ValueError:
        return id_error_without_playlist()
    except:
        return internal_error()

@playlists_bp.route('/playlists/<playlist_id>', methods=['GET'])
def get_playlist(user_id, playlist_id):
    try:
        user_id = int(user_id)
        playlist_id = int(playlist_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM USER
                       WHERE id = %s;
                       ''', [user_id])
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()
        
        cursor.execute('''
                       SELECT * FROM PLAYLIST
                       WHERE id = %s AND user_id = %s;
                       ''', [playlist_id, user_id])
        playlist = cursor.fetchone()

        if playlist is None:
            cursor.close()
            connection.close()
            return no_playlist()
        
        cursor.execute('''
                       SELECT track.id, track.album_id, track.name, track.length_sec 
                       FROM PLAYLIST AS playlist
                       JOIN CONTAIN AS contain
                       ON contain.playlist_id = playlist.id
                       JOIN TRACK AS track
                       ON contain.track_id = track.id
                       WHERE playlist.id = %s AND playlist.user_id = %s;
                       ''', [playlist_id, user_id])
        tracks = cursor.fetchall()

        playlist["tracks"] = tracks
        cursor.close()
        connection.close()
        return jsonify(
            {
                "playlist": playlist
            }
        ), OK
        
    except ValueError:
        return id_error()
    except:
        return internal_error()
    
@playlists_bp.route('/playlists/<playlist_id>', methods=['POST'])
def add_track_to_playlist(user_id, playlist_id):
    
    try:
        user_id = request.view_args.get('user_id')
        playlist_id = request.view_args.get('playlist_id')


        data = request.get_json()
        if not data:
            return no_data()
        
        track_id = data.get('track_id')
        if not track_id:
            return jsonify(
                {
                    "error": "\"track_id\" must be provided."
                }
            ), BAD_REQUEST

        track_id = int(track_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM TRACK 
                       WHERE id = %s;
                       ''', [track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()

        cursor.execute('''
                       SELECT * FROM USER
                       WHERE id = %s;
                       ''', [user_id])
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()
        
        cursor.execute('''
                       SELECT * FROM PLAYLIST
                       WHERE id = %s AND user_id = %s;
                       ''', [playlist_id, user_id])
        playlist = cursor.fetchone()

        if playlist is None:
            cursor.close()
            connection.close()
            return no_playlist()

        cursor.execute('''
                       INSERT INTO CONTAIN (playlist_id, track_id) 
                       VALUES (%s, %s);
                       ''', [playlist_id, track_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track added to the playlist successfully."
            }
        ), CREATED

    except ValueError:
        return id_error_with_track_id()
    except:
        return internal_error()

@playlists_bp.route('/playlists/<playlist_id>/tracks/<track_id>', methods=['DELETE'])
def remove_track_from_playlist(user_id, playlist_id, track_id):
    try:
        user_id = int(user_id)
        playlist_id = int(playlist_id)
        track_id = int(track_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM TRACK 
                       WHERE id = %s;
                       ''', [track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()

        cursor.execute('''
                       SELECT * FROM USER
                       WHERE id = %s;
                       ''', [user_id])
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()
        
        cursor.execute('''
                       SELECT * FROM PLAYLIST
                       WHERE id = %s AND user_id = %s;
                       ''', [playlist_id, user_id])
        playlist = cursor.fetchone()

        if playlist is None:
            cursor.close()
            connection.close()
            return no_playlist()
        
        cursor.execute('''
                       SELECT * FROM CONTAIN
                       WHERE playlist_id = %s AND track_id = %s;
                       ''', [playlist_id, track_id])
        track_in_playlist = cursor.fetchone()

        if track_in_playlist is None:
            cursor.close()
            connection.close()
            return not_in_playlist()
        
        cursor.execute('''
                       DELETE FROM CONTAIN 
                       WHERE track_id = %s AND playlist_id = %s
                       LIMIT 1;
                       ''', [track_id, playlist_id])
        
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track removed from the playlist successfully."
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()
