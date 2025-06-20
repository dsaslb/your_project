import re
import hashlib
import secrets
from datetime import datetime, timedelta
from flask import request, session
from extensions import db
from models import User, ActionLog
import os
import uuid
import bleach
from werkzeug.utils import secure_filename

def password_strong(password):
    """비밀번호 강도 검증 (강화된 버전)"""
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."
    
    if not re.search(r'[A-Z]', password):
        return False, "비밀번호는 대문자를 포함해야 합니다."
    
    if not re.search(r'[a-z]', password):
        return False, "비밀번호는 소문자를 포함해야 합니다."
    
    if not re.search(r'\d', password):
        return False, "비밀번호는 숫자를 포함해야 합니다."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호는 특수문자를 포함해야 합니다."
    
    # 연속된 문자나 숫자 체크
    if re.search(r'(.)\1{2,}', password):
        return False, "비밀번호에 연속된 같은 문자가 3개 이상 포함될 수 없습니다."
    
    # 키보드 패턴 체크
    keyboard_patterns = ['qwerty', 'asdfgh', 'zxcvbn', '123456', 'abcdef']
    password_lower = password.lower()
    for pattern in keyboard_patterns:
        if pattern in password_lower:
            return False, "비밀번호에 키보드 패턴이 포함될 수 없습니다."
    
    return True, "비밀번호가 유효합니다."

def validate_password_strength(password):
    """비밀번호 강도 검증 (기존 호환성)"""
    return password_strong(password)

def validate_username(username):
    """사용자명 유효성 검증"""
    if len(username) < 3:
        return False, "사용자명은 최소 3자 이상이어야 합니다."
    
    if len(username) > 20:
        return False, "사용자명은 최대 20자까지 가능합니다."
    
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "사용자명은 영문자, 숫자, 언더스코어만 사용 가능합니다."
    
    # 예약어 체크
    reserved_words = ['admin', 'root', 'system', 'test', 'guest', 'user']
    if username.lower() in reserved_words:
        return False, "사용할 수 없는 사용자명입니다."
    
    return True, "사용자명이 유효합니다."

