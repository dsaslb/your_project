from services.notice_service import create_notice_for_event  # pyright: ignore
from utils.logger import log_action, log_error  # pyright: ignore
from models_main import Schedule, User
from extensions import db
from sqlalchemy import and_
from flask_login import current_user, login_required
from flask import Blueprint, flash, jsonify, render_template, request, redirect, url_for
from dateutil import parser as date_parser
from datetime import datetime, timedelta
args = None  # pyright: ignore
query = None  # pyright: ignore


schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule", methods=["GET"])
@login_required
def schedule_view():
    from_date_str = request.args.get() if args else None"from", datetime.now() if args else None.strftime("%Y-%m-%d"))
    to_date_str = request.args.get() if args else None"to", datetime.now() if args else None.strftime("%Y-%m-%d"))

    try:
        from_dt = date_parser.parse(from_date_str).date()
        to_dt = date_parser.parse(to_date_str).date()
    except ValueError:
        flash("날짜 형식이 올바르지 않습니다. (YYYY-MM-DD)", "error")
        from_dt = datetime.now().date()
        to_dt = datetime.now().date()

    if from_dt > to_dt:
        flash("시작일은 종료일보다 늦을 수 없습니다.", "error")
        from_dt, to_dt = to_dt, from_dt

    days_diff = (to_dt - from_dt).days
    if days_diff > 90:
        flash("최대 90일까지 조회 가능합니다.", "warning")
        to_dt = from_dt + timedelta(days=90)

    days = [(from_dt + timedelta(days=i)) for i in range(days_diff + 1)]

    # 통합된 Schedule 모델에서 근무와 청소 스케줄 분리
    all_schedules = Schedule.query.filter(
        Schedule.date >= from_dt,
        Schedule.date <= to_dt
    ).all()

    work_schedules = [s for s in all_schedules if s.type == 'work']
    clean_schedules = [s for s in all_schedules if s.type == 'clean']

    return render_template(
        "schedule.html",
        from_date=from_dt.strftime("%Y-%m-%d"),
        to_date=to_dt.strftime("%Y-%m-%d"),
        dates=days,
        work_schedules=work_schedules,
        clean_schedules=clean_schedules,
    )


@schedule_bp.route("/clean")
@login_required
def clean():
    # 청소 스케줄만 조회
    plans = Schedule.query.filter_by(type='clean').order_by(Schedule.date.desc()).all()
    return render_template("clean.html", plans=plans)


