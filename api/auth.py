import datetime
import secrets

import jwt
from flask import (Blueprint, current_app, flash, jsonify, redirect,
                   render_template, request, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

from models import User, db

api_auth_bp = Blueprint("api_auth", __name__, url_prefix="/api/auth")
auth_bp = Blueprint("auth", __name__)


@api_auth_bp.route("/login", methods=["POST"])
def api_login():
    """
    사용자 로그인 API
    ---
    tags:
      - Auth
    summary: 사용자 인증 및 세션 로그인
    description: 사용자명과 비밀번호를 받아 인증 후 사용자 정보를 반환합니다.
    """
    data = request.json
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"message": "사용자명과 비밀번호를 입력해주세요."}), 400

    user = User.query.filter_by(username=data["username"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"message": "잘못된 사용자명 또는 비밀번호입니다."}), 401

    if user.status != "approved":
        return jsonify({"message": "승인 대기 중인 계정입니다."}), 401

    # Flask-Login으로 세션 로그인
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

    return jsonify({
        "message": "로그인 성공",
        "user": user_data
    }), 200


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """웹 로그인 페이지"""
    if request.method == "POST":
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

        # next 파라미터가 있으면 해당 페이지로, 없으면 대시보드로
        next_page = request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard"))

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
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("회원가입이 완료되었습니다. 로그인해주세요.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")
