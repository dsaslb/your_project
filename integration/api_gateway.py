"""
API 게이트웨이 시스템
요청 라우팅, 인증, 권한 관리, 속도 제한, 로깅, 모니터링 기능
"""

import json
import logging
import time
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
from collections import defaultdict, deque
import threading
import requests
from functools import wraps

# 로깅 설정
logger = logging.getLogger(__name__)

class RequestMethod(Enum):
    """HTTP 요청 메서드"""
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

@dataclass
class RouteDefinition:
    """라우트 정의"""
    id: str
    path: str
    method: RequestMethod
    target_url: str
    auth_type: AuthType
    rate_limit: int  # 분당 요청 수
    timeout: int  # 초 단위
    retry_count: int
    headers: Dict[str, str]
    parameters: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool

@dataclass
class ApiKey:
    """API 키"""
    id: str
    key: str
    name: str
    user_id: str
    permissions: List[str]
    rate_limit: int
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool
    last_used: Optional[datetime]

@dataclass
class RequestLog:
    """요청 로그"""
    id: str
    route_id: str
    method: str
    path: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    request_headers: Dict[str, str]
    request_body: Optional[str]
    response_status: int
    response_headers: Dict[str, str]
    response_body: Optional[str]
    processing_time: float
    timestamp: datetime
    error_message: Optional[str]

class RateLimiter:
    """속도 제한 관리"""
    
    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(lambda: deque())
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str, limit: int, window: int = 60) -> bool:
        """요청 허용 여부 확인"""
        with self.lock:
            now = time.time()
            requests = self.requests[key]
            
            # 윈도우 시간 이전의 요청 제거
            while requests and requests[0] < now - window:
                requests.popleft()
            
            # 제한 확인
            if len(requests) >= limit:
                return False
            
            # 새 요청 추가
            requests.append(now)
            return True
    
    def get_remaining(self, key: str, limit: int, window: int = 60) -> int:
        """남은 요청 수 조회"""
        with self.lock:
            now = time.time()
            requests = self.requests[key]
            
            # 윈도우 시간 이전의 요청 제거
            while requests and requests[0] < now - window:
                requests.popleft()
            
            return max(0, limit - len(requests))

