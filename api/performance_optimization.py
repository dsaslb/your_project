from flask import Blueprint, jsonify, request, current_app, g
from functools import wraps
import hashlib
import json
import time
from typing import Dict, Any, Optional, Union
import logging
import threading

performance_bp = Blueprint('performance', __name__)

# Redis 클라이언트 초기화 (선택적)
redis_client = None
try:
    import redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    # 연결 테스트
    redis_client.ping()
except (ImportError, Exception):
    redis_client = None
    logging.warning("Redis not available, using in-memory cache")

# psutil import (시스템 리소스 모니터링용)
try:
    import psutil
except ImportError:
    psutil = None
    logging.warning("psutil not available, system monitoring disabled")

# 메모리 기반 캐시 (Redis가 없을 때 사용)
memory_cache = {}
cache_lock = threading.Lock()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cache_response(expire_time=300):
    """응답 캐싱 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"cache:{f.__name__}:{hashlib.md5(str(request.args).encode()).hexdigest()}"
            
            # Redis가 있으면 Redis 사용, 없으면 메모리 캐시 사용
            if redis_client:
                # Redis 캐시에서 데이터 확인
                cached_data = redis_client.get(cache_key)
                if cached_data:
                    logger.info(f"Redis 캐시 히트: {cache_key}")
                    return json.loads(cached_data)  # type: ignore
                
                # 캐시 미스 - 함수 실행
                result = f(*args, **kwargs)
                
                # 결과 Redis 캐싱
                redis_client.setex(cache_key, expire_time, json.dumps(result))
                logger.info(f"Redis 캐시 저장: {cache_key}")
                
                return result
            else:
                # 메모리 캐시 사용
                with cache_lock:
                    if cache_key in memory_cache:
                        cache_data = memory_cache[cache_key]
                        if time.time() < cache_data['expires']:
                            logger.info(f"메모리 캐시 히트: {cache_key}")
                            return cache_data['data']
                        else:
                            del memory_cache[cache_key]
                
                # 캐시 미스 - 함수 실행
                result = f(*args, **kwargs)
                
                # 결과 메모리 캐싱
                with cache_lock:
                    memory_cache[cache_key] = {
                        'data': result,
                        'expires': time.time() + expire_time
                    }
                logger.info(f"메모리 캐시 저장: {cache_key}")
                
                return result
        return decorated
    return decorator

def rate_limit(max_requests=100, window=60):
    """요청 제한 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            client_ip = request.remote_addr
            rate_key = f"rate_limit:{client_ip}:{f.__name__}"
            
            if redis_client:
                # Redis 기반 요청 제한
                current_requests = redis_client.get(rate_key)
                if current_requests and int(current_requests) >= max_requests:  # type: ignore
                    return jsonify({'error': '요청 제한 초과'}), 429
                
                # 요청 수 증가
                pipe = redis_client.pipeline()
                pipe.incr(rate_key)
                pipe.expire(rate_key, window)
                pipe.execute()
            else:
                # 메모리 기반 요청 제한 (간단한 구현)
                with cache_lock:
                    if rate_key not in memory_cache:
                        memory_cache[rate_key] = {'count': 0, 'reset_time': time.time() + window}
                    
                    cache_data = memory_cache[rate_key]
                    if time.time() > cache_data['reset_time']:
                        cache_data['count'] = 0
                        cache_data['reset_time'] = time.time() + window
                    
                    if cache_data['count'] >= max_requests:
                        return jsonify({'error': '요청 제한 초과'}), 429
                    
                    cache_data['count'] += 1
            
            return f(*args, **kwargs)
        return decorated
    return decorator

@performance_bp.route('/api/performance/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 전체 삭제"""
    try:
        if redis_client:
            keys = redis_client.keys("cache:*")
            if keys:
                redis_client.delete(*keys)  # type: ignore
                logger.info(f"Redis 캐시 삭제 완료: {len(keys)}개 키")  # type: ignore
                deleted_keys = len(keys) if isinstance(keys, (list, tuple, set)) else 0  # pyright: ignore
                # 메모리 캐시도 함께 삭제 (cache:로 시작하는 키만)
                with cache_lock:
                    memory_cache_keys = [k for k in memory_cache.keys() if k.startswith("cache:")]
                    for key in memory_cache_keys:
                        del memory_cache[key]
                    logger.info(f"메모리 캐시 삭제 완료: {len(memory_cache_keys)}개 키")
        return jsonify({'message': '캐시가 삭제되었습니다', 'deleted_keys': deleted_keys})
    except Exception as e:
        logger.error(f"캐시 삭제 오류: {e}")
        return jsonify({'error': '캐시 삭제 실패'}), 500

@performance_bp.route('/api/performance/cache/stats', methods=['GET'])
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        if redis_client:
            cache_keys = redis_client.keys("cache:*")
            rate_limit_keys = redis_client.keys("rate_limit:*")
            
            stats = {
                'cache_entries': len(cache_keys) if cache_keys else 0,  # type: ignore
                'rate_limit_entries': len(rate_limit_keys) if rate_limit_keys else 0,  # type: ignore
                'total_memory': redis_client.info()['used_memory_human'],  # type: ignore
                'connected_clients': redis_client.info()['connected_clients'],  # type: ignore
                'cache_type': 'redis'
            }
        else:
            # 메모리 캐시 통계
            with cache_lock:
                cache_keys = [k for k in memory_cache.keys() if k.startswith("cache:")]
                rate_limit_keys = [k for k in memory_cache.keys() if k.startswith("rate_limit:")]
            
            stats = {
                'cache_entries': len(cache_keys),
                'rate_limit_entries': len(rate_limit_keys),
                'total_memory': f"{len(memory_cache)} entries",
                'connected_clients': 1,
                'cache_type': 'memory'
            }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"캐시 통계 조회 오류: {e}")
        return jsonify({'error': '통계 조회 실패'}), 500

