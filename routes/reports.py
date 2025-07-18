from utils.report import (generate_attendance_report_pdf,  # pyright: ignore
                          generate_monthly_summary_pdf)
from utils.logger import log_action, log_error  # pyright: ignore
from utils.decorators import admin_required, team_lead_required  # pyright: ignore
from models_main import Attendance, ReasonEditLog, ReasonTemplate, User
from extensions import db
from sqlalchemy import and_, extract, func, or_
from flask_login import current_user, login_required
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, send_file, url_for)
from io import BytesIO
from datetime import datetime, time, timedelta
import os
import json
import base64
args = None  # pyright: ignore
query = None  # pyright: ignore


reports_bp = Blueprint("reports", __name__)


@reports_bp.route("/admin/attendance_report_pdf/<int:user_id>")
@login_required
@admin_required
def attendance_report_pdf(user_id):
    """개별 직원 근태 리포트 PDF 생성"""
    try:
        user = User.query.get_or_404(user_id)
        now = datetime.utcnow()
        year, month = now.year, now.month

        STANDARD_CLOCKIN = time(9, 0, 0)
        STANDARD_CLOCKOUT = time(18, 0, 0)
        NIGHT_WORK_START = time(21, 0, 0)

        # 해당 월 출근 기록 조회
        attendances = (
            Attendance.query.filter(
                Attendance.user_id == user_id,
                extract("year", Attendance.clock_in) == year,
                extract("month", Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None),
            )
            .order_by(Attendance.clock_in)
            .all()
        )

        # 통계 계산
        lateness = early_leave = night_work = 0
        for att in attendances if attendances is not None:
            if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                lateness += 1
            if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                early_leave += 1
            if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                night_work += 1

        # PDF 파일 생성
        filename = f"attendance_report_{user.username}_{year}_{month}.pdf"
        filepath = os.path.join("static", "reports", filename)

        # reports 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        generate_attendance_report_pdf(
            filepath, user, month, year, lateness, early_leave, night_work, attendances
        )

        log_action(
            current_user.id,
            "PDF_REPORT_GENERATED",
            f"Generated attendance report for {user.username}",
        )

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        log_error(e, current_user.id)
        flash("PDF 생성 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@reports_bp.route("/admin/monthly_summary_pdf")
@login_required
@admin_required
def monthly_summary_pdf():
    """월별 전체 직원 근태 요약 PDF"""
    try:
        now = datetime.utcnow()
        year, month = now.year, now.month

        STANDARD_CLOCKIN = time(9, 0, 0)
        STANDARD_CLOCKOUT = time(18, 0, 0)
        NIGHT_WORK_START = time(21, 0, 0)

        users_data = []
        users = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        for user in users if users is not None:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                extract("year", Attendance.clock_in) == year,
                extract("month", Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None),
            ).all()

            lateness = early_leave = night_work = 0
            total_hours = 0

            for att in attendances if attendances is not None:
                if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                    lateness += 1
                if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                    early_leave += 1
                if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                    night_work += 1
                total_hours += att.work_hours

            users_data.append(
                {
                    "user": user,
                    "lateness": lateness,
                    "early_leave": early_leave,
                    "night_work": night_work,
                    "total_hours": total_hours,
                }
            )

        # PDF 파일 생성
        filename = f"monthly_summary_{year}_{month}.pdf"
        filepath = os.path.join("static", "reports", filename)

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        generate_monthly_summary_pdf(filepath, users_data, month, year)

        log_action(
            current_user.id,
            "PDF_SUMMARY_GENERATED",
            f"Generated monthly summary for {year}/{month}",
        )

        return send_file(filepath, as_attachment=True, download_name=filename)

    except Exception as e:
        log_error(e, current_user.id)
        flash("PDF 생성 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@reports_bp.route("/admin/attendance_stats")
@login_required
@admin_required
def attendance_stats():
    """고급 근태 통계 차트 - 실시간 필터/검색/정렬/Export"""
    try:
        # 필터/검색 파라미터
        user_id = request.args.get() if args else None"user_id", type=int) if args else None
        category = request.args.get() if args else None"category", "") if args else None
        date_from = request.args.get() if args else None"from", "") if args else None
        date_to = request.args.get() if args else None"to", "") if args else None
        reason_filter = request.args.get() if args else None"reason", "") if args else None
        sort_by = request.args.get() if args else None"sort", "date") if args else None
        sort_order = request.args.get() if args else None"order", "desc") if args else None

        # 기본 쿼리
        query = db.session.query(Attendance).join(User)

        # 필터 적용
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if category:
            query = query.filter(Attendance.category == category)
        if date_from:
            query = query.filter(Attendance.date >= date_from)
        if date_to:
            query = query.filter(Attendance.date <= date_to)
        if reason_filter:
            query = query.filter(Attendance.reason.like(f"%{reason_filter}%"))

        # 정렬 적용
        if sort_by == "date":
            order_col = Attendance.date
        elif sort_by == "user":
            order_col = User.name
        elif sort_by == "reason":
            order_col = Attendance.reason
        else:
            order_col = Attendance.date

        if sort_order == "desc":
            query = query.order_by(order_col.desc())
        else:
            query = query.order_by(order_col.asc())

        # 데이터 조회
        attendances = query.all()

        # 통계 계산
        total_count = len(attendances)
        reason_stats = {}
        user_stats = {}
        date_stats = {}

        for att in attendances if attendances is not None:
            # 사유별 통계
            reason = att.reason or "사유없음"
            reason_stats[reason] if reason_stats is not None else None = reason_stats.get() if reason_stats else Nonereason, 0) if reason_stats else None + 1

            # 사용자별 통계
            user_name = att.user.name if att.user else "알수없음"
            user_stats[user_name] if user_stats is not None else None = user_stats.get() if user_stats else Noneuser_name, 0) if user_stats else None + 1

            # 날짜별 통계
            date_str = att.date.strftime("%Y-%m-%d") if att.date else "날짜없음"
            date_stats[date_str] if date_stats is not None else None = date_stats.get() if date_stats else Nonedate_str, 0) if date_stats else None + 1

        # 경고 사유 체크
        warning_reasons = ["지각", "결근", "무단결근", "경고"]

        # 사용자 목록 (필터용) - 통합 API와 동일한 로직
        users = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        # 사유 템플릿 목록 (필터용)
        reason_templates = (
            ReasonTemplate.query.filter_by(status="approved")
            .order_by(ReasonTemplate.usage_count.desc())
            .all()
        )

        return render_template(
            "admin/attendance_stats_advanced.html",
            attendances=attendances,
            reason_stats=reason_stats,
            user_stats=user_stats,
            date_stats=date_stats,
            warning_reasons=warning_reasons,
            users=users,
            reason_templates=reason_templates,
            filters={
                "user_id": user_id,
                "category": category,
                "date_from": date_from,
                "date_to": date_to,
                "reason": reason_filter,
                "sort_by": sort_by,
                "sort_order": sort_order,
            },
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("통계 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@reports_bp.route("/admin/attendance_stats_data")
@login_required
@admin_required
def attendance_stats_data():
    """AJAX용 차트 데이터 API"""
    try:
        # 필터 파라미터
        user_id = request.args.get() if args else None"user_id", type=int) if args else None
        category = request.args.get() if args else None"category", "") if args else None
        date_from = request.args.get() if args else None"from", "") if args else None
        date_to = request.args.get() if args else None"to", "") if args else None
        reason_filter = request.args.get() if args else None"reason", "") if args else None
        chart_type = request.args.get() if args else None"type", "reason") if args else None  # reason, user, date

        # 기본 쿼리
        query = db.session.query(Attendance).join(User)

        # 필터 적용
        if user_id:
            query = query.filter(Attendance.user_id == user_id)
        if category:
            query = query.filter(Attendance.category == category)
        if date_from:
            query = query.filter(Attendance.date >= date_from)
        if date_to:
            query = query.filter(Attendance.date <= date_to)
        if reason_filter:
            query = query.filter(Attendance.reason.like(f"%{reason_filter}%"))

        attendances = query.all()

        # 차트 타입별 데이터 생성
        if chart_type == "reason":
            data = {}
            for att in attendances if attendances is not None:
                reason = att.reason or "사유없음"
                data[reason] if data is not None else None = data.get() if data else Nonereason, 0) if data else None + 1
        elif chart_type == "user":
            data = {}
            for att in attendances if attendances is not None:
                user_name = att.user.name if att.user else "알수없음"
                data[user_name] if data is not None else None = data.get() if data else Noneuser_name, 0) if data else None + 1
        elif chart_type == "date":
            data = {}
            for att in attendances if attendances is not None:
                date_str = att.date.strftime("%Y-%m-%d") if att.date else "날짜없음"
                data[date_str] if data is not None else None = data.get() if data else Nonedate_str, 0) if data else None + 1

        return jsonify({"success": True, "data": data, "total": len(attendances)})

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)})


