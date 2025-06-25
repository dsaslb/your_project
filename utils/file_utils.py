import os
import uuid
from werkzeug.utils import secure_filename
from datetime import datetime
import time
import zipfile

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

def delete_file(path):
    """파일을 삭제합니다."""
    return safe_remove(path)

def backup_files(source_dir, backup_dir):
    """파일들을 백업합니다."""
    try:
        if not os.path.exists(source_dir):
            return False
        
        os.makedirs(backup_dir, exist_ok=True)
        
        # 간단한 백업 로직 (실제로는 더 복잡할 수 있음)
        import shutil
        shutil.copytree(source_dir, backup_dir, dirs_exist_ok=True)
        return True
    except Exception:
        return False

def restore_files(backup_dir, target_dir):
    """백업된 파일들을 복원합니다."""
    try:
        if not os.path.exists(backup_dir):
            return False
        
        os.makedirs(target_dir, exist_ok=True)
        
        # 간단한 복원 로직 (실제로는 더 복잡할 수 있음)
        import shutil
        shutil.copytree(backup_dir, target_dir, dirs_exist_ok=True)
        return True
    except Exception:
        return False

def save_file(file):
    """파일을 저장합니다 (save_uploaded_file의 별칭)."""
    return save_uploaded_file(file)

def cleanup_old_backups(backup_dir, days=30):
    """지정한 일수보다 오래된 백업(.bak/.sqlite3/.zip) 파일 자동 삭제"""
    now = time.time()
    removed = []
    for fname in os.listdir(backup_dir):
        if not (fname.endswith('.bak') or fname.endswith('.sqlite3') or fname.endswith('.zip')):
            continue
        fpath = os.path.join(backup_dir, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > days * 86400:
                os.remove(fpath)
                removed.append(fname)
    return removed

def compress_backup_files(backup_dir, compress_after_days=3):
    """지정한 일수보다 오래된 백업 파일을 zip으로 압축 (원본 삭제)"""
    now = time.time()
    compressed = []
    for fname in os.listdir(backup_dir):
        if not (fname.endswith('.bak') or fname.endswith('.sqlite3')):
            continue
        fpath = os.path.join(backup_dir, fname)
        if os.path.isfile(fpath):
            if now - os.path.getmtime(fpath) > compress_after_days * 86400:
                zipname = fpath + '.zip'
                with zipfile.ZipFile(zipname, 'w', zipfile.ZIP_DEFLATED) as zf:
                    zf.write(fpath, arcname=fname)
                os.remove(fpath)
                compressed.append(zipname)
    return compressed

def send_backup_notification(success, admin_email, msg):
    """백업 성공/실패시 관리자에게 이메일 알림 (샘플)"""
    from utils.email_utils import send_email
    subject = '[백업 성공]' if success else '[백업 실패]'
    send_email(admin_email, subject, msg)

def upload_backup_to_cloud(filepath, bucket_name, key):
    """(샘플) AWS S3에 백업 파일 업로드"""
    try:
        import boto3
        s3 = boto3.client('s3')
        s3.upload_file(filepath, bucket_name, key)
        return True
    except Exception as e:
        print('S3 업로드 실패:', e)
        return False 