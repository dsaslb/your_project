from flask import Blueprint, request, jsonify, g
from datetime import datetime, timedelta
from functools import wraps
import jwt
import re
import html
import uuid

security_bp = Blueprint('security_enhanced', __name__, url_prefix='/api/security')

# 간단한 설정
SECRET_KEY = 'your-secret-key'
JWT_EXPIRATION = 3600
RATE_LIMIT = 100
WINDOW_SECONDS = 60

# 메모리 기반 레이트리밋
rate_limit_data = {}

def rate_limiter(ip):
    now = datetime.utcnow()
    info = rate_limit_data.get(ip)
    if not info or (now - info['start']).total_seconds() > WINDOW_SECONDS:
        rate_limit_data[ip] = {'count': 1, 'start': now}
        return True
    if info['count'] >= RATE_LIMIT:
        return False
    info['count'] += 1
    return True

def validate_input(data):
    if isinstance(data, str):
        if len(data) > 1000:
            return False
        if re.search(r'<script.*?>.*?</script>', data, re.IGNORECASE):
            return False
    if isinstance(data, dict):
        return all(validate_input(v) for v in data.values())
    if isinstance(data, list):
        return all(validate_input(item) for item in data)
    return True

def security_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        ip = request.remote_addr or 'unknown'
        if not rate_limiter(ip):
            return jsonify({'error': 'Too many requests'}), 429
        if request.is_json:
            data = request.get_json()
            if not validate_input(data):
                return jsonify({'error': 'Invalid input'}), 400
        auth = request.headers.get('Authorization')
        if auth and auth.startswith('Bearer '):
            token = auth.split(' ')[1]
            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                g.user_id = payload.get('user_id')
            except Exception:
                return jsonify({'error': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

@security_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    if email == 'admin@example.com' and password == 'password':
        payload = {
            'user_id': 1,
            'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4())
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
        return jsonify({'success': True, 'token': token})
    return jsonify({'error': 'Invalid credentials'}), 401

@security_bp.route('/protected', methods=['GET'])
@security_required
def protected():
    return jsonify({'success': True, 'user_id': getattr(g, 'user_id', None)}) 