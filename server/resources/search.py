from flask import Blueprint, jsonify, request
from database import db

OK = 200
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

search_bp = Blueprint('search', __name__)
db = db()

@search_bp.route('/search', methods=["GET"])
def search():
    try:
        query = request.args.get('q')
        query_filter = request.args.get('filter')
        order_by = request.args.get('order_by', 'asc')
        limit = request.args.get('limit', 10)
        offset = request.args.get('offset',0)

        if query is None:
            return jsonify(
                {
                    "error": "Search query is not provided."
                }
            ), BAD_REQUEST

        query = query.lower()
        query_filter = query_filter.lower()
        order_by = order_by.lower()
        limit = int(limit)
        offset = int(offset)

        if query_filter != "artist" or query_filter != "album" or query_filter != "track":
            return jsonify(
                {
                    "error": "Filter can only be one of the following: \"artist\", \"album\", or \"track\"."
                }
            ), BAD_REQUEST
        
        if order_by != "asc" or order_by != "desc":
            return jsonify(
                {
                    "error": "Ordering can only be either one of the following: \"asc\" or \"desc\"."
                }
            )

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        if query_filter == "artist":
            cursor.execute('''
                           SELECT id, name, short_info FROM ARTIST
                           WHERE name LIKE %s
                           ORDER BY %s
                           LIMIT %s
                           OFFSET %s;
                           ''', [f"%{query}%", order_by, limit, offset])

        if query_filter == "album":
            cursor.execute('''
                           SELECT id, artist_id, name, type, release_date FROM ALBUM
                           WHERE name LIKE %s
                           ORDER BY %s
                           LIMIT %s
                           OFFSET %s;
                           ''', [f"%{query}%", order_by, limit, offset])
            
        if query_filter == "track":
            cursor.execute('''
                           SELECT id, album_id, name, length_sec FROM ALBUM
                           WHERE name LIKE %s
                           ORDER BY %s
                           LIMIT %s
                           OFFSET %s;
                           ''', [f"%{query}%", order_by, limit, offset])

        result = cursor.fetchall()

        return jsonify(
            {
                "message": "Search executed successfully",
                "result": result
            }
        ), OK
    except ValueError:
        return jsonify(
            {
                "error": "Limit and offset must be an integer."
            }
        ), BAD_REQUEST
    except:
        return jsonify(
            {
                "error": "internal error"
            }
        ), INTERNAL_SERVER_ERROR
