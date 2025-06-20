from functools import wraps
from flask import request, jsonify
import jwt

from models import User
from config import DevConfig

def token_required(f):
    """Decorator to protect routes with JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, DevConfig.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401
        
        if current_user is None:
            return jsonify({'message': 'User not found!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated 

def admin_required(f):
    """Decorator to protect routes with admin-only JWT authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].replace('Bearer ', '')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, DevConfig.SECRET_KEY, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
        except Exception:
            return jsonify({'message': 'Token is invalid!'}), 401

        if current_user is None or not current_user.is_admin():
            return jsonify({'message': 'Admin privileges required!'}), 403

        return f(current_user, *args, **kwargs)

    return decorated 