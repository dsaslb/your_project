"""
멱등성 처리 유틸리티
- API 요청의 중복 처리 방지
- 멱등성 키 검증 및 관리
"""
from functools import wraps
from flask import request, jsonify, current_app
from extensions import db
from models_sync import IdempotencyKey
import time
import logging

logger = logging.getLogger(__name__)

def require_idempotency_key():
    """멱등성 키를 요구하는 데코레이터"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # 헤더에서 멱등성 키 추출
            key = request.headers.get("X-Idempotency-Key")
            if not key:
                return jsonify({
                    "error": "Missing Idempotency-Key header",
                    "code": "MISSING_IDEMPOTENCY_KEY"
                }), 400
            
            # 키 형식 검증 (UUID 형식 권장)
            if len(key) < 10 or len(key) > 64:
                return jsonify({
                    "error": "Invalid Idempotency-Key format",
                    "code": "INVALID_IDEMPOTENCY_KEY"
                }), 400
            
            try:
                # 기존 키 확인
                existing_key = IdempotencyKey.query.get(key)
                if existing_key:
                    logger.info(f"Duplicate idempotency key detected: {key}")
                    return jsonify({
                        "ok": True, 
                        "duplicate": True,
                        "message": "Request already processed"
                    }), 200
                
                # 함수 실행
                start_time = time.time()
                result = fn(*args, **kwargs)
                processing_time = int((time.time() - start_time) * 1000)
                
                # 성공 시 키 저장
                try:
                    idem_key = IdempotencyKey(key=key)
                    db.session.add(idem_key)
                    db.session.commit()
                    logger.info(f"Idempotency key stored: {key}, processing_time: {processing_time}ms")
                except Exception as e:
                    logger.error(f"Failed to store idempotency key: {e}")
                    db.session.rollback()
                
                return result
                
            except Exception as e:
                logger.error(f"Error in idempotency check: {e}")
                db.session.rollback()
                raise
                
        return wrapper
    return decorator

def check_idempotency_key(key: str) -> bool:
    """멱등성 키 존재 여부 확인"""
    if not key:
        return False
    
    try:
        existing_key = IdempotencyKey.query.get(key)
        return existing_key is not None
    except Exception as e:
        logger.error(f"Error checking idempotency key: {e}")
        return False

def store_idempotency_key(key: str) -> bool:
    """멱등성 키 저장"""
    if not key:
        return False
    
    try:
        # 중복 확인
        if check_idempotency_key(key):
            return True
            
        idem_key = IdempotencyKey(key=key)
        db.session.add(idem_key)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to store idempotency key: {e}")
        db.session.rollback()
        return False

def cleanup_old_idempotency_keys(days: int = 7):
    """오래된 멱등성 키 정리"""
    try:
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        deleted_count = IdempotencyKey.query.filter(
            IdempotencyKey.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        logger.info(f"Cleaned up {deleted_count} old idempotency keys")
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up idempotency keys: {e}")
        db.session.rollback()
        return 0