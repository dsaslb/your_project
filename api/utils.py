from models_main import User
from flask import current_app, jsonify, request
import jwt
from functools import wraps
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore


def token_required(f):
    """Decorator to protect routes with JWT authentication."""

    @wraps(f)
    def decorated(*args,  **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.filter_by(id=data["user_id"]).first()
        except Exception:
            return jsonify({"message": "Token is invalid!"}), 401

        if current_user is None:
            return jsonify({"message": "User not found!"}), 401

        return f(current_user, *args, **kwargs)

    return decorated


def admin_required(f):
    """Decorator to protect routes with admin-only JWT authentication."""

    @wraps(f)
    def decorated(*args,  **kwargs):
        token = None
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].replace("Bearer ", "")

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            data = jwt.decode(
                token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"]
            )
            current_user = User.query.filter_by(id=data["user_id"]).first()
        except Exception:
            return jsonify({"message": "Token is invalid!"}), 401

        if current_user is None or not current_user.is_admin():
            return jsonify({"message": "Admin privileges required!"}), 403

        return f(current_user, *args, **kwargs)

    return decorated


def get_current_user():
    """현재 사용자 조회"""
    import jwt
    from flask import current_app

    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header

    if not token:
        return None

    try:
        jwt_secret = str(current_app.config.get("JWT_SECRET_KEY") or "your-secret-key")
        data = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if not data or "user_id" not in data:
            return None
        current_user = User.query.filter_by(id=data["user_id"]).first()
        return current_user
    except:
        return None
