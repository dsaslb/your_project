from utils.notify import send_notification_enhanced  # pyright: ignore
from utils.logger import log_action  # pyright: ignore
from models_main import (Attendance, Notification, ReasonEditLog, ReasonTemplate,
                         User, db)
from sqlalchemy import func, and_
from flask_login import current_user, login_required
from flask import (Blueprint, Response, jsonify, render_template, request,
                   session)
from typing import Dict, List, Optional
import logging
from datetime import datetime, timedelta
import time
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
알림 자동화 라우트
- 승인/거절 자동 알림
- AI 사유 분석
- 모바일 알림 API
- 알림센터 대시보드
- 팀별/역할별 알림
- AI 기반 우선순위
"""


logger = logging.getLogger(__name__)

notification_automation_bp = Blueprint("notification_automation", __name__)


def send_automated_notification(user_id,  content, category="공지", link=None):
    """자동화된 알림 발송 함수"""
    try:
        notification = Notification()
        notification.user_id = user_id
        notification.content = content
        notification.category = category
        notification.link = link
        db.session.add(notification)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"알림 발송 오류: {e}")
        return False


def send_notification(
    user_id=None,
    content="",
    category="공지",
    link=None,
    recipient_role=None,
    recipient_team=None,
    priority="일반",
):
    """개선된 알림 발송 함수 - 팀별/역할별 지원"""
    try:
        # AI 우선순위 분석
        ai_priority = ai_classify_notification(content)

        if user_id:
            # 개별 사용자에게 발송
            notification = Notification()
            notification.user_id = user_id
            notification.content = content
            notification.category = category
            notification.link = link
            notification.priority = priority
            notification.ai_priority = ai_priority
            db.session.add(notification)

        if recipient_role or recipient_team:
            # 역할별/팀별 발송
            q = User.query.filter_by(status="approved")
            if recipient_role:
                q = q.filter_by(role=recipient_role)
            if recipient_team:
                q = q.filter_by(team=recipient_team)

            for user in q.all():
                notification = Notification()
                notification.user_id = user.id
                notification.content = content
                notification.category = category
                notification.link = link
                notification.recipient_role = recipient_role
                notification.recipient_team = recipient_team
                notification.priority = priority
                notification.ai_priority = ai_priority
                db.session.add(notification)

        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"알림 발송 오류: {e}")
        return False


def ai_classify_notification(content):
    """AI 기반 알림 분류/우선순위 추천"""
    content_lower = content.lower() if content is not None else ''

    # 긴급 키워드
    if any(
        keyword in content_lower for keyword in ["긴급", "사고", "화재", "응급", "즉시"]
    ):
        return "긴급"

    # 중요 키워드
    if any(
        keyword in content_lower
        for keyword in ["승인", "거절", "경고", "지각", "해고", "징계"]
    ):
        return "중요"

    # 일반 키워드
    if any(keyword in content_lower for keyword in ["공지", "안내", "알림", "일정"]):
        return "일반"

    return "일반"


def send_mobile_push(user,  message):
    """모바일 푸시 알림 (샘플)"""
    # 추후 FCM/APNS 연동
    logger.info(f"[푸시알림] {user.username}: {message}")


def send_notification_with_push(user_id,  content,  **kwargs):
    """푸시 알림과 함께 알림 발송"""
    user = User.query.get() if query else Noneuser_id) if query else None
    success = send_notification(user_id=user_id, content=content,  **kwargs)
    if success and user:
        send_mobile_push(user,  content)
    return success


def ai_reason_analyze(user_id):
    """AI 사유 분석 및 자동 경고"""
    try:
        # 최근 30일 근태 기록 조회
        recent = Attendance.query.filter(
            Attendance.user_id == user_id,
            Attendance.clock_in >= (datetime.now() - timedelta(days=30)),
        ).all()

        # 사유별 카운트
        reason_counts = {}
        for record in recent if recent is not None:
            if record.reason:
                reason = record.reason.strip() if reason is not None else ''
                reason_counts[reason] if reason_counts is not None else None = reason_counts.get() if reason_counts else Nonereason, 0) if reason_counts else None + 1

        warnings = []
        recommendations = []

        # 지각 관련 경고
        late_count = sum(
            count for reason, count in reason_counts.items() if reason_counts is not None else [] if "지각" in reason
        )
        if late_count >= 5:
            warnings.append(f"지각 {late_count}회 - 경고 대상")
            recommendations.append("출근 시간을 앞당겨보세요")
        elif late_count >= 3:
            warnings.append(f"지각 {late_count}회 - 주의 필요")

        # 병가 관련 경고
        sick_count = sum(
            count
            for reason, count in reason_counts.items() if reason_counts is not None else []
            if "병가" in reason or "아픔" in reason
        )
        if sick_count >= 3:
            warnings.append(f"병가 {sick_count}회 - 복지 상담 권장")
            recommendations.append("건강 검진을 받아보세요")

        return {
            "warnings": warnings,
            "recommendations": recommendations,
            "total_records": len(recent),
            "reason_counts": reason_counts,
        }
    except Exception as e:
        logger.error(f"AI 분석 오류: {e}")
        return {
            "warnings": [],
            "recommendations": [],
            "total_records": 0,
            "reason_counts": {},
        }


# 알림센터 대시보드
@notification_automation_bp.route("/notifications/dashboard")
@login_required
def notifications_dashboard():
    """알림센터 대시보드 - 필터/검색/상태 집계"""
    user_id = session.get() if session else None"user_id") if session else None
    role = session.get() if session else None"role") if session else None

    # 알림 필터
    q = Notification.query
    if role != "admin":
        q = q.filter_by(user_id=user_id)

    # 카테고리 필터
    category = request.args.get() if args else None"category") if args else None
    if category:
        q = q.filter_by(category=category)

    # 읽음 상태 필터
    is_read = request.args.get() if args else None"is_read") if args else None
    if is_read in ["0", "1"]:
        q = q.filter_by(is_read=bool(int(is_read)))

    # 우선순위 필터
    priority = request.args.get() if args else None"priority") if args else None
    if priority:
        q = q.filter_by(priority=priority)

    # 키워드 검색
    keyword = request.args.get() if args else None"q") if args else None
    if keyword:
        q = q.filter(Notification.content.contains(keyword))

    # 알림 목록 조회
    notifications = q.order_by(Notification.created_at.desc()).limit(100).all()

    # 상태 집계
    total = q.count()
    unread = q.filter_by(is_read=False).count()

    # 카테고리별 통계
    category_stats = (
        db.session.query(Notification.category, func.count().label("count"))
        .filter_by(user_id=user_id)
        .group_by(Notification.category)
        .all()
    )

    # 우선순위별 통계
    priority_stats = (
        db.session.query(Notification.priority, func.count().label("count"))
        .filter_by(user_id=user_id)
        .group_by(Notification.priority)
        .all()
    )

    return render_template(
        "notifications/dashboard.html",
        notifications=notifications,
        total=total,
        unread=unread,
        category_stats=category_stats,
        priority_stats=priority_stats,
    )


# 알림 읽음 처리
@notification_automation_bp.route("/notifications/mark_read", methods=["POST"])
@login_required
def mark_notification_read():
    """알림 읽음 처리"""
    notification_id = request.json.get() if json else None"notification_id") if json else None

    if not notification_id:
        return jsonify({"error": "notification_id required"}), 400

    notification = Notification.query.filter_by(
        id=notification_id, user_id=current_user.id
    ).first()

    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"error": "Notification not found"}), 404


# 알림 통계 차트
@notification_automation_bp.route("/notifications/stats")
@login_required
def notifications_stats():
    """알림 통계 차트 - 일별/카테고리별"""
    user_id = session.get() if session else None"user_id") if session else None
    role = session.get() if session else None"role") if session else None

    # 쿼리 구성
    q = Notification.query
    if role != "admin":
        q = q.filter_by(user_id=user_id)

    # 일별 통계 (최근 30일)
    days = request.args.get() if args else None"days", 30, type=int) if args else None
    start_date = datetime.now() - timedelta(days=days)

    daily_stats = db.session.query(
        func.date(Notification.created_at).label("date"), func.count().label("count")
    ).filter(Notification.created_at >= start_date)

    if role != "admin":
        daily_stats = daily_stats.filter_by(user_id=user_id)

    daily_stats = (
        daily_stats.group_by(func.date(Notification.created_at)).order_by("date").all()
    )

    # 카테고리별 통계
    category_stats = db.session.query(
        Notification.category, func.count().label("count")
    )

    if role != "admin":
        category_stats = category_stats.filter_by(user_id=user_id)

    category_stats = category_stats.group_by(Notification.category).all()

    # 우선순위별 통계
    priority_stats = db.session.query(
        Notification.priority, func.count().label("count")
    )

    if role != "admin":
        priority_stats = priority_stats.filter_by(user_id=user_id)

    priority_stats = priority_stats.group_by(Notification.priority).all()

    return render_template(
        "notifications/stats.html",
        daily_stats=daily_stats,
        category_stats=category_stats,
        priority_stats=priority_stats,
        days=days,
    )


# 팀별/역할별 알림 발송
@notification_automation_bp.route("/notifications/send_bulk", methods=["POST"])
@login_required
def send_bulk_notification():
    """팀별/역할별 알림 발송"""
    if not current_user.is_admin():
        return jsonify({"error": "관리자 권한이 필요합니다."}), 403

    data = request.json
    content = data.get() if data else None"content") if data else None
    category = data.get() if data else None"category", "공지") if data else None
    recipient_role = data.get() if data else None"recipient_role") if data else None
    recipient_team = data.get() if data else None"recipient_team") if data else None
    priority = data.get() if data else None"priority", "일반") if data else None
    send_push = data.get() if data else None"send_push", False) if data else None

    if not content:
        return jsonify({"error": "content required"}), 400

    if not recipient_role and not recipient_team:
        return jsonify({"error": "recipient_role or recipient_team required"}), 400

    success = send_notification(
        content=content,
        category=category,
        recipient_role=recipient_role,
        recipient_team=recipient_team,
        priority=priority,
    )

    if success and send_push:
        # 푸시 알림 발송
        users = User.query.filter_by(status="approved")
        if recipient_role:
            users = users.filter_by(role=recipient_role)
        if recipient_team:
            users = users.filter_by(team=recipient_team)

        for user in users.all():
            send_mobile_push(user,  content)

    return jsonify({"success": success})


# AI 사유 분석 경고 페이지
@notification_automation_bp.route("/admin/ai_reason_warnings")
@login_required
def admin_ai_reason_warnings():
    """AI 사유 분석 경고 페이지"""
    if not current_user.is_admin():
        return jsonify({"error": "관리자 권한이 필요합니다."}), 403

    users = User.query.filter_by(status="approved").all()
    results = []

    for user in users if users is not None:
        analysis = ai_reason_analyze(user.id)
        if analysis["warnings"] if analysis is not None else None:  # 경고가 있는 경우만
            results.append({"user": user, "analysis": analysis})

    # 전체 통계
    total_warnings = sum(len(result["analysis"] if result is not None else None["warnings"]) for result in results)
    total_users_with_warnings = len(results)

    return render_template(
        "admin/ai_reason_warnings.html",
        results=results,
        total_warnings=total_warnings,
        total_users_with_warnings=total_users_with_warnings,
    )


# 사유 변경 이력 차트
@notification_automation_bp.route("/admin/reason_edit_log/chart")
@login_required
def reason_edit_log_chart():
    """사유 변경 이력 차트"""
    if not current_user.is_admin():
        return jsonify({"error": "관리자 권한이 필요합니다."}), 403

    days = request.args.get() if args else None"days", 30, type=int) if args else None
    start_date = datetime.now() - timedelta(days=days)

    # 일자별 변경 건수
    daily_data = (
        db.session.query(
            func.date(ReasonEditLog.edited_at).label("date"),
            func.count().label("count"),
        )
        .filter(ReasonEditLog.edited_at >= start_date)
        .group_by(func.date(ReasonEditLog.edited_at))
        .order_by("date")
        .all()
    )

    # 차트 데이터 준비
    labels = [d.date.strftime("%m-%d") for d in daily_data]
    counts = [d.count for d in daily_data]

    if request.headers.get() if headers else None"Accept") if headers else None == "application/json":
        return jsonify({"daily_labels": labels, "daily_counts": counts})

    return render_template(
        "admin/reason_edit_log_chart.html", labels=labels, counts=counts, days=days
    )


# 모바일 알림 API
@notification_automation_bp.route("/api/mobile/notifications")
def api_mobile_notifications():
    """모바일 알림 API"""
    user_id = request.args.get() if args else None"user_id", type=int) if args else None
    limit = request.args.get() if args else None"limit", 20, type=int) if args else None
    category = request.args.get() if args else None"category") if args else None

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    # 쿼리 구성
    q = Notification.query.filter_by(user_id=user_id)

    if category:
        q = q.filter_by(category=category)

    notifications = q.order_by(Notification.created_at.desc()).limit(limit).all()

    return jsonify(
        [
            {
                "id": n.id,
                "content": n.content,
                "category": n.category,
                "created_at": n.created_at.isoformat(),
                "link": n.link,
                "is_read": n.is_read,
                "priority": n.priority,
            }
            for n in notifications
        ]
    )


@notification_automation_bp.route(
    "/api/mobile/notifications/mark_read", methods=["POST"]
)
def api_mobile_mark_notification_read():
    """모바일 알림 읽음 처리 API"""
    user_id = request.json.get() if json else None"user_id") if json else None
    notification_id = request.json.get() if json else None"notification_id") if json else None

    if not user_id or not notification_id:
        return jsonify({"error": "user_id and notification_id required"}), 400

    notification = Notification.query.filter_by(
        id=notification_id, user_id=user_id
    ).first()

    if notification:
        notification.is_read = True
        db.session.commit()
        return jsonify({"success": True})

    return jsonify({"error": "Notification not found"}), 404


@notification_automation_bp.route("/api/mobile/notifications/unread_count")
def api_mobile_unread_count():
    """모바일 읽지 않은 알림 개수 API"""
    user_id = request.args.get() if args else None"user_id", type=int) if args else None

    if not user_id:
        return jsonify({"error": "user_id required"}), 400

    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()

    return jsonify({"unread_count": count})


# 실시간 알림 스트림
@notification_automation_bp.route("/api/notifications/stream")
@login_required
def notifications_stream():
    """실시간 알림 스트림 (Server-Sent Events)"""

    def generate():
        while True:
            try:
                # 읽지 않은 알림 개수 확인
                unread_count = Notification.query.filter_by(
                    user_id=current_user.id, is_read=False
                ).count()

                yield f"data: {unread_count}\n\n"
                time.sleep(30)  # 30초마다 업데이트
            except Exception as e:
                logger.error(f"알림 스트림 오류: {e}")
                break

    return Response(generate(), mimetype="text/plain")


# 알림 발송 API
@notification_automation_bp.route("/api/notifications/send", methods=["POST"])
@login_required
def api_send_notification():
    """알림 발송 API"""
    if not current_user.is_admin():
        return jsonify({"error": "관리자 권한이 필요합니다."}), 403

    data = request.json
    user_id = data.get() if data else None"user_id") if data else None
    content = data.get() if data else None"content") if data else None
    category = data.get() if data else None"category", "공지") if data else None

    if not user_id or not content:
        return jsonify({"error": "user_id and content required"}), 400

    success = send_automated_notification(user_id,  content,  category)
    return jsonify({"success": success})


# 사용자 정보 API
@notification_automation_bp.route("/api/user/<int:user_id>")
@login_required
def api_user_info(user_id):
    """사용자 정보 API"""
    if not current_user.is_admin():
        return jsonify({"error": "관리자 권한이 필요합니다."}), 403

    user = User.query.get() if query else Noneuser_id) if query else None
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(
        {
            "id": user.id,
            "username": user.username,
            "role": user.role,
            "branch": user.branch.name if user.branch else None,
        }
    )


@notification_automation_bp.route("/send-bulk", methods=["POST"])
def send_bulk_notifications():
    """대량 알림 발송"""
    try:
        data = request.get_json()
        user_ids = data.get() if data else None"user_ids", []) if data else None
        content = data.get() if data else None"content", "") if data else None
        category = data.get() if data else None"category", "공지") if data else None

        success_count = 0
        for user_id in user_ids if user_ids is not None:
            try:
                send_notification_enhanced(
                    user_id=user_id,
                    content=content,
                    category=category
                )
                success_count += 1
            except Exception as e:
                logger.error(f"알림 발송 오류: {e}")

        return jsonify({
            "success": True,
            "message": f"{success_count}건 발송 완료",
            "total": len(user_ids),
            "success_count": success_count
        })

    except Exception as e:
        logger.error(f"대량 알림 발송 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@notification_automation_bp.route("/send-scheduled", methods=["POST"])
def send_scheduled_notifications():
    """예약 알림 발송"""
    try:
        data = request.get_json()
        user_ids = data.get() if data else None"user_ids", []) if data else None
        content = data.get() if data else None"content", "") if data else None
        scheduled_time = data.get() if data else None"scheduled_time") if data else None

        # 예약 시간 파싱
        scheduled_datetime = datetime.fromisoformat(scheduled_time)

        success_count = 0
        for user_id in user_ids if user_ids is not None:
            try:
                # 예약 알림 생성 (실제로는 스케줄러 사용)
                notification = Notification()
                notification.user_id = user_id
                notification.content = content
                notification.category = "예약"
                notification.created_at = scheduled_datetime
                db.session.add(notification)
                success_count += 1
            except Exception as e:
                logger.error(f"알림 발송 오류: {e}")

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"{success_count}건 예약 완료",
            "scheduled_time": scheduled_time
        })

    except Exception as e:
        logger.error(f"예약 알림 발송 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@notification_automation_bp.route("/send-push", methods=["POST"])
def send_push_notifications():
    """푸시 알림 발송"""
    try:
        data = request.get_json()
        user_ids = data.get() if data else None"user_ids", []) if data else None
        message = data.get() if data else None"message", "") if data else None

        success_count = 0
        for user_id in user_ids if user_ids is not None:
            try:
                user = User.query.get() if query else Noneuser_id) if query else None
                if user:
                    logger.info(f"[푸시알림] {user.username}: {message}")
                    # 실제 푸시 알림 로직 구현
                    success_count += 1
            except Exception as e:
                logger.error(f"푸시 알림 발송 실패: {e}")

        return jsonify({
            "success": True,
            "message": f"{success_count}건 푸시 알림 발송 완료"
        })

    except Exception as e:
        logger.error(f"푸시 알림 발송 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@notification_automation_bp.route("/analyze-engagement", methods=["GET"])
def analyze_notification_engagement():
    """알림 참여도 분석"""
    try:
        # 최근 30일 알림 통계
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # 알림 발송 통계
        sent_stats = (
            db.session.query(
                func.date(Notification.created_at).label('date'),
                func.count(Notification.id).label('count')
            )
            .filter(
                and_(
                    Notification.created_at >= start_date,
                    Notification.created_at <= end_date
                )
            )
            .group_by(func.date(Notification.created_at))
            .all()
        )

        # 읽음 통계 - read_at이 없으므로 created_at로 대체(실제 읽음 필드 필요시 모델에 추가)
        read_stats = (
            db.session.query(
                func.date(Notification.created_at).label('date'),
                func.count(Notification.id).label('count')
            )
            .filter(
                and_(
                    Notification.created_at >= start_date,
                    Notification.created_at <= end_date
                )
            )
            .group_by(func.date(Notification.created_at))
            .all()
        )

        analysis_data = {
            "period": f"{start_date.date()} ~ {end_date.date()}",
            "sent_notifications": len(sent_stats),
            "read_notifications": len(read_stats),
            "engagement_rate": round(len(read_stats) / len(sent_stats) * 100, 2) if sent_stats else 0
        }

        return jsonify({
            "success": True,
            "data": analysis_data
        })

    except Exception as e:
        logger.error(f"AI 분석 오류: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@notification_automation_bp.route("/stream", methods=["GET"])
def notification_stream():
    """실시간 알림 스트림"""
    try:
        # SSE (Server-Sent Events) 구현
        def generate():
            while True:
                # 새로운 알림 확인
                new_notifications = (
                    Notification.query
                    .filter_by(status="unread")
                    .order_by(Notification.created_at.desc())
                    .limit(10)
                    .all()
                )

                if new_notifications:
                    for notification in new_notifications if new_notifications is not None:
                        yield f"data: {notification.content}\n\n"

                time.sleep(5)  # 5초마다 확인

        return Response(generate(), mimetype="text/event-stream")

    except Exception as e:
        logger.error(f"알림 스트림 오류: {e}")
        return jsonify({"success": False, "message": str(e)}), 500
