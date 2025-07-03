from datetime import datetime, timedelta
from dateutil import parser as date_parser

from flask import Blueprint, flash, jsonify, render_template, request
from flask_login import current_user, login_required
from sqlalchemy import and_

from extensions import db
from models import Schedule, User
from utils.logger import log_action, log_error
from services.notice_service import create_notice_for_event

schedule_bp = Blueprint("schedule", __name__)


@schedule_bp.route("/schedule", methods=["GET"])
@login_required
def schedule_view():
    from_date_str = request.args.get("from", datetime.now().strftime("%Y-%m-%d"))
    to_date_str = request.args.get("to", datetime.now().strftime("%Y-%m-%d"))

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


@schedule_bp.route("/schedule_fc")
@login_required
def schedule_fc():
    return render_template("schedule_fc.html")


@schedule_bp.route("/api/schedule", methods=["POST"])
@login_required
def api_add_schedule():
    """스케줄 추가 API"""
    try:
        data = request.json
        schedule = Schedule(
            user_id=data.get("user_id"),
            branch_id=data.get("branch_id"),
            date=datetime.strptime(data["date"], "%Y-%m-%d").date(),
            start_time=datetime.strptime(data["start_time"], "%H:%M").time(),
            end_time=datetime.strptime(data["end_time"], "%H:%M").time(),
            type=data.get("type", "work"),
            category=data.get("category", "근무"),
            memo=data.get("memo"),
            team=data.get("team"),
            plan=data.get("plan"),
            manager_id=data.get("manager_id"),
        )
        db.session.add(schedule)
        db.session.commit()
        # 알림 자동 등록
        create_notice_for_event(
            title="새 스케줄 등록",
            content=f"{schedule.date} {schedule.category} 스케줄이 추가되었습니다.",
            type="notice",
            priority="medium",
            author_id=current_user.id,
            target_audience="all",
            category=schedule.category
        )
        log_action(current_user.id, "schedule_add", f"스케줄 추가: {schedule.id}")
        return jsonify({"success": True, "message": "스케줄이 추가되었습니다."})
    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "message": "스케줄 추가 중 오류가 발생했습니다."})


@schedule_bp.route("/api/schedule/<int:schedule_id>", methods=["PUT"])
@login_required
def api_update_schedule(schedule_id):
    """스케줄 수정 API"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.json
        
        schedule.date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        schedule.start_time = datetime.strptime(data["start_time"], "%H:%M").time()
        schedule.end_time = datetime.strptime(data["end_time"], "%H:%M").time()
        schedule.type = data.get("type", "work")
        schedule.category = data.get("category", "근무")
        schedule.memo = data.get("memo")
        schedule.team = data.get("team")
        schedule.plan = data.get("plan")
        schedule.manager_id = data.get("manager_id")
        
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