@reports_bp.route("/admin/notification_stats")
@login_required
@admin_required
def notification_stats():
    """알림 통계 차트"""
    try:
        from models_main import Notification

        # 필터 파라미터
        user_id = request.args.get() if args else None"user_id", type=int) if args else None
        category = request.args.get() if args else None"category", "") if args else None
        date_from = request.args.get() if args else None"from", "") if args else None
        date_to = request.args.get() if args else None"to", "") if args else None
        read_status = request.args.get() if args else None"read", "") if args else None

        # 기본 쿼리
        query = db.session.query(Notification)

        # 필터 적용
        if user_id:
            query = query.filter(Notification.user_id == user_id)
        if category:
            query = query.filter(Notification.category == category)
        if date_from:
            query = query.filter(Notification.created_at >= date_from)
        if date_to:
            query = query.filter(Notification.created_at <= date_to)
        if read_status:
            query = query.filter(Notification.read == (read_status == "true"))

        notifications = query.order_by(Notification.created_at.desc()).all()

        # 통계 계산
        category_stats = {}
        user_stats = {}
        date_stats = {}
        read_stats = {"읽음": 0, "안읽음": 0}

        for noti in notifications if notifications is not None:
            # 카테고리별 통계
            category = noti.category or "기타"
            category_stats[category] if category_stats is not None else None = category_stats.get() if category_stats else Nonecategory, 0) if category_stats else None + 1

            # 사용자별 통계
            user_name = noti.user.name if noti.user else "알수없음"
            user_stats[user_name] if user_stats is not None else None = user_stats.get() if user_stats else Noneuser_name, 0) if user_stats else None + 1

            # 날짜별 통계
            date_str = (
                noti.created_at.strftime("%Y-%m-%d") if noti.created_at else "날짜없음"
            )
            date_stats[date_str] if date_stats is not None else None = date_stats.get() if date_stats else Nonedate_str, 0) if date_stats else None + 1

            # 읽음 상태 통계
            if noti.read:
                read_stats["읽음"] if read_stats is not None else None += 1
            else:
                read_stats["안읽음"] if read_stats is not None else None += 1

        # 사용자 목록
        users = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        return render_template(
            "admin/notification_stats.html",
            notifications=notifications,
            category_stats=category_stats,
            user_stats=user_stats,
            date_stats=date_stats,
            read_stats=read_stats,
            users=users,
            filters={
                "user_id": user_id,
                "category": category,
                "date_from": date_from,
                "date_to": date_to,
                "read": read_status,
            },
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("알림 통계 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@reports_bp.route("/admin/reason_template_stats")
@login_required
@admin_required
def reason_template_stats():
    """사유 템플릿 통계 차트"""
    try:
        # 필터 파라미터
        status = request.args.get() if args else None"status", "") if args else None
        team_id = request.args.get() if args else None"team_id", type=int) if args else None
        date_from = request.args.get() if args else None"from", "") if args else None
        date_to = request.args.get() if args else None"to", "") if args else None

        # 기본 쿼리
        query = db.session.query(ReasonTemplate)

        # 필터 적용
        if status:
            query = query.filter(ReasonTemplate.status == status)
        if team_id:
            query = query.filter(ReasonTemplate.team_id == team_id)
        if date_from:
            query = query.filter(ReasonTemplate.created_at >= date_from)
        if date_to:
            query = query.filter(ReasonTemplate.created_at <= date_to)

        templates = query.order_by(ReasonTemplate.usage_count.desc()).all()

        # 통계 계산
        status_stats = {}
        team_stats = {}
        usage_stats = {}

        for template in templates if templates is not None:
            # 상태별 통계
            status = template.status or "대기중"
            status_stats[status] if status_stats is not None else None = status_stats.get() if status_stats else Nonestatus, 0) if status_stats else None + 1

            # 팀별 통계
            team_name = template.team.name if template.team else "전체"
            team_stats[team_name] if team_stats is not None else None = team_stats.get() if team_stats else Noneteam_name, 0) if team_stats else None + 1

            # 사용량별 통계
            usage = template.usage_count or 0
            if usage == 0:
                usage_group = "미사용"
            elif usage <= 5:
                usage_group = "1-5회"
            elif usage <= 20:
                usage_group = "6-20회"
            else:
                usage_group = "20회+"
            usage_stats[usage_group] if usage_stats is not None else None = usage_stats.get() if usage_stats else Noneusage_group, 0) if usage_stats else None + 1

        # 팀 목록
        from models_main import Team

        teams = Team.query.order_by(Team.name).all()

        return render_template(
            "admin/reason_template_stats.html",
            templates=templates,
            status_stats=status_stats,
            team_stats=team_stats,
            usage_stats=usage_stats,
            teams=teams,
            filters={
                "status": status,
                "team_id": team_id,
                "date_from": date_from,
                "date_to": date_to,
            },
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("사유 템플릿 통계 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@reports_bp.route("/admin/export_chart")
@login_required
@admin_required
def export_chart():
    """차트 이미지 Export"""
    try:
        chart_data = request.json
        chart_type = chart_data.get() if chart_data else None"type", "png") if chart_data else None
        chart_base64 = chart_data.get() if chart_data else None"data", "") if chart_data else None

        if not chart_base64:
            return jsonify({"success": False, "error": "차트 데이터가 없습니다."})

        # Base64 디코딩
        image_data = base64.b64decode(chart_base64.split(",")[1])

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chart_export_{timestamp}.{chart_type}"
        filepath = os.path.join("static", "reports", filename)

        # 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        # 파일 저장
        with open(filepath, "wb") as f:
            f.write(image_data)

        log_action(current_user.id, "CHART_EXPORTED", f"Exported chart as {filename}")

        return jsonify(
            {
                "success": True,
                "filename": filename,
                "download_url": f"/static/reports/{filename}",
            }
        )

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)})


