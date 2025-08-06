import os
import json
import time
import hashlib
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import uuid
from collections import defaultdict, deque
import jwt
import requests

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GatewayConfig:
    """게이트웨이 설정 클래스"""
    data_dir: str
    jwt_secret: str = "your-secret-key"
    rate_limit_window: int = 3600
    rate_limit_max_requests: int = 1000
    enable_rate_limiting: bool = True
    enable_logging: bool = True

@dataclass
class APIRoute:
    """API 라우트 정보"""
    route_id: str
    name: str
    path: str
    method: str
    target_url: str
    service_name: str
    is_active: bool = True
    requires_auth: bool = True
    created_at: datetime = None

@dataclass
class APIMetric:
    """API 메트릭 정보"""
    metric_id: str
    route_id: str
    method: str
    path: str
    status_code: int
    response_time: float
    ip_address: str
    timestamp: datetime = None

class GatewayManager:
    """API 게이트웨이 관리자 클래스"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
        self.routes: Dict[str, APIRoute] = {}
        self.metrics: List[APIMetric] = []
        
        # 설정 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 라우트 생성
        self.create_default_routes()
        
        # 기존 데이터 로드
        self.load_data()
        
        # 인메모리 속도 제한 저장소
        self._rate_limit_store: Dict[str, deque] = {}
    
    def init_database(self):
        """게이트웨이 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'gateway.db')
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # API 라우트 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_routes (
                route_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                path TEXT NOT NULL,
                method TEXT NOT NULL,
                target_url TEXT NOT NULL,
                service_name TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                requires_auth BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        ''')
        
        # API 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS api_metrics (
                metric_id TEXT PRIMARY KEY,
                route_id TEXT NOT NULL,
                method TEXT NOT NULL,
                path TEXT NOT NULL,
                status_code INTEGER NOT NULL,
                response_time REAL NOT NULL,
                ip_address TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_routes(self):
        """기본 API 라우트 생성"""
        default_routes = [
            {
                "name": "대시보드 API",
                "path": "/api/dashboard",
                "method": "GET",
                "target_url": "http://localhost:5001/api/dashboard",
                "service_name": "dashboard"
            },
            {
                "name": "매장 관리 API",
                "path": "/api/stores",
                "method": "GET",
                "target_url": "http://localhost:5002/api/stores",
                "service_name": "store-management"
            },
            {
                "name": "재고 관리 API",
                "path": "/api/inventory",
                "method": "GET",
                "target_url": "http://localhost:5003/api/inventory",
                "service_name": "inventory-management"
            },
            {
                "name": "주문 관리 API",
                "path": "/api/orders",
                "method": "GET",
                "target_url": "http://localhost:5004/api/orders",
                "service_name": "order-management"
            },
            {
                "name": "인증 API",
                "path": "/api/auth",
                "method": "POST",
                "target_url": "http://localhost:5005/api/auth",
                "service_name": "auth",
                "requires_auth": False
            },
            {
                "name": "분석 API",
                "path": "/api/analytics",
                "method": "GET",
                "target_url": "http://localhost:5006/api/analytics",
                "service_name": "analytics"
            }
        ]
        
        for route_data in default_routes:
            self.create_route(**route_data)
    
    def create_route(self, name: str, path: str, method: str, target_url: str,
                    service_name: str, is_active: bool = True, requires_auth: bool = True) -> str:
        """API 라우트 생성"""
        route_id = str(uuid.uuid4())
        
        route = APIRoute(
            route_id=route_id,
            name=name,
            path=path,
            method=method,
            target_url=target_url,
            service_name=service_name,
            is_active=is_active,
            requires_auth=requires_auth,
            created_at=datetime.utcnow()
        )
        
        self.routes[route_id] = route
        self._save_route(route)
        
        logger.info(f"API 라우트 생성: {name} -> {target_url}")
        return route_id
    
    def route_request(self, request) -> Tuple[Any, int]:
        """요청 라우팅 및 처리"""
        start_time = time.time()
        
        try:
            # 1. 라우트 찾기
            route = self._find_route(request.path, request.method)
            if not route:
                return self._create_error_response("Route not found", 404), 404
            
            # 2. 인증 검증
            if route.requires_auth:
                auth_result = self._validate_auth(request)
                if not auth_result['valid']:
                    return self._create_error_response(auth_result['message'], 401), 401
            
            # 3. 속도 제한 검사
            if self.config.enable_rate_limiting:
                rate_limit_result = self._check_rate_limit(request)
                if not rate_limit_result['allowed']:
                    return self._create_error_response("Rate limit exceeded", 429), 429
            
            # 4. 프록시 요청
            proxy_response = self._proxy_request(request, route)
            
            # 5. 메트릭 로깅
            response_time = time.time() - start_time
            self._log_metric(request, route, proxy_response.status_code, response_time)
            
            return proxy_response, proxy_response.status_code
            
        except Exception as e:
            logger.error(f"요청 처리 오류: {str(e)}")
            response_time = time.time() - start_time
            self._log_metric(request, None, 500, response_time, error=str(e))
            return self._create_error_response("Internal server error", 500), 500
    
    def _find_route(self, path: str, method: str) -> Optional[APIRoute]:
        """요청에 맞는 라우트 찾기"""
        for route in self.routes.values():
            if not route.is_active:
                continue
            
            # 경로 패턴 매칭
            if self._match_path(route.path, path) and route.method.upper() == method.upper():
                return route
        
        return None
    
    def _match_path(self, route_path: str, request_path: str) -> bool:
        """경로 패턴 매칭"""
        if route_path.endswith('/*'):
            base_path = route_path[:-2]
            return request_path.startswith(base_path)
        else:
            return route_path == request_path
    
    def _validate_auth(self, request) -> Dict[str, Any]:
        """인증 검증"""
        try:
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {'valid': False, 'message': 'Missing or invalid authorization header'}
            
            token = auth_header.split(' ')[1]
            
            # JWT 토큰 검증
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=['HS256'])
            
            # 토큰 만료 검사
            if 'exp' in payload and payload['exp'] < time.time():
                return {'valid': False, 'message': 'Token expired'}
            
            return {'valid': True, 'user': payload}
            
        except jwt.InvalidTokenError:
            return {'valid': False, 'message': 'Invalid token'}
        except Exception as e:
            logger.error(f"인증 검증 오류: {str(e)}")
            return {'valid': False, 'message': 'Authentication error'}
    
    def _check_rate_limit(self, request) -> Dict[str, Any]:
        """속도 제한 검사"""
        try:
            identifier = request.remote_addr
            key = f"rate_limit:{identifier}"
            
            current_time = time.time()
            if key not in self._rate_limit_store:
                self._rate_limit_store[key] = deque()
            
            # 오래된 요청 제거
            while self._rate_limit_store[key] and self._rate_limit_store[key][0] < current_time - self.config.rate_limit_window:
                self._rate_limit_store[key].popleft()
            
            if len(self._rate_limit_store[key]) >= self.config.rate_limit_max_requests:
                return {'allowed': False}
            
            self._rate_limit_store[key].append(current_time)
            return {'allowed': True}
            
        except Exception as e:
            logger.error(f"속도 제한 검사 오류: {str(e)}")
            return {'allowed': True}
    
    def _proxy_request(self, request, route: APIRoute):
        """프록시 요청 처리"""
        try:
            # 요청 URL 구성
            target_url = route.target_url + request.path.replace(route.path, '', 1)
            if request.query_string:
                target_url += '?' + request.query_string.decode()
            
            # 요청 헤더 준비
            headers = dict(request.headers)
            headers.pop('Host', None)
            
            # 프록시 요청 전송
            proxy_response = requests.request(
                method=request.method,
                url=target_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                timeout=30
            )
            
            return proxy_response
            
        except requests.RequestException as e:
            logger.error(f"프록시 요청 오류: {str(e)}")
            return self._create_error_response("Service unavailable", 503)
    
    def _log_metric(self, request, route: Optional[APIRoute], 
                   status_code: int, response_time: float, error: str = None):
        """메트릭 로깅"""
        try:
            metric = APIMetric(
                metric_id=str(uuid.uuid4()),
                route_id=route.route_id if route else None,
                method=request.method,
                path=request.path,
                status_code=status_code,
                response_time=response_time,
                ip_address=request.remote_addr,
                timestamp=datetime.utcnow()
            )
            
            self.metrics.append(metric)
            self._save_metric(metric)
            
            # 로그 출력
            if self.config.enable_logging:
                log_message = f"{request.method} {request.path} {status_code} {response_time:.3f}s"
                if error:
                    log_message += f" (error: {error})"
                logger.info(log_message)
                
        except Exception as e:
            logger.error(f"메트릭 로깅 오류: {str(e)}")
    
    def _create_error_response(self, message: str, status_code: int):
        """에러 응답 생성"""
        error_data = {
            'status': 'error',
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return error_data, status_code
    
    def get_gateway_stats(self) -> Dict[str, Any]:
        """게이트웨이 통계 조회"""
        try:
            stats = {
                'total_routes': len(self.routes),
                'active_routes': len([r for r in self.routes.values() if r.is_active]),
                'total_metrics': len(self.metrics)
            }
            
            # 최근 메트릭 분석
            recent_metrics = [m for m in self.metrics if m.timestamp > datetime.utcnow() - timedelta(hours=1)]
            
            if recent_metrics:
                stats.update({
                    'requests_last_hour': len(recent_metrics),
                    'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
                    'success_rate': len([m for m in recent_metrics if 200 <= m.status_code < 400]) / len(recent_metrics) * 100
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"통계 조회 오류: {str(e)}")
            return {}
    
    def load_data(self):
        """데이터 로드"""
        try:
            self._load_routes()
            self._load_metrics()
            
            logger.info(f"게이트웨이 데이터 로드 완료: {len(self.routes)}개 라우트")
            
        except Exception as e:
            logger.error(f"게이트웨이 데이터 로드 오류: {str(e)}")
    
    # 데이터베이스 저장 메서드들
    def _save_route(self, route: APIRoute):
        """라우트를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'gateway.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO api_routes 
            (route_id, name, path, method, target_url, service_name, is_active, requires_auth, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            route.route_id,
            route.name,
            route.path,
            route.method,
            route.target_url,
            route.service_name,
            route.is_active,
            route.requires_auth,
            route.created_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_metric(self, metric: APIMetric):
        """메트릭을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'gateway.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO api_metrics 
            (metric_id, route_id, method, path, status_code, response_time, ip_address, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.metric_id,
            metric.route_id,
            metric.method,
            metric.path,
            metric.status_code,
            metric.response_time,
            metric.ip_address,
            metric.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _load_routes(self):
        """데이터베이스에서 라우트 로드"""
        db_path = os.path.join(self.config.data_dir, 'gateway.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM api_routes')
        rows = cursor.fetchall()
        
        for row in rows:
            route = APIRoute(
                route_id=row[0],
                name=row[1],
                path=row[2],
                method=row[3],
                target_url=row[4],
                service_name=row[5],
                is_active=bool(row[6]),
                requires_auth=bool(row[7]),
                created_at=datetime.fromisoformat(row[8])
            )
            self.routes[route.route_id] = route
        
        conn.close()
    
    def _load_metrics(self):
        """데이터베이스에서 메트릭 로드"""
        db_path = os.path.join(self.config.data_dir, 'gateway.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM api_metrics ORDER BY timestamp DESC LIMIT 1000')
        rows = cursor.fetchall()
        
        for row in rows:
            metric = APIMetric(
                metric_id=row[0],
                route_id=row[1],
                method=row[2],
                path=row[3],
                status_code=row[4],
                response_time=row[5],
                ip_address=row[6],
                timestamp=datetime.fromisoformat(row[7])
            )
            self.metrics.append(metric)
        
        conn.close() 