class ApiGateway:
    """API 게이트웨이"""
    
    def __init__(self, db_path: str = "data/integration/gateway.db"):
        self.db_path = db_path
        self.routes: Dict[str, RouteDefinition] = {}
        self.api_keys: Dict[str, ApiKey] = {}
        self.rate_limiter = RateLimiter()
        self.middleware: List[Callable] = []
        self.error_handlers: Dict[int, Callable] = {}
        
        # 통계
        self.request_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
        
        # 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self.initialize_database()
        
        # 기본 미들웨어 등록
        self.register_default_middleware()
        
        # 기본 에러 핸들러 등록
        self.register_default_error_handlers()
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 라우트 정의 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS routes (
                        id TEXT PRIMARY KEY,
                        path TEXT NOT NULL,
                        method TEXT NOT NULL,
                        target_url TEXT NOT NULL,
                        auth_type TEXT NOT NULL,
                        rate_limit INTEGER NOT NULL,
                        timeout INTEGER NOT NULL,
                        retry_count INTEGER NOT NULL,
                        headers TEXT NOT NULL,
                        parameters TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        is_active INTEGER NOT NULL
                    )
                """)
                
                # API 키 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS api_keys (
                        id TEXT PRIMARY KEY,
                        key TEXT NOT NULL UNIQUE,
                        name TEXT NOT NULL,
                        user_id TEXT NOT NULL,
                        permissions TEXT NOT NULL,
                        rate_limit INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        expires_at TEXT,
                        is_active INTEGER NOT NULL,
                        last_used TEXT
                    )
                """)
                
                # 요청 로그 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS request_logs (
                        id TEXT PRIMARY KEY,
                        route_id TEXT NOT NULL,
                        method TEXT NOT NULL,
                        path TEXT NOT NULL,
                        user_id TEXT,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT NOT NULL,
                        request_headers TEXT NOT NULL,
                        request_body TEXT,
                        response_status INTEGER NOT NULL,
                        response_headers TEXT NOT NULL,
                        response_body TEXT,
                        processing_time REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        error_message TEXT,
                        FOREIGN KEY (route_id) REFERENCES routes (id)
                    )
                """)
                
                # 인덱스 생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_routes_path ON routes(path)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_routes_method ON routes(method)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_key ON api_keys(key)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_timestamp ON request_logs(timestamp)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_user_id ON request_logs(user_id)")
                
                conn.commit()
                logger.info("API 게이트웨이 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def register_default_middleware(self):
        """기본 미들웨어 등록"""
        self.add_middleware(self.logging_middleware)
        self.add_middleware(self.rate_limit_middleware)
        self.add_middleware(self.auth_middleware)
        self.add_middleware(self.cors_middleware)
    
    def register_default_error_handlers(self):
        """기본 에러 핸들러 등록"""
        self.register_error_handler(400, self.bad_request_handler)
        self.register_error_handler(401, self.unauthorized_handler)
        self.register_error_handler(403, self.forbidden_handler)
        self.register_error_handler(404, self.not_found_handler)
        self.register_error_handler(429, self.too_many_requests_handler)
        self.register_error_handler(500, self.internal_server_error_handler)
    
    def add_route(self, path: str, method: RequestMethod, target_url: str,
                 auth_type: AuthType = AuthType.NONE, rate_limit: int = 100,
                 timeout: int = 30, retry_count: int = 3, headers: Dict[str, str] = None,
                 parameters: Dict[str, Any] = None) -> str:
        """라우트 추가"""
        try:
            route_id = str(uuid.uuid4())
            now = datetime.now()
            
            route = RouteDefinition(
                id=route_id,
                path=path,
                method=method,
                target_url=target_url,
                auth_type=auth_type,
                rate_limit=rate_limit,
                timeout=timeout,
                retry_count=retry_count,
                headers=headers or {},
                parameters=parameters or {},
                created_at=now,
                updated_at=now,
                is_active=True
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO routes 
                    (id, path, method, target_url, auth_type, rate_limit, timeout, retry_count, headers, parameters, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    route.id, route.path, route.method.value, route.target_url,
                    route.auth_type.value, route.rate_limit, route.timeout,
                    route.retry_count, json.dumps(route.headers),
                    json.dumps(route.parameters), route.created_at.isoformat(),
                    route.updated_at.isoformat(), 1 if route.is_active else 0
                ))
                conn.commit()
            
            self.routes[route_id] = route
            logger.info(f"라우트 추가: {method.value} {path} -> {target_url}")
            
            return route_id
            
        except Exception as e:
            logger.error(f"라우트 추가 오류: {str(e)}")
            raise
    
    def get_route(self, path: str, method: RequestMethod) -> Optional[RouteDefinition]:
        """라우트 조회"""
        try:
            # 정확한 매치 먼저 확인
            for route in self.routes.values():
                if route.path == path and route.method == method and route.is_active:
                    return route
            
            # 패턴 매치 확인 (간단한 구현)
            for route in self.routes.values():
                if self._match_path_pattern(route.path, path) and route.method == method and route.is_active:
                    return route
            
            return None
            
        except Exception as e:
            logger.error(f"라우트 조회 오류: {str(e)}")
            return None
    
    def _match_path_pattern(self, pattern: str, path: str) -> bool:
        """패턴 매치 (간단한 구현)"""
        # 정확한 매치
        if pattern == path:
            return True
        
        # 파라미터 패턴 매치 (예: /users/{id})
        if '{' in pattern and '}' in pattern:
            # 간단한 파라미터 추출
            pattern_parts = pattern.split('/')
            path_parts = path.split('/')
            
            if len(pattern_parts) != len(path_parts):
                return False
            
            for i, pattern_part in enumerate(pattern_parts):
                if pattern_part.startswith('{') and pattern_part.endswith('}'):
                    continue  # 파라미터 부분은 무시
                if pattern_part != path_parts[i]:
                    return False
            
            return True
        
        return False
    
    def create_api_key(self, name: str, user_id: str, permissions: List[str] = None,
                      rate_limit: int = 1000, expires_at: datetime = None) -> str:
        """API 키 생성"""
        try:
            api_key_id = str(uuid.uuid4())
            key = self._generate_api_key()
            now = datetime.now()
            
            api_key = ApiKey(
                id=api_key_id,
                key=key,
                name=name,
                user_id=user_id,
                permissions=permissions or [],
                rate_limit=rate_limit,
                created_at=now,
                expires_at=expires_at,
                is_active=True,
                last_used=None
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO api_keys 
                    (id, key, name, user_id, permissions, rate_limit, created_at, expires_at, is_active, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    api_key.id, api_key.key, api_key.name, api_key.user_id,
                    json.dumps(api_key.permissions), api_key.rate_limit,
                    api_key.created_at.isoformat(),
                    api_key.expires_at.isoformat() if api_key.expires_at else None,
                    1 if api_key.is_active else 0, None
                ))
                conn.commit()
            
            self.api_keys[api_key_id] = api_key
            logger.info(f"API 키 생성: {name} (사용자: {user_id})")
            
            return key
            
        except Exception as e:
            logger.error(f"API 키 생성 오류: {str(e)}")
            raise
    
    def _generate_api_key(self) -> str:
        """API 키 생성"""
        import secrets
        return f"ak_{secrets.token_urlsafe(32)}"
    
    def validate_api_key(self, key: str) -> Optional[ApiKey]:
        """API 키 검증"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM api_keys 
                    WHERE key = ? AND is_active = 1
                """, (key,))
                row = cursor.fetchone()
                
                if row:
                    api_key = ApiKey(
                        id=row[0], key=row[1], name=row[2], user_id=row[3],
                        permissions=json.loads(row[4]), rate_limit=row[5],
                        created_at=datetime.fromisoformat(row[6]),
                        expires_at=datetime.fromisoformat(row[7]) if row[7] else None,
                        is_active=bool(row[8]),
                        last_used=datetime.fromisoformat(row[9]) if row[9] else None
                    )
                    
                    # 만료 확인
                    if api_key.expires_at and datetime.now() > api_key.expires_at:
                        return None
                    
                    # 마지막 사용 시간 업데이트
                    self._update_api_key_usage(api_key.id)
                    
                    return api_key
                
                return None
                
        except Exception as e:
            logger.error(f"API 키 검증 오류: {str(e)}")
            return None
    
    def _update_api_key_usage(self, api_key_id: str):
        """API 키 사용 시간 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE api_keys 
                    SET last_used = ? 
                    WHERE id = ?
                """, (datetime.now().isoformat(), api_key_id))
                conn.commit()
        except Exception as e:
            logger.error(f"API 키 사용 시간 업데이트 오류: {str(e)}")
    
    def add_middleware(self, middleware: Callable):
        """미들웨어 추가"""
        self.middleware.append(middleware)
        logger.info(f"미들웨어 추가: {middleware.__name__}")
    
    def register_error_handler(self, status_code: int, handler: Callable):
        """에러 핸들러 등록"""
        self.error_handlers[status_code] = handler
        logger.info(f"에러 핸들러 등록: {status_code}")
    
    def process_request(self, method: str, path: str, headers: Dict[str, str] = None,
                       body: str = None, ip_address: str = None, user_agent: str = None) -> Dict[str, Any]:
        """요청 처리"""
        try:
            start_time = time.time()
            self.request_count += 1
            
            # 요청 컨텍스트 생성
            context = {
                'method': method,
                'path': path,
                'headers': headers or {},
                'body': body,
                'ip_address': ip_address or 'unknown',
                'user_agent': user_agent or 'unknown',
                'user_id': None,
                'api_key': None,
                'route': None,
                'response': None,
                'error': None
            }
            
            # 라우트 찾기
            route = self.get_route(path, RequestMethod(method))
            if not route:
                return self._handle_error(404, "라우트를 찾을 수 없습니다", context)
            
            context['route'] = route
            
            # 미들웨어 실행
            for middleware in self.middleware:
                try:
                    result = middleware(context)
                    if result is not None:
                        return result
                except Exception as e:
                    logger.error(f"미들웨어 실행 오류: {str(e)}")
                    return self._handle_error(500, f"미들웨어 오류: {str(e)}", context)
            
            # 타겟 서비스로 요청 전달
            try:
                response = self._forward_request(route, context)
                context['response'] = response
                
                # 응답 로깅
                self._log_request(context, response.get('status', 200), None)
                
                return response
                
            except Exception as e:
                logger.error(f"요청 전달 오류: {str(e)}")
                return self._handle_error(500, f"서비스 오류: {str(e)}", context)
                
        except Exception as e:
            logger.error(f"요청 처리 오류: {str(e)}")
            self.error_count += 1
            return self._handle_error(500, f"게이트웨이 오류: {str(e)}", context)
    
    def _forward_request(self, route: RouteDefinition, context: Dict) -> Dict[str, Any]:
        """요청을 타겟 서비스로 전달"""
        try:
            # 요청 준비
            url = route.target_url
            method = context['method']
            headers = context['headers'].copy()
            body = context['body']
            
            # 라우트 헤더 추가
            headers.update(route.headers)
            
            # 요청 전송
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=body,
                timeout=route.timeout,
                allow_redirects=False
            )
            
            # 응답 준비
            result = {
                'status': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'url': url
            }
            
            return result
            
        except requests.exceptions.Timeout:
            raise Exception("요청 타임아웃")
        except requests.exceptions.ConnectionError:
            raise Exception("서비스 연결 오류")
        except Exception as e:
            raise Exception(f"요청 전달 실패: {str(e)}")
    
    def _handle_error(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        """에러 처리"""
        self.error_count += 1
        
        # 에러 핸들러 실행
        handler = self.error_handlers.get(status_code)
        if handler:
            try:
                return handler(status_code, message, context)
            except Exception as e:
                logger.error(f"에러 핸들러 실행 오류: {str(e)}")
        
        # 기본 에러 응답
        error_response = {
            'status': status_code,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': True,
                'status_code': status_code,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
        
        # 에러 로깅
        self._log_request(context, status_code, message)
        
        return error_response
    
    def _log_request(self, context: Dict, status_code: int, error_message: str = None):
        """요청 로깅"""
        try:
            log_id = str(uuid.uuid4())
            processing_time = time.time() - context.get('start_time', time.time())
            
            log = RequestLog(
                id=log_id,
                route_id=context.get('route', {}).get('id', 'unknown'),
                method=context['method'],
                path=context['path'],
                user_id=context.get('user_id'),
                ip_address=context['ip_address'],
                user_agent=context['user_agent'],
                request_headers=context['headers'],
                request_body=context.get('body'),
                response_status=status_code,
                response_headers=context.get('response', {}).get('headers', {}),
                response_body=context.get('response', {}).get('body'),
                processing_time=processing_time,
                timestamp=datetime.now(),
                error_message=error_message
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO request_logs 
                    (id, route_id, method, path, user_id, ip_address, user_agent, request_headers, request_body, response_status, response_headers, response_body, processing_time, timestamp, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    log.id, log.route_id, log.method, log.path, log.user_id,
                    log.ip_address, log.user_agent, json.dumps(log.request_headers),
                    log.request_body, log.response_status, json.dumps(log.response_headers),
                    log.response_body, log.processing_time, log.timestamp.isoformat(),
                    log.error_message
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"요청 로깅 오류: {str(e)}")
    
    # 미들웨어 함수들
    def logging_middleware(self, context: Dict):
        """로깅 미들웨어"""
        logger.info(f"요청: {context['method']} {context['path']} from {context['ip_address']}")
        return None
    
    def rate_limit_middleware(self, context: Dict):
        """속도 제한 미들웨어"""
        route = context['route']
        user_id = context.get('user_id', context['ip_address'])
        
        # API 키 기반 속도 제한
        if context.get('api_key'):
            api_key = context['api_key']
            if not self.rate_limiter.is_allowed(f"api_key:{api_key.id}", api_key.rate_limit):
                return self._handle_error(429, "API 키 속도 제한 초과", context)
        
        # 라우트 기반 속도 제한
        if not self.rate_limiter.is_allowed(f"route:{route.id}:{user_id}", route.rate_limit):
            return self._handle_error(429, "속도 제한 초과", context)
        
        return None
    
    def auth_middleware(self, context: Dict):
        """인증 미들웨어"""
        route = context['route']
        
        if route.auth_type == AuthType.NONE:
            return None
        
        # API 키 인증
        if route.auth_type == AuthType.API_KEY:
            api_key = context['headers'].get('X-API-Key') or context['headers'].get('Authorization', '').replace('Bearer ', '')
            if not api_key:
                return self._handle_error(401, "API 키가 필요합니다", context)
            
            validated_key = self.validate_api_key(api_key)
            if not validated_key:
                return self._handle_error(401, "유효하지 않은 API 키입니다", context)
            
            context['api_key'] = validated_key
            context['user_id'] = validated_key.user_id
            return None
        
        # JWT 인증 (간단한 구현)
        elif route.auth_type == AuthType.JWT:
            auth_header = context['headers'].get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                return self._handle_error(401, "JWT 토큰이 필요합니다", context)
            
            # JWT 검증 로직 구현 필요
            # context['user_id'] = jwt_user_id
            return None
        
        return None
    
    def cors_middleware(self, context: Dict):
        """CORS 미들웨어"""
        # CORS 헤더 추가
        context['response_headers'] = context.get('response_headers', {})
        context['response_headers'].update({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-API-Key'
        })
        return None
    
    # 에러 핸들러 함수들
    def bad_request_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Bad Request', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def unauthorized_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 401,
            'headers': {'Content-Type': 'application/json', 'WWW-Authenticate': 'Bearer'},
            'body': json.dumps({'error': 'Unauthorized', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def forbidden_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 403,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Forbidden', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def not_found_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Not Found', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def too_many_requests_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 429,
            'headers': {'Content-Type': 'application/json', 'Retry-After': '60'},
            'body': json.dumps({'error': 'Too Many Requests', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def internal_server_error_handler(self, status_code: int, message: str, context: Dict) -> Dict[str, Any]:
        return {
            'status': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal Server Error', 'message': message}),
            'url': context.get('route', {}).get('target_url', 'unknown')
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """게이트웨이 통계 조회"""
        try:
            uptime = datetime.now() - self.start_time
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 총 요청 수
                cursor.execute("SELECT COUNT(*) FROM request_logs")
                total_requests = cursor.fetchone()[0]
                
                # 오늘 요청 수
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM request_logs 
                    WHERE DATE(timestamp) = DATE('now')
                """)
                today_requests = cursor.fetchone()[0]
                
                # 에러 수
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM request_logs 
                    WHERE response_status >= 400
                """)
                error_requests = cursor.fetchone()[0]
                
                # 평균 응답 시간
                cursor.execute("""
                    SELECT AVG(processing_time) 
                    FROM request_logs 
                    WHERE processing_time > 0
                """)
                avg_response_time = cursor.fetchone()[0] or 0
                
                # 활성 라우트 수
                cursor.execute("SELECT COUNT(*) FROM routes WHERE is_active = 1")
                active_routes = cursor.fetchone()[0]
                
                # 활성 API 키 수
                cursor.execute("SELECT COUNT(*) FROM api_keys WHERE is_active = 1")
                active_api_keys = cursor.fetchone()[0]
                
                return {
                    'uptime_seconds': uptime.total_seconds(),
                    'total_requests': total_requests,
                    'today_requests': today_requests,
                    'error_requests': error_requests,
                    'success_rate': ((total_requests - error_requests) / total_requests * 100) if total_requests > 0 else 0,
                    'avg_response_time': avg_response_time,
                    'active_routes': active_routes,
                    'active_api_keys': active_api_keys,
                    'request_count': self.request_count,
                    'error_count': self.error_count
                }
                
        except Exception as e:
            logger.error(f"통계 조회 오류: {str(e)}")
            return {}
    
    def cleanup_old_logs(self, days: int = 30):
        """오래된 로그 정리"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM request_logs 
                    WHERE timestamp < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"오래된 로그 {deleted_count}개 정리 완료")
                return deleted_count
                
        except Exception as e:
            logger.error(f"로그 정리 오류: {str(e)}")
            return 0 