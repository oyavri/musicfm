from flask import Blueprint, jsonify, request
from database import db

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
CONFLICT = 409
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

def id_error_including_user():
    return jsonify(
        {
            "error": "Artist ID, album ID, track ID, and user ID must be an integer."
        }
    )

def id_error_including_user_and_rate():
    return jsonify(
        {
            "error": "Artist ID, album ID, track ID, user ID, and rate must be an integer."
        }
    )

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

def no_user():
    return jsonify(
        {
            "error": "There is no such user with given ID."
        }
    ), NOT_FOUND

def no_like():
    return jsonify(
        {
            "error": "User has not liked such track with given ID."
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

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()

        cursor.execute('''
                       SELECT track.id, track.album_id, track.name, track.length_sec FROM TRACK AS track
                       JOIN ALBUM as album
                       ON track.album_id = album.id
                       JOIN ARTIST as artist
                       ON album.artist_id = artist.id
                       WHERE artist.id = %s AND album.id = %s;
                       ''', [artist_id, album_id])
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

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()

        cursor.execute('''
                       SELECT track.id, track.album_id, track.name, track.length_sec FROM TRACK AS track
                       JOIN ALBUM as album
                       ON track.album_id = album.id
                       JOIN ARTIST as artist
                       ON album.artist_id = artist.id
                       WHERE artist.id = %s AND album.id = %s AND track.id = %s;
                       ''', [artist_id, album_id, track_id])
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

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       INSERT INTO TRACK (album_id, name, length_sec) 
                       VALUES (%s, %s, %s);
                       ''', [album_id, name, length_sec])
        connection.commit()

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

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute('''
                       UPDATE TRACK 
                       SET name = %s, length_sec = %s"
                       WHERE id = %s;
                       ''', [name, length_sec, track_id])
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
        print(f"Received data: {data}")

        if not data:
            return jsonify({"error": "No data provided"}), BAD_REQUEST

        name = data.get("name")
        length_sec = data.get("length_sec")
        print(f"Fields to update: name={name}, length_sec={length_sec}")

        if not name and not length_sec:
            return jsonify(
                {"error": "No modifiable field has been specified."}
            ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        # Verify track existence
        cursor.execute(
            "SELECT * FROM TRACK WHERE id = %s AND album_id = %s;", [track_id, album_id]
        )
        track = cursor.fetchone()
        print(f"Fetched track: {track}")

        if not track:
            return jsonify({"error": "Track not found"}), NOT_FOUND

        # Update query
        set_clauses = []
        params = []

        if name:
            set_clauses.append("name = %s")
            params.append(name)
        if length_sec:
            set_clauses.append("length_sec = %s")
            params.append(length_sec)

        set_clause = ", ".join(set_clauses)
        params.append(track_id)

        cursor.execute(
            f"UPDATE TRACK SET {set_clause} WHERE id = %s;", params
        )
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify({"message": "Track updated successfully"}), OK

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": f"Internal error: {e}"}), INTERNAL_SERVER_ERROR


@tracks_bp.route('/tracks/<track_id>', methods=['DELETE'])
def delete_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()
        
        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute('''
                       DELETE FROM TRACK
                       WHERE id = %s;
                       ''', [track_id])
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
    
## LIKE PART ##

@tracks_bp.route('/tracks/<track_id>/likes', methods=['GET'])
def get_likes_of_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute('''
                       SELECT COUNT(*) AS like_count FROM USER AS user
                       JOIN USER_LIKE AS user_like
                       ON user.id = user_like.user_id
                       WHERE user_like.track_id = %s;
                       ''', [track_id])
        likes = cursor.fetchall()

        if not likes:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "message": "No user has liked this track yet."
                }
            ), OK
        
        cursor.close()
        connection.close()

        return jsonify(likes), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>/likes', methods=['POST'])
def like_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        user_id = data.get('user_id')
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
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
                       SELECT * FROM USER_LIKE 
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        like = cursor.fetchone()

        if like is not None:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "User has already liked this track."
                }
            ), CONFLICT

        cursor.execute('''
                       INSERT INTO USER_LIKE (user_id, track_id) 
                       VALUES (%s, %s);
                       ''', [user_id, track_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track liked successfully."
            }
        ), OK
    
    except ValueError:
        return id_error_including_user()
    except:
        return internal_error()
    
@tracks_bp.route('/tracks/<track_id>/likes', methods=['DELETE'])
def unlike_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify(
                {
                    "error": "\"user_id\" must be provided."
                }
            ), BAD_REQUEST
        
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
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
                       SELECT * FROM USER_LIKE
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        like = cursor.fetchone()

        if like is None:
            cursor.close()
            connection.close()
            return no_like()
        
        cursor.execute('''
                       DELETE FROM USER_LIKE
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track unliked successfully."
            }
        ), OK
    
    except ValueError:
        return id_error_including_user()
    except:
        return internal_error()


