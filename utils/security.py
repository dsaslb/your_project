import hashlib
import os
import uuid
from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import Dict, Optional

from flask import flash, redirect, request, url_for
from werkzeug.utils import secure_filename

try:
    import bleach
except ImportError:
    bleach = None

# 필요한 모델들 import
try:
    from extensions import db
    from models import ActionLog, User
except ImportError:
    # 모델이 아직 로드되지 않은 경우를 위한 더미 클래스
    class DummyModel:
        pass

    User = ActionLog = DummyModel
    db = None

logger = logging.getLogger(__name__)

def password_strong(password):
    """비밀번호 강도 검사"""
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)

    score = sum([has_upper, has_lower, has_digit, has_special])

    if score < 3:
        return (
            False,
            "비밀번호는 대문자, 소문자, 숫자, 특수문자 중 3가지 이상을 포함해야 합니다.",
        )

    return True, "강력한 비밀번호입니다."


def validate_password_strength(password):
    """비밀번호 유효성 검사"""
    return password_strong(password)[0]


def validate_username(username):
    """사용자명 유효성 검사"""
    if not username or len(username) < 3:
        return False, "사용자명은 최소 3자 이상이어야 합니다."

    if len(username) > 20:
        return False, "사용자명은 최대 20자까지 가능합니다."

    # 특수문자 제한
    allowed_chars = set(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
    )
    if not all(c in allowed_chars for c in username):
        return (
            False,
            "사용자명에는 영문, 숫자, 언더스코어(_), 하이픈(-)만 사용 가능합니다.",
        )

    return True, "유효한 사용자명입니다."


def validate_email(email):
    """이메일 유효성 검사"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def generate_secure_token():
    """보안 토큰 생성"""
    return hashlib.sha256(os.urandom(32)).hexdigest()


def hash_sensitive_data(data):
    """민감한 데이터 해시화"""
    return hashlib.sha256(str(data).encode()).hexdigest()


def check_rate_limit(user_id, action, limit=5, window=300):
    """속도 제한 확인"""
    try:
        from datetime import datetime, timedelta

        recent_window = datetime.utcnow() - timedelta(seconds=window)

        recent_actions = ActionLog.query.filter(
            ActionLog.user_id == user_id,
            ActionLog.action == action,
            ActionLog.created_at >= recent_window,
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


def create_audit_trail(user_id: int, action: str, details: str, ip_address: str = None):
    """감사 로그 생성"""
    try:
        audit_log = {
            "user_id": user_id,
            "action": action,
            "details": details,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # 실제 구현에서는 데이터베이스에 저장
        log_action(user_id, f"AUDIT_{action}", details)
        
        return True
        
    except Exception as e:
        logger.error(f"Audit trail creation failed: {e}")
        return False


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
    if bleach:
        cleaned_content = bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True,  # 허용되지 않은 태그를 제거
        )
    else:
        # Bleach가 없는 경우 기본 정제
        cleaned_content = sanitize_input(content)

    return cleaned_content


def sanitize_filename(filename):
    """파일명 정제"""
    return secure_filename(filename)


def safe_remove(file_path):
    """파일 안전 삭제"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False


def validate_file_size(file, max_size_mb=10):
    """파일 크기 검증"""
    if not file:
        return False, "파일이 없습니다."

    # 파일 크기 확인 (바이트 단위)
    file.seek(0, 2)  # 파일 끝으로 이동
    file_size = file.tell()
    file.seek(0)  # 파일 시작으로 복귀

    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        return False, f"파일 크기가 {max_size_mb}MB를 초과합니다."

    return True, "파일 크기가 적절합니다."


def escape_html(text):
    """HTML 이스케이프"""
    if not text:
        return ""

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#x27;")
    )


def admin_required(f):
    """관리자 권한 데코레이터"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_login import current_user

        if not current_user.is_authenticated:
            flash("로그인이 필요합니다.", "error")
            return redirect(url_for("auth.login"))
        if not current_user.is_admin():
            flash("관리자 권한이 필요합니다.", "error")
            return redirect(url_for("index"))
        return f(*args, **kwargs)

    return decorated_function


def rate_limit_exceeded(identifier, limit=5, window=300):
    """속도 제한 초과 확인"""
    try:
        from datetime import datetime, timedelta

        recent_window = datetime.utcnow() - timedelta(seconds=window)

        recent_actions = ActionLog.query.filter(
            ActionLog.ip_address == identifier, ActionLog.created_at >= recent_window
        ).count()

        return recent_actions >= limit
    except Exception:
        return False


def increment_failed_attempts(user_id):
    """실패 시도 횟수 증가"""
    # 구현은 필요에 따라 추가
    pass


def reset_failed_attempts(user_id):
    """실패 시도 횟수 초기화"""
    # 구현은 필요에 따라 추가
    pass


def validate_phone(phone):
    """전화번호 유효성 검사"""
    import re

    pattern = r"^[0-9-+\s()]+$"
    return bool(re.match(pattern, phone)) if phone else True


def is_suspicious_request():
    """의심스러운 요청 감지"""
    if not request:
        return False

    # User-Agent 체크
    user_agent = request.headers.get("User-Agent", "")
    suspicious_agents = ["bot", "crawler", "spider", "scraper"]

    if any(agent in user_agent.lower() for agent in suspicious_agents):
        return True

    # 요청 빈도 체크
    client_ip = get_client_ip()
    if rate_limit_exceeded(client_ip, limit=10, window=60):
        return True

    return False
