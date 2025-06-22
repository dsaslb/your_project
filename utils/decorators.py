from functools import wraps
from flask import abort, session, flash, redirect, url_for, request
from flask_login import current_user
import os
import logging

# 로거 설정
logger = logging.getLogger(__name__)

def owner_or_admin(obj_getter):
    """소유자 또는 관리자 권한 확인 데코레이터"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                obj = obj_getter(*args, **kwargs)
                if not obj:
                    abort(404)
                
                # 현재 사용자 확인
                if not current_user.is_authenticated:
                    flash('로그인이 필요합니다.', 'warning')
                    return redirect(url_for('login'))
                
                # 소유자 또는 관리자 권한 확인
                is_owner = False
                if hasattr(obj, 'user_id'):
                    is_owner = obj.user_id == current_user.id
                elif hasattr(obj, 'author_id'):
                    is_owner = obj.author_id == current_user.id
                
                is_admin = current_user.is_admin() or current_user.is_manager()
                
                if not (is_owner or is_admin):
                    logger.warning(f'Unauthorized access attempt: {current_user.id} -> {request.endpoint}')
                    flash('접근 권한이 없습니다.', 'error')
                    abort(403)
                
                return f(*args, **kwargs)
                
            except Exception as e:
                logger.error(f'Permission check error: {e}')
                flash('권한 확인 중 오류가 발생했습니다.', 'error')
                abort(500)
                
        return wrapper
    return decorator

def admin_required(f):
    """관리자 권한 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        
        if not (current_user.is_admin() or current_user.is_manager()):
            logger.warning(f'Admin access denied: {current_user.id} -> {request.endpoint}')
            flash("관리자 권한이 필요합니다.", 'error')
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function

def require_perm(permission):
    """지정된 권한을 확인하는 데코레이터. 현재는 is_admin으로만 동작."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('로그인이 필요합니다.', 'warning')
                return redirect(url_for('login'))
            
            # TODO: 추후 User 모델에 세분화된 권한 시스템 도입 시 아래 로직 수정
            # 예: if not current_user.has_permission(permission):
            if not current_user.is_admin:
                flash('이 작업을 수행할 권한이 없습니다.', 'error')
                return redirect(request.referrer or url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def login_required(f):
    """로그인 확인 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('로그인이 필요합니다.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 파일 보안 함수들
def allowed_file(filename):
    """허용된 파일 확장자 확인"""
    allowed_ext = {
        'jpg', 'jpeg', 'png', 'gif', 'webp',  # 이미지
        'txt', 'md', 'log', 'csv', 'pdf',     # 문서
        'doc', 'docx', 'xls', 'xlsx',         # 오피스 문서
        'zip', 'rar'                          # 압축파일
    }
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_ext

def safe_remove(file_path):
    """안전한 파일 삭제"""
    if file_path and os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f'File deleted successfully: {file_path}')
            return True
        except Exception as e:
            logger.error(f"파일 삭제 실패: {file_path} / {e}")
            return False
    return False

def get_file_size_mb(file_path):
    """파일 크기 MB 단위로 반환"""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0

def validate_file_size(file, max_size_mb=10):
    """파일 크기 검증"""
    if file:
        file.seek(0, 2)  # 파일 끝으로 이동
        size_mb = file.tell() / (1024 * 1024)
        file.seek(0)  # 파일 시작으로 복귀
        return size_mb <= max_size_mb
    return True

def sanitize_filename(filename):
    """파일명 안전화"""
    import re
    # 특수문자 제거 및 공백을 언더스코어로 변경
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    return filename.strip('_')

# XSS 방어 함수
def escape_html(text):
    """HTML 특수문자 이스케이프"""
    import html
    return html.escape(text)

# 미리보기 관련 상수
MAX_PREVIEW_SIZE = 5000  # 미리보기 최대 바이트 제한
MAX_FILE_SIZE_MB = 10    # 최대 파일 크기 (MB) 