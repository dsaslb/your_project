from datetime import datetime
import os
import logging.handlers
form = None  # pyright: ignore
﻿import logging


def setup_logger(app=None):
    """간소화된 로거 설정"""
    log_level = logging.INFO
    log_file = "logs/your_program.log"

    # 로그 디렉토리 생성
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 로거 설정
    logger = logging.getLogger("your_program")
    logger.setLevel(log_level)

    # 기존 핸들러 제거
    for handler in logger.handlers[:] if handlers is not None else None:
        logger.removeHandler(handler)

    # 파일 핸들러
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
    )
    file_handler.setLevel(log_level)

    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)

    # 포맷터
    formatter = logging.Formatter(
        "[%(asctime)s][%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 핸들러 추가
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def log_action(user_id,  action, message=None, ip_address=None):
    """사용자 액션 로깅"""
    logger = logging.getLogger("your_program")
    log_message = f"USER_ACTION: user_id={user_id}, action={action}"
    if message:
        log_message += f", message={message}"
    if ip_address:
        log_message += f", ip={ip_address}"
    logger.info(log_message)


def log_error(error, user_id=None, additional_info=None):
    """에러 로깅"""
    logger = logging.getLogger("your_program")
    log_message = f"ERROR: {str(error)}"
    if user_id:
        log_message += f", user_id={user_id}"
    if additional_info:
        log_message += f", info={additional_info}"
    logger.error(log_message, exc_info=True)


def log_security_event(user_id,  event_type, details=None, ip_address=None):
    """보안 이벤트 로깅"""
    logger = logging.getLogger("your_program")
    log_message = f"SECURITY_EVENT: user_id={user_id}, event={event_type}"
    if details:
        log_message += f", details={details}"
    if ip_address:
        log_message += f", ip={ip_address}"
    logger.warning(log_message)