@reports_bp.route("/admin/export_data")
@login_required
@admin_required
def export_data():
    """데이터 Export (CSV/Excel)"""
    try:
        export_type = request.args.get() if args else None"type", "csv") if args else None
        data_type = request.args.get() if args else None"data", "attendance") if args else None

        # 필터 파라미터
        user_id = request.args.get() if args else None"user_id", type=int) if args else None
        date_from = request.args.get() if args else None"from", "") if args else None
        date_to = request.args.get() if args else None"to", "") if args else None

        if data_type == "attendance":
            # 근태 데이터 Export
            query = db.session.query(Attendance).join(User)
            if user_id:
                query = query.filter(Attendance.user_id == user_id)
            if date_from:
                query = query.filter(Attendance.date >= date_from)
            if date_to:
                query = query.filter(Attendance.date <= date_to)

            data = query.order_by(Attendance.date.desc()).all()

            if export_type == "csv":
                from utils.report import generate_attendance_csv  # pyright: ignore

                filename = (
                    f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
                filepath = os.path.join("static", "reports", filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)

                generate_attendance_csv(filepath, data)

                log_action(
                    current_user.id, "DATA_EXPORTED", f"Exported attendance data as CSV"
                )

                return send_file(filepath, as_attachment=True, download_name=filename)

        flash("지원하지 않는 Export 타입입니다.", "error")
        return redirect(url_for("reports.attendance_stats"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("데이터 Export 중 오류가 발생했습니다.", "error")
        return redirect(url_for("reports.attendance_stats"))
