"""
API 게이트웨이 시스템
라우팅, 인증, 권한 부여, 속도 제한, 로깅을 포함한 완전한 API 게이트웨이 플랫폼
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web, ClientSession, ClientTimeout
import websockets
import sqlite3
from pathlib import Path
import pickle
import hashlib
import hmac
import base64
import secrets
import struct
import socket
import ssl
import jwt
from jwt.exceptions import InvalidTokenError
import redis
from redis.exceptions import RedisError
import rate_limit
from rate_limit import RateLimiter
import circuit_breaker
from circuit_breaker import CircuitBreaker

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RouteType(Enum):
    """라우트 타입"""
    PROXY = "proxy"
    AGGREGATE = "aggregate"
    TRANSFORM = "transform"
    CACHE = "cache"
    WEBHOOK = "webhook"

class AuthType(Enum):
    """인증 타입"""
    NONE = "none"
    API_KEY = "api_key"
    JWT = "jwt"
    OAUTH2 = "oauth2"
    BASIC = "basic"

class RateLimitType(Enum):
    """속도 제한 타입"""
    NONE = "none"
    FIXED_WINDOW = "fixed_window"
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"

@dataclass
class Route:
    """라우트 정의"""
    route_id: str
    path: str
    method: str
    route_type: RouteType
    target_service: str
    target_endpoint: str
    auth_type: AuthType
    rate_limit_type: RateLimitType
    rate_limit_config: Dict[str, Any]
    timeout: int
    retry_config: Dict[str, Any]
    circuit_breaker_config: Dict[str, Any]
    cache_config: Dict[str, Any]
    transform_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class APIRequest:
    """API 요청"""
    request_id: str
    route_id: str
    method: str
    path: str
    headers: Dict[str, str]
    query_params: Dict[str, str]
    body: Any
    client_ip: str
    user_agent: str
    timestamp: datetime
    user_id: str = None
    session_id: str = None

@dataclass
class APIResponse:
    """API 응답"""
    request_id: str
    status_code: int
    headers: Dict[str, str]
    body: Any
    response_time: float
    timestamp: datetime
    error_message: str = None

@dataclass
class RateLimitRule:
    """속도 제한 규칙"""
    rule_id: str
    route_id: str
    limit_type: RateLimitType
    requests_per_minute: int
    burst_size: int
    window_size: int
    key_template: str
    created_at: datetime

class APIGateway:
    """API 게이트웨이 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.routes: Dict[str, Route] = {}
        self.rate_limiters: Dict[str, RateLimiter] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.cache: Dict[str, Any] = {}
        
        # Redis 클라이언트 (캐싱 및 세션)
        self.redis_client = None
        self._init_redis()
        
        # HTTP 클라이언트 세션
        self.http_session = None
        
        # 서비스 레지스트리
        self.service_registry = config.get('service_registry', {})
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './api_gateway.db'))
        self._init_database()
        
        # 기본 라우트 로드
        self._load_default_routes()
        
        # 웹 서버
        self.app = web.Application()
        self._setup_middleware()
        self._setup_routes()
        
        # 모니터링
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
        logger.info("API 게이트웨이 시스템 초기화 완료")
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 0),
                decode_responses=True
            )
            
            # Redis 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 클라이언트 초기화 완료")
            
        except RedisError as e:
            logger.warning(f"Redis 클라이언트 초기화 실패: {e}")
            self.redis_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 라우트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS routes (
                    route_id TEXT PRIMARY KEY,
                    path TEXT,
                    method TEXT,
                    route_type TEXT,
                    target_service TEXT,
                    target_endpoint TEXT,
                    auth_type TEXT,
                    rate_limit_type TEXT,
                    rate_limit_config TEXT,
                    timeout INTEGER,
                    retry_config TEXT,
                    circuit_breaker_config TEXT,
                    cache_config TEXT,
                    transform_config TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 요청 로그 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_logs (
                    request_id TEXT PRIMARY KEY,
                    route_id TEXT,
                    method TEXT,
                    path TEXT,
                    client_ip TEXT,
                    user_agent TEXT,
                    user_id TEXT,
                    status_code INTEGER,
                    response_time REAL,
                    timestamp TEXT,
                    error_message TEXT,
                    FOREIGN KEY (route_id) REFERENCES routes (route_id)
                )
            ''')
            
            # 속도 제한 규칙 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rate_limit_rules (
                    rule_id TEXT PRIMARY KEY,
                    route_id TEXT,
                    limit_type TEXT,
                    requests_per_minute INTEGER,
                    burst_size INTEGER,
                    window_size INTEGER,
                    key_template TEXT,
                    created_at TEXT,
                    FOREIGN KEY (route_id) REFERENCES routes (route_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("API 게이트웨이 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_default_routes(self):
        """기본 라우트 로드"""
        try:
            default_routes = [
                {
                    'path': '/api/v1/users',
                    'method': 'GET',
                    'route_type': RouteType.PROXY,
                    'target_service': 'user_service',
                    'target_endpoint': '/users',
                    'auth_type': AuthType.JWT,
                    'rate_limit_type': RateLimitType.SLIDING_WINDOW,
                    'rate_limit_config': {'requests_per_minute': 100, 'burst_size': 10},
                    'timeout': 30,
                    'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                    'circuit_breaker_config': {'failure_threshold': 5, 'recovery_timeout': 60},
                    'cache_config': {'enabled': True, 'ttl': 300},
                    'transform_config': {}
                },
                {
                    'path': '/api/v1/auth/login',
                    'method': 'POST',
                    'route_type': RouteType.PROXY,
                    'target_service': 'auth_service',
                    'target_endpoint': '/auth/login',
                    'auth_type': AuthType.NONE,
                    'rate_limit_type': RateLimitType.FIXED_WINDOW,
                    'rate_limit_config': {'requests_per_minute': 10, 'burst_size': 5},
                    'timeout': 30,
                    'retry_config': {'max_retries': 1, 'backoff_factor': 1},
                    'circuit_breaker_config': {'failure_threshold': 3, 'recovery_timeout': 30},
                    'cache_config': {'enabled': False},
                    'transform_config': {}
                },
                {
                    'path': '/api/v1/payments',
                    'method': 'POST',
                    'route_type': RouteType.PROXY,
                    'target_service': 'payment_service',
                    'target_endpoint': '/payments',
                    'auth_type': AuthType.JWT,
                    'rate_limit_type': RateLimitType.TOKEN_BUCKET,
                    'rate_limit_config': {'requests_per_minute': 50, 'burst_size': 20},
                    'timeout': 60,
                    'retry_config': {'max_retries': 2, 'backoff_factor': 1.5},
                    'circuit_breaker_config': {'failure_threshold': 3, 'recovery_timeout': 120},
                    'cache_config': {'enabled': False},
                    'transform_config': {}
                },
                {
                    'path': '/api/v1/notifications',
                    'method': 'POST',
                    'route_type': RouteType.PROXY,
                    'target_service': 'notification_service',
                    'target_endpoint': '/notifications',
                    'auth_type': AuthType.JWT,
                    'rate_limit_type': RateLimitType.SLIDING_WINDOW,
                    'rate_limit_config': {'requests_per_minute': 200, 'burst_size': 50},
                    'timeout': 30,
                    'retry_config': {'max_retries': 3, 'backoff_factor': 2},
                    'circuit_breaker_config': {'failure_threshold': 5, 'recovery_timeout': 60},
                    'cache_config': {'enabled': False},
                    'transform_config': {}
                }
            ]
            
            for route_info in default_routes:
                self.create_route(route_info)
            
            logger.info(f"{len(default_routes)}개 기본 라우트 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 라우트 로드 오류: {e}")
    
    def _setup_middleware(self):
        """미들웨어 설정"""
        try:
            # CORS 미들웨어
            self.app.middlewares.append(self._cors_middleware)
            
            # 로깅 미들웨어
            self.app.middlewares.append(self._logging_middleware)
            
            # 인증 미들웨어
            self.app.middlewares.append(self._auth_middleware)
            
            # 속도 제한 미들웨어
            self.app.middlewares.append(self._rate_limit_middleware)
            
            logger.info("미들웨어 설정 완료")
            
        except Exception as e:
            logger.error(f"미들웨어 설정 오류: {e}")
    
    async def _cors_middleware(self, request, handler):
        """CORS 미들웨어"""
        try:
            response = await handler(request)
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            return response
        except Exception as e:
            logger.error(f"CORS 미들웨어 오류: {e}")
            return await handler(request)
    
    async def _logging_middleware(self, request, handler):
        """로깅 미들웨어"""
        try:
            start_time = time.time()
            
            # 요청 로깅
            request_id = str(uuid.uuid4())
            request['request_id'] = request_id
            
            logger.info(f"요청 시작: {request_id} - {request.method} {request.path}")
            
            # 핸들러 실행
            response = await handler(request)
            
            # 응답 시간 계산
            response_time = time.time() - start_time
            
            # 응답 로깅
            logger.info(f"요청 완료: {request_id} - {response.status} ({response_time:.3f}s)")
            
            # 메트릭 업데이트
            self.request_count += 1
            self.response_times.append(response_time)
            
            if response.status >= 400:
                self.error_count += 1
            
            return response
            
        except Exception as e:
            logger.error(f"로깅 미들웨어 오류: {e}")
            self.error_count += 1
            return web.Response(status=500, text="Internal Server Error")
    
    async def _auth_middleware(self, request, handler):
        """인증 미들웨어"""
        try:
            route = self._find_route(request.path, request.method)
            
            if not route:
                return await handler(request)
            
            if route.auth_type == AuthType.NONE:
                return await handler(request)
            
            # 인증 토큰 추출
            auth_header = request.headers.get('Authorization', '')
            
            if route.auth_type == AuthType.JWT:
                if not auth_header.startswith('Bearer '):
                    return web.Response(status=401, text="Unauthorized")
                
                token = auth_header[7:]
                user_id = await self._verify_jwt_token(token)
                
                if not user_id:
                    return web.Response(status=401, text="Invalid token")
                
                request['user_id'] = user_id
                
            elif route.auth_type == AuthType.API_KEY:
                if not auth_header.startswith('ApiKey '):
                    return web.Response(status=401, text="Unauthorized")
                
                api_key = auth_header[7:]
                user_id = await self._verify_api_key(api_key)
                
                if not user_id:
                    return web.Response(status=401, text="Invalid API key")
                
                request['user_id'] = user_id
            
            return await handler(request)
            
        except Exception as e:
            logger.error(f"인증 미들웨어 오류: {e}")
            return web.Response(status=401, text="Authentication failed")
    
    async def _rate_limit_middleware(self, request, handler):
        """속도 제한 미들웨어"""
        try:
            route = self._find_route(request.path, request.method)
            
            if not route or route.rate_limit_type == RateLimitType.NONE:
                return await handler(request)
            
            # 속도 제한 키 생성
            user_id = request.get('user_id', 'anonymous')
            client_ip = request.remote
            
            if route.rate_limit_config.get('key_template') == 'user':
                rate_limit_key = f"rate_limit:{route.route_id}:{user_id}"
            else:
                rate_limit_key = f"rate_limit:{route.route_id}:{client_ip}"
            
            # 속도 제한 확인
            rate_limiter = self.rate_limiters.get(route.route_id)
            if rate_limiter:
                if not rate_limiter.is_allowed(rate_limit_key):
                    return web.Response(status=429, text="Rate limit exceeded")
            
            return await handler(request)
            
        except Exception as e:
            logger.error(f"속도 제한 미들웨어 오류: {e}")
            return await handler(request)
    
    def _setup_routes(self):
        """라우트 설정"""
        try:
            # 동적 라우트 핸들러
            async def dynamic_handler(request):
                return await self._handle_request(request)
            
            # 모든 경로에 대해 동적 핸들러 등록
            self.app.router.add_route('*', '/{path:.*}', dynamic_handler)
            
            logger.info("라우트 설정 완료")
            
        except Exception as e:
            logger.error(f"라우트 설정 오류: {e}")
    
    def create_route(self, route_info: Dict[str, Any]) -> str:
        """라우트 생성"""
        try:
            route_id = str(uuid.uuid4())
            
            route = Route(
                route_id=route_id,
                path=route_info['path'],
                method=route_info['method'],
                route_type=RouteType(route_info['route_type']),
                target_service=route_info['target_service'],
                target_endpoint=route_info['target_endpoint'],
                auth_type=AuthType(route_info['auth_type']),
                rate_limit_type=RateLimitType(route_info['rate_limit_type']),
                rate_limit_config=route_info.get('rate_limit_config', {}),
                timeout=route_info.get('timeout', 30),
                retry_config=route_info.get('retry_config', {}),
                circuit_breaker_config=route_info.get('circuit_breaker_config', {}),
                cache_config=route_info.get('cache_config', {}),
                transform_config=route_info.get('transform_config', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.routes[route_id] = route
            
            # 속도 제한기 생성
            if route.rate_limit_type != RateLimitType.NONE:
                self.rate_limiters[route_id] = RateLimiter(
                    requests_per_minute=route.rate_limit_config.get('requests_per_minute', 100),
                    burst_size=route.rate_limit_config.get('burst_size', 10)
                )
            
            # 서킷 브레이커 생성
            self.circuit_breakers[route_id] = CircuitBreaker(
                failure_threshold=route.circuit_breaker_config.get('failure_threshold', 5),
                recovery_timeout=route.circuit_breaker_config.get('recovery_timeout', 60)
            )
            
            # 데이터베이스에 저장
            self._save_route_to_db(route)
            
            logger.info(f"라우트 생성 완료: {route_id}")
            return route_id
            
        except Exception as e:
            logger.error(f"라우트 생성 오류: {e}")
            raise
    
    def _find_route(self, path: str, method: str) -> Optional[Route]:
        """라우트 찾기"""
        try:
            for route in self.routes.values():
                if route.path == path and route.method == method:
                    return route
            return None
        except Exception as e:
            logger.error(f"라우트 찾기 오류: {e}")
            return None
    
    async def _handle_request(self, request) -> web.Response:
        """요청 처리"""
        try:
            start_time = time.time()
            request_id = request.get('request_id', str(uuid.uuid4()))
            
            # 라우트 찾기
            route = self._find_route(request.path, request.method)
            
            if not route:
                return web.Response(status=404, text="Route not found")
            
            # 요청 정보 생성
            api_request = APIRequest(
                request_id=request_id,
                route_id=route.route_id,
                method=request.method,
                path=request.path,
                headers=dict(request.headers),
                query_params=dict(request.query),
                body=await request.text() if request.body_exists else None,
                client_ip=request.remote,
                user_agent=request.headers.get('User-Agent', ''),
                timestamp=datetime.now(),
                user_id=request.get('user_id'),
                session_id=request.headers.get('X-Session-ID')
            )
            
            # 캐시 확인
            if route.cache_config.get('enabled', False):
                cached_response = await self._get_cached_response(api_request)
                if cached_response:
                    return cached_response
            
            # 서킷 브레이커 확인
            circuit_breaker = self.circuit_breakers.get(route.route_id)
            if circuit_breaker and not circuit_breaker.is_closed():
                return web.Response(status=503, text="Service temporarily unavailable")
            
            # 타겟 서비스 호출
            try:
                response = await self._call_target_service(route, api_request)
                
                # 성공 시 서킷 브레이커 리셋
                if circuit_breaker:
                    circuit_breaker.on_success()
                
                # 응답 캐싱
                if route.cache_config.get('enabled', False) and response.status == 200:
                    await self._cache_response(api_request, response)
                
                return response
                
            except Exception as e:
                # 실패 시 서킷 브레이커 업데이트
                if circuit_breaker:
                    circuit_breaker.on_failure()
                
                logger.error(f"타겟 서비스 호출 오류: {e}")
                return web.Response(status=500, text="Internal Server Error")
            
        except Exception as e:
            logger.error(f"요청 처리 오류: {e}")
            return web.Response(status=500, text="Internal Server Error")
    
    async def _call_target_service(self, route: Route, api_request: APIRequest) -> web.Response:
        """타겟 서비스 호출"""
        try:
            # 타겟 URL 구성
            target_service = self.service_registry.get(route.target_service)
            if not target_service:
                raise ValueError(f"서비스를 찾을 수 없습니다: {route.target_service}")
            
            target_url = f"http://{target_service['host']}:{target_service['port']}{route.target_endpoint}"
            
            # HTTP 세션 생성
            if not self.http_session:
                timeout = ClientTimeout(total=route.timeout)
                self.http_session = ClientSession(timeout=timeout)
            
            # 요청 헤더 준비
            headers = {}
            for key, value in api_request.headers.items():
                if key.lower() not in ['host', 'content-length']:
                    headers[key] = value
            
            # 요청 본문 준비
            data = None
            if api_request.body:
                if api_request.method in ['POST', 'PUT', 'PATCH']:
                    data = api_request.body
                    headers['Content-Type'] = 'application/json'
            
            # HTTP 요청 전송
            async with self.http_session.request(
                method=api_request.method,
                url=target_url,
                headers=headers,
                data=data,
                params=api_request.query_params
            ) as response:
                
                # 응답 본문 읽기
                response_body = await response.text()
                
                # 응답 헤더 준비
                response_headers = {}
                for key, value in response.headers.items():
                    if key.lower() not in ['transfer-encoding', 'connection']:
                        response_headers[key] = value
                
                return web.Response(
                    status=response.status,
                    headers=response_headers,
                    text=response_body
                )
                
        except Exception as e:
            logger.error(f"타겟 서비스 호출 오류: {e}")
            raise
    
    async def _verify_jwt_token(self, token: str) -> Optional[str]:
        """JWT 토큰 검증"""
        try:
            # JWT 시크릿 키 (실제로는 설정에서 가져옴)
            secret_key = self.config.get('jwt_secret', 'your-secret-key')
            
            # 토큰 디코딩
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            
            # 사용자 ID 반환
            return payload.get('user_id')
            
        except InvalidTokenError as e:
            logger.warning(f"JWT 토큰 검증 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT 토큰 검증 오류: {e}")
            return None
    
    async def _verify_api_key(self, api_key: str) -> Optional[str]:
        """API 키 검증"""
        try:
            if not self.redis_client:
                return None
            
            # Redis에서 API 키 검증
            user_id = self.redis_client.get(f"api_key:{api_key}")
            
            if user_id:
                return user_id.decode('utf-8')
            
            return None
            
        except Exception as e:
            logger.error(f"API 키 검증 오류: {e}")
            return None
    
    async def _get_cached_response(self, api_request: APIRequest) -> Optional[web.Response]:
        """캐시된 응답 조회"""
        try:
            if not self.redis_client:
                return None
            
            # 캐시 키 생성
            cache_key = f"cache:{api_request.route_id}:{hash(api_request.path + str(api_request.query_params))}"
            
            # 캐시에서 응답 조회
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                cached_response = json.loads(cached_data)
                return web.Response(
                    status=cached_response['status_code'],
                    headers=cached_response['headers'],
                    text=cached_response['body']
                )
            
            return None
            
        except Exception as e:
            logger.error(f"캐시 응답 조회 오류: {e}")
            return None
    
    async def _cache_response(self, api_request: APIRequest, response: web.Response):
        """응답 캐싱"""
        try:
            if not self.redis_client:
                return
            
            # 캐시 키 생성
            cache_key = f"cache:{api_request.route_id}:{hash(api_request.path + str(api_request.query_params))}"
            
            # 캐시 데이터 준비
            cache_data = {
                'status_code': response.status,
                'headers': dict(response.headers),
                'body': response.text,
                'timestamp': datetime.now().isoformat()
            }
            
            # 캐시 TTL 설정
            route = self.routes.get(api_request.route_id)
            ttl = route.cache_config.get('ttl', 300) if route else 300
            
            # Redis에 캐시 저장
            self.redis_client.setex(
                cache_key,
                ttl,
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.error(f"응답 캐싱 오류: {e}")
    
    def get_route_info(self, route_id: str) -> Optional[Dict[str, Any]]:
        """라우트 정보 조회"""
        try:
            route = self.routes.get(route_id)
            if not route:
                return None
            
            return {
                'route_id': route.route_id,
                'path': route.path,
                'method': route.method,
                'route_type': route.route_type.value,
                'target_service': route.target_service,
                'target_endpoint': route.target_endpoint,
                'auth_type': route.auth_type.value,
                'rate_limit_type': route.rate_limit_type.value,
                'rate_limit_config': route.rate_limit_config,
                'timeout': route.timeout,
                'retry_config': route.retry_config,
                'circuit_breaker_config': route.circuit_breaker_config,
                'cache_config': route.cache_config,
                'transform_config': route.transform_config,
                'created_at': route.created_at.isoformat(),
                'updated_at': route.updated_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"라우트 정보 조회 오류: {e}")
            return None
    
    def get_gateway_metrics(self) -> Dict[str, Any]:
        """게이트웨이 메트릭 조회"""
        try:
            avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
            
            return {
                'total_requests': self.request_count,
                'error_requests': self.error_count,
                'success_rate': ((self.request_count - self.error_count) / self.request_count * 100) if self.request_count > 0 else 0,
                'average_response_time': avg_response_time,
                'total_routes': len(self.routes),
                'active_circuit_breakers': sum(1 for cb in self.circuit_breakers.values() if not cb.is_closed()),
                'cache_hit_rate': 0.0,  # 실제로는 캐시 히트율 계산 필요
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"게이트웨이 메트릭 조회 오류: {e}")
            return {}
    
    def _save_route_to_db(self, route: Route):
        """라우트를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO routes 
                (route_id, path, method, route_type, target_service, target_endpoint,
                 auth_type, rate_limit_type, rate_limit_config, timeout, retry_config,
                 circuit_breaker_config, cache_config, transform_config, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                route.route_id,
                route.path,
                route.method,
                route.route_type.value,
                route.target_service,
                route.target_endpoint,
                route.auth_type.value,
                route.rate_limit_type.value,
                json.dumps(route.rate_limit_config),
                route.timeout,
                json.dumps(route.retry_config),
                json.dumps(route.circuit_breaker_config),
                json.dumps(route.cache_config),
                json.dumps(route.transform_config),
                route.created_at.isoformat(),
                route.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"라우트 데이터베이스 저장 오류: {e}")
    
    async def start(self, host: str = '0.0.0.0', port: int = 8080):
        """게이트웨이 시작"""
        try:
            logger.info(f"API 게이트웨이 시작: {host}:{port}")
            runner = web.AppRunner(self.app)
            await runner.setup()
            site = web.TCPSite(runner, host, port)
            await site.start()
            
            logger.info("API 게이트웨이 실행 중...")
            
            # 무한 루프로 서버 유지
            while True:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"API 게이트웨이 시작 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            if self.http_session:
                asyncio.create_task(self.http_session.close())
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("API 게이트웨이 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './api_gateway.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'jwt_secret': 'your-secret-key',
        'service_registry': {
            'user_service': {'host': 'localhost', 'port': 8081},
            'auth_service': {'host': 'localhost', 'port': 8082},
            'payment_service': {'host': 'localhost', 'port': 8083},
            'notification_service': {'host': 'localhost', 'port': 8084}
        }
    }
    
    # API 게이트웨이 생성
    gateway = APIGateway(config)
    
    # 사용자 정의 라우트 생성
    custom_route = {
        'path': '/api/v1/custom',
        'method': 'GET',
        'route_type': 'proxy',
        'target_service': 'user_service',
        'target_endpoint': '/custom',
        'auth_type': 'jwt',
        'rate_limit_type': 'sliding_window',
        'rate_limit_config': {'requests_per_minute': 50, 'burst_size': 5},
        'timeout': 30,
        'retry_config': {'max_retries': 3, 'backoff_factor': 2},
        'circuit_breaker_config': {'failure_threshold': 5, 'recovery_timeout': 60},
        'cache_config': {'enabled': True, 'ttl': 300},
        'transform_config': {}
    }
    
    route_id = gateway.create_route(custom_route)
    print(f"라우트 생성 완료: {route_id}")
    
    # 라우트 정보 조회
    route_info = gateway.get_route_info(route_id)
    print(f"라우트 정보: {route_info}")
    
    # 게이트웨이 메트릭 조회
    metrics = gateway.get_gateway_metrics()
    print(f"게이트웨이 메트릭: {metrics}")
    
    # 게이트웨이 시작
    asyncio.run(gateway.start()) 