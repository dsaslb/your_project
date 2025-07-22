"""
플러그인 관리 API
"""

from flask import Blueprint, request, jsonify
from flask_smorest import Api, Blueprint, abort
from marshmallow import Schema, fields, validate
from typing import Dict, List, Any
import sys
import os

# 플러그인 관리자 import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from plugins.plugin_manager import plugin_manager, PluginStatus, PluginPermission

# Blueprint 생성
plugin_blp = Blueprint("plugin_management", __name__, url_prefix="/api/plugins")

# ===== 스키마 정의 =====

class PluginInfoSchema(Schema):
    name = fields.Str(required=True, metadata={"description": "플러그인 이름"})
    version = fields.Str(required=True, metadata={"description": "플러그인 버전"})
    description = fields.Str(required=True, metadata={"description": "플러그인 설명"})
    author = fields.Str(required=True, metadata={"description": "플러그인 작성자"})
    status = fields.Str(required=True, metadata={"description": "플러그인 상태"})
    permissions = fields.List(fields.Str(), required=True, metadata={"description": "필요한 권한"})
    dependencies = fields.List(fields.Str(), required=True, metadata={"description": "의존성"})
    settings = fields.Dict(required=True, metadata={"description": "플러그인 설정"})
    enabled_at = fields.Str(metadata={"description": "활성화 시간"})
    disabled_at = fields.Str(metadata={"description": "비활성화 시간"})
    last_error = fields.Str(metadata={"description": "마지막 오류"})
    created_at = fields.Str(required=True, metadata={"description": "생성 시간"})
    updated_at = fields.Str(required=True, metadata={"description": "업데이트 시간"})
    routes = fields.List(fields.Str(), required=True, metadata={"description": "등록된 라우트"})

class PluginListResponseSchema(Schema):
    success = fields.Bool(required=True, metadata={"description": "성공 여부"})
    data = fields.List(fields.Nested(PluginInfoSchema), required=True, metadata={"description": "플러그인 목록"})
    total = fields.Int(required=True, metadata={"description": "총 개수"})

class PluginActionRequestSchema(Schema):
    plugin_name = fields.Str(required=True, validate=validate.Length(min=1), metadata={"description": "플러그인 이름"})
    user_permissions = fields.List(fields.Str(), metadata={"description": "사용자 권한"})

class PluginSettingsUpdateSchema(Schema):
    settings = fields.Dict(required=True, metadata={"description": "업데이트할 설정"})

class PluginInstallRequestSchema(Schema):
    plugin_path = fields.Str(required=True, validate=validate.Length(min=1), metadata={"description": "플러그인 경로"})
    user_permissions = fields.List(fields.Str(), metadata={"description": "사용자 권한"})

class PluginHookSchema(Schema):
    hook_name = fields.Str(required=True, metadata={"description": "훅 이름"})
    plugin_name = fields.Str(required=True, metadata={"description": "플러그인 이름"})
    callback_name = fields.Str(required=True, metadata={"description": "콜백 함수 이름"})

# ===== 헬퍼 함수 =====

def get_user_permissions():
    """사용자 권한 가져오기 (실제로는 JWT 토큰에서 추출)"""
    # 실제 구현에서는 JWT 토큰에서 사용자 권한을 추출
    return ["read", "write", "admin"]

def check_admin_permission():
    """관리자 권한 확인"""
    user_permissions = get_user_permissions()
    return PluginPermission.ADMIN.value in user_permissions

# ===== API 엔드포인트 =====

@plugin_blp.route("/")
class PluginList(Resource):
    """플러그인 목록 조회"""
    
    @plugin_blp.response(200, PluginListResponseSchema)
    def get(self):
        """모든 플러그인 목록 조회"""
        try:
            plugins = plugin_manager.get_all_plugins()
            return {
                "success": True,
                "data": plugins,
                "total": len(plugins)
            }
        except Exception as e:
            abort(500, description=f"플러그인 목록 조회 실패: {str(e)}")

@plugin_blp.route("/<plugin_name>")
class PluginDetail(Resource):
    """플러그인 상세 정보"""
    
    @plugin_blp.response(200, PluginInfoSchema)
    @plugin_blp.response(404, description="플러그인을 찾을 수 없습니다.")
    def get(self, plugin_name):
        """플러그인 상세 정보 조회"""
        try:
            plugin_info = plugin_manager.get_plugin_info(plugin_name)
            if not plugin_info:
                abort(404, description=f"플러그인을 찾을 수 없습니다: {plugin_name}")
            
            return plugin_info
        except Exception as e:
            abort(500, description=f"플러그인 정보 조회 실패: {str(e)}")

