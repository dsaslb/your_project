"""
간단한 테스트 서버
대시보드 API만 포함
"""
from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

@app.route("/healthz", methods=["GET"])
def healthz():
    """헬스체크"""
    return jsonify({
        "ok": True,
        "database": {"status": "ok", "response_time_ms": 0},
        "system": {"cpu_percent": 0, "memory_percent": 0, "disk_percent": 0},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": 0
    })

@app.route("/api/mobile/dashboard", methods=["GET"])
def get_dashboard():
    """모바일 대시보드 데이터"""
    try:
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

@app.route("/api/mobile/status", methods=["GET"])
def get_status():
    """모바일 앱 상태 확인"""
    return jsonify({
        "status": "ok",
        "message": "모바일 API가 정상적으로 작동 중입니다",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

if __name__ == '__main__':
    print("🚀 간단한 테스트 서버 시작...")
    print("🌐 서버 주소: http://localhost:5000")
    print("📊 대시보드: http://localhost:5000/api/mobile/dashboard")
    print("🏥 헬스체크: http://localhost:5000/healthz")
    app.run(host='0.0.0.0', port=5000, debug=True)
