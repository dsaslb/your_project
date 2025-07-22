"""
고급 데이터 분석 및 비즈니스 인텔리전스 대시보드 라우트
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
import logging

logger = logging.getLogger(__name__)

analytics_dashboard_bp = Blueprint('analytics_dashboard', __name__)

@analytics_dashboard_bp.route("/admin/analytics-dashboard")
@login_required
def admin_analytics_dashboard():
    """고급 데이터 분석 및 비즈니스 인텔리전스 대시보드"""
    try:
        return render_template("admin/analytics_dashboard.html")
    except Exception as e:
        logger.error(f"분석 대시보드 로드 오류: {str(e)}")
        return "대시보드를 로드할 수 없습니다.", 500

@analytics_dashboard_bp.route("/api/analytics/dashboard/status")
def analytics_dashboard_status():
    """분석 대시보드 상태 확인"""
    try:
        return jsonify({
            "success": True,
            "status": "active",
            "message": "분석 대시보드가 정상 동작 중입니다."
        })
    except Exception as e:
        logger.error(f"분석 대시보드 상태 확인 오류: {str(e)}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def init_app(app):
    """애플리케이션에 블루프린트 등록"""
    app.register_blueprint(analytics_dashboard_bp)
    logger.info("분석 대시보드 라우트 등록 완료") 