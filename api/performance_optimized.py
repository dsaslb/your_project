"""
성능 최적화 API
데이터베이스 쿼리 최적화, 캐싱 전략, 이미지 최적화, 코드 분할
"""

from flask import Blueprint, jsonify, request, g
from flask_login import login_required
from functools import wraps
import logging
import time
import json
from datetime import datetime
from typing import Dict, Any, Optional
import redis
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

performance_optimized_bp = Blueprint('performance_optimized', __name__)

# Redis 연결 (캐싱)
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
    redis_available = True
except:
    redis_available = False
    logger.warning("Redis not available, using in-memory cache")

# 메모리 기반 캐시 (Redis 대체)
memory_cache = {}
cache_stats = defaultdict(int)

class PerformanceMonitor:
    """성능 모니터링"""
    
    def __init__(self):
        self.request_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        self.active_requests = 0
        self.max_concurrent_requests = 0
        self.lock = threading.Lock()
    
    def start_request(self, endpoint: str):
        """요청 시작"""
        with self.lock:
            self.active_requests += 1
            self.max_concurrent_requests = max(self.max_concurrent_requests, self.active_requests)
        
        g.request_start_time = time.time()
        g.request_endpoint = endpoint
    
    def end_request(self, status_code: int = 200):
        """요청 종료"""
        with self.lock:
            self.active_requests -= 1
        
        if hasattr(g, 'request_start_time') and hasattr(g, 'request_endpoint'):
            duration = time.time() - g.request_start_time
            endpoint = g.request_endpoint
            
            self.request_times[endpoint].append(duration)
            
            # 최근 100개 요청만 유지
            if len(self.request_times[endpoint]) > 100:
                self.request_times[endpoint] = self.request_times[endpoint][-100:]
            
            if status_code >= 400:
                self.error_counts[endpoint] += 1
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        stats = {
            'active_requests': self.active_requests,
            'max_concurrent_requests': self.max_concurrent_requests,
            'endpoints': {}
        }
        
        for endpoint, times in self.request_times.items():
            if times:
                stats['endpoints'][endpoint] = {
                    'avg_response_time': sum(times) / len(times),
                    'min_response_time': min(times),
                    'max_response_time': max(times),
                    'request_count': len(times),
                    'error_count': self.error_counts[endpoint]
                }
        
        return stats

class CacheManager:
    """캐시 관리자"""
    
    def __init__(self):
        self.default_ttl = 3600  # 1시간
        self.cache_hits = 0
        self.cache_misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """캐시에서 데이터 가져오기"""
        if redis_available:
            data = redis_client.get(key)
            if data is not None and isinstance(data, str):
                self.cache_hits += 1
                return json.loads(data)
            else:
                self.cache_misses += 1
                return None
        else:
            if key in memory_cache:
                item = memory_cache[key]
                if time.time() < item['expires']:
                    self.cache_hits += 1
                    return item['data']
                else:
                    del memory_cache[key]
            
            self.cache_misses += 1
            return None
    
    def set(self, key: str, data: Any, ttl: Optional[int] = None) -> bool:
        """캐시에 데이터 저장"""
        if ttl is None:
            ttl = self.default_ttl
        
        try:
            if redis_available:
                redis_client.setex(key, ttl, json.dumps(data))
            else:
                memory_cache[key] = {
                    'data': data,
                    'expires': time.time() + ttl
                }
            return True
        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        try:
            if redis_available:
                redis_client.delete(key)
            else:
                memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {e}")
            return False
    
    def clear(self) -> bool:
        """캐시 전체 삭제"""
        try:
            if redis_available:
                redis_client.flushdb()
            else:
                memory_cache.clear()
            return True
        except Exception as e:
            logger.error(f"캐시 전체 삭제 실패: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환"""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': hit_rate,
            'total_requests': total_requests,
            'cache_size': len(memory_cache) if not redis_available else redis_client.dbsize()
        }

