import logging
import logging.handlers
import os
from datetime import datetime
from flask import request, session
from extensions import db
from models import ActionLog
import time
import shutil
import gzip

def setup_logger(app=None):
    """애플리케이션 로거 설정"""
    if app:
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        log_file = app.config.get('LOG_FILE', 'logs/restaurant.log')
        max_bytes = app.config.get('LOG_MAX_BYTES', 10 * 1024 * 1024)  # 10MB
        backup_count = app.config.get('LOG_BACKUP_COUNT', 5)
    else:
        log_level = logging.INFO
        log_file = 'logs/restaurant.log'
        max_bytes = 10 * 1024 * 1024
        backup_count = 5

    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 로거 설정
    logger = logging.getLogger('restaurant')
    logger.setLevel(log_level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러 (로테이션)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes, 
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][%(name)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def setup_security_logger():
    """보안 전용 로거 설정"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for handler in security_logger.handlers[:]:
        security_logger.removeHandler(handler)

    # 보안 로그 파일 핸들러 (일별 로테이션)
    security_handler = logging.handlers.TimedRotatingFileHandler(
        'logs/security.log',
        when='midnight',
        interval=1,
        backupCount=30,  # 30일간 보관
        encoding='utf-8'
    )
    security_handler.setLevel(logging.INFO)

    # 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][SECURITY] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    security_handler.setFormatter(formatter)

    security_logger.addHandler(security_handler)
    return security_logger

def setup_error_logger():
    """에러 전용 로거 설정"""
    log_dir = 'logs'
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    error_logger = logging.getLogger('error')
    error_logger.setLevel(logging.ERROR)

    # 기존 핸들러 제거
    for handler in error_logger.handlers[:]:
        error_logger.removeHandler(handler)

    # 에러 로그 파일 핸들러
    error_handler = logging.handlers.RotatingFileHandler(
        'logs/error.log',
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)

    # 포맷터
    formatter = logging.Formatter(
        '[%(asctime)s][%(levelname)s][ERROR] %(message)s\n%(pathname)s:%(lineno)d\n',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    error_handler.setFormatter(formatter)

    error_logger.addHandler(error_handler)
    return error_logger

def log_action(user_id, action, message=None, ip_address=None):
    """사용자 액션 로깅"""
    logger = logging.getLogger('restaurant')
    log_message = f"USER_ACTION: user_id={user_id}, action={action}"
    if message:
        log_message += f", message={message}"
    if ip_address:
        log_message += f", ip={ip_address}"
    logger.info(log_message)

def log_error(error, user_id=None, additional_info=None):
    """에러 로깅"""
    error_logger = logging.getLogger('error')
    log_message = f"ERROR: {str(error)}"
    if user_id:
        log_message += f", user_id={user_id}"
    if additional_info:
        log_message += f", info={additional_info}"
    error_logger.error(log_message, exc_info=True)

def log_security_event(user_id, event_type, details=None, ip_address=None):
    """보안 이벤트 로깅"""
    security_logger = logging.getLogger('security')
    log_message = f"SECURITY_EVENT: user_id={user_id}, event={event_type}"
    if details:
        log_message += f", details={details}"
    if ip_address:
        log_message += f", ip={ip_address}"
    security_logger.warning(log_message)

def cleanup_old_logs(days=30):
    """오래된 로그 정리"""
    try:
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 데이터베이스 로그 정리
        ActionLog.query.filter(ActionLog.created_at < cutoff_date).delete()
        db.session.commit() 
        
        logger = logging.getLogger('restaurant')
        logger.info(f"Cleaned up logs older than {days} days")
        
    except Exception as e:
        log_error(e)

def compress_old_logs(log_dir='logs', compress_after_days=7):
    """오래된 로그 파일 압축"""
    try:
        if not os.path.exists(log_dir):
            return
        
        now = time.time()
        compress_cutoff = now - (compress_after_days * 24 * 60 * 60)
        
        compressed_count = 0
        for filename in os.listdir(log_dir):
            if not filename.endswith('.log'):
                continue
                
            file_path = os.path.join(log_dir, filename)
            
            # 이미 압축된 파일은 건너뛰기
            if filename.endswith('.gz'):
                continue
            
            # 파일인지 확인
            if not os.path.isfile(file_path):
                continue
            
            # 수정 시간 확인
            file_mtime = os.path.getmtime(file_path)
            if file_mtime < compress_cutoff:
                try:
                    # 압축 파일명
                    gz_filename = filename + '.gz'
                    gz_path = os.path.join(log_dir, gz_filename)
                    
                    # 이미 압축 파일이 있으면 건너뛰기
                    if os.path.exists(gz_path):
                        continue
                    
                    # 파일 압축
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(gz_path, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                    
                    # 원본 파일 삭제
                    os.remove(file_path)
                    compressed_count += 1
                    print(f"Compressed log file: {filename}")
                    
                except Exception as e:
                    print(f"Failed to compress {filename}: {e}")
        
        return compressed_count
    except Exception as e:
        print(f"Log compression failed: {e}")
        return 0

def get_log_stats(log_dir='logs'):
    """로그 파일 통계"""
    try:
        if not os.path.exists(log_dir):
            return {}
        
        stats = {
            'total_files': 0,
            'total_size': 0,
            'file_types': {},
            'oldest_file': None,
            'newest_file': None
        }
        
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            
            if not os.path.isfile(file_path):
                continue
            
            file_size = os.path.getsize(file_path)
            file_mtime = os.path.getmtime(file_path)
            
            stats['total_files'] += 1
            stats['total_size'] += file_size
            
            # 파일 타입별 통계
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in stats['file_types']:
                stats['file_types'][file_ext] = {'count': 0, 'size': 0}
            stats['file_types'][file_ext]['count'] += 1
            stats['file_types'][file_ext]['size'] += file_size
            
            # 가장 오래된/최신 파일
            if stats['oldest_file'] is None or file_mtime < stats['oldest_file'][1]:
                stats['oldest_file'] = (filename, file_mtime)
            if stats['newest_file'] is None or file_mtime > stats['newest_file'][1]:
                stats['newest_file'] = (filename, file_mtime)
        
        return stats
    except Exception as e:
        print(f"Failed to get log stats: {e}")
        return {}

def rotate_logs_manually():
    """수동 로그 로테이션"""
    try:
        # 메인 로그 로테이션
        main_logger = logging.getLogger('restaurant')
        for handler in main_logger.handlers:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.doRollover()
        
        # 보안 로그 로테이션
        security_logger = logging.getLogger('security')
        for handler in security_logger.handlers:
            if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
                handler.doRollover()
        
        print("Manual log rotation completed")
        return True
    except Exception as e:
        print(f"Manual log rotation failed: {e}")
        return False

# CLI 명령어용 함수들
def cleanup_logs_command():
    """CLI 명령어용 로그 정리"""
    deleted = cleanup_old_logs()
    compressed = compress_old_logs()
    stats = get_log_stats()
    
    print(f"Log cleanup completed:")
    print(f"- Deleted files: {deleted}")
    print(f"- Compressed files: {compressed}")
    print(f"- Total files: {stats.get('total_files', 0)}")
    print(f"- Total size: {stats.get('total_size', 0) / (1024*1024):.2f} MB")

def show_log_stats_command():
    """CLI 명령어용 로그 통계"""
    stats = get_log_stats()
    
    print("Log Statistics:")
    print(f"- Total files: {stats.get('total_files', 0)}")
    print(f"- Total size: {stats.get('total_size', 0) / (1024*1024):.2f} MB")
    
    if stats.get('file_types'):
        print("\nFile types:")
        for ext, info in stats['file_types'].items():
            print(f"  {ext}: {info['count']} files, {info['size'] / 1024:.2f} KB")
    
    if stats.get('oldest_file'):
        oldest_time = datetime.fromtimestamp(stats['oldest_file'][1])
        print(f"\nOldest file: {stats['oldest_file'][0]} ({oldest_time})")
    
    if stats.get('newest_file'):
        newest_time = datetime.fromtimestamp(stats['newest_file'][1])
        print(f"Newest file: {stats['newest_file'][0]} ({newest_time})")

def get_user_activity_logs(user_id, limit=50):
    """사용자 활동 로그 조회"""
    try:
        return ActionLog.query.filter_by(user_id=user_id)\
                             .order_by(ActionLog.created_at.desc())\
                             .limit(limit).all()
    except Exception as e:
        log_error(e)
        return []

def get_action_logger():
    """액션 로깅 전용 로거"""
    logger = logging.getLogger("actionlog")
    if not logger.handlers:
        # 로그 디렉토리 생성
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        handler = logging.handlers.RotatingFileHandler(
            'logs/action.log', 
            maxBytes=200000, 
            backupCount=10,
            encoding='utf-8'
        )
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

# 액션 로거 인스턴스 생성
action_logger = get_action_logger()

def log_action_consistency(user_id, action, details=None, ip_address=None):
    """일관된 액션 로깅"""
    try:
        # 액션 로그에 기록
        action_logger.info(f"ACTION: user_id={user_id}, action={action}, details={details}, ip={ip_address}")
        
        # 데이터베이스에도 기록 (기존 방식 유지)
        log_action(user_id, action, details, ip_address)
        
    except Exception as e:
        # 로깅 실패 시 기본 로거에 기록
        basic_logger = logging.getLogger('restaurant')
        basic_logger.error(f"Action logging failed: {e}") 