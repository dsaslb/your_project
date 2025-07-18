from datetime import datetime
from flask import Blueprint, jsonify

form = None  # pyright: ignore

health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """백엔드 서버 상태 확인 API"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Backend server is running",
            }
        ),
        200,
    )


@health_bp.route("/api/health", methods=["GET"])
def api_health_check():
    """API 경로로 접근하는 health check"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "message": "Backend server is running",
            }
        ),
        200,
    )
