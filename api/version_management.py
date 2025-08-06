"""
API 버전 관리 시스템
API 버전 호환성, 하위 호환성, 버전별 문서화
"""

import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Callable
from functools import wraps
from flask import Flask, request, jsonify, Blueprint
from werkzeug.exceptions import BadRequest

logger = logging.getLogger(__name__)


class APIVersionManager:
    """API 버전 관리자"""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.versions = {}
        self.deprecated_versions = set()
        self.version_handlers = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Flask 앱에 버전 관리 설정"""
        self.app = app
        
        # 버전별 블루프린트 등록
        self._register_version_blueprints()
        
        # 버전 미들웨어 등록
        app.before_request(self._version_middleware)
        
        logger.info("API 버전 관리 시스템 초기화 완료")
    
    def register_version(self, version: str, deprecated: bool = False):
        """API 버전 등록"""
        self.versions[version] = {
            'created_at': datetime.utcnow(),
            'deprecated': deprecated,
            'endpoints': {},
            'changes': []
        }
        
        if deprecated:
            self.deprecated_versions.add(version)
        
        logger.info(f"API 버전 등록: {version} (deprecated: {deprecated})")
    
    def add_endpoint(self, version: str, endpoint: str, handler: Callable, 
                    deprecated: bool = False, replacement: str = None):
        """버전별 엔드포인트 등록"""
        if version not in self.versions:
            self.register_version(version)
        
        self.versions[version]['endpoints'][endpoint] = {
            'handler': handler,
            'deprecated': deprecated,
            'replacement': replacement,
            'added_at': datetime.utcnow()
        }
        
        logger.info(f"엔드포인트 등록: {version} - {endpoint}")
    
    def mark_deprecated(self, version: str, endpoint: str, replacement: str = None):
        """엔드포인트를 deprecated로 표시"""
        if version in self.versions and endpoint in self.versions[version]['endpoints']:
            self.versions[version]['endpoints'][endpoint]['deprecated'] = True
            self.versions[version]['endpoints'][endpoint]['replacement'] = replacement
            
            logger.warning(f"엔드포인트 deprecated: {version} - {endpoint}")
    
    def _version_middleware(self):
        """버전 미들웨어"""
        # API 요청인지 확인
        if not request.path.startswith('/api/'):
            return
        
        # 버전 추출
        version = self._extract_version(request.path)
        
        if not version:
            # 기본 버전 사용
            version = 'v1'
        
        # deprecated 버전 경고
        if version in self.deprecated_versions:
            logger.warning(f"Deprecated API 버전 사용: {version}")
            # 경고 헤더 추가
            request.environ['HTTP_X_API_VERSION_DEPRECATED'] = 'true'
        
        # 버전 정보를 request에 저장
        request.api_version = version
    
    def _extract_version(self, path: str) -> Optional[str]:
        """경로에서 버전 추출"""
        parts = path.split('/')
        for part in parts:
            if part.startswith('v') and part[1:].isdigit():
                return part
        return None
    
    def _register_version_blueprints(self):
        """버전별 블루프린트 등록"""
        for version in self.versions:
            blueprint = Blueprint(f'api_{version}', __name__, url_prefix=f'/api/{version}')
            
            # 버전별 엔드포인트 등록
            for endpoint, config in self.versions[version]['endpoints'].items():
                blueprint.add_url_rule(
                    endpoint,
                    view_func=self._create_version_handler(config['handler'], version, endpoint),
                    methods=['GET', 'POST', 'PUT', 'DELETE']
                )
            
            self.app.register_blueprint(blueprint)
    
    def _create_version_handler(self, handler: Callable, version: str, endpoint: str):
        """버전별 핸들러 생성"""
        def version_handler(*args, **kwargs):
            try:
                # 버전별 전처리
                result = self._preprocess_request(version, endpoint, request)
                if result:
                    return result
                
                # 핸들러 실행
                response = handler(*args, **kwargs)
                
                # 버전별 후처리
                response = self._postprocess_response(version, endpoint, response)
                
                return response
                
            except Exception as e:
                return self._handle_version_error(version, endpoint, e)
        
        return version_handler
    
    def _preprocess_request(self, version: str, endpoint: str, request) -> Optional[Any]:
        """요청 전처리"""
        # deprecated 엔드포인트 경고
        if (version in self.versions and 
            endpoint in self.versions[version]['endpoints'] and
            self.versions[version]['endpoints'][endpoint]['deprecated']):
            
            replacement = self.versions[version]['endpoints'][endpoint]['replacement']
            warning_msg = f"이 엔드포인트는 deprecated되었습니다."
            if replacement:
                warning_msg += f" 대신 {replacement}를 사용하세요."
            
            logger.warning(f"Deprecated 엔드포인트 사용: {version} - {endpoint}")
        
        return None
    
    def _postprocess_response(self, version: str, endpoint: str, response) -> Any:
        """응답 후처리"""
        # 버전 정보 헤더 추가
        if hasattr(response, 'headers'):
            response.headers['X-API-Version'] = version
            response.headers['X-API-Endpoint'] = endpoint
        
        return response
    
    def _handle_version_error(self, version: str, endpoint: str, error: Exception) -> Any:
        """버전별 에러 처리"""
        error_response = {
            'error': {
                'code': 'VERSION_ERROR',
                'message': f'API 버전 {version}에서 오류가 발생했습니다.',
                'endpoint': endpoint,
                'version': version,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
        
        logger.error(f"API 버전 에러: {version} - {endpoint} - {error}")
        
        return jsonify(error_response), 500
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """버전 정보 조회"""
        if version not in self.versions:
            return {'error': '버전을 찾을 수 없습니다.'}
        
        version_info = self.versions[version].copy()
        
        # 엔드포인트 정보 정리
        endpoints = {}
        for endpoint, config in version_info['endpoints'].items():
            endpoints[endpoint] = {
                'deprecated': config['deprecated'],
                'replacement': config['replacement'],
                'added_at': config['added_at'].isoformat()
            }
        
        version_info['endpoints'] = endpoints
        version_info['created_at'] = version_info['created_at'].isoformat()
        
        return version_info
    
    def get_all_versions(self) -> Dict[str, Any]:
        """모든 버전 정보 조회"""
        versions_info = {}
        for version in self.versions:
            versions_info[version] = self.get_version_info(version)
        
        return {
            'versions': versions_info,
            'deprecated_versions': list(self.deprecated_versions),
            'current_version': 'v1',  # 현재 기본 버전
            'latest_version': max(self.versions.keys()) if self.versions else None
        }
    
    def add_version_change(self, version: str, change_type: str, description: str, 
                          affected_endpoints: List[str] = None):
        """버전 변경사항 추가"""
        if version not in self.versions:
            self.register_version(version)
        
        change = {
            'type': change_type,  # 'added', 'modified', 'deprecated', 'removed'
            'description': description,
            'affected_endpoints': affected_endpoints or [],
            'timestamp': datetime.utcnow()
        }
        
        self.versions[version]['changes'].append(change)
        
        logger.info(f"버전 변경사항 추가: {version} - {change_type} - {description}")


# 전역 API 버전 관리자
api_version_manager = APIVersionManager()


def api_version(version: str, deprecated: bool = False):
    """API 버전 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 버전 등록
            api_version_manager.add_endpoint(version, request.path, func, deprecated)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def deprecated_endpoint(replacement: str = None):
    """Deprecated 엔드포인트 데코레이터"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # deprecated 표시
            current_version = getattr(request, 'api_version', 'v1')
            api_version_manager.mark_deprecated(current_version, request.path, replacement)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 버전별 API 엔드포인트 예시
@api_version('v1')
def get_users_v1():
    """v1 사용자 목록 API"""
    return jsonify({
        'version': 'v1',
        'users': [],
        'pagination': {'page': 1, 'per_page': 20}
    })


@api_version('v2')
def get_users_v2():
    """v2 사용자 목록 API (개선된 버전)"""
    return jsonify({
        'version': 'v2',
        'users': [],
        'pagination': {'page': 1, 'per_page': 20},
        'filters': {'role': None, 'status': None},
        'sorting': {'field': 'created_at', 'order': 'desc'}
    })


@deprecated_endpoint('/api/v2/users')
@api_version('v1', deprecated=True)
def get_users_v1_deprecated():
    """v1 사용자 목록 API (deprecated)"""
    return jsonify({
        'version': 'v1',
        'deprecated': True,
        'replacement': '/api/v2/users',
        'users': []
    })


def init_api_versions(app: Flask):
    """API 버전 초기화"""
    api_version_manager.init_app(app)
    
    # 기본 버전 등록
    api_version_manager.register_version('v1')
    api_version_manager.register_version('v2')
    
    # v1을 deprecated로 표시
    api_version_manager.register_version('v1', deprecated=True)
    
    # 버전 변경사항 추가
    api_version_manager.add_version_change(
        'v2', 
        'added', 
        '사용자 목록 API에 필터링 및 정렬 기능 추가',
        ['/users']
    )
    
    api_version_manager.add_version_change(
        'v1', 
        'deprecated', 
        'v1 API를 v2로 대체',
        ['/users']
    )
    
    logger.info("API 버전 시스템 초기화 완료") 