"""JWT helper functions"""
from flask_jwt_extended import get_jwt_identity
import json


def parse_jwt_identity():
    """Parse JWT identity yang berupa string JSON"""
    identity = get_jwt_identity()
    
    # Parse JWT identity yang berupa string JSON
    if isinstance(identity, str):
        try:
            identity = json.loads(identity)
        except json.JSONDecodeError:
            return None
    
    return identity


def get_user_id_from_jwt():
    """Get user_id from JWT identity"""
    identity = parse_jwt_identity()
    user_id = identity.get('user_id') if identity else None
    return int(user_id) if user_id else None


def get_role_from_jwt():
    """Get role from JWT identity"""
    identity = parse_jwt_identity()
    role = identity.get('role') if identity else None
    return role
