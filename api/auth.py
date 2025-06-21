from flask import Blueprint, request, jsonify, current_app, render_template, redirect, url_for, flash
from werkzeug.security import check_password_hash, generate_password_hash
import jwt
import datetime

from models import User, db

api_auth_bp = Blueprint('api_auth', __name__, url_prefix='/api/auth')
auth_bp = Blueprint('auth', __name__)

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
        }, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"msg": "Could not generate token", "error": str(e)}), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """웹 로그인 페이지"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            return '사용자명과 비밀번호를 입력해주세요.'
        
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return '잘못된 사용자명 또는 비밀번호입니다.'
        
        # 로그인 성공 처리 (Flask-Login 사용)
        from flask_login import login_user
        login_user(user)
        return '로그인되었습니다. <a href="/dashboard">대시보드로 이동</a>'
    
    # CSRF 토큰 생성
    from flask_wtf.csrf import generate_csrf
    csrf_token = generate_csrf()
    
    return f'''
    <html>
    <head><title>로그인</title></head>
    <body>
        <h2>로그인</h2>
        <form method="POST">
            <input type="hidden" name="csrf_token" value="{csrf_token}"/>
            <p>사용자명: <input name="username" placeholder="사용자명" required></p>
            <p>비밀번호: <input name="password" type="password" placeholder="비밀번호" required></p>
            <button type="submit">로그인</button>
        </form>
        <p><a href="/register">회원가입</a></p>
    </body>
    </html>
    '''

@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    from flask_login import logout_user
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """회원가입 페이지"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        
        if not username or not password:
            flash('사용자명과 비밀번호를 입력해주세요.', 'error')
            return render_template('auth/register.html')
        
        # 중복 사용자명 확인
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자명입니다.', 'error')
            return render_template('auth/register.html')
        
        # 새 사용자 생성
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html') 