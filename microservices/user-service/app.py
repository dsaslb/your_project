"""
User Service
사용자 관리, 인증, 권한 관리 담당 마이크로서비스
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from typing import Dict, Any, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 설정
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DB_PATH = os.getenv('USER_DB_PATH', 'user_service.db')

def init_db():
    """데이터베이스 초기화"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 사용자 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'employee',
            branch_id TEXT,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 세션 테이블 생성
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("User Service 데이터베이스 초기화 완료")

def get_db_connection():
    """데이터베이스 연결"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'user-service',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """사용자 로그인"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'error': '사용자명과 비밀번호가 필요합니다'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 사용자 조회
        cursor.execute('SELECT * FROM users WHERE username = ? AND is_active = 1', (username,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user['password_hash'], password):
            conn.close()
            return jsonify({'error': '잘못된 사용자명 또는 비밀번호입니다'}), 401
        
        # JWT 토큰 생성
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'role': user['role'],
            'branch_id': user['branch_id'],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
        
        # 세션 저장
        expires_at = datetime.utcnow() + timedelta(hours=24)
        cursor.execute(
            'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
            (user['id'], token, expires_at)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'branch_id': user['branch_id']
            }
        })
        
    except Exception as e:
        logger.error(f"로그인 오류: {e}")
        return jsonify({'error': '로그인 처리 중 오류가 발생했습니다'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """사용자 로그아웃"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 세션 삭제
        cursor.execute('DELETE FROM sessions WHERE token = ?', (token,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '로그아웃되었습니다'})
        
    except Exception as e:
        logger.error(f"로그아웃 오류: {e}")
        return jsonify({'error': '로그아웃 처리 중 오류가 발생했습니다'}), 500

@app.route('/api/auth/verify', methods=['GET'])
def verify_token():
    """토큰 검증"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        
        # JWT 토큰 검증
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # 세션 확인
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM sessions WHERE token = ? AND expires_at > ?', 
                      (token, datetime.utcnow()))
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return jsonify({'error': '유효하지 않은 세션입니다'}), 401
        
        return jsonify({
            'valid': True,
            'user': {
                'id': payload['user_id'],
                'username': payload['username'],
                'role': payload['role'],
                'branch_id': payload['branch_id']
            }
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': '토큰이 만료되었습니다'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': '유효하지 않은 토큰입니다'}), 401
    except Exception as e:
        logger.error(f"토큰 검증 오류: {e}")
        return jsonify({'error': '토큰 검증 중 오류가 발생했습니다'}), 500

@app.route('/api/users', methods=['GET'])
def get_users():
    """사용자 목록 조회"""
    try:
        # 권한 확인 (관리자만)
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        if payload['role'] not in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 쿼리 파라미터
        role = request.args.get('role')
        branch_id = request.args.get('branch_id')
        is_active = request.args.get('is_active')
        
        query = 'SELECT id, username, email, role, branch_id, is_active, created_at FROM users WHERE 1=1'
        params = []
        
        if role:
            query += ' AND role = ?'
            params.append(role)
        
        if branch_id:
            query += ' AND branch_id = ?'
            params.append(branch_id)
        
        if is_active is not None:
            query += ' AND is_active = ?'
            params.append(is_active == 'true')
        
        cursor.execute(query, params)
        users = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'users': [dict(user) for user in users]
        })
        
    except Exception as e:
        logger.error(f"사용자 목록 조회 오류: {e}")
        return jsonify({'error': '사용자 목록 조회 중 오류가 발생했습니다'}), 500

@app.route('/api/users', methods=['POST'])
def create_user():
    """사용자 생성"""
    try:
        # 권한 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        if payload['role'] not in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        role = data.get('role', 'employee')
        branch_id = data.get('branch_id')
        
        if not all([username, email, password]):
            return jsonify({'error': '필수 필드가 누락되었습니다'}), 400
        
        # 비밀번호 해시화
        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, branch_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, branch_id))
            
            user_id = cursor.lastrowid
            conn.commit()
            
            return jsonify({
                'message': '사용자가 생성되었습니다',
                'user_id': user_id
            }), 201
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return jsonify({'error': '이미 존재하는 사용자명 또는 이메일입니다'}), 409
        finally:
            conn.close()
        
    except Exception as e:
        logger.error(f"사용자 생성 오류: {e}")
        return jsonify({'error': '사용자 생성 중 오류가 발생했습니다'}), 500

@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """사용자 정보 수정"""
    try:
        # 권한 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # 본인 또는 관리자만 수정 가능
        if payload['user_id'] != user_id and payload['role'] not in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 업데이트할 필드 구성
        update_fields = []
        params = []
        
        if 'email' in data:
            update_fields.append('email = ?')
            params.append(data['email'])
        
        if 'role' in data and payload['role'] in ['admin', 'super_admin']:
            update_fields.append('role = ?')
            params.append(data['role'])
        
        if 'branch_id' in data:
            update_fields.append('branch_id = ?')
            params.append(data['branch_id'])
        
        if 'is_active' in data and payload['role'] in ['admin', 'super_admin']:
            update_fields.append('is_active = ?')
            params.append(data['is_active'])
        
        if update_fields:
            update_fields.append('updated_at = CURRENT_TIMESTAMP')
            params.append(user_id)
            
            query = f'UPDATE users SET {", ".join(update_fields)} WHERE id = ?'
            cursor.execute(query, params)
            conn.commit()
        
        conn.close()
        
        return jsonify({'message': '사용자 정보가 업데이트되었습니다'})
        
    except Exception as e:
        logger.error(f"사용자 수정 오류: {e}")
        return jsonify({'error': '사용자 수정 중 오류가 발생했습니다'}), 500

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """사용자 삭제 (비활성화)"""
    try:
        # 권한 확인
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': '인증 토큰이 필요합니다'}), 401
        
        token = auth_header.split(' ')[1]
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        if payload['role'] not in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다'}), 403
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET is_active = 0 WHERE id = ?', (user_id,))
        conn.commit()
        conn.close()
        
        return jsonify({'message': '사용자가 비활성화되었습니다'})
        
    except Exception as e:
        logger.error(f"사용자 삭제 오류: {e}")
        return jsonify({'error': '사용자 삭제 중 오류가 발생했습니다'}), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('USER_SERVICE_PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True) 