"""
동적 API 라우팅 시스템
플러그인에서 제공하는 API를 동적으로 라우팅하는 시스템
"""

from flask import Flask, jsonify, Blueprint
from typing import Dict, List, Any, Optional
import logging
from .plugin_manager import plugin_manager

logger = logging.getLogger(__name__)

class DynamicAPIRouter:
    """동적 API 라우터"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.plugin_blueprints: Dict[str, Blueprint] = {}
        self.route_registry: Dict[str, Dict[str, Any]] = {}
        
    def register_plugin_routes(self, plugin_name: str) -> bool:
        """플러그인의 API 라우트 등록"""
        try:
            # 플러그인에서 라우트 정보 가져오기
            routes = plugin_manager.get_plugin_routes(plugin_name)
            if not routes:
                logger.info(f"플러그인 {plugin_name}에 등록할 라우트가 없습니다")
                return True
            
            # 플러그인용 Blueprint 생성
            blueprint_name = f"plugin_{plugin_name}"
            blueprint = Blueprint(blueprint_name, __name__)
            
            # 각 라우트 등록
            for route_info in routes:
                self._register_route(blueprint, route_info, plugin_name)
            
            # Blueprint 등록
            self.app.register_blueprint(blueprint, url_prefix=f"/api/plugins/{plugin_name}")
            self.plugin_blueprints[plugin_name] = blueprint
            
            logger.info(f"플러그인 {plugin_name}의 {len(routes)}개 라우트 등록 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 라우트 등록 실패: {e}")
            return False
    
    def unregister_plugin_routes(self, plugin_name: str) -> bool:
        """플러그인의 API 라우트 등록 해제"""
        try:
            if plugin_name in self.plugin_blueprints:
                # Blueprint 제거
                blueprint = self.plugin_blueprints[plugin_name]
                self.app.blueprints.pop(blueprint.name, None)
                del self.plugin_blueprints[plugin_name]
                
                # 라우트 레지스트리에서 제거
                routes_to_remove = [
                    route_id for route_id, info in self.route_registry.items()
                    if info.get('plugin') == plugin_name
                ]
                for route_id in routes_to_remove:
                    del self.route_registry[route_id]
                
                logger.info(f"플러그인 {plugin_name}의 라우트 등록 해제 완료")
                return True
            
            return True
            
        except Exception as e:
            logger.error(f"플러그인 {plugin_name} 라우트 등록 해제 실패: {e}")
            return False
    
    def _register_route(self, blueprint: Blueprint, route_info: Dict[str, Any], plugin_name: str):
        """개별 라우트 등록"""
        route_path = route_info.get('path', '')
        methods = route_info.get('methods', ['GET'])
        handler_name = route_info.get('handler', '')
        permissions = route_info.get('permissions', [])
        
        # 라우트 ID 생성
        route_id = f"{plugin_name}:{route_path}:{','.join(methods)}"
        
        # 라우트 핸들러 생성
        def route_handler(*args, **kwargs):
            try:
                # 권한 확인
                if not self._check_permissions(permissions):
                    return jsonify({'error': '권한이 없습니다'}), 403
                
                # 플러그인 인스턴스에서 핸들러 호출
                plugin_instance = plugin_manager.loaded_plugins.get(plugin_name)
                if not plugin_instance:
                    return jsonify({'error': '플러그인이 로드되지 않았습니다'}), 503
                
                if hasattr(plugin_instance, handler_name):
                    handler = getattr(plugin_instance, handler_name)
                    return handler(*args, **kwargs)
                else:
                    return jsonify({'error': f'핸들러 {handler_name}을 찾을 수 없습니다'}), 404
                    
            except Exception as e:
                logger.error(f"플러그인 {plugin_name} 라우트 {route_path} 실행 오류: {e}")
                return jsonify({'error': '내부 서버 오류'}), 500
        
        # Blueprint에 라우트 등록
        blueprint.add_url_rule(
            route_path,
            f"{plugin_name}_{handler_name}",
            route_handler,
            methods=methods
        )
        
        # 라우트 레지스트리에 등록
        self.route_registry[route_id] = {
            'plugin': plugin_name,
            'path': route_path,
            'methods': methods,
            'handler': handler_name,
            'permissions': permissions
        }
    
    def _check_permissions(self, required_permissions: List[str]) -> bool:
        """권한 확인"""
        # TODO: 실제 권한 확인 로직 구현
        # 현재는 모든 권한을 허용
        return True
    
    def get_all_routes(self) -> List[Dict[str, Any]]:
        """등록된 모든 라우트 조회"""
        return list(self.route_registry.values())
    
    def get_plugin_routes(self, plugin_name: str) -> List[Dict[str, Any]]:
        """특정 플러그인의 라우트 조회"""
        return [
            route_info for route_info in self.route_registry.values()
            if route_info.get('plugin') == plugin_name
        ]
    
    def reload_all_plugins(self) -> bool:
        """모든 플러그인 재로드"""
        try:
            # 현재 로드된 플러그인 목록
            loaded_plugins = list(plugin_manager.get_loaded_plugins())
            
            # 모든 플러그인 언로드
            for plugin_name in loaded_plugins:
                self.unregister_plugin_routes(plugin_name)
                plugin_manager.unload_plugin(plugin_name)
            
            # 활성화된 플러그인 다시 로드
            all_plugins = plugin_manager.get_all_plugins()
            for plugin_name, metadata in all_plugins.items():
                if metadata.enabled:
                    if plugin_manager.load_plugin(plugin_name):
                        self.register_plugin_routes(plugin_name)
            
            logger.info("모든 플러그인 재로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"플러그인 재로드 실패: {e}")
            return False

# 전역 라우터 인스턴스 (Flask 앱 초기화 후 설정)
dynamic_router: Optional[DynamicAPIRouter] = None

def init_dynamic_router(app: Flask) -> DynamicAPIRouter:
    """동적 라우터 초기화"""
    global dynamic_router
    dynamic_router = DynamicAPIRouter(app)
    return dynamic_router 