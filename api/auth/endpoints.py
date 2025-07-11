"""Routes for module auth"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, decode_token
from flask_bcrypt import Bcrypt
from helper.db_helper import get_connection, close_connection
import json

bcrypt = Bcrypt()
auth_endpoints = Blueprint('auth', __name__)


@auth_endpoints.route('/login', methods=['POST'])
def login():
    """Routes for authentication"""
    try:
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            return jsonify({"msg": "Username and password are required"}), 400

        connection = None
        try:
            connection = get_connection()
            
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            request_query = (username,)
            
            cursor.execute(query, request_query)
            user = cursor.fetchone()
            cursor.close()

            if not user:
                return jsonify({"msg": "Bad username or password"}), 401

            if not bcrypt.check_password_hash(user.get('password'), password):
                return jsonify({"msg": "Bad username or password"}), 401

            # Convert identity to JSON string for JWT
            identity_data = {
                'username': username, 
                'user_id': user.get('user_id'), 
                'role': user.get('role', 'user')
            }
            identity_string = json.dumps(identity_data)
            
            access_token = create_access_token(identity=identity_string)
            decoded_token = decode_token(access_token)
            expires = decoded_token['exp']
            
            response_data = {
                "access_token": access_token, 
                "expires_in": expires, 
                "type": "Bearer",
                "role": user.get('role', 'user'),
                "user_id": user.get('user_id')
            }
            return jsonify(response_data)
            
        except Exception as e:
            return jsonify({"msg": f"Database error: {str(e)}"}), 500
        finally:
            if connection:
                close_connection(connection)
                
    except Exception as e:
        return jsonify({"msg": f"Error: {str(e)}"}), 500


@auth_endpoints.route('/register', methods=['POST'])
def register():
    """Routes for register"""
    username = request.form.get('username')
    password = request.form.get('password')
    email = request.form.get('email')
    
    if not username or not password or not email:
        return jsonify({"msg": "Username, password, and email are required"}), 400
    
    # To hash a password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        
        # Check if username or email already exists
        check_query = "SELECT * FROM users WHERE username = %s OR email = %s"
        cursor.execute(check_query, (username, email))
        existing_user = cursor.fetchone()
        
        if existing_user:
            cursor.close()
            return jsonify({"message": "Username or email already exists"}), 400
        
        insert_query = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
        request_insert = (username, hashed_password, email)
        cursor.execute(insert_query, request_insert)
        connection.commit()
        new_id = cursor.lastrowid
        cursor.close()
        
        if new_id:
            return jsonify({"message": "OK",
                            "description": "User created",
                            "username": username,
                            "email": email}), 201
        return jsonify({"message": "Failed, cant register user"}), 501
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}"}), 500
    finally:
        if connection:
            close_connection(connection)
