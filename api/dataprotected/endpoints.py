"""Routes for module protected endpoints"""
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from helper.jwt_helper import get_role_from_jwt
from helper.db_helper import get_connection, close_connection
from datetime import date

protected_endpoints = Blueprint('data_protected', __name__)


@protected_endpoints.route('/data', methods=['GET'])
@jwt_required()
def get_data():
    """
    Routes for demonstrate protected data endpoints, 
    need jwt to visit this endpoint
    """
    current_user = get_jwt_identity()
    claims = get_jwt()
    roles = claims.get('roles', 'user')
    
    return jsonify({
        "message": "OK",
        "user_logged": current_user,
        "roles": roles
    }), 200