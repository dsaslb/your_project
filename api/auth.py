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
    사용자 로그인 API
    ---
    tags:
      - Auth
    summary: 사용자 인증 및 JWT 토큰 발급
    description: 사용자명과 비밀번호를 받아 인증 후 JWT 토큰을 반환합니다.
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: 사용자명
              example: "admin"
            password:
              type: string
              description: 비밀번호
              example: "password123"
    responses:
      200:
        description: 로그인 성공
        schema:
          type: object
          properties:
            token:
              type: string
              description: JWT 토큰
              example: "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
      400:
        description: 잘못된 요청
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Username and password are required"
      401:
        description: 인증 실패
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Invalid credentials"
      500:
        description: 서버 오류
        schema:
          type: object
          properties:
            msg:
              type: string
              example: "Could not generate token"
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