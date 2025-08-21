from functools import wraps
from flask import request, jsonify, current_app
import json
import uuid
from datetime import datetime, timedelta

def require_idempotency_key():
    """멱등성 키를 요구하는 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 헤더에서 멱등성 키 추출
            idempotency_key = request.headers.get('X-Idempotency-Key')
            
            if not idempotency_key:
                return jsonify({
                    "error": "X-Idempotency-Key 헤더가 필요합니다",
                    "code": "MISSING_IDEMPOTENCY_KEY"
                }), 400
            
            # UUID 형식 검증
            try:
                uuid.UUID(idempotency_key)
            except ValueError:
                return jsonify({
                    "error": "유효하지 않은 Idempotency Key 형식입니다",
                    "code": "INVALID_IDEMPOTENCY_KEY"
                }), 400
            
            # 현재 사용자 ID (인증된 사용자만)
            user_id = getattr(request, 'user_id', None)
            if not user_id:
                return jsonify({
                    "error": "인증이 필요합니다",
                    "code": "AUTHENTICATION_REQUIRED"
                }), 401
            
            # 데이터베이스에서 기존 키 확인
            try:
                from models.idempotency import IdempotencyKey
                from extensions import db
                
                existing_key = IdempotencyKey.query.get(idempotency_key)
                
                if existing_key:
                    # 만료된 키인지 확인
                    if existing_key.is_expired():
                        # 만료된 키 삭제
                        db.session.delete(existing_key)
                        db.session.commit()
                    else:
                        # 이전 응답이 있으면 반환
                        if existing_key.response_json:
                            try:
                                response_data = json.loads(existing_key.response_json)
                                return jsonify({
                                    **response_data,
                                    "duplicate": True,
                                    "message": "중복 요청이 감지되었습니다. 이전 응답을 반환합니다."
                                })
                            except json.JSONDecodeError:
                                pass
                        
                        # 응답이 없으면 중복 요청으로 처리
                        return jsonify({
                            "error": "중복 요청이 감지되었습니다",
                            "code": "DUPLICATE_REQUEST",
                            "idempotency_key": idempotency_key
                        }), 409
                
                # 새로운 키 생성
                new_key = IdempotencyKey(
                    key=idempotency_key,
                    user_id=user_id,
                    endpoint=request.endpoint,
                    method=request.method
                )
                
                # 함수 실행
                response = f(*args, **kwargs)
                
                # 응답을 JSON으로 저장 (선택사항)
                if hasattr(response, 'json'):
                    new_key.response_json = json.dumps(response.json)
                elif hasattr(response, 'data'):
                    new_key.response_json = response.data.decode('utf-8')
                
                # 키 저장
                db.session.add(new_key)
                db.session.commit()
                
                return response
                
            except Exception as e:
                current_app.logger.error(f"Idempotency 처리 중 오류: {str(e)}")
                # 오류가 발생해도 원본 함수는 실행
                return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def generate_idempotency_key():
    """새로운 멱등성 키 생성"""
    return str(uuid.uuid4())

def validate_idempotency_key(key):
    """멱등성 키 유효성 검증"""
    try:
        uuid.UUID(key)
        return True
    except ValueError:
        return False
