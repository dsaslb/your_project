from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash
import jwt
import datetime

from models import User, db
from config import DevConfig

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')

@api_auth_bp.route('/login', methods=['POST'])
def api_login():
    """
    User login API endpoint.
    Receives username and password, returns JWT token upon success.
    """
    data = request.json
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({"msg": "Username and password are required"}), 400

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({"msg": "Invalid credentials"}), 401

    try:
        token = jwt.encode({
            'user_id': user.id,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, DevConfig.SECRET_KEY, algorithm='HS256')

        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"msg": "Could not generate token", "error": str(e)}), 500 