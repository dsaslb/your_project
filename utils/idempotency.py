#!/usr/bin/env python3
"""
멱등성 키 유틸리티
"""

import uuid
from functools import wraps
from flask import request, jsonify, current_app
from extensions import db

def is_valid_uuid(uuid_string):
    """UUID 유효성 검사"""
    try:
        uuid.UUID(str(uuid_string))
        return True
    except ValueError:
        return False

def require_idempotency_key():
    """멱등성 키 검증 데코레이터 - 중복 요청 방지"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 멱등성 키 헤더 확인
            idempotency_key = request.headers.get('X-Idempotency-Key')
            
            if not idempotency_key:
                return jsonify({
                    "error": "Missing idempotency key",
                    "message": "X-Idempotency-Key 헤더가 필요합니다."
                }), 400
            
            if not is_valid_uuid(idempotency_key):
                return jsonify({
                    "error": "Invalid idempotency key",
                    "message": "유효하지 않은 멱등성 키입니다."
                }), 400
            
            # 중복 요청 확인 (메모리 기반 임시 구현)
            # TODO: 데이터베이스 테이블 생성 문제 해결 후 실제 IdempotencyKey 모델 사용
            cache_key = f"idempotency:{idempotency_key}"
            
            current_app.logger.info(f"멱등성 키 검증 시작: {idempotency_key}")
            current_app.logger.info(f"캐시 키: {cache_key}")
            
            # Flask 앱의 임시 캐시 사용
            if not hasattr(current_app, '_idempotency_cache'):
                current_app._idempotency_cache = {}
                current_app.logger.info("멱등성 캐시 초기화")
            
            current_app.logger.info(f"현재 캐시 크기: {len(current_app._idempotency_cache)}")
            current_app.logger.info(f"캐시된 키들: {list(current_app._idempotency_cache.keys())[:5]}")
            
            if cache_key in current_app._idempotency_cache:
                # 중복 요청 감지 - 이전 응답 반환
                cached_response = current_app._idempotency_cache[cache_key]
                current_app.logger.info(f"중복 멱등성 키 감지: {idempotency_key}")
                current_app.logger.info(f"캐시된 응답: {cached_response}")
                return jsonify({
                    "ok": True,
                    "duplicate": True,
                    "message": "이미 처리된 요청입니다.",
                    "cached_response": cached_response
                }), 200
            
            current_app.logger.info(f"새로운 요청 - 원본 함수 실행")
            
            # 원본 함수 실행
            result = f(*args, **kwargs)
            
            current_app.logger.info(f"원본 함수 실행 완료, 결과 타입: {type(result)}")
            current_app.logger.info(f"결과 상태 코드: {getattr(result, 'status_code', 'N/A')}")
            
            # 성공 시 응답 캐시에 저장
            if result and hasattr(result, 'status_code') and result.status_code < 400:
                try:
                    # 응답 데이터 추출 - Flask 응답 객체 처리
                    if hasattr(result, 'json'):
                        response_data = result.json
                        current_app.logger.info("result.json 사용")
                    elif hasattr(result, 'get_json'):
                        response_data = result.get_json()
                        current_app.logger.info("result.get_json() 사용")
                    else:
                        # 응답 텍스트에서 JSON 파싱 시도
                        try:
                            import json
                            response_data = json.loads(result.data.decode('utf-8'))
                            current_app.logger.info("result.data에서 JSON 파싱")
                        except Exception as parse_error:
                            current_app.logger.warning(f"JSON 파싱 실패: {parse_error}")
                            response_data = {"status": "success", "status_code": result.status_code}
                    
                    current_app.logger.info(f"캐시에 저장할 응답 데이터: {response_data}")
                    current_app._idempotency_cache[cache_key] = response_data
                    current_app.logger.info(f"멱등성 키 캐시 저장 완료: {idempotency_key}")
                    
                    # 캐시 크기 제한 (메모리 보호)
                    if len(current_app._idempotency_cache) > 1000:
                        # 가장 오래된 키 제거
                        oldest_key = next(iter(current_app._idempotency_cache))
                        del current_app._idempotency_cache[oldest_key]
                        current_app.logger.info("오래된 멱등성 키 캐시 정리")
                        
                except Exception as e:
                    current_app.logger.warning(f"멱등성 키 캐시 저장 실패: {e}")
            else:
                current_app.logger.info(f"응답이 성공이 아니거나 상태 코드가 없음 - 캐시 저장 건너뜀")
            
            return result
        return decorated_function
    return decorator

def cleanup_expired_keys(hours=24):
    """만료된 키 정리 (임시 구현)"""
    current_app.logger.info(f"만료된 키 정리 (임시 구현): {hours}시간")
    return 0  # 임시로 0 반환