@plugin_blp.route("/<plugin_name>/enable")
class PluginEnable(Resource):
    """플러그인 활성화"""
    
    @plugin_blp.arguments(PluginActionRequestSchema)
    @plugin_blp.response(200, description="플러그인 활성화 성공")
    @plugin_blp.response(400, description="플러그인 활성화 실패")
    @plugin_blp.response(403, description="권한이 없습니다.")
    def post(self, data, plugin_name):
        """플러그인 활성화"""
        try:
            user_permissions = data.get('user_permissions', get_user_permissions())
            
            if not plugin_manager.check_permissions(["admin"], user_permissions):
                abort(403, description="플러그인 활성화 권한이 없습니다.")
            
            success = plugin_manager.enable_plugin(plugin_name, user_permissions)
            
            if success:
                return {
                    "success": True,
                    "message": f"플러그인 {plugin_name}이(가) 활성화되었습니다."
                }
            else:
                abort(400, description=f"플러그인 {plugin_name} 활성화에 실패했습니다.")
                
        except Exception as e:
            abort(500, description=f"플러그인 활성화 중 오류: {str(e)}")

@plugin_blp.route("/<plugin_name>/disable")
class PluginDisable(Resource):
    """플러그인 비활성화"""
    
    @plugin_blp.arguments(PluginActionRequestSchema)
    @plugin_blp.response(200, description="플러그인 비활성화 성공")
    @plugin_blp.response(400, description="플러그인 비활성화 실패")
    @plugin_blp.response(403, description="권한이 없습니다.")
    def post(self, data, plugin_name):
        """플러그인 비활성화"""
        try:
            user_permissions = data.get('user_permissions', get_user_permissions())
            
            if not plugin_manager.check_permissions(["admin"], user_permissions):
                abort(403, description="플러그인 비활성화 권한이 없습니다.")
            
            success = plugin_manager.disable_plugin(plugin_name, user_permissions)
            
            if success:
                return {
                    "success": True,
                    "message": f"플러그인 {plugin_name}이(가) 비활성화되었습니다."
                }
            else:
                abort(400, description=f"플러그인 {plugin_name} 비활성화에 실패했습니다.")
                
        except Exception as e:
            abort(500, description=f"플러그인 비활성화 중 오류: {str(e)}")

@plugin_blp.route("/<plugin_name>/settings")
class PluginSettings(Resource):
    """플러그인 설정 관리"""
    
    @plugin_blp.response(200, description="플러그인 설정 조회 성공")
    @plugin_blp.response(404, description="플러그인을 찾을 수 없습니다.")
    def get(self, plugin_name):
        """플러그인 설정 조회"""
        try:
            plugin_info = plugin_manager.get_plugin_info(plugin_name)
            if not plugin_info:
                abort(404, description=f"플러그인을 찾을 수 없습니다: {plugin_name}")
            
            return {
                "success": True,
                "plugin_name": plugin_name,
                "settings": plugin_info.get("settings", {})
            }
        except Exception as e:
            abort(500, description=f"플러그인 설정 조회 실패: {str(e)}")
    
    @plugin_blp.arguments(PluginSettingsUpdateSchema)
    @plugin_blp.response(200, description="플러그인 설정 업데이트 성공")
    @plugin_blp.response(400, description="플러그인 설정 업데이트 실패")
    @plugin_blp.response(403, description="권한이 없습니다.")
    def put(self, data, plugin_name):
        """플러그인 설정 업데이트"""
        try:
            user_permissions = get_user_permissions()
            settings = data.get("settings", {})
            
            success = plugin_manager.update_plugin_settings(plugin_name, settings, user_permissions)
            
            if success:
                return {
                    "success": True,
                    "message": f"플러그인 {plugin_name} 설정이 업데이트되었습니다."
                }
            else:
                abort(400, description=f"플러그인 {plugin_name} 설정 업데이트에 실패했습니다.")
                
        except Exception as e:
            abort(500, description=f"플러그인 설정 업데이트 중 오류: {str(e)}")

@plugin_blp.route("/install")
class PluginInstall(Resource):
    """플러그인 설치"""
    
    @plugin_blp.arguments(PluginInstallRequestSchema)
    @plugin_blp.response(200, description="플러그인 설치 성공")
    @plugin_blp.response(400, description="플러그인 설치 실패")
    @plugin_blp.response(403, description="권한이 없습니다.")
    def post(self, data):
        """플러그인 설치"""
        try:
            if not check_admin_permission():
                abort(403, description="플러그인 설치 권한이 없습니다.")
            
            plugin_path = data.get("plugin_path")
            user_permissions = data.get("user_permissions", get_user_permissions())
            
            success = plugin_manager.install_plugin(plugin_path, user_permissions)
            
            if success:
                return {
                    "success": True,
                    "message": f"플러그인이 설치되었습니다: {plugin_path}"
                }
            else:
                abort(400, description="플러그인 설치에 실패했습니다.")
                
        except Exception as e:
            abort(500, description=f"플러그인 설치 중 오류: {str(e)}")

