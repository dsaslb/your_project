#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import hashlib
import os
import re
import secrets
import time
import uuid
from datetime import datetime, timedelta
from functools import wraps

import bleach
from flask import current_app, flash, redirect, request, session, url_for
from werkzeug.utils import secure_filename

from extensions import db
from models import ActionLog, User


def password_strong(password):
    """비밀번호 강도 체크"""
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    if not re.search(r"[A-Z]", password):
        return False, "비밀번호는 대문자를 포함해야 합니다."

    if not re.search(r"[a-z]", password):
        return False, "비밀번호는 소문자를 포함해야 합니다."

    if not re.search(r"\d", password):
        return False, "비밀번호는 숫자를 포함해야 합니다."

    if not re.search(r"[^A-Za-z0-9]", password):
        return False, "비밀번호는 특수문자를 포함해야 합니다."

    return True, "비밀번호가 안전합니다."


def validate_password_strength(password):
    """비밀번호 강도 검증 (기존 호환성)"""
    return password_strong(password)


def validate_username(username):
    """사용자명 유효성 검증"""
    if len(username) < 3:
        return False, "사용자명은 최소 3자 이상이어야 합니다."

    if len(username) > 20:
        return False, "사용자명은 최대 20자까지 가능합니다."

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        return False, "사용자명은 영문자, 숫자, 언더스코어만 사용 가능합니다."

    # 예약어 체크
    reserved_words = ["admin", "root", "system", "test", "guest", "user"]
    if username.lower() in reserved_words:
        return False, "사용할 수 없는 사용자명입니다."

    return True, "사용자명이 유효합니다."


def validate_email(email):
    """이메일 형식 검증"""
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def generate_secure_token():
    """보안 토큰 생성"""
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data):
    """민감한 데이터 해시화"""
    return hashlib.sha256(data.encode()).hexdigest()


def check_rate_limit(user_id, action, limit=5, window=300):
    """사용자별 요청 제한 확인"""
    try:
        from datetime import datetime, timedelta

        window_start = datetime.utcnow() - timedelta(seconds=window)

        recent_actions = ActionLog.query.filter(
            ActionLog.user_id == user_id,
            ActionLog.action == action,
            ActionLog.created_at >= window_start,
        ).count()

        return recent_actions < limit
    except Exception:
        return True  # 에러 시 제한하지 않음


def log_security_event(user_id, action, message, ip_address=None, user_agent=None):
    """보안 이벤트 로깅"""
    if not ip_address:
        ip_address = request.remote_addr if request else None
    if not user_agent:
        user_agent = request.headers.get("User-Agent") if request else None

    log = ActionLog(
        user_id=user_id,
        action=action,
        message=message,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.session.add(log)
    db.session.commit()


def sanitize_input(text):
    """입력값 정제"""
    if not text:
        return ""

    # XSS 방지를 위한 기본 정제
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    text = text.replace('"', "&quot;").replace("'", "&#x27;")

    return text.strip()


def validate_file_upload(filename, allowed_extensions=None):
    """파일 업로드 검증"""
    if not filename:
        return False, "파일이 선택되지 않았습니다."

    if allowed_extensions is None:
        allowed_extensions = {
            ".txt",
            ".pdf",
            ".doc",
            ".docx",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
        }

    import os

    file_ext = os.path.splitext(filename)[1].lower()

    if file_ext not in allowed_extensions:
        return False, f"허용되지 않는 파일 형식입니다: {file_ext}"

    return True, "파일이 유효합니다."


def get_client_ip():
    """클라이언트 IP 주소 가져오기"""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0]
    return request.remote_addr


def is_suspicious_activity(user_id, action_type):
    """의심스러운 활동 감지"""
    try:
        from datetime import datetime, timedelta

        recent_window = datetime.utcnow() - timedelta(minutes=5)

        # 최근 5분간의 동일한 액션 횟수 확인
        recent_actions = ActionLog.query.filter(
            ActionLog.user_id == user_id,
            ActionLog.action == action_type,
            ActionLog.created_at >= recent_window,
        ).count()

        # 임계값 초과 시 의심스러운 활동으로 판단
        if recent_actions > 10:
            return True

        return False
    except Exception:
        return False


