from models_main import User, db
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
import jwt
import datetime
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore

from extensions import csrf


api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")
security_auth_bp = Blueprint("security_auth", __name__, url_prefix="/api/security/auth")
auth_bp = Blueprint("auth", __name__)


# --- 자동 admin 계정 생성 및 초기화 ---
def ensure_admin_account():
    from extensions import db
    from werkzeug.security import generate_password_hash
    
    # users 테이블에서 admin 조회
    admin = db.session.execute(
        db.text("SELECT * FROM users WHERE username = 'admin'"),
    ).fetchone()
    
    if not admin:
        # 새 admin 사용자 생성
        password_hash = generate_password_hash("admin123", method="pbkdf2:sha256")
        db.session.execute(
            db.text("""
                INSERT INTO users (username, email, password_hash, role, status, created_at, updated_at)
                VALUES ('admin', 'admin@your_program.com', :password_hash, 'admin', 'approved', datetime('now'), datetime('now'))
            """),
            {"password_hash": password_hash}
        )
        db.session.commit()
        print("✅ Admin 계정이 생성되었습니다.")
    else:
        # 기존 admin 비밀번호 업데이트
        password_hash = generate_password_hash("admin123", method="pbkdf2:sha256")
        db.session.execute(
            db.text("UPDATE users SET password_hash = :password_hash, status = 'approved' WHERE username = 'admin'"),
            {"password_hash": password_hash}
        )
        db.session.commit()
        print("✅ Admin 계정이 업데이트되었습니다.")

# Flask 앱 생성 후에 호출
try:
    ensure_admin_account()
except Exception as e:
    print(f"[경고] admin 계정 자동 생성 실패: {e}")


@api_auth_bp.route("/login", methods=["POST"])
@csrf.exempt
def api_login():
    """
    사용자 로그인 API
    ---
    tags:
      - Auth
    summary: 사용자 인증 및 JWT 토큰 발급
    description: 사용자명과 비밀번호를 받아 인증 후 JWT 토큰을 반환합니다.
    """
    # 디버그: JWT_SECRET_KEY 값 출력
    secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
    print(f"DEBUG: JWT_SECRET_KEY = {secret_key}")
    print(f"DEBUG: current_app.config keys = {list(current_app.config.keys())}")

    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "사용자명과 비밀번호를 입력해주세요."}), 400

    # users 테이블에서 직접 조회
    from extensions import db
    user = db.session.execute(
        db.text("SELECT * FROM users WHERE username = :username"),
        {"username": data["username"]}
    ).fetchone()
    
    # User 객체로 변환
    if user:
        class UserObj:
            def __init__(self, row):
                self.id = row.id
                self.username = row.username
                self.email = row.email
                self.password_hash = row.password_hash
                self.role = row.role
                self.status = row.status
                self.branch_id = row.branch_id
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
            
            def check_password(self, password):
                from werkzeug.security import check_password_hash
                return check_password_hash(self.password_hash, password)
            
            def get_id(self):
                return str(self.id)
        
        user = UserObj(user)
    else:
        user = None
    if user:
        print("비밀번호 일치:", user.check_password(data["password"]))
    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "잘못된 사용자명 또는 비밀번호입니다."}), 401

    if user.status != "approved":
        return jsonify({"message": "승인 대기 중인 계정입니다."}), 401

    # JWT 토큰 생성
    secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')

    # 액세스 토큰 (1시간)
    access_token = jwt.encode(
        {
            'user_id': user.id,
            'username': user.username,
            'role': user.role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        },
        secret_key,
        algorithm='HS256'
    )

    # 리프레시 토큰 (7일)
    refresh_token = jwt.encode(
        {
            'user_id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
        },
        secret_key,
        algorithm='HS256'
    )

    # Flask-Login 세션도 설정 (웹 페이지 접근용)
    from flask_login import login_user
    login_user(user)

    # 사용자 정보 반환 (비밀번호 제외)
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "status": user.status,
        "branch_id": user.branch_id,
    }

    # 역할별 백엔드 대시보드로 리다이렉트
    if user.role == "super_admin":
        redirect_to = "/admin/backend"
    elif user.role == "admin":
        redirect_to = "/admin/backend"
    elif user.role == "brand_admin":
        redirect_to = "/admin/backend"
    elif user.role == "store_admin":
        redirect_to = "/admin/backend"
    elif user.role == "manager":
        redirect_to = "/admin/backend"
    else:
        redirect_to = "/admin/backend"

    # JWT access_token을 쿠키로 내려주기 (프론트엔드 인증 유지)
    from flask import make_response
    resp = make_response(jsonify({
        "message": "로그인 성공",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_data,
        "redirect_to": redirect_to,
        "success": True
    }))
    resp.set_cookie(
        "access_token",
        access_token,
        httponly=True,
        samesite='Lax',
        secure=False,
        path="/"
        # domain 옵션은 명시하지 않음 (자동으로 현재 접속 주소에 저장)
    )
    return resp


