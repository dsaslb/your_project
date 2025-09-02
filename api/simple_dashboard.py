"""
간단한 대시보드 API
모바일 앱용 대시보드 데이터 제공
"""
from flask import Blueprint, jsonify
from datetime import datetime, timezone

simple_dashboard_bp = Blueprint("simple_dashboard", __name__)

@simple_dashboard_bp.route("/api/mobile/dashboard", methods=["GET"])
def get_dashboard():
    """모바일 대시보드 데이터 (인증 없음)"""
    try:
        # 기본 대시보드 데이터
        dashboard_data = {
            "user": {
                "id": 1,
                "username": "개발자",
                "role": "employee"
            },
            "today_schedule": "09:00 - 18:00",
            "attendance_status": "출근",
            "pending_orders": 3,
            "inventory_alerts": 2,
            "quick_stats": {
                "today_orders": 15,
                "pending_orders": 3,
                "today_revenue": 450000,
                "staff_on_duty": 8
            },
            "recent_activities": [
                {
                    "id": 1,
                    "type": "order",
                    "title": "새 주문 접수",
                    "message": "테이블 5번에서 김치찌개 2개 주문",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "priority": "normal"
                },
                {
                    "id": 2,
                    "type": "inventory",
                    "title": "재고 부족 알림",
                    "message": "김치 재고가 부족합니다",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "priority": "high"
                }
            ],
            "quick_actions": [
                {
                    "id": "new_order",
                    "title": "새 주문",
                    "icon": "plus-circle",
                    "color": "blue"
                },
                {
                    "id": "inventory_check",
                    "title": "재고 확인",
                    "icon": "package",
                    "color": "green"
                },
                {
                    "id": "attendance",
                    "title": "출퇴근",
                    "icon": "clock",
                    "color": "orange"
                },
                {
                    "id": "reports",
                    "title": "보고서",
                    "icon": "chart-bar",
                    "color": "purple"
                }
            ],
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return jsonify(dashboard_data)
        
    except Exception as e:
        return jsonify({
            "error": "대시보드 데이터를 불러올 수 없습니다",
            "message": str(e)
        }), 500

@simple_dashboard_bp.route("/api/mobile/status", methods=["GET"])
def get_status():
    """모바일 앱 상태 확인"""
    return jsonify({
        "status": "ok",
        "message": "모바일 API가 정상적으로 작동 중입니다",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