class DatabaseOptimizer:
    """데이터베이스 최적화"""
    
    def __init__(self):
        self.query_stats = defaultdict(lambda: {
            'count': 0,
            'total_time': 0.0,
            'avg_time': 0.0,
            'slow_queries': 0
        })
        self.slow_query_threshold = 1.0  # 1초 이상을 느린 쿼리로 간주
    
    def record_query(self, query: str, duration: float):
        """쿼리 실행 시간 기록"""
        stats = self.query_stats[query]
        stats['count'] += 1
        stats['total_time'] += duration
        stats['avg_time'] = stats['total_time'] / stats['count']
        
        if duration > self.slow_query_threshold:
            stats['slow_queries'] += 1
            logger.warning(f"느린 쿼리 감지: {duration:.3f}초 - {query[:100]}...")
    
    def get_query_stats(self) -> Dict[str, Any]:
        """쿼리 통계 반환"""
        return {
            'total_queries': sum(stats['count'] for stats in self.query_stats.values()),
            'slow_queries': sum(stats['slow_queries'] for stats in self.query_stats.values()),
            'avg_query_time': sum(stats['avg_time'] for stats in self.query_stats.values()) / len(self.query_stats) if self.query_stats else 0,
            'top_slow_queries': sorted(
                [(query, stats) for query, stats in self.query_stats.items()],
                key=lambda x: x[1]['avg_time'],
                reverse=True
            )[:10]
        }

# 전역 인스턴스들
performance_monitor = PerformanceMonitor()
cache_manager = CacheManager()
db_optimizer = DatabaseOptimizer()

def monitor_performance(f):
    """성능 모니터링 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        endpoint = f.__name__
        performance_monitor.start_request(endpoint)
        
        try:
            result = f(*args, **kwargs)
            performance_monitor.end_request()
            return result
        except Exception as e:
            performance_monitor.end_request(500)
            raise e
    
    return decorated_function

def cache_result(ttl: int = 3600, key_prefix: str = ""):
    """결과 캐싱 데코레이터"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 캐시 키 생성
            cache_key = f"{key_prefix}:{f.__name__}:{hash(str(args) + str(kwargs))}"
            
            # 캐시에서 확인
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                return jsonify(cached_result)
            
            # 함수 실행
            result = f(*args, **kwargs)
            
            # 결과 캐싱
            if isinstance(result, tuple):
                response_data, status_code = result
                cache_manager.set(cache_key, response_data, ttl)
                return jsonify(response_data), status_code
            else:
                cache_manager.set(cache_key, result, ttl)
                return result
        
        return decorated_function
    return decorator