@performance_bp.route('/api/performance/health', methods=['GET'])
def health_check():
    """시스템 상태 확인"""
    try:
        # Redis 연결 확인
        redis_status = 'disconnected'
        if redis_client:
            try:
                redis_ping = redis_client.ping()
                redis_status = 'connected' if redis_ping else 'disconnected'
            except:
                redis_status = 'disconnected'
        
        # 시스템 리소스 확인 (실제 환경에서는 psutil 사용)
        import os
        import psutil
        
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_data = {
            'status': 'healthy',
            'timestamp': time.time(),
            'services': {
                'redis': redis_status,
                'database': 'connected',  # TODO: 실제 DB 연결 확인
                'api': 'running'
            },
            'resources': {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent
            }
        }
        
        return jsonify(health_data)
    except Exception as e:
        logger.error(f"상태 확인 오류: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/api/performance/cdn/upload', methods=['POST'])
def cdn_upload():
    """CDN 업로드 (실제 환경에서는 AWS S3, CloudFront 등 사용)"""
    try:
        # 파일 업로드 처리
        if 'file' not in request.files:
            return jsonify({'error': '파일이 없습니다'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '파일이 선택되지 않았습니다'}), 400
        
        # 파일 해시 생성
        file_hash = hashlib.md5(file.read()).hexdigest()
        file.seek(0)  # 파일 포인터 리셋
        
        # 파일 저장 (실제 환경에서는 CDN에 업로드)
        filename = f"{file_hash}_{file.filename}"
        file_path = f"static/uploads/{filename}"
        
        # 디렉토리 생성
        import os
        os.makedirs("static/uploads", exist_ok=True)
        
        file.save(file_path)
        
        # CDN URL 생성 (실제 환경에서는 CDN 도메인 사용)
        cdn_url = f"https://cdn.example.com/{filename}"
        
        return jsonify({
            'message': '파일 업로드 완료',
            'cdn_url': cdn_url,
            'file_hash': file_hash
        })
        
    except Exception as e:
        logger.error(f"CDN 업로드 오류: {e}")
        return jsonify({'error': '업로드 실패'}), 500

@performance_bp.route('/api/performance/load-balancer/status', methods=['GET'])
def load_balancer_status():
    """로드 밸런서 상태 확인"""
    try:
        # 서버 인스턴스 정보 (실제 환경에서는 AWS ELB, Nginx 등 사용)
        instances = [
            {
                'id': 'server-1',
                'status': 'healthy',
                'load': 0.65,
                'response_time': 45,
                'requests_per_second': 120
            },
            {
                'id': 'server-2', 
                'status': 'healthy',
                'load': 0.72,
                'response_time': 52,
                'requests_per_second': 98
            }
        ]
        
        total_requests = sum(instance['requests_per_second'] for instance in instances)
        avg_response_time = sum(instance['response_time'] for instance in instances) / len(instances)
        
        status_data = {
            'instances': instances,
            'total_requests_per_second': total_requests,
            'average_response_time': avg_response_time,
            'healthy_instances': len([i for i in instances if i['status'] == 'healthy']),
            'total_instances': len(instances)
        }
        
        return jsonify(status_data)
        
    except Exception as e:
        logger.error(f"로드 밸런서 상태 확인 오류: {e}")
        return jsonify({'error': '상태 확인 실패'}), 500

# 성능 모니터링 미들웨어
@performance_bp.before_request
def before_request():
    """요청 전 처리 - 성능 모니터링"""
    # Flask g 객체를 사용하여 요청별 데이터 저장
    g.start_time = time.time()

@performance_bp.after_request
def after_request(response):
    """요청 후 처리 - 응답 시간 기록"""
    if hasattr(g, 'start_time'):
        response_time = time.time() - g.start_time
        logger.info(f"요청 처리 시간: {response_time:.3f}초 - {request.endpoint}")
        
        # 응답 시간 메트릭 저장
        redis_client.lpush('response_times', response_time)  # type: ignore
        redis_client.ltrim('response_times', 0, 999)  # type: ignore # 최근 1000개만 유지
    
    return response 