"""
공통 데이터 캐싱 매니저
- Redis 캐시 연동
- 메모리 캐시 (Flask g 객체 활용)
- 계층별 데이터 분리 저장
"""

import json
import pickle
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from functools import wraps
import hashlib

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    print("Redis not available, using memory cache only")

from flask import g, current_app, request


class CacheManager:
    """공통 데이터 캐싱 매니저"""
    
    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.memory_cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        self.performance_metrics = {
            'avg_get_time': 0,
            'avg_set_time': 0,
            'total_operations': 0
        }
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app
        
        # Redis 연결 설정
        if REDIS_AVAILABLE and app.config.get('REDIS_URL'):
            try:
                self.redis_client = redis.from_url(app.config['REDIS_URL'])
                self.redis_client.ping()  # 연결 테스트
                print("✅ Redis 캐시 연결 성공")
            except Exception as e:
                print(f"⚠️ Redis 연결 실패, 메모리 캐시만 사용: {e}")
                self.redis_client = None
        
        # Flask g 객체에 캐시 매니저 등록
        app.before_request(self._before_request)
        app.teardown_appcontext(self._teardown_appcontext)
    
    def _before_request(self):
        """요청 전 공통 데이터 로드"""
        g.cache_manager = self
        g.common_data = {}
        
        # 로그인한 사용자 정보 캐시
        if hasattr(g, 'user') and g.user:
            g.common_data['user_info'] = self.get_user_info(g.user.id)
        
        # 관리자 공통 데이터
        if hasattr(g, 'user') and g.user and g.user.is_admin():
            g.common_data['admin_stats'] = self.get_admin_stats()
            g.common_data['system_status'] = self.get_system_status()
    
    def _teardown_appcontext(self, exception=None):
        """요청 후 정리"""
        if hasattr(g, 'common_data'):
            del g.common_data
    
    def get(self, key: str, default: Any = None) -> Any:
        """캐시에서 데이터 조회"""
        import time
        start_time = time.time()
        
        try:
            # 1. 메모리 캐시 확인
            if key in self.memory_cache:
                data, expiry = self.memory_cache[key]
                if expiry > datetime.now():
                    self.cache_stats['hits'] += 1
                    self._update_performance_metrics('get', time.time() - start_time)
                    return data
                else:
                    del self.memory_cache[key]
            
            # 2. Redis 캐시 확인
            if self.redis_client:
                try:
                    data = self.redis_client.get(key)
                    if data:
                        self.cache_stats['hits'] += 1
                        self._update_performance_metrics('get', time.time() - start_time)
                        return pickle.loads(data)
                except Exception as e:
                    print(f"Redis 조회 오류: {e}")
                    self.cache_stats['errors'] += 1
            
            self.cache_stats['misses'] += 1
            self._update_performance_metrics('get', time.time() - start_time)
            return default
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            self._update_performance_metrics('get', time.time() - start_time)
            return default
    
    def set(self, key: str, value: Any, expire: int = 3600) -> bool:
        """캐시에 데이터 저장"""
        import time
        start_time = time.time()
        
        try:
            expiry = datetime.now() + timedelta(seconds=expire)
            
            # 1. 메모리 캐시 저장
            self.memory_cache[key] = (value, expiry)
            
            # 2. Redis 캐시 저장
            if self.redis_client:
                try:
                    self.redis_client.setex(key, expire, pickle.dumps(value))
                except Exception as e:
                    print(f"Redis 저장 오류: {e}")
                    self.cache_stats['errors'] += 1
            
            self.cache_stats['sets'] += 1
            self._update_performance_metrics('set', time.time() - start_time)
            return True
            
        except Exception as e:
            self.cache_stats['errors'] += 1
            self._update_performance_metrics('set', time.time() - start_time)
            return False
    
    def delete(self, key: str) -> bool:
        """캐시에서 데이터 삭제"""
        # 메모리 캐시에서 삭제
        self.memory_cache.pop(key, None)
        
        # Redis 캐시에서 삭제
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                return True
            except Exception as e:
                print(f"Redis 삭제 오류: {e}")
                return False
        
        return True
    
    def clear_pattern(self, pattern: str) -> bool:
        """패턴에 맞는 캐시 모두 삭제"""
        # 메모리 캐시에서 패턴 매칭 삭제
        keys_to_delete = [k for k in self.memory_cache.keys() if pattern in k]
        for key in keys_to_delete:
            del self.memory_cache[key]
        
        # Redis 캐시에서 패턴 매칭 삭제
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                return True
            except Exception as e:
                print(f"Redis 패턴 삭제 오류: {e}")
                return False
        
        return True
    
    def get_user_info(self, user_id: int) -> Dict:
        """사용자 정보 캐시 조회"""
        cache_key = f"user_info:{user_id}"
        user_info = self.get(cache_key)
        
        if not user_info:
            from models_main import User
            user = User.query.get(user_id)
            if user:
                user_info = {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'grade': user.grade,
                    'permissions': user.get_permissions(),
                    'branch_id': user.branch_id,
                    'brand_id': user.brand_id,
                    'industry_id': user.industry_id
                }
                self.set(cache_key, user_info, 1800)  # 30분 캐시
        
        return user_info
    
    def get_admin_stats(self) -> Dict:
        """관리자 통계 데이터 캐시 조회"""
        cache_key = "admin_stats"
        stats = self.get(cache_key)
        
        if not stats:
            from models_main import User, Brand, Branch, Industry
            from sqlalchemy import func
            
            stats = {
                'total_users': User.query.count(),
                'total_brands': Brand.query.count(),
                'total_branches': Branch.query.count(),
                'total_industries': Industry.query.count(),
                'active_users': User.query.filter_by(status='approved').count(),
                'pending_users': User.query.filter_by(status='pending').count(),
                'updated_at': datetime.now().isoformat()
            }
            self.set(cache_key, stats, 300)  # 5분 캐시
        
        return stats
    
    def get_system_status(self) -> Dict:
        """시스템 상태 캐시 조회"""
        cache_key = "system_status"
        status = self.get(cache_key)
        
        if not status:
            import psutil
            import os
            
            status = {
                'cpu_percent': psutil.cpu_percent(),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'uptime': datetime.now() - datetime.fromtimestamp(psutil.boot_time()),
                'updated_at': datetime.now().isoformat()
            }
            self.set(cache_key, status, 60)  # 1분 캐시
        
        return status
    
    def get_industry_tree(self, industry_id: Optional[int] = None) -> Dict:
        """업종별 계층 구조 트리 캐시 조회"""
        cache_key = f"industry_tree:{industry_id or 'all'}"
        tree = self.get(cache_key)
        
        if not tree:
            from models_main import Industry, Brand, Branch, User
            
            if industry_id:
                # 특정 업종 트리
                industry = Industry.query.get(industry_id)
                if industry:
                    tree = self._build_industry_tree(industry)
            else:
                # 전체 업종 트리
                industries = Industry.query.filter_by(is_active=True).all()
                tree = {
                    'industries': [self._build_industry_tree(industry) for industry in industries]
                }
            
            self.set(cache_key, tree, 1800)  # 30분 캐시
        
        return tree
    
    def _build_industry_tree(self, industry) -> Dict:
        """업종별 트리 구조 생성"""
        from models_main import Brand, Branch, User
        
        brands = Brand.query.filter_by(industry_id=industry.id).all()
        brand_trees = []
        
        for brand in brands:
            branches = Branch.query.filter_by(brand_id=brand.id).all()
            branch_trees = []
            
            for branch in branches:
                users = User.query.filter_by(branch_id=branch.id).all()
                branch_trees.append({
                    'id': branch.id,
                    'name': branch.name,
                    'store_code': branch.store_code,
                    'status': branch.status,
                    'users': [{
                        'id': user.id,
                        'username': user.username,
                        'role': user.role,
                        'status': user.status
                    } for user in users]
                })
            
            brand_trees.append({
                'id': brand.id,
                'name': brand.name,
                'code': brand.code,
                'status': brand.status,
                'branches': branch_trees
            })
        
        return {
            'id': industry.id,
            'name': industry.name,
            'code': industry.code,
            'color': industry.color,
            'brands': brand_trees
        }
    
    def invalidate_user_cache(self, user_id: int):
        """사용자 관련 캐시 무효화"""
        self.delete(f"user_info:{user_id}")
        self.clear_pattern(f"user_*:{user_id}")
    
    def invalidate_industry_cache(self, industry_id: Optional[int] = None):
        """업종 관련 캐시 무효화"""
        if industry_id:
            self.delete(f"industry_tree:{industry_id}")
        else:
            self.clear_pattern("industry_tree:*")
    
    def invalidate_admin_cache(self):
        """관리자 관련 캐시 무효화"""
        self.delete("admin_stats")
        self.delete("system_status")
    
    def _update_performance_metrics(self, operation: str, duration: float):
        """성능 메트릭 업데이트"""
        self.performance_metrics['total_operations'] += 1
        
        if operation == 'get':
            current_avg = self.performance_metrics['avg_get_time']
            total_ops = self.cache_stats['hits'] + self.cache_stats['misses']
            self.performance_metrics['avg_get_time'] = (current_avg * (total_ops - 1) + duration) / total_ops
        elif operation == 'set':
            current_avg = self.performance_metrics['avg_set_time']
            total_sets = self.cache_stats['sets']
            self.performance_metrics['avg_set_time'] = (current_avg * (total_sets - 1) + duration) / total_sets
    
    def get_cache_stats(self) -> Dict:
        """캐시 통계 조회"""
        total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
        hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'stats': self.cache_stats.copy(),
            'performance': self.performance_metrics.copy(),
            'hit_rate': round(hit_rate, 2),
            'memory_cache_size': len(self.memory_cache),
            'redis_available': self.redis_client is not None
        }
    
    def get_cache_health(self) -> Dict:
        """캐시 상태 모니터링"""
        stats = self.get_cache_stats()
        
        health_status = "healthy"
        warnings = []
        
        # 히트율 체크
        if stats['hit_rate'] < 50:
            health_status = "warning"
            warnings.append(f"캐시 히트율이 낮습니다: {stats['hit_rate']}%")
        
        # 에러율 체크
        total_ops = stats['stats']['hits'] + stats['stats']['misses'] + stats['stats']['sets']
        error_rate = (stats['stats']['errors'] / total_ops * 100) if total_ops > 0 else 0
        
        if error_rate > 5:
            health_status = "critical"
            warnings.append(f"캐시 에러율이 높습니다: {error_rate:.1f}%")
        
        # 메모리 캐시 크기 체크
        if stats['memory_cache_size'] > 1000:
            health_status = "warning"
            warnings.append(f"메모리 캐시 크기가 큽니다: {stats['memory_cache_size']}개")
        
        return {
            'status': health_status,
            'stats': stats,
            'warnings': warnings,
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_expired_cache(self):
        """만료된 캐시 정리"""
        current_time = datetime.now()
        expired_keys = []
        
        for key, (value, expiry) in self.memory_cache.items():
            if expiry <= current_time:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            print(f"만료된 캐시 {len(expired_keys)}개 정리 완료")
        
        return len(expired_keys)


# 캐시 데코레이터
def cached(expire: int = 3600, key_prefix: str = ""):
    """캐시 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 캐시 키 생성
            args_str = str(args) + str(kwargs)
            cache_key = f"{key_prefix}:{func.__name__}:{hashlib.md5(args_str.encode()).hexdigest()}"
            
            # 캐시에서 조회
            cache_manager = getattr(g, 'cache_manager', None)
            if cache_manager:
                cached_result = cache_manager.get(cache_key)
                if cached_result is not None:
                    return cached_result
            
            # 함수 실행
            result = func(*args, **kwargs)
            
            # 캐시에 저장
            if cache_manager:
                cache_manager.set(cache_key, result, expire)
            
            return result
        return wrapper
    return decorator


# 전역 캐시 매니저 인스턴스
cache_manager = CacheManager()