def create_audit_trail(user_id, action, resource_type, resource_id, details=None):
    """감사 추적 기록 생성"""
    try:
        audit_log = ActionLog(
            user_id=user_id,
            action=action,
            message=(
                f"{resource_type}:{resource_id} - {details}"
                if details
                else f"{resource_type}:{resource_id}"
            ),
            ip_address=get_client_ip(),
            user_agent=request.headers.get("User-Agent") if request else None,
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Audit trail creation failed: {e}")


def check_account_lockout(user):
    """계정 잠금 상태 확인"""
    if user.is_locked:
        return True, "계정이 잠겼습니다. 관리자에게 문의하세요."

    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = user.locked_until - datetime.utcnow()
        minutes = int(remaining.total_seconds() // 60)
        return True, f"계정이 {minutes}분 후에 잠금 해제됩니다."

    return False, None


def handle_failed_login(user):
    """로그인 실패 처리"""
    user.failed_login += 1

    if user.failed_login >= 5:
        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
        log_security_event(
            user.id,
            "account_locked",
            f"계정 잠금: {user.failed_login}회 연속 로그인 실패",
        )

    db.session.commit()


def reset_login_attempts(user):
    """로그인 시도 초기화"""
    if user.failed_login > 0:
        user.failed_login = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()
        log_security_event(user.id, "login_success", "로그인 성공")


def validate_password(password):
    """비밀번호 유효성 검사 (간소화 버전)"""
    if len(password) < 6:
        return False, "비밀번호는 최소 6자 이상이어야 합니다."
    return True, ""


def hash_password(password):
    """비밀번호 해시화"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    """비밀번호 검증"""
    salt = hashed[:32]
    stored_hash = hashed[32:]
    hash_obj = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    )
    return hash_obj.hex() == stored_hash


def allowed_file(filename):
    """허용된 파일 확장자 확인 (강화된 버전)"""
    allowed_ext = {
        "jpg",
        "jpeg",
        "png",
        "gif",
        "webp",
        "txt",
        "md",
        "log",
        "csv",
        "pdf",
    }
    blocked_ext = {
        "exe",
        "js",
        "bat",
        "sh",
        "py",
        "php",
        "asp",
        "aspx",
        "jsp",
        "jar",
        "war",
        "ear",
    }

    if not filename or "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()

    if ext in blocked_ext:
        return False

    if ext not in allowed_ext:
        return False

    return True


def save_uploaded_file(file):
    """업로드된 파일을 안전하게 저장"""
    if not file or not file.filename:
        return None, "파일이 없습니다."

    if not allowed_file(file.filename):
        return None, "허용되지 않는 파일 형식입니다."

    filename = secure_filename(file.filename)

    # 고유한 파일명 생성
    unique_filename = f"{uuid.uuid4().hex}_{filename}"

    upload_folder = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_path = os.path.join(upload_folder, unique_filename)

    try:
        file.save(file_path)
        return file_path, None
    except Exception as e:
        return None, f"파일 저장 중 오류 발생: {e}"


def clean_comment(content):
    """댓글 내용 정제 (강화된 버전)"""
    if not isinstance(content, str):
        content = str(content)

    # 허용할 태그와 속성 정의 (더 엄격하게)
    allowed_tags = ["p", "br", "strong", "em", "u", "a", "ul", "ol", "li", "blockquote"]
    allowed_attrs = {"a": ["href", "title"]}

    # Bleach 라이브러리를 사용하여 HTML 정제
    cleaned_content = bleach.clean(
        content,
        tags=allowed_tags,
        attributes=allowed_attrs,
        strip=True,  # 허용되지 않은 태그를 제거
    )

    return cleaned_content


def sanitize_filename(filename):
    return secure_filename(filename)


def safe_remove(file_path):
    """파일을 안전하게 삭제"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        # 로깅 추가 가능
        return False
    return False


def validate_file_size(file, max_size_mb=10):
    """업로드 파일 크기 검증"""
    max_size_bytes = max_size_mb * 1024 * 1024

    # 파일 크기 확인을 위해 파일 포인터 이동
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0, os.SEEK_SET)  # 포인터 원위치

    if file_length > max_size_bytes:
        return False, f"파일 크기는 {max_size_mb}MB를 초과할 수 없습니다."

    return True, ""


def escape_html(text):
    """HTML 이스케이프 처리"""
    if not text:
        return ""
    import html

    return html.escape(text)


def admin_required(f):
    """관리자 권한 데코레이터"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            flash("로그인이 필요합니다.", "error")
            return redirect(url_for("login"))

        from models import User

        user = User.query.get(session["user_id"])
        if not user or user.role != "admin":
            flash("관리자만 접근 가능합니다.", "error")
            return redirect(url_for("dashboard"))

        return f(*args, **kwargs)

    return decorated_function


def rate_limit_exceeded(identifier, limit=5, window=300):
    """요청 제한 체크"""
    from extensions import cache

    key = f"rate_limit:{identifier}"
    current_count = cache.get(key, 0)

    if current_count >= limit:
        return True

    cache.set(key, current_count + 1, timeout=window)
    return False


def increment_failed_attempts(user_id):
    """로그인 실패 횟수 증가 (간소화 버전)"""
    # 실제로는 데이터베이스에 저장해야 함
    pass


def reset_failed_attempts(user_id):
    """로그인 실패 횟수 초기화 (간소화 버전)"""
    # 실제로는 데이터베이스에서 초기화해야 함
    pass


def validate_phone(phone):
    """전화번호 형식 검증"""
    pattern = r"^[0-9-+\s()]{10,15}$"
    return re.match(pattern, phone) is not None


def is_suspicious_request():
    """의심스러운 요청 감지"""
    user_agent = request.headers.get("User-Agent", "")

    # 봇이나 스크래퍼 감지
    suspicious_patterns = [
        "bot",
        "crawler",
        "spider",
        "scraper",
        "curl",
        "wget",
        "python-requests",
        "java",
        "perl",
        "ruby",
    ]

    for pattern in suspicious_patterns:
        if pattern.lower() in user_agent.lower():
            return True

    return False
