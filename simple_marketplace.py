#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 모듈 마켓플레이스 시스템
4단계 설치 플로우: 설치 → 활성화 → 설정 → 온보딩
"""

import os
import json
import sqlite3
from datetime import datetime
from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    current_user,
)
import uuid
from datetime import datetime

# 메뉴 통합 시스템 import
try:
    from core.backend.menu_integration_system import menu_system
except ImportError:
    # 메뉴 시스템이 없을 경우 더미 클래스 사용
    class DummyMenuSystem:
        def install_module(self, *args, **kwargs):
            return {"status": "activated", "menus_created": 3}

        def get_user_menus(self, user_id, role):
            # 사용자 역할에 따른 더미 메뉴 반환
            if role == "admin":
                return [
                    {
                        "id": 1,
                        "menu_name": "출근 관리",
                        "menu_icon": "fas fa-clock",
                        "menu_url": "/attendance",
                        "sub_menus": [
                            {
                                "id": 11,
                                "menu_name": "출근 기록",
                                "menu_icon": "fas fa-list",
                                "menu_url": "/attendance/records",
                            },
                            {
                                "id": 12,
                                "menu_name": "근무 통계",
                                "menu_icon": "fas fa-chart-bar",
                                "menu_url": "/attendance/stats",
                            },
                        ],
                    },
                    {
                        "id": 2,
                        "menu_name": "재고 관리",
                        "menu_icon": "fas fa-boxes",
                        "menu_url": "/inventory",
                        "sub_menus": [
                            {
                                "id": 21,
                                "menu_name": "재고 현황",
                                "menu_icon": "fas fa-eye",
                                "menu_url": "/inventory/status",
                            },
                            {
                                "id": 22,
                                "menu_name": "입출고 관리",
                                "menu_icon": "fas fa-exchange-alt",
                                "menu_url": "/inventory/transactions",
                            },
                        ],
                    },
                    {
                        "id": 3,
                        "menu_name": "개발 모드",
                        "menu_icon": "fas fa-code",
                        "menu_url": "/dev-mode",
                        "sub_menus": [
                            {
                                "id": 31,
                                "menu_name": "프로젝트 관리",
                                "menu_icon": "fas fa-project-diagram",
                                "menu_url": "/dev-mode",
                            },
                            {
                                "id": 32,
                                "menu_name": "컴포넌트 라이브러리",
                                "menu_icon": "fas fa-puzzle-piece",
                                "menu_url": "/dev-mode/components",
                            },
                        ],
                    },
                ]
            elif role == "manager":
                return [
                    {
                        "id": 3,
                        "menu_name": "팀 관리",
                        "menu_icon": "fas fa-users",
                        "menu_url": "/team",
                        "sub_menus": [
                            {
                                "id": 31,
                                "menu_name": "직원 목록",
                                "menu_icon": "fas fa-list",
                                "menu_url": "/team/employees",
                            },
                            {
                                "id": 32,
                                "menu_name": "근무 스케줄",
                                "menu_icon": "fas fa-calendar",
                                "menu_url": "/team/schedule",
                            },
                        ],
                    },
                    {
                        "id": 4,
                        "menu_name": "개발 모드",
                        "menu_icon": "fas fa-code",
                        "menu_url": "/dev-mode",
                        "sub_menus": [
                            {
                                "id": 41,
                                "menu_name": "프로젝트 관리",
                                "menu_icon": "fas fa-project-diagram",
                                "menu_url": "/dev-mode",
                            }
                        ],
                    },
                ]
            else:
                return [
                    {
                        "id": 4,
                        "menu_name": "내 정보",
                        "menu_icon": "fas fa-user",
                        "menu_url": "/profile",
                        "sub_menus": [
                            {
                                "id": 41,
                                "menu_name": "개인 정보",
                                "menu_icon": "fas fa-id-card",
                                "menu_url": "/profile/info",
                            },
                            {
                                "id": 42,
                                "menu_name": "근무 기록",
                                "menu_icon": "fas fa-history",
                                "menu_url": "/profile/attendance",
                            },
                        ],
                    }
                ]

        def get_menu_statistics(self):
            return {
                "total_menus": 4,
                "module_menu_counts": {
                    "attendance": 2,
                    "inventory": 2,
                    "team": 2,
                    "profile": 2,
                },
                "popular_menus": [
                    {"name": "출근 관리", "access_count": 15},
                    {"name": "재고 관리", "access_count": 12},
                    {"name": "팀 관리", "access_count": 8},
                ],
                "recent_menus": [
                    {"name": "출근 기록", "last_access": "2024-01-15 10:30:00"},
                    {"name": "재고 현황", "last_access": "2024-01-15 09:15:00"},
                ],
            }

    menu_system = DummyMenuSystem()

# 개발 모드 시스템 import
try:
    from core.backend.module_development_system import dev_system
except ImportError:
    # 개발 시스템이 없을 경우 더미 클래스 사용
    class DummyDevSystem:
        def create_project(self, *args, **kwargs):
            return {"project_id": "dummy", "name": "Dummy", "status": "development"}

        def get_projects(self, *args, **kwargs):
            return []

        def get_component_library(self):
            return {"basic": [], "advanced": []}

        def get_deployment_statistics(self, *args, **kwargs):
            return {"total_projects": 0, "status_counts": {}, "recent_deployments": []}

    dev_system = DummyDevSystem()

import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("simple_marketplace.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "simple-secret-key-123"


# 에러 핸들러 추가
@app.errorhandler(404)
def not_found_error(error):
    logger.warning(f"404 오류: {request.url}")
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 오류: {error}")
    return render_template("errors/500.html"), 500


@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"예상치 못한 오류: {e}")
    return jsonify({"error": "서버 오류가 발생했습니다"}), 500


# 간단한 사용자 시스템
class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


# 간단한 사용자 데이터 (실제로는 DB 사용)
users = {
    "admin": User("admin", "admin", "admin"),
    "manager": User("manager", "manager", "manager"),
    "employee": User("employee", "employee", "employee"),
}

# 간단한 캐시 시스템
cache = {}


def get_cached_data(key, ttl=300):
    """캐시된 데이터 조회"""
    if key in cache:
        data, timestamp = cache[key]
        if (datetime.now() - timestamp).seconds < ttl:
            return data
        else:
            del cache[key]
    return None


def set_cached_data(key, data):
    """데이터 캐시 저장"""
    cache[key] = (data, datetime.now())


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    return users.get(user_id)


# 간단한 모듈 데이터
modules = [
    {
        "id": "attendance",
        "name": "출퇴근 관리",
        "description": "직원 출퇴근 시간을 관리하는 모듈",
        "version": "1.0.0",
        "author": "시스템",
        "category": "인사관리",
        "status": "active",
        "installed": False,
        "features": [
            "직원 출근/퇴근 시간 기록",
            "근무 시간 통계 및 분석",
            "지각/조퇴 관리",
            "월간 근무 리포트",
            "휴가 신청 및 승인",
        ],
    },
    {
        "id": "schedule",
        "name": "스케줄 관리",
        "description": "직원 근무 스케줄을 관리하는 모듈",
        "version": "1.0.0",
        "author": "시스템",
        "category": "인사관리",
        "status": "active",
        "installed": False,
        "features": [
            "월간/주간 근무 스케줄",
            "교대 근무 관리",
            "휴가 스케줄 관리",
            "스케줄 충돌 확인",
            "자동 스케줄 생성",
        ],
    },
    {
        "id": "inventory",
        "name": "재고 관리",
        "description": "매장 재고를 관리하는 모듈",
        "version": "1.0.0",
        "author": "시스템",
        "category": "재고관리",
        "status": "active",
        "installed": False,
        "features": [
            "실시간 재고 현황",
            "입고/출고 관리",
            "재고 알림 설정",
            "재고 이동 이력",
            "재고 리포트 생성",
        ],
    },
]

# 설치 진행 상태 저장
installation_progress = {}


# 라우트
@app.route("/")
def index():
    return render_template("simple_index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # 간단한 인증 (실제로는 DB에서 확인)
        if username in users and password == "password":
            login_user(users[username])
            return redirect(url_for("dashboard"))
        else:
            flash("로그인 실패")

    return render_template("simple_login.html")


@app.route("/dashboard")
@login_required
def dashboard():
    # 사용자별 메뉴 가져오기
    user_menus = menu_system.get_user_menus(current_user.id, current_user.role)
    return render_template("simple_dashboard.html", user=current_user, menus=user_menus)


@app.route("/marketplace")
@login_required
def marketplace():
    return render_template("simple_marketplace.html", modules=modules)


@app.route("/api/modules")
@login_required
def api_modules():
    return jsonify(modules)


@app.route("/api/modules/<module_id>/install", methods=["POST"])
@login_required
def install_module(module_id):
    """4단계 설치 플로우 시작"""
    try:
        logger.info(f"모듈 설치 요청: {module_id} by {current_user.username}")

        module = next((m for m in modules if m["id"] == module_id), None)
        if not module:
            logger.warning(f"모듈을 찾을 수 없음: {module_id}")
            return (
                jsonify({"success": False, "message": "모듈을 찾을 수 없습니다."}),
                404,
            )

        # 이미 설치된 모듈인지 확인
        if module.get("installed", False):
            logger.info(f"이미 설치된 모듈: {module_id}")
            return (
                jsonify({"success": False, "message": "이미 설치된 모듈입니다."}),
                400,
            )

        # 1단계: 설치 및 활성화
        result = menu_system.install_module(module_id, current_user.id, module)
        installation_id = result.get("installation_id", str(uuid.uuid4()))

        # 설치 진행 상태 저장
        installation_progress[installation_id] = {
            "module_id": module_id,
            "step": "activated",
            "progress": 50,
            "user_id": current_user.id,
            "timestamp": datetime.now().isoformat(),
        }

        # 모듈 설치 상태 업데이트
        module["installed"] = True

        logger.info(f"모듈 설치 완료: {module_id}")
        return jsonify(
            {
                "success": True,
                "message": f'{module["name"]} 모듈이 설치되었습니다.',
                "installation_id": installation_id,
                "next_step": "configuration",
                "progress": 50,
                "module": {
                    "id": module["id"],
                    "name": module["name"],
                    "status": "installed",
                },
            }
        )
    except Exception as e:
        logger.error(f"모듈 설치 오류: {module_id} - {str(e)}")
        return jsonify({"success": False, "message": f"설치 실패: {str(e)}"}), 500


@app.route("/api/modules/<module_id>/configure", methods=["POST"])
@login_required
def configure_module(module_id):
    """3단계: 모듈 설정"""
    data = request.get_json()
    installation_id = data.get("installation_id")
    settings = data.get("settings", {})

    if not installation_id:
        return jsonify({"success": False, "message": "설치 ID가 필요합니다."})

    try:
        result = menu_system.configure_module(int(installation_id), settings)

        # 진행 상태 업데이트
        if installation_id in installation_progress:
            installation_progress[installation_id]["step"] = "configured"
            installation_progress[installation_id]["progress"] = 75

        return jsonify(
            {
                "success": True,
                "message": "모듈 설정이 완료되었습니다.",
                "next_step": "onboarding",
                "progress": 75,
            }
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"설정 실패: {str(e)}"})


@app.route("/api/modules/<module_id>/onboarding", methods=["POST"])
@login_required
def complete_onboarding(module_id):
    """4단계: 온보딩 완료"""
    data = request.get_json()
    installation_id = data.get("installation_id")

    if not installation_id:
        return jsonify({"success": False, "message": "설치 ID가 필요합니다."})

    try:
        result = menu_system.complete_onboarding(int(installation_id))

        # 진행 상태 업데이트
        if installation_id in installation_progress:
            installation_progress[installation_id]["step"] = "completed"
            installation_progress[installation_id]["progress"] = 100

        return jsonify(
            {"success": True, "message": "모듈 설치가 완료되었습니다!", "progress": 100}
        )
    except Exception as e:
        return jsonify({"success": False, "message": f"온보딩 실패: {str(e)}"})


@app.route("/api/modules/<module_id>/uninstall", methods=["POST"])
@login_required
def uninstall_module(module_id):
    for module in modules:
        if module["id"] == module_id:
            try:
                result = menu_system.uninstall_module(module_id, current_user.id)
                module["installed"] = False
                return jsonify(
                    {
                        "success": True,
                        "message": f'{module["name"]} 모듈이 제거되었습니다.',
                    }
                )
            except Exception as e:
                return jsonify({"success": False, "message": f"제거 실패: {str(e)}"})

    return jsonify({"success": False, "message": "모듈을 찾을 수 없습니다."})


@app.route("/modules/<module_id>")
@login_required
def module_detail(module_id):
    module = next((m for m in modules if m["id"] == module_id), None)
    if module:
        return render_template("simple_module_detail.html", module=module)
    return "모듈을 찾을 수 없습니다.", 404


@app.route("/modules/<module_id>/install-flow")
@login_required
def module_install_flow(module_id):
    """4단계 설치 플로우 페이지"""
    module = next((m for m in modules if m["id"] == module_id), None)
    if not module:
        return "모듈을 찾을 수 없습니다.", 404

    return render_template("simple_install_flow.html", module=module)


@app.route("/api/menu/statistics")
@login_required
def api_menu_statistics():
    """메뉴 통계 API"""
    try:
        stats = menu_system.get_menu_statistics()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/menu-management")
@login_required
def menu_management():
    """메뉴 관리 페이지"""
    try:
        stats = menu_system.get_menu_statistics()
        user_menus = menu_system.get_user_menus(current_user.id, current_user.role)
        return render_template(
            "simple_menu_management.html", stats=stats, menus=user_menus
        )
    except Exception as e:
        return render_template("simple_menu_management.html", stats={}, menus=[])


# 개발 모드 라우트
@app.route("/dev-mode")
@login_required
def dev_mode():
    """개발 모드 대시보드"""
    try:
        projects = dev_system.get_projects(current_user.id)
        stats = dev_system.get_deployment_statistics(current_user.id)
        return render_template("simple_dev_mode.html", projects=projects, stats=stats)
    except Exception as e:
        return render_template("simple_dev_mode.html", projects=[], stats={})


@app.route("/dev-mode/projects/new", methods=["GET", "POST"])
@login_required
def create_project():
    """새 프로젝트 생성"""
    if request.method == "POST":
        data = request.get_json()
        result = dev_system.create_project(
            data["name"], data["description"], data["module_type"], current_user.id
        )
        return jsonify(result)

    return render_template("simple_create_project.html")


@app.route("/dev-mode/projects/<project_id>")
@login_required
def project_editor(project_id):
    """프로젝트 에디터"""
    try:
        project = dev_system.get_project(project_id)
        component_library = dev_system.get_component_library()
        if project:
            return render_template(
                "simple_project_editor.html",
                project=project,
                component_library=component_library,
            )
        else:
            return "프로젝트를 찾을 수 없습니다.", 404
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}", 500


# 개발 모드 API
@app.route("/api/dev/projects")
@login_required
def api_dev_projects():
    """개발 프로젝트 목록 API"""
    try:
        projects = dev_system.get_projects(current_user.id)
        return jsonify({"success": True, "data": projects})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/projects/<project_id>")
@login_required
def api_dev_project(project_id):
    """개발 프로젝트 상세 API"""
    try:
        project = dev_system.get_project(project_id)
        if project:
            return jsonify({"success": True, "data": project})
        else:
            return jsonify(
                {"success": False, "message": "프로젝트를 찾을 수 없습니다."}
            )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/projects/<project_id>/components", methods=["POST"])
@login_required
def api_add_component(project_id):
    """컴포넌트 추가 API"""
    try:
        data = request.get_json()
        result = dev_system.add_component(project_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/projects/<project_id>/components/<component_id>", methods=["PUT"])
@login_required
def api_update_component(project_id, component_id):
    """컴포넌트 업데이트 API"""
    try:
        data = request.get_json()
        result = dev_system.update_component(project_id, component_id, data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route(
    "/api/dev/projects/<project_id>/components/<component_id>", methods=["DELETE"]
)
@login_required
def api_delete_component(project_id, component_id):
    """컴포넌트 삭제 API"""
    try:
        result = dev_system.delete_component(project_id, component_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/projects/<project_id>/versions", methods=["POST"])
@login_required
def api_create_version(project_id):
    """버전 생성 API"""
    try:
        data = request.get_json()
        result = dev_system.create_version(
            project_id, data["version_name"], data["description"], current_user.id
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/projects/<project_id>/deploy", methods=["POST"])
@login_required
def api_deploy_project(project_id):
    """프로젝트 배포 API"""
    try:
        data = request.get_json()
        result = dev_system.deploy_project(
            project_id, data["version_id"], data["environment"], current_user.id
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


@app.route("/api/dev/test-data/<project_id>/<data_type>", methods=["POST"])
@login_required
def api_generate_test_data(project_id, data_type):
    """테스트 데이터 생성 API"""
    try:
        result = dev_system.generate_test_data(project_id, data_type)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# 메뉴 관련 API
@app.route("/api/menu/user-menus")
@login_required
def api_user_menus():
    """사용자별 메뉴 API"""
    try:
        user_menus = menu_system.get_user_menus(current_user.id, current_user.role)
        return jsonify({"success": True, "data": user_menus})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/menu/menu-access/<int:menu_id>", methods=["POST"])
@login_required
def api_menu_access(menu_id):
    """메뉴 접근 기록 API"""
    try:
        # 메뉴 접근 기록 로직 (간단한 구현)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


# admin_dashboard 라우트 추가
@app.route("/admin_dashboard")
@login_required
def admin_dashboard():
    """관리자 대시보드"""
    try:
        # 간단한 통계 데이터
        stats = {
            "total_branches": 5,
            "total_staff": 25,
            "total_sales": 15000000,
            "notifications": [],
        }
        return render_template("admin_dashboard.html", **stats)
    except Exception as e:
        return f"오류가 발생했습니다: {str(e)}", 500


@app.template_global("momentjs")
def momentjs():
    from datetime import datetime

    return datetime.now()


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)