@schedule_bp.route("/clean_manage")
@login_required
def clean_manage():
    """청소 관리 페이지"""
    try:
        # 승인된 직원 목록 조회
        employees = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        # 청소 스케줄 조회
        cleanings = Schedule.query.filter_by(type='clean').order_by(Schedule.date.desc()).all()

        return render_template("clean_manage.html", employees=employees, cleanings=cleanings)

    except Exception as e:
        flash("청소 관리 페이지 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("dashboard"))


@schedule_bp.route("/schedule_fc")
@login_required
def schedule_fc():
    return render_template("schedule_fc.html")


@schedule_bp.route("/api/schedule", methods=["POST"])
# @login_required
def api_add_schedule():
    """스케줄 추가 API"""
    try:
        data = request.json

        # 더미 응답 데이터
        dummy_response = {
            "success": True,
            "message": "스케줄이 성공적으로 추가되었습니다.",
            "schedule": {
                "id": 999,
                "user_id": data.get() if data else None"user_id") if data else None,
                "date": data.get() if data else None"date") if data else None,
                "start_time": data.get() if data else None"start_time") if data else None,
                "end_time": data.get() if data else None"end_time") if data else None,
                "type": data.get() if data else None"type", "work") if data else None,
                "category": data.get() if data else None"category", "근무") if data else None,
                "memo": data.get() if data else None"memo") if data else None,
                "team": data.get() if data else None"team") if data else None,
                "branch_id": data.get() if data else None"branch_id", 1) if data else None,
                "manager_id": data.get() if data else None"manager_id", 1) if data else None
            }
        }

        return jsonify(dummy_response)

    except Exception as e:
        return jsonify({"success": False, "message": "스케줄 추가 중 오류가 발생했습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@login_required
def api_update_schedule(schedule_id):
    """스케줄 수정 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.json

        schedule.date = datetime.strptime(data["date"] if data is not None else None, "%Y-%m-%d").date()
        schedule.start_time = datetime.strptime(data["start_time"] if data is not None else None, "%H:%M").time()
        schedule.end_time = datetime.strptime(data["end_time"] if data is not None else None, "%H:%M").time()
        schedule.type = data.get() if data else None"type", "work") if data else None
        schedule.category = data.get() if data else None"category", "근무") if data else None
        schedule.memo = data.get() if data else None"memo") if data else None
        schedule.team = data.get() if data else None"team") if data else None
        schedule.plan = data.get() if data else None"plan") if data else None
        schedule.manager_id = data.get() if data else None"manager_id") if data else None

        db.session.commit()

        log_action(current_user.id, "schedule_update", f"스케줄 수정: {schedule_id}")
        return jsonify({"success": True, "message": "스케줄이 수정되었습니다."})
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "message": "스케줄 수정 중 오류가 발생했습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def api_delete_schedule(schedule_id):
    """스케줄 삭제 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        db.session.delete(schedule)
        db.session.commit()

        log_action(current_user.id, "schedule_delete", f"스케줄 삭제: {schedule_id}")
        return jsonify({"success": True, "message": "스케줄이 삭제되었습니다."})
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "message": "스케줄 삭제 중 오류가 발생했습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["GET"])
@login_required
def api_get_schedule(schedule_id):
    """스케줄 조회 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        return jsonify({
            "id": schedule.id,
            "user_id": schedule.user_id,
            "branch_id": schedule.branch_id,
            "date": schedule.date.strftime("%Y-%m-%d"),
            "start_time": schedule.start_time.strftime("%H:%M"),
            "end_time": schedule.end_time.strftime("%H:%M"),
            "type": schedule.type,
            "category": schedule.category,
            "memo": schedule.memo,
            "team": schedule.team,
            "plan": schedule.plan,
            "manager_id": schedule.manager_id,
        })
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "message": "스케줄 조회 중 오류가 발생했습니다."})


@schedule_bp.route("/api/schedule")
@login_required
def get_schedules():
    """스케줄 목록 조회 API"""
    schedule_type = request.args.get() if args else None'type', 'work') if args else None

    # 더미 스케줄 데이터
    schedules = [
        {
            "id": 1,
            "staff": "홍길동",
            "date": "2024-01-15",
            "shift": "오전",
            "status": "confirmed",
            "start_time": "09:00",
            "end_time": "17:00",
            "type": schedule_type
        },
        {
            "id": 2,
            "staff": "김철수",
            "date": "2024-01-15",
            "shift": "오후",
            "status": "pending",
            "start_time": "17:00",
            "end_time": "22:00",
            "type": schedule_type
        },
        {
            "id": 3,
            "staff": "이영희",
            "date": "2024-01-16",
            "shift": "오전",
            "status": "confirmed",
            "start_time": "09:00",
            "end_time": "17:00",
            "type": schedule_type
        }
    ]

    return jsonify({"success": True, "data": schedules})


@schedule_bp.route("/api/schedule", methods=["POST"])
@login_required
def create_schedule():
    """스케줄 생성 API"""
    data = request.get_json()

    # 더미 응답
    new_schedule = {
        "id": 999,
        "staff": data.get() if data else None'staff', '새 직원') if data else None,
        "date": data.get() if data else None'date', '2024-01-15') if data else None,
        "shift": data.get() if data else None'shift', '오전') if data else None,
        "status": "pending",
        "start_time": data.get() if data else None'start_time', '09:00') if data else None,
        "end_time": data.get() if data else None'end_time', '17:00') if data else None,
        "type": data.get() if data else None'type', 'work') if data else None
    }

    return jsonify({"success": True, "data": new_schedule, "message": "스케줄이 생성되었습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@login_required
def update_schedule(schedule_id):
    """스케줄 수정 API"""
    data = request.get_json()

    # 더미 응답
    updated_schedule = {
        "id": schedule_id,
        "staff": data.get() if data else None'staff', '수정된 직원') if data else None,
        "date": data.get() if data else None'date', '2024-01-15') if data else None,
        "shift": data.get() if data else None'shift', '오전') if data else None,
        "status": data.get() if data else None'status', 'confirmed') if data else None,
        "start_time": data.get() if data else None'start_time', '09:00') if data else None,
        "end_time": data.get() if data else None'end_time', '17:00') if data else None,
        "type": data.get() if data else None'type', 'work') if data else None
    }

    return jsonify({"success": True, "data": updated_schedule, "message": "스케줄이 수정되었습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["DELETE"])
@login_required
def delete_schedule(schedule_id):
    """스케줄 삭제 API"""
    return jsonify({"success": True, "message": f"스케줄 {schedule_id}가 삭제되었습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>")
@login_required
def get_schedule_detail(schedule_id):
    """스케줄 상세 조회 API"""
    # 더미 상세 데이터
    schedule_detail = {
        "id": schedule_id,
        "staff": "홍길동",
        "date": "2024-01-15",
        "shift": "오전",
        "status": "confirmed",
        "start_time": "09:00",
        "end_time": "17:00",
        "type": "work",
        "memo": "특별한 업무가 있을 수 있습니다.",
        "created_at": "2024-01-10T10:00:00Z",
        "updated_at": "2024-01-12T15:30:00Z"
    }

    return jsonify({"success": True, "data": schedule_detail})


@schedule_bp.route("/api/schedule/calendar")
@login_required
def get_calendar_data():
    """캘린더 데이터 API"""
    # 더미 캘린더 데이터
    calendar_data = {
        "events": [
            {
                "id": 1,
                "title": "홍길동 - 오전",
                "start": "2024-01-15T09:00:00",
                "end": "2024-01-15T17:00:00",
                "type": "work",
                "status": "confirmed"
            },
            {
                "id": 2,
                "title": "김철수 - 오후",
                "start": "2024-01-15T17:00:00",
                "end": "2024-01-15T22:00:00",
                "type": "work",
                "status": "pending"
            }
        ]
    }

    return jsonify({"success": True, "data": calendar_data})