@security_auth_bp.route("/login", methods=["POST"])
def security_api_login():
    """
    보안 로그인 API (호환성을 위한 별칭)
    """
    return api_login()


@api_auth_bp.route("/refresh", methods=["POST"])
def api_refresh():
    """JWT 토큰 리프레시 API"""
    data = request.json
    if not data or not data.get("refresh_token"):
        return jsonify({"message": "리프레시 토큰이 필요합니다."}), 400

    try:
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
        payload = jwt.decode(data["refresh_token"], secret_key, algorithms=['HS256'])
        # users 테이블에서 사용자 조회
        from extensions import db
        user = db.session.execute(
            db.text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": payload['user_id']}
        ).fetchone()
        
        if user:
            class UserObj:
                def __init__(self, row):
                    self.id = row.id
                    self.username = row.username
                    self.email = row.email
                    self.role = row.role
                    self.status = row.status
                    self.branch_id = row.branch_id
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                
                def get_id(self):
                    return str(self.id)
            
            user = UserObj(user)
        else:
            user = None
        if not user:
            return jsonify({"message": "유효하지 않은 토큰입니다."}), 401

        # 새로운 액세스 토큰 생성
        access_token = jwt.encode(
            {
                'user_id': user.id,
                'username': user.username,
                'role': user.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            secret_key,
            algorithm='HS256'
        )

        return jsonify({
            "access_token": access_token,
            "message": "토큰이 갱신되었습니다."
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"message": "토큰이 만료되었습니다."}), 401
    except jwt.InvalidTokenError:
        return jsonify({"message": "유효하지 않은 토큰입니다."}), 401


@auth_bp.route("/login", methods=["GET", "POST"])
@csrf.exempt
def login():
    """웹 로그인 페이지"""
    if request.method == "POST":
        # JSON 요청인 경우 API 로그인으로 처리
        if request.is_json:
            return api_login()

        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            flash("사용자명과 비밀번호를 입력해주세요.", "error")
            return render_template("auth/login.html")

        # 테이블명이 'users'이므로 직접 쿼리
        from extensions import db
        user = db.session.execute(
            db.text("SELECT * FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
        
        # User 객체로 변환
        if user:
            class UserObj:
                def __init__(self, row):
                    self.id = row.id
                    self.username = row.username
                    self.email = row.email
                    self.password_hash = row.password_hash
                    self.role = row.role
                    self.status = row.status
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                
                def check_password(self, password):
                    from werkzeug.security import check_password_hash
                    return check_password_hash(self.password_hash, password)
                
                def get_id(self):
                    return str(self.id)
            
            user = UserObj(user)
        else:
            user = None

        if not user or not user.check_password(password):
            flash("잘못된 사용자명 또는 비밀번호입니다.", "error")
            return render_template("auth/login.html")

        # 로그인 성공 처리 (Flask-Login 사용)
        from flask_login import login_user

        print(f"DEBUG: 로그인 시도 - username: {user.username}, role: {user.role}, status: {user.status}")
        
        login_user(user)
        
        print(f"DEBUG: Flask-Login 완료 - user.is_authenticated: {user.is_authenticated}")

        # 역할별 백엔드 대시보드로 리다이렉트
        if user.role == "super_admin":
            redirect_to = "/dashboard"
        elif user.role == "admin":
            redirect_to = "/dashboard"
        elif user.role == "brand_admin":
            redirect_to = "/dashboard"
        elif user.role == "store_admin":
            redirect_to = "/dashboard"
        elif user.role == "manager":
            redirect_to = "/dashboard"
        else:
            redirect_to = "/dashboard"

        print(f"DEBUG: 리다이렉트 대상: {redirect_to}")

        # next 파라미터가 있으면 해당 페이지로, 없으면 역할별 페이지로
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            print(f"DEBUG: next 파라미터로 리다이렉트: {next_page}")
            return redirect(next_page)
        
        print(f"DEBUG: 최종 리다이렉트: {redirect_to}")
        return redirect(redirect_to)

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """로그아웃"""
    from flask_login import logout_user

    logout_user()
    flash("로그아웃되었습니다.", "info")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """회원가입 페이지"""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        if not username or not password:
            flash("사용자명과 비밀번호를 입력해주세요.", "error")
            return render_template("auth/register.html")

        # 중복 사용자명 확인 (users 테이블)
        from extensions import db
        existing_user = db.session.execute(
            db.text("SELECT username FROM users WHERE username = :username"),
            {"username": username}
        ).fetchone()
        
        if existing_user:
            flash("이미 존재하는 사용자명입니다.", "error")
            return render_template("auth/register.html")

        # 새 사용자 생성 (users 테이블에 직접 삽입)
        from werkzeug.security import generate_password_hash
        password_hash = generate_password_hash(password, method="pbkdf2:sha256")
        
        db.session.execute(
            db.text("""
                INSERT INTO users (username, email, password_hash, role, status, created_at, updated_at)
                VALUES (:username, :email, :password_hash, 'employee', 'approved', datetime('now'), datetime('now'))
            """),
            {
                "username": username,
                "email": email,
                "password_hash": password_hash
            }
        )
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@api_auth_bp.route("/quick_admin_login", methods=["POST"])
def api_quick_admin_login():
    """관리자(admin) 계정으로 바로 로그인 API (테스트/개발용)"""
    try:
        # admin 계정 확인 및 생성 (테이블명: users)
        from extensions import db
        admin = db.session.execute(
            db.text("SELECT * FROM users WHERE username = 'admin'"),
        ).fetchone()
        if not admin:
            # 새 admin 사용자 생성 (users 테이블에 직접 삽입)
            from werkzeug.security import generate_password_hash
            password_hash = generate_password_hash("admin123", method="pbkdf2:sha256")
            
            db.session.execute(
                db.text("""
                    INSERT INTO users (username, email, password_hash, role, status, created_at, updated_at)
                    VALUES ('admin', 'admin@your_program.com', :password_hash, 'admin', 'approved', datetime('now'), datetime('now'))
                """),
                {"password_hash": password_hash}
            )
            db.session.commit()
            
            # 생성된 admin 사용자 조회
            admin = db.session.execute(
                db.text("SELECT * FROM users WHERE username = 'admin'"),
            ).fetchone()
            db.session.commit()

        # JWT 토큰 생성
        secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')

        # 액세스 토큰 (1시간)
        access_token = jwt.encode(
            {
                'user_id': admin.id,
                'username': admin.username,
                'role': admin.role,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
            },
            secret_key,
            algorithm='HS256'
        )

        # 리프레시 토큰 (7일)
        refresh_token = jwt.encode(
            {
                'user_id': admin.id,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
            },
            secret_key,
            algorithm='HS256'
        )

        # 사용자 정보 반환 (비밀번호 제외)
        user_data = {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email,
            "role": admin.role,
            "status": admin.status,
            "branch_id": admin.branch_id,
        }

        return jsonify({
            "message": "관리자 로그인 성공",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data,
            "redirect_to": "/admin/backend"
        }), 200

    except Exception:
        return jsonify({"message": "로그인 실패가 발생했습니다."}), 500


@auth_bp.route("/quick_admin_login", methods=["POST", "GET"])
def quick_admin_login():
    """관리자(admin) 계정으로 바로 로그인 (테스트/개발용)"""
    from flask_login import login_user
    from extensions import db
    
    # users 테이블에서 admin 조회
    admin = db.session.execute(
        db.text("SELECT * FROM users WHERE username = 'admin'"),
    ).fetchone()
    
    if admin:
        # AdminUser 객체 생성
        class AdminUser:
            def __init__(self, row):
                self.id = row.id
                self.username = row.username
                self.email = row.email
                self.role = row.role
                self.status = row.status
                self.is_authenticated = True
                self.is_active = True
                self.is_anonymous = False
                
            def get_id(self):
                return str(self.id)
        
        admin_user = AdminUser(admin)
        login_user(admin_user)
        return redirect("/dashboard")
    else:
        return "Admin 사용자를 찾을 수 없습니다.", 404


@api_auth_bp.route("/profile", methods=["GET"])
def api_profile():
    """사용자 프로필 정보 조회 API"""
    try:
        # JWT 토큰에서 사용자 ID 추출
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "인증 토큰이 필요합니다."}), 401

        token = auth_header.split(' ')[1]
        secret_key = current_app.config.get('SECRET_KEY', 'default-secret-key')

        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "토큰이 만료되었습니다."}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "유효하지 않은 토큰입니다."}), 401

        # users 테이블에서 사용자 정보 조회
        from extensions import db
        user = db.session.execute(
            db.text("SELECT * FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if user:
            class UserObj:
                def __init__(self, row):
                    self.id = row.id
                    self.username = row.username
                    self.email = row.email
                    self.role = row.role
                    self.status = row.status
                    self.branch_id = row.branch_id
                    self.created_at = row.created_at
                    self.is_authenticated = True
                    self.is_active = True
                    self.is_anonymous = False
                
                def get_id(self):
                    return str(self.id)
            
            user = UserObj(user)
        else:
            user = None
        if not user:
            return jsonify({"message": "사용자를 찾을 수 없습니다."}), 404

        # 사용자 정보 반환 (비밀번호 제외)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status,
            "branch_id": user.branch_id,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }

        return jsonify(user_data), 200

    except Exception:
        return jsonify({"message": "프로필 조회 중 오류가 발생했습니다."}), 500


@api_auth_bp.route("/me", methods=["GET", "OPTIONS"])
def api_auth_me():
    """현재 로그인된 사용자 정보 반환 (JWT 토큰 기반)"""
    if request.method == "OPTIONS":
        # CORS preflight 요청에 대해 200 OK와 CORS 헤더 반환
        response = jsonify({"success": True, "message": "CORS preflight OK"})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get("Origin", "*"))
        response.headers.add("Access-Control-Allow-Credentials", "true")
        response.headers.add("Access-Control-Allow-Methods", "GET,OPTIONS")
        response.headers.add("Access-Control-Allow-Headers", request.headers.get("Access-Control-Request-Headers", "*"))
        return response, 200
    from api.utils import get_current_user
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "인증이 필요합니다."}), 401
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "name": getattr(user, "name", None),
        "role": user.role,
        "status": user.status,
        "branch_id": getattr(user, "branch_id", None),
        "created_at": user.created_at.isoformat() if hasattr(user, "created_at") and user.created_at else None,
        "last_login": user.last_login.isoformat() if hasattr(user, "last_login") and user.last_login else None,
    }
    return jsonify({"success": True, "data": user_data}), 200
