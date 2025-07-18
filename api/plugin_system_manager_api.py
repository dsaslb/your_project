from typing import Dict, Optional, Any
import logging
from datetime import datetime
from flask import Blueprint, jsonify
from typing import Optional
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
플러그인 시스템 매니저 API
플러그인 시스템의 전반적인 관리를 담당하는 API
"""


# 로깅 설정
logger = logging.getLogger(__name__)

# 블루프린트 생성
plugin_system_manager_bp = Blueprint('plugin_system_manager', __name__, url_prefix='/api/plugin-system')


class PluginSystemManager:
    """플러그인 시스템 매니저"""

    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.system_status = {
            "total_plugins": 0,
            "active_plugins": 0,
            "disabled_plugins": 0,
            "error_plugins": 0,
            "last_scan": None,
            "system_health": "healthy"
        }

    def scan_plugins(self) -> Dict[str, Any]:
        """플러그인 스캔"""
        try:
            # 플러그인 디렉토리 스캔
            import os
            plugin_dir = "plugins"
            if not os.path.exists(plugin_dir):
                return {"error": "플러그인 디렉토리를 찾을 수 없습니다"}

            plugins = {}
            for item in os.listdir(plugin_dir):
                plugin_path = os.path.join(plugin_dir, item)
                if os.path.isdir(plugin_path):
                    config_path = os.path.join(plugin_path, "config", "plugin.json")
                    if os.path.exists(config_path):
                        plugins[item] = {
                            "name": item,
                            "path": plugin_path,
                            "config_path": config_path,
                            "status": "found"
                        }

            self.plugins = plugins
            self.system_status["total_plugins"] = len(plugins)
            self.system_status["last_scan"] = datetime.utcnow().isoformat()

            return {
                "success": True,
                "plugins": plugins,
                "system_status": self.system_status
            }

        except Exception as e:
            logger.error(f"플러그인 스캔 실패: {e}")
            return {"error": str(e)}

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return self.system_status

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """특정 플러그인 정보 조회"""
        return self.plugins.get(plugin_name)

    def validate_plugin(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 유효성 검사"""
        try:
            plugin_info = self.get_plugin_info(plugin_name)
            if not plugin_info:
                return {"valid": False, "error": "플러그인을 찾을 수 없습니다"}

            # config.json 파일 검사
            import json
            import os

            config_path = plugin_info["config_path"]
            if not os.path.exists(config_path):
                return {"valid": False, "error": "config.json 파일이 없습니다"}

            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 필수 필드 검사
            required_fields = ["name", "version", "description", "author"]
            missing_fields = [field for field in required_fields if field not in config]

            if missing_fields:
                return {
                    "valid": False,
                    "error": f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
                }

            return {
                "valid": True,
                "config": config,
                "plugin_info": plugin_info
            }

        except Exception as e:
            logger.error(f"플러그인 유효성 검사 실패: {e}")
            return {"valid": False, "error": str(e)}


# 전역 인스턴스
plugin_system_manager = PluginSystemManager()


@plugin_system_manager_bp.route('/status', methods=['GET'])
def get_system_status():
    """시스템 상태 조회"""
    try:
        status = plugin_system_manager.get_system_status()
        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        logger.error(f"시스템 상태 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@plugin_system_manager_bp.route('/scan', methods=['POST'])
def scan_plugins():
    """플러그인 스캔"""
    try:
        result = plugin_system_manager.scan_plugins()
        if "error" in result:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400

        return jsonify(result)
    except Exception as e:
        logger.error(f"플러그인 스캔 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@plugin_system_manager_bp.route('/plugins', methods=['GET'])
def get_plugins():
    """플러그인 목록 조회"""
    try:
        plugins = plugin_system_manager.plugins
        return jsonify({
            "success": True,
            "data": {
                "plugins": plugins,
                "count": len(plugins)
            }
        })
    except Exception as e:
        logger.error(f"플러그인 목록 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@plugin_system_manager_bp.route('/plugins/<plugin_name>', methods=['GET'])
def get_plugin_info(plugin_name: str):
    """특정 플러그인 정보 조회"""
    try:
        plugin_info = plugin_system_manager.get_plugin_info(plugin_name)
        if not plugin_info:
            return jsonify({
                "success": False,
                "error": "플러그인을 찾을 수 없습니다"
            }), 404

        return jsonify({
            "success": True,
            "data": plugin_info
        })
    except Exception as e:
        logger.error(f"플러그인 정보 조회 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@plugin_system_manager_bp.route('/plugins/<plugin_name>/validate', methods=['POST'])
def validate_plugin(plugin_name: str):
    """플러그인 유효성 검사"""
    try:
        result = plugin_system_manager.validate_plugin(plugin_name)
        if not result["valid"]:
            return jsonify({
                "success": False,
                "error": result["error"]
            }), 400

        return jsonify({
            "success": True,
            "data": result
        })
    except Exception as e:
        logger.error(f"플러그인 유효성 검사 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@plugin_system_manager_bp.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    try:
        # 기본 시스템 상태 확인
        status = plugin_system_manager.get_system_status()

        # 추가적인 시스템 검사
        import os
        plugin_dir = "plugins"
        plugin_dir_exists = os.path.exists(plugin_dir)

        health_status = {
            "status": "healthy",
            "plugin_directory": plugin_dir_exists,
            "total_plugins": status["total_plugins"],
            "last_scan": status["last_scan"],
            "timestamp": datetime.utcnow().isoformat()
        }

        if not plugin_dir_exists:
            health_status["status"] = "warning"
            health_status["message"] = "플러그인 디렉토리가 없습니다"

        return jsonify({
            "success": True,
            "data": health_status
        })
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# 초기화 함수


def initialize_plugin_system():
    """플러그인 시스템 초기화"""
    try:
        logger.info("플러그인 시스템 매니저 초기화 시작")
        plugin_system_manager.scan_plugins()
        logger.info("플러그인 시스템 매니저 초기화 완료")
    except Exception as e:
        logger.error(f"플러그인 시스템 매니저 초기화 실패: {e}")

# 앱 시작 시 자동 초기화


def auto_initialize():
    """자동 초기화"""
    initialize_plugin_system()