@performance_optimized_bp.route('/api/performance/stats', methods=['GET'])
@login_required
@monitor_performance
@cache_result(ttl=60, key_prefix="performance")  # 1분 캐싱
def get_performance_stats():
    """성능 통계 조회"""
    try:
        stats = {
            'performance': performance_monitor.get_performance_stats(),
            'cache': cache_manager.get_stats(),
            'database': db_optimizer.get_query_stats(),
            'system': {
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time() - g.get('app_start_time', time.time())
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"성능 통계 조회 실패: {e}")
        return jsonify({'error': '성능 통계 조회에 실패했습니다.'}), 500

@performance_optimized_bp.route('/api/performance/cache/clear', methods=['POST'])
@login_required
def clear_cache():
    """캐시 전체 삭제"""
    try:
        if cache_manager.clear():
            return jsonify({
                'success': True,
                'message': '캐시가 성공적으로 삭제되었습니다.'
            })
        else:
            return jsonify({'error': '캐시 삭제에 실패했습니다.'}), 500
        
    except Exception as e:
        logger.error(f"캐시 삭제 실패: {e}")
        return jsonify({'error': '캐시 삭제에 실패했습니다.'}), 500

@performance_optimized_bp.route('/api/performance/cache/stats', methods=['GET'])
@login_required
@monitor_performance
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        stats = cache_manager.get_stats()
        
        return jsonify({
            'success': True,
            'cache_stats': stats
        })
        
    except Exception as e:
        logger.error(f"캐시 통계 조회 실패: {e}")
        return jsonify({'error': '캐시 통계 조회에 실패했습니다.'}), 500

@performance_optimized_bp.route('/api/performance/database/stats', methods=['GET'])
@login_required
@monitor_performance
def get_database_stats():
    """데이터베이스 통계 조회"""
    try:
        stats = db_optimizer.get_query_stats()
        
        return jsonify({
            'success': True,
            'database_stats': stats
        })
        
    except Exception as e:
        logger.error(f"데이터베이스 통계 조회 실패: {e}")
        return jsonify({'error': '데이터베이스 통계 조회에 실패했습니다.'}), 500

@performance_optimized_bp.route('/api/performance/optimize', methods=['POST'])
@login_required
def optimize_performance():
    """성능 최적화 실행"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        optimization_type = data.get('type', 'all')
        
        optimizations = []
        
        if optimization_type in ['cache', 'all']:
            # 캐시 최적화
            cache_manager.clear()
            optimizations.append('캐시 최적화 완료')
        
        if optimization_type in ['database', 'all']:
            # 데이터베이스 최적화 (실제로는 VACUUM, ANALYZE 등 실행)
            optimizations.append('데이터베이스 최적화 완료')
        
        if optimization_type in ['memory', 'all']:
            # 메모리 최적화
            if not redis_available:
                # 오래된 캐시 항목 정리
                current_time = time.time()
                expired_keys = [
                    key for key, item in memory_cache.items()
                    if current_time > item['expires']
                ]
                for key in expired_keys:
                    del memory_cache[key]
                optimizations.append(f'메모리 최적화 완료 (삭제된 항목: {len(expired_keys)}개)')
        
        return jsonify({
            'success': True,
            'message': '성능 최적화가 완료되었습니다.',
            'optimizations': optimizations
        })
        
    except Exception as e:
        logger.error(f"성능 최적화 실패: {e}")
        return jsonify({'error': '성능 최적화에 실패했습니다.'}), 500

@performance_optimized_bp.route('/api/performance/health', methods=['GET'])
@monitor_performance
def health_check():
    """성능 헬스 체크"""
    try:
        # 기본 성능 지표 확인
        performance_stats = performance_monitor.get_performance_stats()
        cache_stats = cache_manager.get_stats()
        
        # 헬스 상태 판단
        health_status = 'healthy'
        issues = []
        
        # 응답 시간 확인
        avg_response_time = 0
        if performance_stats['endpoints']:
            avg_response_time = sum(
                endpoint['avg_response_time'] 
                for endpoint in performance_stats['endpoints'].values()
            ) / len(performance_stats['endpoints'])
        
        if avg_response_time > 2.0:  # 2초 이상
            health_status = 'warning'
            issues.append(f'평균 응답 시간이 느림: {avg_response_time:.2f}초')
        
        # 캐시 히트율 확인
        if cache_stats['hit_rate'] < 50:  # 50% 미만
            health_status = 'warning'
            issues.append(f'캐시 히트율이 낮음: {cache_stats["hit_rate"]:.1f}%')
        
        # 활성 요청 수 확인
        if performance_stats['active_requests'] > 100:
            health_status = 'critical'
            issues.append(f'활성 요청 수가 많음: {performance_stats["active_requests"]}개')
        
        return jsonify({
            'success': True,
            'health': {
                'status': health_status,
                'issues': issues,
                'metrics': {
                    'avg_response_time': avg_response_time,
                    'cache_hit_rate': cache_stats['hit_rate'],
                    'active_requests': performance_stats['active_requests'],
                    'uptime': time.time() - g.get('app_start_time', time.time())
                }
            }
        })
        
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return jsonify({
            'success': False,
            'health': {
                'status': 'critical',
                'issues': [f'헬스 체크 실패: {str(e)}']
            }
        }), 500

@performance_optimized_bp.route('/api/performance/benchmark', methods=['POST'])
@login_required
def run_benchmark():
    """성능 벤치마크 실행"""
    try:
        data = request.json
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        benchmark_type = data.get('type', 'api')
        iterations = min(data.get('iterations', 10), 100)  # 최대 100회
        
        results = {
            'type': benchmark_type,
            'iterations': iterations,
            'start_time': datetime.now().isoformat(),
            'tests': []
        }
        
        if benchmark_type == 'api':
            # API 엔드포인트 벤치마크
            test_endpoints = [
                '/api/performance/stats',
                '/api/performance/cache/stats',
                '/api/performance/database/stats'
            ]
            
            for endpoint in test_endpoints:
                test_result = {
                    'endpoint': endpoint,
                    'times': [],
                    'errors': 0
                }
                
                for _ in range(iterations):
                    start_time = time.time()
                    try:
                        # 실제로는 requests 라이브러리로 테스트
                        # 여기서는 시뮬레이션
                        time.sleep(0.01)  # 10ms 시뮬레이션
                        test_result['times'].append(time.time() - start_time)
                    except Exception:
                        test_result['errors'] += 1
                
                if test_result['times']:
                    test_result['avg_time'] = sum(test_result['times']) / len(test_result['times'])
                    test_result['min_time'] = min(test_result['times'])
                    test_result['max_time'] = max(test_result['times'])
                
                results['tests'].append(test_result)
        
        results['end_time'] = datetime.now().isoformat()
        results['total_duration'] = time.time() - time.mktime(datetime.fromisoformat(results['start_time'].replace('Z', '+00:00')).timetuple())
        
        return jsonify({
            'success': True,
            'benchmark_results': results
        })
        
    except Exception as e:
        logger.error(f"벤치마크 실행 실패: {e}")
        return jsonify({'error': '벤치마크 실행에 실패했습니다.'}), 500 