from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

likes_bp = Blueprint('likes', __name__, url_prefix="/users/<user_id>")
db = db()

def id_error():
    return jsonify(
        {
            "error": "User ID must be an integer."
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

def no_like():
    return jsonify(
        {
            "error": "User has not liked such track with given ID."
        }
    ), NOT_FOUND

@likes_bp.route('/likes', methods=['GET'])
def get_likes(user_id):
    try:
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(f'''
                       SELECT * FROM USER 
                       WHERE id = {user_id};
                       ''')
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()
        
        cursor.execute(f'''SELECT track.id, track.name, track.length_sec, track.album_id FROM USER AS user 
                       JOIN USER_LIKE as user_like
                       ON user_like.user_id = user.id
                       JOIN TRACK as track
                       ON user_like.track_id = track.id
                       WHERE user.id = {user_id};
                       ''')
        likedTracks = cursor.fetchall()

        if not likedTracks:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "message": "The user has not liked any track yet."
                }
            ), OK
        
        cursor.close()
        connection.close()

        return jsonify(likedTracks), OK
        
    except ValueError:
        return id_error()
    except:
        return internal_error()

@likes_bp.route('/likes', methods=['POST'])
def add_like(user_id):
    try:
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(f'''
                       SELECT * FROM USER 
                       WHERE id = {user_id};
                       ''')
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()

        cursor.execute(f'''
                       SELECT * FROM TRACK 
                       WHERE id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute(f'''
                       SELECT * FROM USER_LIKE
                       WHERE user_id = {user_id} AND track_id = {track_id};
                       ''')
        like = cursor.fetchone()

        if like:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "User has already liked this track"
                }
            ), BAD_REQUEST
        
        cursor.execute('''
                       INSERT INTO USER_LIKE (user_id, track_id) 
                       VALUES (%s, %s);
                       ''', (user_id, track_id))
        cursor.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": f"Track with ID: {track_id} liked by user with ID: {user_id} successfully.",
            }
        ), CREATED
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@likes_bp.route('/likes', methods=['DELETE'])
def remove_like(user_id):
    try:
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(f'''
                       SELECT * FROM USER 
                       WHERE id = {user_id};
                       ''')
        user = cursor.fetchone()

        if user is None:
            cursor.close()
            connection.close()
            return no_user()
        
        cursor.execute(f'''
                       SELECT * FROM TRACK 
                       WHERE id = {track_id};
                       ''')
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()

        cursor.execute(f'''
                       SELECT * FROM USER_LIKE
                       WHERE user_id = {user_id} AND track_id = {track_id};
                       ''')
        like = cursor.fetchone()

        if like is None:
            cursor.close()
            connection.close()
            return no_like()
        
        cursor.execute(f'''
                       DELETE FROM USER_LIKE 
                       WHERE user_id = {user_id} AND track_id = {track_id};
                       ''')
        cursor.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": f"Track with ID: {track_id} liked by user with ID: {user_id} successfully.",
            }
        ), CREATED
    
    except ValueError:
        return id_error()
    except:
        return internal_error()
