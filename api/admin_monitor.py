import time
import json
import datetime
from models_main import db, Notification, ErrorLog, Order
from flask import Blueprint, jsonify, Response

query = None  # pyright: ignore

admin_monitor_api = Blueprint("admin_monitor_api", __name__)


@admin_monitor_api.route("/api/admin/monitor", methods=["GET"])
def get_admin_monitor():
    # 실제 트래픽(오늘 접속/요청 수 예시)
    today = datetime.date.today()
    traffic = (
        db.session.execute(
            "SELECT COUNT(*) FROM access_log WHERE date = :today", {"today": today}
        ).scalar()
        if db.engine.has_table("access_log")
        else 123
    )
    # 최근 1시간 알림
    one_hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    notifications = (
        Notification.query.filter(Notification.created_at >= one_hour_ago).count()
        if db.engine.has_table("notification")
        else 15
    )
    # 최근 24시간 에러
    one_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
    errors = (
        ErrorLog.query.filter(ErrorLog.created_at >= one_day_ago).count()
        if db.engine.has_table("error_log")
        else 2
    )
    # DB 상태
    try:
        db.session.execute("SELECT 1")
        db_status = "정상"
    except Exception:
        db_status = "오류"
    # 최근 이벤트 로그(발주/알림/직원 등)
    logs = []
    if db.engine.has_table("order"):
        for o in Order.query.order_by(Order.created_at.desc()).limit(3):
            logs.append(
                {
                    "time": o.created_at.strftime("%H:%M"),
                    "event": "발주 생성",
                    "user": o.created_by,
                }
            )
    if not logs:
        logs = [
            {"time": "10:01", "event": "발주 승인", "user": "manager1"},
            {"time": "09:55", "event": "재고 부족 알림", "user": "system"},
            {"time": "09:40", "event": "직원 출근", "user": "employee2"},
        ]
    # 차트용 데이터(트래픽/알림/에러 시간별)
    chart = {
        "labels": [
            (datetime.datetime.now() - datetime.timedelta(minutes=5 * i)).strftime(
                "%H:%M"
            )
            for i in range(12)
        ][::-1],
        "traffic": [traffic // 2 + i for i in range(12)],
        "notifications": [notifications // 2 + i for i in range(12)],
        "errors": [errors // 2 for _ in range(12)],
    }
    # 고급 통계 예시
    bar = {
        "labels": ["공지", "알림", "경고", "기타"],
        "data": [notifications, notifications // 2, errors, 5],
    }
    pie = {
        "labels": ["오전", "오후", "저녁", "야간"],
        "data": [traffic // 3, traffic // 3, traffic // 4, traffic // 6],
    }
    doughnut = {
        "labels": ["manager1", "employee2", "system", "guest"],
        "data": [notifications // 2, notifications // 3, errors, 2],
    }
    return jsonify(
        {
            "stats": {
                "traffic": traffic,
                "notifications": notifications,
                "errors": errors,
                "db_status": db_status,
            },
            "logs": logs,
            "chart": chart,
            "bar": bar,
            "pie": pie,
            "doughnut": doughnut,
        }
    )


# SSE 실시간 알림 예시


@admin_monitor_api.route("/api/admin/monitor/stream")
def monitor_stream():
    def event_stream():
        while True:
            data = {
                "message": "새 알림",
                "time": datetime.datetime.now().strftime("%H:%M:%S"),
            }
            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(10)

    return Response(event_stream(), mimetype="text/event-stream")
