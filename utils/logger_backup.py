import gzip
import logging
import logging.handlers
import os
import shutil
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask import request, session

from extensions import db
from models import ActionLog, SystemLog
from utils.logger import log_action

logger = logging.getLogger(__name__)


def setup_logger(app=None):
    """애플리케이션 로거 설정"""
    if app:
        log_level = getattr(logging, app.config.get("LOG_LEVEL", "INFO"))
        log_file = app.config.get("LOG_FILE", "logs/restaurant.log")
        max_bytes = app.config.get("LOG_MAX_BYTES", 10 * 1024 * 1024)  # 10MB
        backup_count = app.config.get("LOG_BACKUP_COUNT", 5)
    else:
        log_level = logging.INFO
        log_file = "logs/restaurant.log"
        max_bytes = 10 * 1024 * 1024
        backup_count = 5

    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 로거 설정
    logger = logging.getLogger("restaurant")
    logger.setLevel(log_level)

    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 파일 핸들러 (로테이션)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    file_handler.setLevel(log_level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # 포맷터
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def setup_security_logger():
    """보안 전용 로거 설정"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    security_logger = logging.getLogger("security")
    security_logger.setLevel(logging.INFO)

    # 기존 핸들러 제거
    for handler in security_logger.handlers[:]:
        security_logger.removeHandler(handler)

    # 보안 로그 파일 핸들러 (일별 로테이션)
    security_handler = logging.handlers.TimedRotatingFileHandler(
        "logs/security.log",
        when="midnight",
        interval=1,
        backupCount=30,  # 30일간 보관
        encoding="utf-8",
    )
    security_handler.setLevel(logging.INFO)

    # 포맷터
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][SECURITY] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    security_handler.setFormatter(formatter)

    security_logger.addHandler(security_handler)
    return security_logger


def setup_error_logger():
    """에러 전용 로거 설정"""
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    error_logger = logging.getLogger("error")
    error_logger.setLevel(logging.ERROR)

    # 기존 핸들러 제거
    for handler in error_logger.handlers[:]:
        error_logger.removeHandler(handler)

    # 에러 로그 파일 핸들러
    error_handler = logging.handlers.RotatingFileHandler(
        "logs/error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=10,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)

    # 포맷터
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s][ERROR] %(message)s\n%(pathname)s:%(lineno)d\n",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    error_handler.setFormatter(formatter)

    error_logger.addHandler(error_handler)
    return error_logger


def log_action(user_id, action, message=None, ip_address=None):
    """사용자 액션 로깅"""
    logger = logging.getLogger("restaurant")
    log_message = f"USER_ACTION: user_id={user_id}, action={action}"
    if message:
        log_message += f", message={message}"
    if ip_address:
        log_message += f", ip={ip_address}"
    logger.info(log_message)


def log_error(error, user_id=None, additional_info=None):
    """에러 로깅"""
    error_logger = logging.getLogger("error")
    log_message = f"ERROR: {str(error)}"
    if user_id:
        log_message += f", user_id={user_id}"
    if additional_info:
        log_message += f", info={additional_info}"
    error_logger.error(log_message, exc_info=True)


def log_security_event(user_id, event_type, details=None, ip_address=None):
    """보안 이벤트 로깅"""
    security_logger = logging.getLogger("security")
    log_message = f"SECURITY_EVENT: user_id={user_id}, event={event_type}"
    if details:
        log_message += f", details={details}"
    if ip_address:
        log_message += f", ip={ip_address}"
    security_logger.warning(log_message)


def cleanup_old_logs(days=30):
    """오래된 로그 정리"""
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # 데이터베이스 로그 정리
        ActionLog.query.filter(ActionLog.created_at < cutoff_date).delete()
        db.session.commit()

        logger.info(f"Cleaned up logs older than {days} days")

    except Exception as e:
        log_error(e)


def compress_log_file(filename: str) -> bool:
    """로그 파일 압축"""
    try:
        if not os.path.exists(filename):
            return False
            
        compressed_filename = f"{filename}.gz"
        
        with open(filename, 'rb') as f_in:
            with gzip.open(compressed_filename, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # 원본 파일 삭제
        os.remove(filename)
        
        logger.info(f"Compressed log file: {filename}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to compress {filename}: {e}")
        return False


def compress_old_logs():
    """오래된 로그 파일들 압축"""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return
            
        cutoff_date = datetime.now() - timedelta(days=7)
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log'):
                filepath = os.path.join(log_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    compress_log_file(filepath)
                    
    except Exception as e:
        logger.error(f"Log compression failed: {e}")


def get_log_statistics() -> Dict:
    """로그 파일 통계 조회"""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return {}
            
        stats = {
            "total_files": 0,
            "total_size": 0,
            "file_types": {},
            "oldest_file": None,
            "newest_file": None
        }
        
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath):
                stats["total_files"] += 1
                stats["total_size"] += os.path.getsize(filepath)
                
                # 파일 확장자별 통계
                ext = os.path.splitext(filename)[1]
                if ext not in stats["file_types"]:
                    stats["file_types"][ext] = {"count": 0, "size": 0}
                stats["file_types"][ext]["count"] += 1
                stats["file_types"][ext]["size"] += os.path.getsize(filepath)
                
                # 가장 오래된/최신 파일
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if not stats["oldest_file"] or file_time < stats["oldest_file"][1]:
                    stats["oldest_file"] = (filename, file_time)
                if not stats["newest_file"] or file_time > stats["newest_file"][1]:
                    stats["newest_file"] = (filename, file_time)
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get log stats: {e}")
        return {}


def manual_log_rotation():
    """수동 로그 로테이션"""
    try:
        compress_old_logs()
        cleanup_old_logs()
        logger.info("Manual log rotation completed")
        return True
        
    except Exception as e:
        logger.error(f"Manual log rotation failed: {e}")
        return False


def cleanup_old_logs():
    """오래된 로그 파일 정리"""
    try:
        log_dir = "logs"
        if not os.path.exists(log_dir):
            return
            
        cutoff_date = datetime.now() - timedelta(days=30)
        deleted = 0
        compressed = 0
        
        for filename in os.listdir(log_dir):
            filepath = os.path.join(log_dir, filename)
            if os.path.isfile(filepath):
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                
                if file_time < cutoff_date:
                    if filename.endswith('.gz'):
                        os.remove(filepath)
                        deleted += 1
                    else:
                        if compress_log_file(filepath):
                            compressed += 1
        
        stats = get_log_statistics()
        logger.info(f"Log cleanup completed:")
        logger.info(f"- Deleted files: {deleted}")
        logger.info(f"- Compressed files: {compressed}")
        logger.info(f"- Total files: {stats.get('total_files', 0)}")
        logger.info(f"- Total size: {stats.get('total_size', 0) / (1024*1024):.2f} MB")
        
    except Exception as e:
        logger.error(f"Log cleanup failed: {e}")


def print_log_statistics():
    """로그 통계 출력"""
    try:
        stats = get_log_statistics()
        
        logger.info("Log Statistics:")
        logger.info(f"- Total files: {stats.get('total_files', 0)}")
        logger.info(f"- Total size: {stats.get('total_size', 0) / (1024*1024):.2f} MB")
        
        if stats.get('file_types'):
            logger.info("\nFile types:")
            for ext, info in stats['file_types'].items():
                logger.info(f"  {ext}: {info['count']} files, {info['size'] / 1024:.2f} KB")
        
        if stats.get('oldest_file'):
            oldest_time = stats['oldest_file'][1].strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"\nOldest file: {stats['oldest_file'][0]} ({oldest_time})")
        
        if stats.get('newest_file'):
            newest_time = stats['newest_file'][1].strftime('%Y-%m-%d %H:%M:%S')
            logger.info(f"Newest file: {stats['newest_file'][0]} ({newest_time})")
            
    except Exception as e:
        logger.error(f"Failed to print log statistics: {e}")


def get_user_activity_logs(user_id, limit=50):
    """사용자 활동 로그 조회"""
    try:
        return (
            ActionLog.query.filter_by(user_id=user_id)
            .order_by(ActionLog.created_at.desc())
            .limit(limit)
            .all()
        )
    except Exception as e:
        log_error(e)
        return []


def get_action_logger():
    """액션 로깅 전용 로거"""
    logger = logging.getLogger("actionlog")
    if not logger.handlers:
        # 로그 디렉토리 생성
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        handler = logging.handlers.RotatingFileHandler(
            "logs/action.log", maxBytes=200000, backupCount=10, encoding="utf-8"
        )
        formatter = logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s")
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
        action_logger.info(
            f"ACTION: user_id={user_id}, action={action}, details={details}, ip={ip_address}"
        )

        # 데이터베이스에도 기록 (기존 방식 유지)
        log_action(user_id, action, details, ip_address)

    except Exception as e:
        # 로깅 실패 시 기본 로거에 기록
        basic_logger = logging.getLogger("restaurant")
        basic_logger.error(f"Action logging failed: {e}")
