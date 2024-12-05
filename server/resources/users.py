from flask import Blueprint, jsonify, request
from database import db
import re

OK = 200
CREATED = 201
BAD_REQUEST = 400
NOT_FOUND = 404
INTERNAL_SERVER_ERROR = 500

users_bp = Blueprint('users', __name__)
db = db()

def is_valid_email(email):
    pattern = r"^.+@.+$"
    return (len(email) > 5 and re.match(pattern, email))
    

def is_valid_gender(gender):
    if gender == 'M' or gender == 'F':
        return True
    return False

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

def no_data():
    return jsonify(
        {
            "error": "Unsupported format of request."
        }
    ), BAD_REQUEST

@users_bp.route('/users', methods=['GET'])
def get_users():
    try:
        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute(f'''
                       SELECT * FROM USER;
                       ''')
        users = cursor.fetchall()

        if not users:
            return jsonify(
                {
                    "message": "There is no user in the database."
                }
            ), OK

        cursor.close()
        connection.close()
        return jsonify(users), OK
    except:
        return internal_error()


@users_bp.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
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

        cursor.close()
        connection.close()
        return jsonify(user), OK
    except ValueError:
        return id_error()
    except:
        return internal_error()

@users_bp.route('/users', methods=['POST'])
def add_user(user_id):
    try:
        user_id = int(user_id)

        data = request.get_json()

        nickname = data.get('nickname')
        email = data.get('email')
        gender = data.get('gender')

        if not data:
            return no_data()
        
        if not nickname:
            return jsonify(
                {
                    "error": "\"nickname\" field of the user must be provided."
                }
            ), BAD_REQUEST
        if not email:
            return jsonify(
                {
                    "error": "\"email\" field of the user must be provided."
                }
            ), BAD_REQUEST
        if not gender:
            return jsonify(
                {
                    "error": "\"gender\" field of the user must be provided, field can only be one of the following: \"M\", \"F\" or empty."
                }
            ), BAD_REQUEST
        
        if not is_valid_email(email):
            return jsonify(
                {
                    "error": "Emails must be longer than 5 characters and in the format of \"<one-or-more-characters>@<one-or-more-characters>\"."
                }
            ), BAD_REQUEST
        
        if not is_valid_gender(gender):
            return jsonify(
                {
                    "error": "Gender must be either one of \"M\" or \"F\", or not provided."
                }
            ), BAD_REQUEST

        connection = db.connect()
        cursor = connection.cursor(dictionary=True)

        cursor.execute('''
                       INSERT INTO USER (nickname, email, gender) 
                       VALUES (%s, %s, %s);
                       ''', (nickname, email, gender))
        cursor.commit()

        user_id = cursor.lastrowid

        cursor.close()
        connection.close()
        return jsonify(
            {
                "message": "User added successfully",
                "user": {
                    "id": user_id,
                    "nickname": nickname,
                    "email": email,
                    "gender": gender
                }
            }
        ), CREATED
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@users_bp.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        user_id = int(user_id)

        data = request.get_json()

        nickname = data.get('nickname')
        email = data.get('email')
        gender = data.get('gender')

        if not data:
            return no_data()
        
        if not nickname:
            return jsonify(
                {
                    "error": "\"nickname\" field of the user must be provided."
                }
            ), BAD_REQUEST
        if not email:
            return jsonify(
                {
                    "error": "\"email\" field of the user must be provided."
                }
            ), BAD_REQUEST
        if not gender:
            return jsonify(
                {
                    "error": "\"gender\" field of the user must be provided, field can only be one of the following: \"M\", \"F\" or empty."
                }
            ), BAD_REQUEST
        
        if not is_valid_email(email):
            return jsonify(
                {
                    "error": "Emails must be longer than 5 characters and in the format of \"<one-or-more-characters>@<one-or-more-characters>\"."
                }
            ), BAD_REQUEST
        
        if not is_valid_gender(gender):
            return jsonify(
                {
                    "error": "Genders must be either one of \"M\" or \"F\", or not provided."
                }
            ), BAD_REQUEST

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
                       UPDATE USER
                       SET nickname = {nickname}, email = {email}, gender = {gender} 
                       WHERE id = {user_id};
                       ''')
        cursor.commit()

        cursor.close()
        connection.close()
        return jsonify(
            {
                "message": "User updated successfully",
                "user": {
                    "id": user_id,
                    "nickname": nickname,
                    "email": email,
                    "gender": gender
                }
            }
        ), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()


@users_bp.route('/users/<user_id>', methods=['PATCH'])
def modify_user(user_id):
    try:
        user_id = int(user_id)

        data = request.get_json()

        nickname = data.get('nickname')
        email = data.get('email')
        gender = data.get('gender')

        if not data:
            return no_data()
        
        if not nickname and not email and not gender:
            return jsonify(
                {
                    "error": "No modifiable field has been specified. Modifiable fields are: \"gender\", \"gender\", and \"gender\"."
                }
            ), BAD_REQUEST
        
        if email:
            if not is_valid_email(email):
                return jsonify(
                    {
                        "error": "Emails must be longer than 5 characters and in the format of \"<one-or-more-characters>@<one-or-more-characters>\"."
                    }
                ), BAD_REQUEST
        
        if gender:
            if not is_valid_gender(gender):
                return jsonify(
                    {
                        "error": "Genders must be either one of \"M\" or \"F\", or not provided."
                    }
                ), BAD_REQUEST

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
                       UPDATE USER
                       SET {f"nickname = \"{nickname}\"," if nickname else ""} 
                           {f"email = \"{email}\","} 
                           {f"gender = \"{gender}\""} 
                       WHERE id = {user_id};
                       ''')
        cursor.commit()

        cursor.close()
        connection.close()
        
        return jsonify(
            {
                "message": "User updated successfully",
                "user": {
                    "id": user_id,
                    "nickname": nickname,
                    "email": email,
                    "gender": gender
                }
            }
        ), OK
    
    except ValueError:
        return id_error()
    except:
        return internal_error()

@users_bp.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        user_id = int(user_id)

        connection = db.connect()
        cursor = connection.cursor()

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
                       DELETE FROM USER 
                       WHERE id = {user_id};
                       ''')
        cursor.commit()

        cursor.close()
        connection.close()

        return jsonify(
            {
                "message": "User deleted successfully."
            }
        ), OK

    except ValueError:
        return id_error()
    except:
        return internal_error()
