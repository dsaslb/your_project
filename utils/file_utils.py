import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime

# 최대 파일 크기 (1MB)
MAX_PREVIEW_SIZE = 1024 * 1024

def save_uploaded_file(file):
    """업로드된 파일을 저장하고 경로를 반환합니다."""
    if not file:
        return ""
    
    # 파일명 보안 처리
    filename = secure_filename(file.filename)
    
    # 고유한 파일명 생성
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = str(uuid.uuid4())[:8]
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{timestamp}_{unique_id}{ext}"
    
    # 업로드 디렉토리 생성
    upload_dir = os.path.join('static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    
    # 파일 저장
    file_path = os.path.join(upload_dir, new_filename)
    file.save(file_path)
    
    return file_path

def safe_remove(path):
    """파일을 안전하게 삭제합니다."""
    try:
        if path and os.path.exists(path):
            os.remove(path)
            return True
    except Exception:
        pass
    return False

def get_file_size(file_path):
    """파일 크기를 반환합니다."""
    try:
        return os.path.getsize(file_path)
    except:
        return 0

def is_valid_file_type(filename, allowed_extensions):
    """파일 확장자가 허용된 형식인지 확인합니다."""
    if not filename:
        return False
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions 