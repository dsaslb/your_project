"""
모듈 개발 모드 라우트
샌드박스 환경에서 모듈을 개발, 테스트, 배포하는 라우트
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
module_dev_routes_bp = Blueprint(
    "module_dev_routes", __name__, url_prefix="/dev-modules"
)


@module_dev_routes_bp.route("/")
@login_required
def development_dashboard():
    """모듈 개발 대시보드"""
    try:
        return render_template("module_development/dashboard.html")
    except Exception as e:
        logger.error(f"개발 대시보드 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects")
@login_required
def projects_list():
    """개발 프로젝트 목록"""
    try:
        return render_template("module_development/projects.html")
    except Exception as e:
        logger.error(f"프로젝트 목록 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects/new")
@login_required
def new_project():
    """새 프로젝트 생성"""
    try:
        return render_template("module_development/new_project.html")
    except Exception as e:
        logger.error(f"새 프로젝트 페이지 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects/<project_id>")
@login_required
def project_editor(project_id):
    """프로젝트 에디터"""
    try:
        return render_template("module_development/editor.html", project_id=project_id)
    except Exception as e:
        logger.error(f"프로젝트 에디터 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects/<project_id>/preview")
@login_required
def project_preview(project_id):
    """프로젝트 미리보기"""
    try:
        return render_template("module_development/preview.html", project_id=project_id)
    except Exception as e:
        logger.error(f"프로젝트 미리보기 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects/<project_id>/deploy")
@login_required
def project_deploy(project_id):
    """프로젝트 배포"""
    try:
        return render_template("module_development/deploy.html", project_id=project_id)
    except Exception as e:
        logger.error(f"프로젝트 배포 페이지 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/projects/<project_id>/versions")
@login_required
def project_versions(project_id):
    """프로젝트 버전 관리"""
    try:
        return render_template(
            "module_development/versions.html", project_id=project_id
        )
    except Exception as e:
        logger.error(f"프로젝트 버전 관리 페이지 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/designer")
@login_required
def module_designer():
    """모듈 디자이너"""
    try:
        return render_template("module_development/designer.html")
    except Exception as e:
        logger.error(f"모듈 디자이너 로드 실패: {e}")
        return render_template("errors/500.html"), 500


@module_dev_routes_bp.route("/sandbox")
@login_required
def development_sandbox():
    """개발 샌드박스"""
    try:
        return render_template("module_development/sandbox.html")
    except Exception as e:
        logger.error(f"개발 샌드박스 로드 실패: {e}")
        return render_template("errors/500.html"), 500