def validate_email(email):
    """이메일 유효성 검증"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "유효한 이메일 주소를 입력해주세요."
    return True, "이메일이 유효합니다."

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
            ActionLog.created_at >= window_start
        ).count()
        
        return recent_actions < limit
    except Exception:
        return True  # 에러 시 제한하지 않음

def log_security_event(user_id, event_type, details=None, ip_address=None):
    """보안 이벤트 로깅"""
    try:
        if not ip_address:
            ip_address = request.remote_addr if request else None
        
        action_log = ActionLog(
            user_id=user_id,
            action=f'SECURITY_{event_type}',
            message=details,
            ip_address=ip_address,
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(action_log)
        db.session.commit()
    except Exception as e:
        print(f"Security logging failed: {e}")

def sanitize_input(input_string):
    """사용자 입력 데이터 정제"""
    if not input_string:
        return ""
    
    # HTML 태그 제거
    import html
    sanitized = html.escape(input_string)
    
    # 추가적인 정제 작업
    sanitized = re.sub(r'<script.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'<.*?>', '', sanitized)
    
    # SQL 인젝션 패턴 제거
    sql_patterns = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+)',
        r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\')',
        r'(\b(OR|AND)\b\s+\d+\s*=\s*\d+\s*--)',
        r'(\b(OR|AND)\b\s+\'[^\']*\'\s*=\s*\'[^\']*\'--)',
    ]
    
    for pattern in sql_patterns:
        sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
    
    return sanitized.strip()

def validate_file_upload(file, allowed_extensions=None, max_size=None):
    """파일 업로드 유효성 검증"""
    if not file:
        return False, "파일이 선택되지 않았습니다."
    
    if allowed_extensions:
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if file_ext not in allowed_extensions:
            return False, f"허용되지 않는 파일 형식입니다. 허용: {', '.join(allowed_extensions)}"
    
    if max_size:
        file.seek(0, 2)  # 파일 끝으로 이동
        file_size = file.tell()
        file.seek(0)  # 파일 시작으로 복귀
        
        if file_size > max_size:
            return False, f"파일 크기가 너무 큽니다. 최대: {max_size // (1024*1024)}MB"
    
    return True, "파일이 유효합니다."

def get_client_ip():
    """클라이언트 IP 주소 가져오기 (프록시 고려)"""
    if request:
        # X-Forwarded-For 헤더 확인 (프록시 환경)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # X-Real-IP 헤더 확인
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip
        
        return request.remote_addr
    return None

def is_suspicious_activity(user_id, action_type):
    """의심스러운 활동 감지"""
    try:
        from datetime import datetime, timedelta
        recent_window = datetime.utcnow() - timedelta(minutes=5)
        
        # 최근 5분간의 동일한 액션 횟수 확인
        recent_actions = ActionLog.query.filter(
            ActionLog.user_id == user_id,
            ActionLog.action == action_type,
            ActionLog.created_at >= recent_window
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
            message=f"{resource_type}:{resource_id} - {details}" if details else f"{resource_type}:{resource_id}",
            ip_address=get_client_ip(),
            user_agent=request.headers.get('User-Agent') if request else None
        )
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        print(f"Audit trail creation failed: {e}")

def check_account_lockout(user):
    """계정 잠금 확인"""
    if hasattr(user, 'locked_until') and user.locked_until:
        if user.locked_until > datetime.utcnow():
            return True, f"계정이 잠겨있습니다. {user.locked_until.strftime('%H:%M:%S')}까지 대기하세요."
    return False, None

def increment_failed_attempts(user):
    """로그인 실패 횟수 증가"""
    if not hasattr(user, 'login_attempts'):
        user.login_attempts = 0
    
    user.login_attempts += 1
    
    # 5회 실패 시 30분 잠금
    if user.login_attempts >= 5:
        user.locked_until = datetime.utcnow() + timedelta(minutes=30)
    
    db.session.commit()

def reset_failed_attempts(user):
    """로그인 실패 횟수 초기화"""
    if hasattr(user, 'login_attempts'):
        user.login_attempts = 0
    if hasattr(user, 'locked_until'):
        user.locked_until = None
    db.session.commit()

def allowed_file(filename):
    """허용된 파일 확장자 확인 (강화된 버전)"""
    allowed_ext = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'txt', 'md', 'log', 'csv', 'pdf'}
    blocked_ext = {'exe', 'js', 'bat', 'sh', 'py', 'php', 'asp', 'aspx', 'jsp', 'jar', 'war', 'ear'}
    
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[-1].lower()
    return ext in allowed_ext and ext not in blocked_ext

def save_uploaded_file(file):
    """안전한 파일 업로드 처리 (UUID 기반)"""
    if not file or not file.filename:
        raise ValueError("파일이 선택되지 않았습니다.")
    
    if not allowed_file(file.filename):
        raise ValueError("허용되지 않는 파일 형식입니다.")
    
    # 파일 크기 검증
    if not validate_file_size(file, MAX_FILE_SIZE_MB):
        raise ValueError(f"파일 크기가 너무 큽니다. 최대 {MAX_FILE_SIZE_MB}MB까지 가능합니다.")
    
    # UUID 기반 파일명 생성
    ext = file.filename.rsplit('.', 1)[-1].lower()
    new_filename = f"{uuid.uuid4().hex}.{ext}"
    
    # 업로드 디렉토리 생성
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 파일 저장
    save_path = os.path.join(upload_dir, new_filename)
    file.save(save_path)
    
    return os.path.join('uploads', new_filename), ext

def clean_comment(content):
    """댓글 XSS 방지 필터링 (강화된 버전)"""
    if not content:
        return ""
    
    # HTML 태그 제거
    cleaned = bleach.clean(content, tags=[], attributes={}, styles=[], strip=True)
    
    # 추가적인 정제 작업
    cleaned = re.sub(r'<script.*?</script>', '', cleaned, flags=re.IGNORECASE | re.DOTALL)
    cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'on\w+\s*=', '', cleaned, flags=re.IGNORECASE)
    
    return cleaned.strip()

def sanitize_filename(filename):
    """파일명 안전화"""
    return secure_filename(filename)

def safe_remove(file_path):
    """안전한 파일 삭제"""
    if not file_path:
        return
    
    try:
        full_path = os.path.join('static', file_path)
        if os.path.exists(full_path):
            os.remove(full_path)
            print(f"파일 삭제 완료: {full_path}")
    except Exception as e:
        print(f"파일 삭제 실패: {e}")

def validate_file_size(file, max_size_mb=10):
    """파일 크기 검증"""
    if not file:
        return False
    
    file.seek(0, 2)  # 파일 끝으로 이동
    size = file.tell()
    file.seek(0)  # 파일 시작으로 복귀
    
    max_size_bytes = max_size_mb * 1024 * 1024
    return size <= max_size_bytes

def escape_html(text):
    """HTML 이스케이프"""
    if not text:
        return ""
    
    html_escape_table = {
        "&": "&amp;",
        '"': "&quot;",
        "'": "&#39;",
        ">": "&gt;",
        "<": "&lt;",
    }
    
    return "".join(html_escape_table.get(c, c) for c in text)

# 상수 정의
MAX_FILE_SIZE_MB = 10
MAX_PREVIEW_SIZE = 1024 * 10  # 10KB 