@plugin_blp.route("/<plugin_name>/uninstall")
class PluginUninstall(Resource):
    """플러그인 제거"""
    
    @plugin_blp.arguments(PluginActionRequestSchema)
    @plugin_blp.response(200, description="플러그인 제거 성공")
    @plugin_blp.response(400, description="플러그인 제거 실패")
    @plugin_blp.response(403, description="권한이 없습니다.")
    def post(self, data, plugin_name):
        """플러그인 제거"""
        try:
            if not check_admin_permission():
                abort(403, description="플러그인 제거 권한이 없습니다.")
            
            user_permissions = data.get('user_permissions', get_user_permissions())
            
            success = plugin_manager.uninstall_plugin(plugin_name, user_permissions)
            
            if success:
                return {
                    "success": True,
                    "message": f"플러그인 {plugin_name}이(가) 제거되었습니다."
                }
            else:
                abort(400, description=f"플러그인 {plugin_name} 제거에 실패했습니다.")
                
        except Exception as e:
            abort(500, description=f"플러그인 제거 중 오류: {str(e)}")

@plugin_blp.route("/discover")
class PluginDiscover(Resource):
    """플러그인 발견"""
    
    @plugin_blp.response(200, description="플러그인 발견 성공")
    def get(self):
        """사용 가능한 플러그인 발견"""
        try:
            discovered_plugins = plugin_manager.discover_plugins()
            return {
                "success": True,
                "data": discovered_plugins,
                "total": len(discovered_plugins)
            }
        except Exception as e:
            abort(500, description=f"플러그인 발견 실패: {str(e)}")

@plugin_blp.route("/hooks")
class PluginHooks(Resource):
    """플러그인 훅 관리"""
    
    @plugin_blp.response(200, description="훅 목록 조회 성공")
    def get(self):
        """등록된 훅 목록 조회"""
        try:
            hooks = plugin_manager.hooks
            hook_list = []
            
            for hook_name, callbacks in hooks.items():
                hook_list.append({
                    "hook_name": hook_name,
                    "callback_count": len(callbacks),
                    "callbacks": [str(callback) for callback in callbacks]
                })
            
            return {
                "success": True,
                "data": hook_list,
                "total": len(hook_list)
            }
        except Exception as e:
            abort(500, description=f"훅 목록 조회 실패: {str(e)}")

@plugin_blp.route("/hooks/<hook_name>/execute")
class PluginHookExecute(Resource):
    """훅 실행"""
    
    @plugin_blp.response(200, description="훅 실행 성공")
    @plugin_blp.response(404, description="훅을 찾을 수 없습니다.")
    def post(self, hook_name):
        """특정 훅 실행"""
        try:
            if hook_name not in plugin_manager.hooks:
                abort(404, description=f"훅을 찾을 수 없습니다: {hook_name}")
            
            # 요청 데이터를 훅에 전달
            request_data = request.get_json() or {}
            args = request_data.get("args", [])
            kwargs = request_data.get("kwargs", {})
            
            results = plugin_manager.execute_hook(hook_name, *args, **kwargs)
            
            return {
                "success": True,
                "hook_name": hook_name,
                "results": results,
                "result_count": len(results)
            }
        except Exception as e:
            abort(500, description=f"훅 실행 실패: {str(e)}")

@plugin_blp.route("/status")
class PluginStatus(Resource):
    """플러그인 시스템 상태"""
    
    @plugin_blp.response(200, description="플러그인 시스템 상태 조회 성공")
    def get(self):
        """플러그인 시스템 상태 조회"""
        try:
            plugins = plugin_manager.get_all_plugins()
            
            # 상태별 통계
            status_stats = {}
            for plugin in plugins:
                status = plugin.get("status", "unknown")
                status_stats[status] = status_stats.get(status, 0) + 1
            
            # 활성화된 플러그인 수
            enabled_count = status_stats.get("enabled", 0)
            total_count = len(plugins)
            
            return {
                "success": True,
                "total_plugins": total_count,
                "enabled_plugins": enabled_count,
                "disabled_plugins": status_stats.get("disabled", 0),
                "error_plugins": status_stats.get("error", 0),
                "status_distribution": status_stats,
                "system_healthy": enabled_count > 0 and status_stats.get("error", 0) == 0
            }
        except Exception as e:
            abort(500, description=f"플러그인 시스템 상태 조회 실패: {str(e)}") 