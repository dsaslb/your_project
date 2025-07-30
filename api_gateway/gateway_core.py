"""
API 게이트웨이 코어 시스템
엔터프라이즈급 API 관리, 라우팅, 보안, 모니터링 시스템
"""

import logging
import json
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import jwt
import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import yaml
import uuid
import threading
from concurrent.futures import ThreadPoolExecutor
import statistics
import prometheus_client
from prometheus_client import Counter, Histogram, Gauge

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouteMethod(Enum):
    """HTTP 메서드"""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"

class AuthType(Enum):
    """인증 타입"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"

class RateLimitType(Enum):
    """레이트 리미트 타입"""
    USER = "user"
    IP = "ip"
    API_KEY = "api_key"
    GLOBAL = "global"

@dataclass
class APIRoute:
    """API 라우트 정의"""
    id: str
    name: str
    path: str
    method: RouteMethod
    target_url: str
    auth_type: AuthType
    rate_limit: Optional[Dict[str, Any]] = None
    timeout: int = 30
    retry_count: int = 3
    circuit_breaker: Optional[Dict[str, Any]] = None
    caching: Optional[Dict[str, Any]] = None
    transformation: Optional[Dict[str, Any]] = None
    monitoring: bool = True
    enabled: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class APIKey:
    """API 키 정보"""
    id: str
    key: str
    name: str
    user_id: str
    permissions: List[str]
    rate_limits: Dict[str, Any]
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    last_used: Optional[datetime] = None
    is_active: bool = True

@dataclass
class RateLimit:
    """레이트 리미트 정보"""
    key: str
    limit: int
    window: int  # 초 단위
    current_count: int = 0
    reset_time: datetime = None

@dataclass
class CircuitBreaker:
    """서킷 브레이커 정보"""
    service_name: str
    failure_threshold: int
    recovery_timeout: int
    failure_count: int = 0
    last_failure_time: Optional[datetime] = None
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

class APIGatewayCore:
    """API 게이트웨이 코어 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.routes: Dict[str, APIRoute] = {}
        self.api_keys: Dict[str, APIKey] = {}
        self.rate_limits: Dict[str, RateLimit] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.redis_client = None
        self.db_connection = None
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # 메트릭 정의
        self.request_counter = Counter('api_requests_total', 'Total API requests', ['route', 'method', 'status'])
        self.request_duration = Histogram('api_request_duration_seconds', 'API request duration', ['route', 'method'])
        self.active_connections = Gauge('api_active_connections', 'Active API connections')
        self.error_counter = Counter('api_errors_total', 'Total API errors', ['route', 'error_type'])
        
        self._initialize_connections()
        self._load_routes()
        self._load_api_keys()
        self._setup_circuit_breakers()
    
    def _initialize_connections(self):
        """연결 초기화"""
        try:
            # Redis 연결
            self.redis_client = redis.Redis(
                host=self.config['redis']['host'],
                port=self.config['redis']['port'],
                db=self.config['redis']['db'],
                decode_responses=True
            )
            
            # PostgreSQL 연결
            self.db_connection = psycopg2.connect(
                host=self.config['database']['host'],
                port=self.config['database']['port'],
                database=self.config['database']['name'],
                user=self.config['database']['user'],
                password=self.config['database']['password']
            )
            
            # HTTP 세션 생성
            timeout = ClientTimeout(total=30)
            self.session = ClientSession(timeout=timeout)
            
            logger.info("API 게이트웨이 연결 초기화 완료")
            
        except Exception as e:
            logger.error(f"연결 초기화 오류: {e}")
            raise
    
    def _load_routes(self):
        """라우트 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM api_routes WHERE enabled = true
                    ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    route = APIRoute(
                        id=row['id'],
                        name=row['name'],
                        path=row['path'],
                        method=RouteMethod(row['method']),
                        target_url=row['target_url'],
                        auth_type=AuthType(row['auth_type']),
                        rate_limit=row['rate_limit'],
                        timeout=row['timeout'],
                        retry_count=row['retry_count'],
                        circuit_breaker=row['circuit_breaker'],
                        caching=row['caching'],
                        transformation=row['transformation'],
                        monitoring=row['monitoring'],
                        enabled=row['enabled'],
                        created_at=row['created_at'],
                        updated_at=row['updated_at']
                    )
                    self.routes[route.id] = route
            
            logger.info(f"{len(self.routes)}개의 API 라우트 로드 완료")
            
        except Exception as e:
            logger.error(f"라우트 로드 오류: {e}")
    
    def _load_api_keys(self):
        """API 키 로드"""
        try:
            with self.db_connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM api_keys WHERE is_active = true
                    ORDER BY created_at DESC
                """)
                
                for row in cursor.fetchall():
                    api_key = APIKey(
                        id=row['id'],
                        key=row['key'],
                        name=row['name'],
                        user_id=row['user_id'],
                        permissions=row['permissions'],
                        rate_limits=row['rate_limits'],
                        expires_at=row['expires_at'],
                        created_at=row['created_at'],
                        last_used=row['last_used'],
                        is_active=row['is_active']
                    )
                    self.api_keys[api_key.key] = api_key
            
            logger.info(f"{len(self.api_keys)}개의 API 키 로드 완료")
            
        except Exception as e:
            logger.error(f"API 키 로드 오류: {e}")
    
    def _setup_circuit_breakers(self):
        """서킷 브레이커 설정"""
        try:
            # 기본 서킷 브레이커 설정
            default_breakers = {
                'user_service': CircuitBreaker('user_service', 5, 60),
                'product_service': CircuitBreaker('product_service', 5, 60),
                'order_service': CircuitBreaker('order_service', 5, 60),
                'payment_service': CircuitBreaker('payment_service', 3, 120),
                'analytics_service': CircuitBreaker('analytics_service', 10, 30)
            }
            
            self.circuit_breakers.update(default_breakers)
            
            logger.info(f"{len(self.circuit_breakers)}개의 서킷 브레이커 설정 완료")
            
        except Exception as e:
            logger.error(f"서킷 브레이커 설정 오류: {e}")
    
    async def handle_request(self, request: web.Request) -> web.Response:
        """요청 처리"""
        start_time = time.time()
        route_id = None
        status_code = 500
        
        try:
            # 1. 라우트 매칭
            route = self._match_route(request.path, request.method)
            if not route:
                return web.Response(text="Route not found", status=404)
            
            route_id = route.id
            
            # 2. 인증 검사
            auth_result = await self._authenticate_request(request, route)
            if not auth_result['success']:
                return web.Response(text=auth_result['message'], status=401)
            
            # 3. 레이트 리미트 검사
            rate_limit_result = await self._check_rate_limit(request, route, auth_result['user_id'])
            if not rate_limit_result['success']:
                return web.Response(text="Rate limit exceeded", status=429)
            
            # 4. 서킷 브레이커 검사
            circuit_result = self._check_circuit_breaker(route.target_url)
            if not circuit_result['success']:
                return web.Response(text="Service temporarily unavailable", status=503)
            
            # 5. 요청 변환
            transformed_request = await self._transform_request(request, route)
            
            # 6. 백엔드 서비스 호출
            response = await self._call_backend_service(transformed_request, route)
            
            # 7. 응답 변환
            transformed_response = await self._transform_response(response, route)
            
            # 8. 캐싱
            await self._cache_response(request, transformed_response, route)
            
            # 9. 메트릭 업데이트
            status_code = transformed_response.status
            self._update_metrics(route, request.method, status_code, time.time() - start_time)
            
            # 10. 서킷 브레이커 성공 기록
            self._record_circuit_breaker_success(route.target_url)
            
            return transformed_response
            
        except Exception as e:
            logger.error(f"요청 처리 오류: {e}")
            
            # 서킷 브레이커 실패 기록
            if route_id:
                route = self.routes.get(route_id)
                if route:
                    self._record_circuit_breaker_failure(route.target_url)
            
            # 에러 메트릭 업데이트
            self.error_counter.labels(route=route_id or 'unknown', error_type='exception').inc()
            
            return web.Response(text="Internal server error", status=500)
    
    def _match_route(self, path: str, method: str) -> Optional[APIRoute]:
        """라우트 매칭"""
        try:
            for route in self.routes.values():
                if self._path_matches(route.path, path) and route.method.value == method:
                    return route
            return None
            
        except Exception as e:
            logger.error(f"라우트 매칭 오류: {e}")
            return None
    
    def _path_matches(self, route_path: str, request_path: str) -> bool:
        """경로 매칭"""
        try:
            # 간단한 경로 매칭 (실제로는 더 복잡한 패턴 매칭 필요)
            if route_path == request_path:
                return True
            
            # 파라미터 매칭 (예: /users/{id})
            if '{' in route_path:
                route_parts = route_path.split('/')
                request_parts = request_path.split('/')
                
                if len(route_parts) != len(request_parts):
                    return False
                
                for route_part, request_part in zip(route_parts, request_parts):
                    if route_part.startswith('{') and route_part.endswith('}'):
                        continue
                    if route_part != request_part:
                        return False
                
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"경로 매칭 오류: {e}")
            return False
    
    async def _authenticate_request(self, request: web.Request, route: APIRoute) -> Dict[str, Any]:
        """요청 인증"""
        try:
            if route.auth_type == AuthType.NONE:
                return {'success': True, 'user_id': None}
            
            elif route.auth_type == AuthType.API_KEY:
                return await self._authenticate_api_key(request)
            
            elif route.auth_type == AuthType.JWT:
                return await self._authenticate_jwt(request)
            
            elif route.auth_type == AuthType.OAUTH2:
                return await self._authenticate_oauth2(request)
            
            elif route.auth_type == AuthType.BASIC:
                return await self._authenticate_basic(request)
            
            return {'success': False, 'message': 'Unsupported authentication type'}
            
        except Exception as e:
            logger.error(f"인증 오류: {e}")
            return {'success': False, 'message': 'Authentication failed'}
    
    async def _authenticate_api_key(self, request: web.Request) -> Dict[str, Any]:
        """API 키 인증"""
        try:
            # API 키 추출
            api_key = request.headers.get('X-API-Key') or request.query.get('api_key')
            
            if not api_key:
                return {'success': False, 'message': 'API key required'}
            
            # API 키 검증
            key_info = self.api_keys.get(api_key)
            if not key_info or not key_info.is_active:
                return {'success': False, 'message': 'Invalid API key'}
            
            # 만료 검사
            if key_info.expires_at and key_info.expires_at < datetime.now():
                return {'success': False, 'message': 'API key expired'}
            
            # 사용 시간 업데이트
            key_info.last_used = datetime.now()
            
            return {
                'success': True,
                'user_id': key_info.user_id,
                'permissions': key_info.permissions,
                'api_key': key_info
            }
            
        except Exception as e:
            logger.error(f"API 키 인증 오류: {e}")
            return {'success': False, 'message': 'API key authentication failed'}
    
    async def _authenticate_jwt(self, request: web.Request) -> Dict[str, Any]:
        """JWT 인증"""
        try:
            # JWT 토큰 추출
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'Bearer token required'}
            
            token = auth_header[7:]  # 'Bearer ' 제거
            
            # JWT 검증
            secret = self.config.get('jwt_secret', 'your-secret-key')
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            
            return {
                'success': True,
                'user_id': payload.get('user_id'),
                'permissions': payload.get('permissions', []),
                'payload': payload
            }
            
        except jwt.ExpiredSignatureError:
            return {'success': False, 'message': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'message': 'Invalid token'}
        except Exception as e:
            logger.error(f"JWT 인증 오류: {e}")
            return {'success': False, 'message': 'JWT authentication failed'}
    
    async def _authenticate_oauth2(self, request: web.Request) -> Dict[str, Any]:
        """OAuth2 인증"""
        try:
            # OAuth2 토큰 추출
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return {'success': False, 'message': 'Bearer token required'}
            
            token = auth_header[7:]
            
            # OAuth2 토큰 검증 (실제로는 OAuth2 서버에 검증 요청)
            # 여기서는 간단한 구현
            oauth_config = self.config.get('oauth2', {})
            validation_url = oauth_config.get('validation_url')
            
            if validation_url:
                async with self.session.get(validation_url, headers={'Authorization': f'Bearer {token}'}) as response:
                    if response.status == 200:
                        user_info = await response.json()
                        return {
                            'success': True,
                            'user_id': user_info.get('user_id'),
                            'permissions': user_info.get('permissions', []),
                            'user_info': user_info
                        }
            
            return {'success': False, 'message': 'OAuth2 validation failed'}
            
        except Exception as e:
            logger.error(f"OAuth2 인증 오류: {e}")
            return {'success': False, 'message': 'OAuth2 authentication failed'}
    
    async def _authenticate_basic(self, request: web.Request) -> Dict[str, Any]:
        """Basic 인증"""
        try:
            # Basic 인증 헤더 추출
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Basic '):
                return {'success': False, 'message': 'Basic authentication required'}
            
            credentials = auth_header[6:]  # 'Basic ' 제거
            decoded = base64.b64decode(credentials).decode('utf-8')
            username, password = decoded.split(':', 1)
            
            # 사용자 검증 (실제로는 데이터베이스에서 검증)
            # 여기서는 간단한 구현
            if username == 'admin' and password == 'password':
                return {
                    'success': True,
                    'user_id': username,
                    'permissions': ['read', 'write']
                }
            
            return {'success': False, 'message': 'Invalid credentials'}
            
        except Exception as e:
            logger.error(f"Basic 인증 오류: {e}")
            return {'success': False, 'message': 'Basic authentication failed'}
    
    async def _check_rate_limit(self, request: web.Request, route: APIRoute, user_id: Optional[str]) -> Dict[str, Any]:
        """레이트 리미트 검사"""
        try:
            if not route.rate_limit:
                return {'success': True}
            
            # 레이트 리미트 키 생성
            limit_key = self._generate_rate_limit_key(request, route, user_id)
            
            # Redis에서 현재 카운트 확인
            current_count = self.redis_client.get(f"rate_limit:{limit_key}")
            current_count = int(current_count) if current_count else 0
            
            # 리미트 확인
            limit = route.rate_limit.get('limit', 100)
            window = route.rate_limit.get('window', 3600)  # 1시간
            
            if current_count >= limit:
                return {'success': False, 'message': 'Rate limit exceeded'}
            
            # 카운트 증가
            pipe = self.redis_client.pipeline()
            pipe.incr(f"rate_limit:{limit_key}")
            pipe.expire(f"rate_limit:{limit_key}", window)
            pipe.execute()
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"레이트 리미트 검사 오류: {e}")
            return {'success': True}  # 오류 시 허용
    
    def _generate_rate_limit_key(self, request: web.Request, route: APIRoute, user_id: Optional[str]) -> str:
        """레이트 리미트 키 생성"""
        try:
            rate_limit_type = route.rate_limit.get('type', 'ip')
            
            if rate_limit_type == 'user' and user_id:
                return f"user:{user_id}:{route.id}"
            elif rate_limit_type == 'api_key' and user_id:
                return f"apikey:{user_id}:{route.id}"
            else:
                # IP 기반
                client_ip = request.remote
                return f"ip:{client_ip}:{route.id}"
                
        except Exception as e:
            logger.error(f"레이트 리미트 키 생성 오류: {e}")
            return f"global:{route.id}"
    
    def _check_circuit_breaker(self, service_url: str) -> Dict[str, Any]:
        """서킷 브레이커 검사"""
        try:
            service_name = self._extract_service_name(service_url)
            breaker = self.circuit_breakers.get(service_name)
            
            if not breaker:
                return {'success': True}
            
            if breaker.state == "OPEN":
                # 복구 시간 확인
                if breaker.last_failure_time:
                    recovery_time = breaker.last_failure_time + timedelta(seconds=breaker.recovery_timeout)
                    if datetime.now() < recovery_time:
                        return {'success': False, 'message': 'Circuit breaker open'}
                    else:
                        breaker.state = "HALF_OPEN"
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"서킷 브레이커 검사 오류: {e}")
            return {'success': True}
    
    def _extract_service_name(self, url: str) -> str:
        """서비스 이름 추출"""
        try:
            # URL에서 서비스 이름 추출
            if 'user-service' in url:
                return 'user_service'
            elif 'product-service' in url:
                return 'product_service'
            elif 'order-service' in url:
                return 'order_service'
            elif 'payment-service' in url:
                return 'payment_service'
            elif 'analytics-service' in url:
                return 'analytics_service'
            else:
                return 'default_service'
                
        except Exception as e:
            logger.error(f"서비스 이름 추출 오류: {e}")
            return 'default_service'
    
    async def _transform_request(self, request: web.Request, route: APIRoute) -> web.Request:
        """요청 변환"""
        try:
            if not route.transformation:
                return request
            
            # 헤더 변환
            headers = dict(request.headers)
            for header_map in route.transformation.get('headers', []):
                if header_map.get('action') == 'add':
                    headers[header_map['name']] = header_map['value']
                elif header_map.get('action') == 'remove':
                    headers.pop(header_map['name'], None)
            
            # 쿼리 파라미터 변환
            query = dict(request.query)
            for param_map in route.transformation.get('query_params', []):
                if param_map.get('action') == 'add':
                    query[param_map['name']] = param_map['value']
                elif param_map.get('action') == 'remove':
                    query.pop(param_map['name'], None)
            
            # 새로운 요청 생성
            transformed_request = web.Request(
                method=request.method,
                url=request.url,
                headers=headers,
                query=query,
                body=request.body
            )
            
            return transformed_request
            
        except Exception as e:
            logger.error(f"요청 변환 오류: {e}")
            return request
    
    async def _call_backend_service(self, request: web.Request, route: APIRoute) -> web.Response:
        """백엔드 서비스 호출"""
        try:
            # 타임아웃 설정
            timeout = ClientTimeout(total=route.timeout)
            
            # 요청 데이터 준비
            headers = dict(request.headers)
            headers.pop('Host', None)  # Host 헤더 제거
            
            # 백엔드 서비스 호출
            async with ClientSession(timeout=timeout) as session:
                for attempt in range(route.retry_count):
                    try:
                        async with session.request(
                            method=request.method,
                            url=route.target_url,
                            headers=headers,
                            params=request.query,
                            data=request.body
                        ) as response:
                            return response
                    except Exception as e:
                        if attempt == route.retry_count - 1:
                            raise e
                        await asyncio.sleep(1)  # 재시도 전 대기
            
        except Exception as e:
            logger.error(f"백엔드 서비스 호출 오류: {e}")
            raise
    
    async def _transform_response(self, response: web.Response, route: APIRoute) -> web.Response:
        """응답 변환"""
        try:
            if not route.transformation:
                return response
            
            # 응답 헤더 변환
            headers = dict(response.headers)
            for header_map in route.transformation.get('response_headers', []):
                if header_map.get('action') == 'add':
                    headers[header_map['name']] = header_map['value']
                elif header_map.get('action') == 'remove':
                    headers.pop(header_map['name'], None)
            
            # 새로운 응답 생성
            transformed_response = web.Response(
                status=response.status,
                headers=headers,
                body=response.body
            )
            
            return transformed_response
            
        except Exception as e:
            logger.error(f"응답 변환 오류: {e}")
            return response
    
    async def _cache_response(self, request: web.Request, response: web.Response, route: APIRoute):
        """응답 캐싱"""
        try:
            if not route.caching or request.method != 'GET':
                return
            
            # 캐시 키 생성
            cache_key = f"cache:{route.id}:{hashlib.md5(str(request.url).encode()).hexdigest()}"
            
            # 캐시 데이터 준비
            cache_data = {
                'status': response.status,
                'headers': dict(response.headers),
                'body': response.body.decode('utf-8') if response.body else '',
                'timestamp': datetime.now().isoformat()
            }
            
            # TTL 설정
            ttl = route.caching.get('ttl', 300)  # 기본 5분
            
            # Redis에 캐시 저장
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"응답 캐싱 오류: {e}")
    
    def _update_metrics(self, route: APIRoute, method: str, status: int, duration: float):
        """메트릭 업데이트"""
        try:
            # 요청 카운터
            self.request_counter.labels(route=route.name, method=method, status=status).inc()
            
            # 요청 지속시간
            self.request_duration.labels(route=route.name, method=method).observe(duration)
            
            # 활성 연결 수 (간단한 구현)
            if status < 400:
                self.active_connections.inc()
            else:
                self.active_connections.dec()
                
        except Exception as e:
            logger.error(f"메트릭 업데이트 오류: {e}")
    
    def _record_circuit_breaker_success(self, service_url: str):
        """서킷 브레이커 성공 기록"""
        try:
            service_name = self._extract_service_name(service_url)
            breaker = self.circuit_breakers.get(service_name)
            
            if breaker and breaker.state == "HALF_OPEN":
                breaker.state = "CLOSED"
                breaker.failure_count = 0
                
        except Exception as e:
            logger.error(f"서킷 브레이커 성공 기록 오류: {e}")
    
    def _record_circuit_breaker_failure(self, service_url: str):
        """서킷 브레이커 실패 기록"""
        try:
            service_name = self._extract_service_name(service_url)
            breaker = self.circuit_breakers.get(service_name)
            
            if breaker:
                breaker.failure_count += 1
                breaker.last_failure_time = datetime.now()
                
                if breaker.failure_count >= breaker.failure_threshold:
                    breaker.state = "OPEN"
                    
        except Exception as e:
            logger.error(f"서킷 브레이커 실패 기록 오류: {e}")
    
    def create_route(self, route_data: Dict[str, Any]) -> str:
        """라우트 생성"""
        try:
            route_id = str(uuid.uuid4())
            
            route = APIRoute(
                id=route_id,
                name=route_data['name'],
                path=route_data['path'],
                method=RouteMethod(route_data['method']),
                target_url=route_data['target_url'],
                auth_type=AuthType(route_data['auth_type']),
                rate_limit=route_data.get('rate_limit'),
                timeout=route_data.get('timeout', 30),
                retry_count=route_data.get('retry_count', 3),
                circuit_breaker=route_data.get('circuit_breaker'),
                caching=route_data.get('caching'),
                transformation=route_data.get('transformation'),
                monitoring=route_data.get('monitoring', True),
                enabled=route_data.get('enabled', True),
                created_at=datetime.now()
            )
            
            self.routes[route_id] = route
            
            # 데이터베이스에 저장
            self._save_route_to_db(route)
            
            logger.info(f"라우트 생성 완료: {route_id}")
            return route_id
            
        except Exception as e:
            logger.error(f"라우트 생성 오류: {e}")
            raise
    
    def _save_route_to_db(self, route: APIRoute):
        """라우트를 데이터베이스에 저장"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO api_routes 
                    (id, name, path, method, target_url, auth_type, rate_limit, 
                     timeout, retry_count, circuit_breaker, caching, transformation, 
                     monitoring, enabled, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    route.id,
                    route.name,
                    route.path,
                    route.method.value,
                    route.target_url,
                    route.auth_type.value,
                    json.dumps(route.rate_limit) if route.rate_limit else None,
                    route.timeout,
                    route.retry_count,
                    json.dumps(route.circuit_breaker) if route.circuit_breaker else None,
                    json.dumps(route.caching) if route.caching else None,
                    json.dumps(route.transformation) if route.transformation else None,
                    route.monitoring,
                    route.enabled,
                    route.created_at
                ))
                self.db_connection.commit()
                
        except Exception as e:
            logger.error(f"라우트 저장 오류: {e}")
            raise
    
    def get_route_stats(self, route_id: str) -> Optional[Dict[str, Any]]:
        """라우트 통계 조회"""
        try:
            route = self.routes.get(route_id)
            if not route:
                return None
            
            # Redis에서 통계 데이터 조회
            stats = {
                'route_id': route_id,
                'name': route.name,
                'path': route.path,
                'method': route.method.value,
                'total_requests': 0,
                'success_rate': 0.0,
                'avg_response_time': 0.0,
                'error_count': 0,
                'last_request': None
            }
            
            # Prometheus 메트릭에서 데이터 조회
            # 실제 구현에서는 Prometheus API를 사용해야 함
            
            return stats
            
        except Exception as e:
            logger.error(f"라우트 통계 조회 오류: {e}")
            raise
    
    def get_gateway_stats(self) -> Dict[str, Any]:
        """게이트웨이 전체 통계"""
        try:
            stats = {
                'total_routes': len(self.routes),
                'active_routes': len([r for r in self.routes.values() if r.enabled]),
                'total_api_keys': len(self.api_keys),
                'active_api_keys': len([k for k in self.api_keys.values() if k.is_active]),
                'circuit_breakers': {
                    name: {
                        'state': breaker.state,
                        'failure_count': breaker.failure_count,
                        'last_failure': breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
                    }
                    for name, breaker in self.circuit_breakers.items()
                },
                'uptime': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"게이트웨이 통계 조회 오류: {e}")
            raise

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 4
        },
        'database': {
            'host': 'localhost',
            'port': 5432,
            'name': 'your_program',
            'user': 'postgres',
            'password': 'password'
        },
        'jwt_secret': 'your-jwt-secret-key',
        'oauth2': {
            'validation_url': 'https://oauth2-server.com/validate'
        }
    }
    
    # API 게이트웨이 생성
    gateway = APIGatewayCore(config)
    
    # 라우트 생성 예시
    route_id = gateway.create_route({
        'name': 'User API',
        'path': '/api/users/{id}',
        'method': 'GET',
        'target_url': 'http://user-service:8080/users/{id}',
        'auth_type': 'jwt',
        'rate_limit': {
            'type': 'user',
            'limit': 100,
            'window': 3600
        },
        'timeout': 30,
        'retry_count': 3
    })
    
    print(f"라우트 생성 완료: {route_id}")
    
    # 게이트웨이 통계
    stats = gateway.get_gateway_stats()
    print(f"게이트웨이 통계: {stats}") 