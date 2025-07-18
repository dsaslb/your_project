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

    user = User.query.filter_by(username=data["username"]).first()
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

    # 역할별 리다이렉트 페이지 결정 (프론트엔드 Next.js 앱으로 리다이렉트)
    redirect_to = "http://192.168.45.44:3000/dashboard"  # 기본값
    if user.role == "admin":
        redirect_to = "http://192.168.45.44:3000/admin-dashboard"
    elif user.role == "brand_admin":
        redirect_to = "http://192.168.45.44:3000/brand-dashboard"
    elif user.role == "store_admin":
        redirect_to = "http://192.168.45.44:3000/store-dashboard"
    elif user.role == "employee":
        redirect_to = "http://192.168.45.44:3000/employee-dashboard"

    return jsonify({
        "message": "로그인 성공",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": user_data,
        "redirect_to": redirect_to,
        "success": True
    }), 200


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
        user = User.query.get(payload['user_id'])
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

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash("잘못된 사용자명 또는 비밀번호입니다.", "error")
            return render_template("auth/login.html")

        # 로그인 성공 처리 (Flask-Login 사용)
        from flask_login import login_user

        login_user(user)

        # 역할별 리다이렉트 페이지 결정 (프론트엔드 Next.js 앱으로 리다이렉트)
        redirect_to = "http://192.168.45.44:3000/dashboard"  # 기본값
        if user.role == "admin":
            redirect_to = "http://192.168.45.44:3000/admin-dashboard"
        elif user.role == "brand_admin":
            redirect_to = "http://192.168.45.44:3000/brand-dashboard"
        elif user.role == "store_admin":
            redirect_to = "http://192.168.45.44:3000/store-dashboard"
        elif user.role == "employee":
            redirect_to = "http://192.168.45.44:3000/employee-dashboard"

        # next 파라미터가 있으면 해당 페이지로, 없으면 역할별 페이지로
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
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

        # 중복 사용자명 확인
        if User.query.filter_by(username=username).first():
            flash("이미 존재하는 사용자명입니다.", "error")
            return render_template("auth/register.html")

        # 새 사용자 생성
        user = User()
        user.username = username
        user.email = email
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@api_auth_bp.route("/quick_admin_login", methods=["POST"])
def api_quick_admin_login():
    """관리자(admin) 계정으로 바로 로그인 API (테스트/개발용)"""
    try:
        # admin 계정 확인 및 생성
        admin = User.query.filter_by(username="admin").first()
        if not admin:
            admin = User()
            admin.username = "admin"
            admin.role = "super_admin"
            admin.status = "approved"
            admin.set_password("admin123")
            db.session.add(admin)
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
            "redirect_to": "/admin-dashboard"
        }), 200

    except Exception:
        return jsonify({"message": "로그인 실패가 발생했습니다."}), 500


@auth_bp.route("/quick_admin_login", methods=["POST", "GET"])
def quick_admin_login():
    """관리자(admin) 계정으로 바로 로그인 (테스트/개발용)"""
    from flask_login import login_user
    from models_main import User, db
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User()
        admin.username = "admin"
        admin.role = "admin"
        admin.status = "approved"
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
    login_user(admin)
    return redirect(url_for("dashboard"))


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

        # 사용자 정보 조회
        user = User.query.get(user_id)
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