## RATE PART ##

@tracks_bp.route('/tracks/<track_id>/rates', methods=['GET'])
def get_rates_of_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
        track = cursor.fetchone()

        if track is None:
            cursor.close()
            connection.close()
            return no_track()
        
        cursor.execute('''
                       SELECT ROUND(COALESCE(AVG(rate.rate), 0), 2) AS average_rate FROM USER AS user
                       JOIN RATE AS rate
                       ON user.id = rate.user_id 
                       WHERE track_id = %s;
                       ''', [track_id])
        avg_rate = cursor.fetchone()
        
        cursor.close()
        connection.close()

        return jsonify(avg_rate), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>/rates', methods=['POST'])
def rate_track(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify(
                {
                    "error": "\"user_id\" must be provided."
                }
            ), BAD_REQUEST

        user_id = int(user_id)

        rate = data.get('rate')
        if not rate:
            return jsonify(
                {
                    "error": "\"rate\" must be provided."
                }
            ), BAD_REQUEST
        
        rate = int(rate)

        if not (rate > 0 and  rate <= 5):
            return jsonify(
                {
                    "error": "Rate must be an integer between 0 and 5, 5 included."
                }
            ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
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
                       SELECT * FROM RATE 
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        rate = cursor.fetchone()

        if rate is not None:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "User has already rated this track."
                }
            ), CONFLICT

        cursor.execute('''
                       INSERT INTO RATE (user_id, track_id, rate) 
                       VALUES (%s, %s, %s);
                       ''', [user_id, track_id, rate])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Track rated successfully."
            }
        ), OK

    except ValueError:
        return id_error_including_user_and_rate()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>/rates', methods=['PATCH'])
def modify_rate(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify(
                {
                    "error": "\"user_id\" must be provided."
                }
            ), BAD_REQUEST
        
        user_id = int(user_id)

        rate = data.get('rate')
        if not rate:
            return jsonify(
                {
                    "error": "\"rate\" must be provided."
                }
            ), BAD_REQUEST
        
        rate = int(rate)

        if not (rate > 0 and  rate <= 5):
            return jsonify(
                {
                    "error": "Rate must be an integer between 0 and 5, 5 included."
                }
            ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
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
                       SELECT * FROM RATE 
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        rate = cursor.fetchone()

        if rate is None:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "User has not rated this track yet."
                }
            ), BAD_REQUEST
        
        cursor.execute('''
                       UPDATE RATE
                       SET rate = %s
                       WHERE user_id = %s AND track_id = %s;
                       ''', [rate, user_id, track_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Rate updated successfully."
            }
        ), OK

    except ValueError:
        return id_error_including_user_and_rate()
    except:
        return internal_error()

@tracks_bp.route('/tracks/<track_id>/rates', methods=['DELETE'])
def delete_rate(artist_id, album_id, track_id):
    try:
        artist_id = int(artist_id)
        album_id = int(album_id)
        track_id = int(track_id)

        data = request.get_json()
        if not data:
            return no_data()
        
        user_id = data.get('user_id')
        if not user_id:
            return jsonify(
                {
                    "error": "\"user_id\" must be provided."
                }
            ), BAD_REQUEST
        
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       SELECT * FROM ARTIST
                       WHERE id = %s;
                       ''', [artist_id])
        artist = cursor.fetchone()

        if artist is None:
            cursor.close()
            connection.close()
            return no_artist()

        cursor.execute('''
                       SELECT * FROM ALBUM AS album
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s;
                       ''', [album_id, artist_id])
        album = cursor.fetchone()

        if album is None:
            cursor.close()
            connection.close()
            return no_album()
        
        cursor.execute('''
                       SELECT * FROM TRACK AS track
                       JOIN ALBUM AS album
                       ON track.album_id = album.id
                       JOIN ARTIST AS artist
                       ON album.artist_id = artist.id
                       WHERE album.id = %s AND artist.id = %s AND track.id = %s;
                       ''', [album_id, artist_id, track_id])
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
                       SELECT * FROM RATE 
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        rate = cursor.fetchone()

        if rate is None:
            cursor.close()
            connection.close()
            return jsonify(
                {
                    "error": "User has not rated this track yet."
                }
            ), BAD_REQUEST
        
        cursor.execute('''
                       DELETE FROM RATE
                       WHERE user_id = %s AND track_id = %s;
                       ''', [user_id, track_id])
        connection.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "Rate deleted successfully."
            }
        ), OK

    except ValueError:
        return id_error_including_user_and_rate()
    except:
        return internal_error()
