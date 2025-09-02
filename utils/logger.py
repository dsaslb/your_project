import os
import logging
import logging.handlers
import json
from datetime import datetime
from typing import Dict, Any, Optional
import traceback

class StructuredLogger:
    """구조화된 로깅을 위한 클래스"""
    
    def __init__(self, name: str = "your_program"):
        self.logger = logging.getLogger(name)
        self.name = name
    
    def setup(self, app=None, log_level: str = "INFO", log_file: str = "logs/your_program.log"):
        """로거 설정"""
        level = getattr(logging, log_level.upper(), logging.INFO)
        
        # 로그 디렉토리 생성
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.logger.setLevel(level)
        
        # 기존 핸들러 제거
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 파일 핸들러 (구조화된 로그)
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=10, encoding="utf-8"
        )
        file_handler.setLevel(level)
        
        # 에러 로그 파일 핸들러
        error_log_file = log_file.replace('.log', '_error.log')
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
        )
        error_handler.setLevel(logging.ERROR)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 구조화된 포맷터
        structured_formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": %(message)s}',
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        # 일반 포맷터 (콘솔용)
        console_formatter = logging.Formatter(
            "[%(asctime)s][%(levelname)s][%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        file_handler.setFormatter(structured_formatter)
        error_handler.setFormatter(structured_formatter)
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(error_handler)
        self.logger.addHandler(console_handler)
        
        return self.logger
    
    def _format_message(self, message: str, **kwargs) -> str:
        """메시지를 JSON 형식으로 포맷팅"""
        log_data = {
            "message": message,
            **kwargs
        }
        return json.dumps(log_data, ensure_ascii=False)
    
    def info(self, message: str, **kwargs):
        """정보 로그"""
        self.logger.info(self._format_message(message, **kwargs))
    
    def warning(self, message: str, **kwargs):
        """경고 로그"""
        self.logger.warning(self._format_message(message, **kwargs))
    
    def error(self, message: str, **kwargs):
        """에러 로그"""
        self.logger.error(self._format_message(message, **kwargs))
    
    def debug(self, message: str, **kwargs):
        """디버그 로그"""
        self.logger.debug(self._format_message(message, **kwargs))
    
    def critical(self, message: str, **kwargs):
        """치명적 에러 로그"""
        self.logger.critical(self._format_message(message, **kwargs))

def setup_logger(app=None):
    """간단한 로거 설정 (기존 호환성 유지)"""
    structured_logger = StructuredLogger()
    return structured_logger.setup(app)


def log_action(user_id, action, message=None, ip_address=None):
    """사용자 액션 로깅 (기존 호환성 유지)"""
    logger = logging.getLogger("your_program")
    structured_logger = StructuredLogger()
    structured_logger.info(
        "사용자 액션",
        user_id=user_id,
        action=action,
        message=message,
        ip_address=ip_address,
        event_type="user_action"
    )


def log_error(error, user_id=None, additional_info=None):
    """에러 로깅 (기존 호환성 유지)"""
    logger = logging.getLogger("your_program")
    structured_logger = StructuredLogger()
    structured_logger.error(
        "시스템 에러",
        error=str(error),
        user_id=user_id,
        additional_info=additional_info,
        event_type="error",
        traceback=traceback.format_exc()
    )


def log_security_event(user_id, event_type, details=None, ip_address=None):
    """보안 이벤트 로깅 (기존 호환성 유지)"""
    logger = logging.getLogger("your_program")
    structured_logger = StructuredLogger()
    structured_logger.warning(
        "보안 이벤트",
        user_id=user_id,
        event_type=event_type,
        details=details,
        ip_address=ip_address,
        security_level="warning"
    )


# 전역 구조화된 로거 인스턴스
structured_logger = StructuredLogger()

# 전역 logger 변수 (기존 코드 호환성을 위해)
logger = structured_logger.logger