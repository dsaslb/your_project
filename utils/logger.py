import logging
import os
from datetime import datetime
from extensions import db
from models import ActionLog
from flask import request

def setup_logger(name="restaurant", log_file="restaurant.log", level=logging.INFO):
    """로거 설정"""
    # 로그 디렉토리 생성
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_path = os.path.join(log_dir, log_file)
    
    # 로거 생성
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 기존 핸들러 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 파일 핸들러
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    # 포맷터
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# 기본 로거 생성
logger = setup_logger()

def log_user_action(user_id, action, detail=None, ip_address=None, user_agent=None):
    """사용자 액션 로깅 (DB + 파일)"""
    try:
        # DB에 로그 기록
        log_action(user_id, action, detail or "")
        
        # 파일에 로그 기록
        logger.info(f"User Action: {action} by user_id={user_id}, detail={detail}")
        
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")

def log_system_event(event, level="INFO", **kwargs):
    """시스템 이벤트 로깅"""
    message = f"System Event: {event}"
    if kwargs:
        message += f" - {kwargs}"
    
    if level.upper() == "ERROR":
        logger.error(message)
    elif level.upper() == "WARNING":
        logger.warning(message)
    else:
        logger.info(message)

def log_error(error, context=None):
    """에러 로깅"""
    error_msg = f"Error: {error}"
    if context:
        error_msg += f" - Context: {context}"
    logger.error(error_msg)

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """보안 이벤트 로깅"""
    security_logger = setup_logger("security", "security.log")
    
    message = f"Security Event: {event_type}"
    if user_id:
        message += f" - User: {user_id}"
    if ip_address:
        message += f" - IP: {ip_address}"
    if details:
        message += f" - Details: {details}"
    
    security_logger.warning(message)

def get_recent_logs(limit=50):
    """최근 로그 조회"""
    try:
        return ActionLog.query.order_by(ActionLog.created_at.desc()).limit(limit).all()
    except Exception as e:
        logger.error(f"Failed to get recent logs: {e}")
        return []

def log_action(user, action, message):
    """액션 로그 기록"""
    log = ActionLog(user_id=user.id, action=action, message=message)
    db.session.add(log)
    db.session.commit()

def get_user_logs(user_id, limit=50):
    """사용자별 로그 조회"""
    return ActionLog.query.filter_by(user_id=user_id).order_by(ActionLog.created_at.desc()).limit(limit).all()

def get_action_logs(action=None, limit=100):
    """액션별 로그 조회"""
    query = ActionLog.query
    if action:
        query = query.filter_by(action=action)
    return query.order_by(ActionLog.created_at.desc()).limit(limit).all()

def cleanup_old_logs(days=30):
    """오래된 로그 정리"""
    from datetime import datetime, timedelta
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    ActionLog.query.filter(ActionLog.created_at < cutoff_date).delete()
    db.session.commit() 