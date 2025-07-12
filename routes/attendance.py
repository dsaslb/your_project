from datetime import datetime, timedelta
from functools import wraps
import logging
from typing import TYPE_CHECKING, cast

from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required
from sqlalchemy import and_, extract, func, case
from sqlalchemy.sql import ColumnElement

from models import Attendance, User, AttendanceReport, Excuse, ExcuseResponse, db
from utils.logger import log_action
from utils.email_utils import send_email

if TYPE_CHECKING:
    from models import Attendance as AttendanceType

logger = logging.getLogger(__name__)

attendance_bp = Blueprint("attendance", __name__)


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "관리자 권한이 필요합니다"}), 403
        return f(*args, **kwargs)

    return decorated_function


@attendance_bp.route("/api/attendance_stats", methods=["GET"])
@login_required
def attendance_stats():
    """근태 통계 API - 간소화 버전"""
    try:
        # 쿼리 파라미터
        user_id = request.args.get("user_id", type=int)
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        year = request.args.get("year", type=int) or datetime.now().year
        month = request.args.get("month", type=int)

        # 기본 쿼리
        q = db.session.query(Attendance)

        # 필터 적용
        if user_id:
            q = q.filter(Attendance.user_id == user_id)
        if start_date:
            q = q.filter(Attendance.clock_in >= start_date)
        if end_date:
            q = q.filter(Attendance.clock_in <= end_date)
        if month:
            q = q.filter(extract("year", Attendance.clock_in) == year)
            q = q.filter(extract("month", Attendance.clock_in) == month)
        else:
            q = q.filter(extract("year", Attendance.clock_in) == year)

        # 데이터 조회
        attendances = q.order_by(Attendance.clock_in.desc()).all()

        # 결과 데이터 구성
        result = []
        for att in attendances:
            # 근무 시간 계산
            work_hours = 0
            if att.clock_in and att.clock_out:
                work_seconds = (att.clock_out - att.clock_in).total_seconds()
                work_hours = work_seconds / 3600

            # 지각/조퇴 판정
            is_late = False
            is_early_leave = False
            if (
                att.clock_in
                and att.clock_in.time() > datetime.strptime("09:00", "%H:%M").time()
            ):
                is_late = True
            if (
                att.clock_out
                and att.clock_out.time() < datetime.strptime("18:00", "%H:%M").time()
            ):
                is_early_leave = True

            # 사용자 정보 조회
            user = User.query.get(att.user_id) if att.user_id else None
            user_name = ""
            if user:
                user_name = user.name if user.name else user.username

            result.append(
                {
                    "id": att.id,
                    "user_id": att.user_id,
                    "user_name": user_name,
                    "date": att.clock_in.date().isoformat() if att.clock_in else None,
                    "clock_in": (
                        att.clock_in.strftime("%H:%M") if att.clock_in else None
                    ),
                    "clock_out": (
                        att.clock_out.strftime("%H:%M") if att.clock_out else None
                    ),
                    "work_hours": round(work_hours, 2),
                    "is_late": is_late,
                    "is_early_leave": is_early_leave,
                    "is_absent": att.clock_in is None,
                    "overtime_hours": max(0, work_hours - 8) if work_hours > 8 else 0,
                }
            )

        return jsonify({"success": True, "data": result, "total_count": len(result)})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route("/api/attendance_summary", methods=["GET"])
@login_required
def attendance_summary():
    """근태 통계 요약 API"""
    try:
        user_id = request.args.get("user_id", type=int)
        year = request.args.get("year", type=int) or datetime.now().year
        month = request.args.get("month", type=int)

        # 기본 쿼리
        q = db.session.query(Attendance)

        if user_id:
            q = q.filter(Attendance.user_id == user_id)
        if month:
            q = q.filter(extract("year", Attendance.clock_in) == year)
            q = q.filter(extract("month", Attendance.clock_in) == month)
        else:
            q = q.filter(extract("year", Attendance.clock_in) == year)

        attendances = q.all()

        # 통계 계산
        total_days = len(attendances)
        total_hours = 0
        late_count = 0
        early_leave_count = 0
        absent_count = 0
        overtime_hours = 0

        for att in attendances:
            if att.clock_in and att.clock_out:
                work_seconds = (att.clock_out - att.clock_in).total_seconds()
                work_hours = work_seconds / 3600
                total_hours += work_hours

                # 지각/조퇴/야근 판정
                if att.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                    late_count += 1
                if att.clock_out.time() < datetime.strptime("18:00", "%H:%M").time():
                    early_leave_count += 1
                if work_hours > 8:
                    overtime_hours += work_hours - 8
            else:
                absent_count += 1

        # 예상 급여 계산 (시급 12,000원)
        estimated_wage = int(total_hours * 12000)

        return jsonify(
            {
                "success": True,
                "summary": {
                    "total_days": total_days,
                    "total_hours": round(total_hours, 2),
                    "late_count": late_count,
                    "early_leave_count": early_leave_count,
                    "absent_count": absent_count,
                    "overtime_hours": round(overtime_hours, 2),
                    "estimated_wage": estimated_wage,
                    "avg_hours_per_day": (
                        round(total_hours / total_days, 2) if total_days > 0 else 0
                    ),
                },
            }
        )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route("/attendance_stats_simple")
@login_required
@admin_required
def attendance_stats_simple():
    """간소화된 근태 통계 페이지"""
    # 사용자 목록
    users = User.query.filter(User.deleted_at == None).order_by(User.username).all()

    # 기본 통계 데이터
    year = request.args.get("year", type=int) or datetime.now().year
    month = request.args.get("month", type=int)
    user_id = request.args.get("user_id", type=int)

    return render_template(
        "admin/attendance_stats_simple.html",
        users=users,
        year=year,
        month=month,
        user_id=user_id,
    )


@attendance_bp.route("/staff/<int:user_id>/attendance_report/eval", methods=["POST"])
@login_required
@admin_required
def eval_attendance(user_id):
    """근태 평가 저장 및 등급별 경고/알림"""
    try:
        from models import AttendanceReport, Excuse
        from utils.notification_automation import send_notification

        # 평가 입력/저장 로직(점수, 등급 등)
        score = int(request.form.get("score", 0))
        grade = request.form.get("grade")
        comment = request.form.get("comment", "")
        period_from_str = request.form.get("period_from")
        period_to_str = request.form.get("period_to")
        
        if not period_from_str or not period_to_str:
            flash("평가 기간을 입력해주세요.", "error")
            return redirect(url_for("attendance.staff_attendance_report", user_id=user_id))
            
        period_from = datetime.strptime(period_from_str, "%Y-%m-%d").date()
        period_to = datetime.strptime(period_to_str, "%Y-%m-%d").date()

        # 기존 평가 확인
        existing_report = AttendanceReport.query.filter(
            and_(
                AttendanceReport.user_id == user_id,
                AttendanceReport.period_from == period_from,
                AttendanceReport.period_to == period_to,
            )
        ).first()

        if existing_report:
            # 기존 평가 업데이트
            existing_report.score = score
            existing_report.grade = grade
            existing_report.comment = comment
            existing_report.updated_at = datetime.utcnow()
            report = existing_report
        else:
            # 새 평가 생성
            report = AttendanceReport()
            report.user_id = user_id
            report.period_from = period_from
            report.period_to = period_to
            report.score = score
            report.grade = grade
            report.comment = comment
            report.created_by = current_user.id
            db.session.add(report)

        db.session.commit()

        # 등급별 경고/알림/소명 요청
        warning_sent = False
        if grade in ("D", "F") or score < 70:
            warning_sent = True
            # 경고 알림 발송
            send_notification(
                user_id=user_id,
                content=f"최근 근태평가 등급이 '{grade}'(점수: {score}점)입니다. 소명서를 제출해주세요.",
                category="근태경고",
                priority="중요",
                link=url_for("attendance.submit_excuse", user_id=user_id),
            )

            # 관리자에게도 알림
            admins = User.query.filter(User.role == "admin").all()
            for admin in admins:
                send_notification(
                    user_id=admin.id,
                    content=f"{report.user.name or report.user.username}님의 근태평가 등급이 '{grade}'로 경고 상태입니다.",
                    category="근태관리",
                    priority="중요",
                    link=url_for("attendance.admin_excuse_list"),
                )

        flash(
            "평가 결과가 저장되었습니다."
            + (" 경고 알림이 발송되었습니다." if warning_sent else ""),
            "success",
        )
        return redirect(url_for("attendance.staff_attendance_report", user_id=user_id))

    except Exception as e:
        db.session.rollback()
        flash(f"평가 저장 중 오류가 발생했습니다: {str(e)}", "error")
        return redirect(url_for("attendance.staff_attendance_report", user_id=user_id))


@attendance_bp.route("/staff/<int:user_id>/attendance_report")
@login_required
def staff_attendance_report(user_id):
    """직원 근태 리포트 페이지"""
    from models import AttendanceReport, Excuse

    user = User.query.get_or_404(user_id)

    # 최근 평가 조회
    recent_reports = (
        AttendanceReport.query.filter(AttendanceReport.user_id == user_id)
        .order_by(AttendanceReport.created_at.desc())
        .limit(5)
        .all()
    )

    # 소명 요청 조회
    pending_excuses = (
        Excuse.query.filter(and_(Excuse.user_id == user_id, Excuse.status == "pending"))
        .order_by(Excuse.created_at.desc())
        .all()
    )

    return render_template(
        "attendance/staff_attendance_report.html",
        user=user,
        recent_reports=recent_reports,
        pending_excuses=pending_excuses,
    )


@attendance_bp.route("/staff/<int:user_id>/attendance_excuse", methods=["GET", "POST"])
@login_required
def submit_excuse(user_id):
    """소명(이의제기) 제출 폼"""
    from models import Excuse
    from utils.notification_automation import send_notification

    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        try:
            title = request.form.get("title", "").strip()
            content = request.form.get("content", "").strip()
            category = request.form.get("category", "근태평가")
            priority = request.form.get("priority", "일반")

            if not title or not content:
                flash("제목과 내용을 모두 입력해주세요.", "error")
                return render_template(
                    "attendance/attendance_excuse_form.html", user=user
                )

            # 소명서 생성
            excuse = Excuse()
            excuse.user_id = user_id
            excuse.title = title
            excuse.content = content
            excuse.category = category
            excuse.priority = priority
            db.session.add(excuse)
            db.session.commit()

            # 관리자에게 알림
            admins = User.query.filter(User.role == "admin").all()
            for admin in admins:
                send_notification(
                    user_id=admin.id,
                    content=f"{user.name or user.username}님이 소명서를 제출했습니다: {title}",
                    category="소명관리",
                    priority="중요" if priority == "긴급" else "일반",
                    link=url_for("attendance.admin_excuse_list"),
                )

            flash("소명서가 제출되었습니다.", "success")
            return redirect(
                url_for("attendance.staff_attendance_report", user_id=user_id)
            )

        except Exception as e:
            db.session.rollback()
            flash(f"소명서 제출 중 오류가 발생했습니다: {str(e)}", "error")

    return render_template("attendance/attendance_excuse_form.html", user=user)


@attendance_bp.route("/admin/attendance_excuses")
@login_required
@admin_required
def admin_excuse_list():
    """관리자 소명 목록 및 검토 화면"""
    from models import Excuse

    # 필터링 옵션
    status = request.args.get("status", "all")
    priority = request.args.get("priority", "all")
    category = request.args.get("category", "all")

    # 쿼리 구성
    query = db.session.query(Excuse).join(User, Excuse.user_id == User.id)

    if status != "all":
        query = query.filter(Excuse.status == status)
    if priority != "all":
        query = query.filter(Excuse.priority == priority)
    if category != "all":
        query = query.filter(Excuse.category == category)

    excuses = query.order_by(Excuse.created_at.desc()).all()

    # 통계
    stats = {
        "total": len(excuses),
        "pending": len([e for e in excuses if e.status == "pending"]),
        "reviewed": len([e for e in excuses if e.status == "reviewed"]),
        "accepted": len([e for e in excuses if e.status == "accepted"]),
        "rejected": len([e for e in excuses if e.status == "rejected"]),
    }

    return render_template(
        "admin/excuse_list.html",
        excuses=excuses,
        stats=stats,
        current_status=status,
        current_priority=priority,
        current_category=category,
    )


@attendance_bp.route("/admin/excuse/<int:excuse_id>")
@login_required
@admin_required
def admin_excuse_detail(excuse_id):
    """소명 상세 보기"""
    from models import Excuse, ExcuseResponse

    excuse = Excuse.query.get_or_404(excuse_id)
    responses = (
        ExcuseResponse.query.filter(ExcuseResponse.excuse_id == excuse_id)
        .order_by(ExcuseResponse.created_at)
        .all()
    )

    return render_template(
        "admin/excuse_detail.html", excuse=excuse, responses=responses
    )


@attendance_bp.route("/admin/excuse/<int:excuse_id>/review", methods=["POST"])
@login_required
@admin_required
def review_excuse(excuse_id):
    """소명 검토 및 답변"""
    try:
        from models import Excuse, ExcuseResponse
        from utils.notification_automation import send_notification

        excuse = Excuse.query.get_or_404(excuse_id)
        action = request.form.get("action")  # accept/reject
        admin_comment = request.form.get("admin_comment", "").strip()
        response_content = request.form.get("response_content", "").strip()

        if action not in ["accept", "reject"]:
            flash("잘못된 액션입니다.", "error")
            return redirect(
                url_for("attendance.admin_excuse_detail", excuse_id=excuse_id)
            )

        # 소명 상태 업데이트
        excuse.status = "accepted" if action == "accept" else "rejected"
        excuse.reviewed_at = datetime.utcnow()
        excuse.reviewed_by = current_user.id
        excuse.admin_comment = admin_comment

        # 답변 추가
        if response_content:
            response = ExcuseResponse()
            response.excuse_id = excuse_id
            response.responder_id = current_user.id
            response.content = response_content
            response.response_type = "decision"
            db.session.add(response)

        db.session.commit()

        # 사용자에게 알림
        notification_content = f"소명서 '{excuse.title}'가 {'승인' if action == 'accept' else '거절'}되었습니다."
        if admin_comment:
            notification_content += f" 관리자 코멘트: {admin_comment}"

        send_notification(
            user_id=excuse.user_id,
            content=notification_content,
            category="소명결과",
            priority="중요",
            link=url_for("attendance.staff_attendance_report", user_id=excuse.user_id),
        )

        flash(
            f'소명서가 {"승인" if action == "accept" else "거절"}되었습니다.', "success"
        )
        return redirect(url_for("attendance.admin_excuse_list"))

    except Exception as e:
        db.session.rollback()
        flash(f"소명 검토 중 오류가 발생했습니다: {str(e)}", "error")
        return redirect(url_for("attendance.admin_excuse_detail", excuse_id=excuse_id))


@attendance_bp.route("/admin/excuse/<int:excuse_id>/response", methods=["POST"])
@login_required
@admin_required
def add_excuse_response(excuse_id):
    """소명에 답변 추가"""
    try:
        from models import Excuse, ExcuseResponse
        from utils.notification_automation import send_notification

        content = request.form.get("content", "").strip()
        response_type = request.form.get("response_type", "comment")

        if not content:
            flash("답변 내용을 입력해주세요.", "error")
            return redirect(
                url_for("attendance.admin_excuse_detail", excuse_id=excuse_id)
            )

        response = ExcuseResponse()
        response.excuse_id = excuse_id
        response.responder_id = current_user.id
        response.content = content
        response.response_type = response_type
        db.session.add(response)
        db.session.commit()

        # 사용자에게 알림
        excuse = Excuse.query.get(excuse_id)
        send_notification(
            user_id=excuse.user_id,
            content=f"소명서 '{excuse.title}'에 관리자 답변이 추가되었습니다.",
            category="소명답변",
            link=url_for("attendance.staff_attendance_report", user_id=excuse.user_id),
        )

        flash("답변이 추가되었습니다.", "success")
        return redirect(url_for("attendance.admin_excuse_detail", excuse_id=excuse_id))

    except Exception as e:
        db.session.rollback()
        flash(f"답변 추가 중 오류가 발생했습니다: {str(e)}", "error")
        return redirect(url_for("attendance.admin_excuse_detail", excuse_id=excuse_id))


@attendance_bp.route("/admin/generate_report_pdf")
@login_required
@admin_required
def generate_report_pdf():
    """PDF 리포트 생성 및 다운로드"""
    try:
        import os
        from datetime import date, timedelta

        period = request.args.get("period", "week")
        user_id = request.args.get("user_id", type=int)

        # 기간 설정
        if period == "week":
            from_date = date.today() - timedelta(days=7)
        elif period == "month":
            from_date = date.today().replace(day=1)
        else:
            from_date = date.today() - timedelta(days=30)

        to_date = date.today()

        # 데이터 조회
        if user_id:
            records = (
                Attendance.query.filter(
                    and_(
                        Attendance.user_id == user_id,
                        Attendance.clock_in >= from_date,
                        Attendance.clock_in <= to_date,
                    )
                )
                .order_by(Attendance.clock_in.desc())
                .all()
            )

            user = User.query.get(user_id)
            title = f"{user.name or user.username}님의 {period} 근태 리포트"
        else:
            records = (
                Attendance.query.filter(
                    and_(
                        Attendance.clock_in >= from_date, Attendance.clock_in <= to_date
                    )
                )
                .order_by(Attendance.clock_in.desc())
                .all()
            )

            title = f"전체 직원 {period} 근태 리포트"

        # 통계 계산
        stats = {
            "total_days": len(records),
            "total_hours": 0,
            "late_count": 0,
            "early_leave_count": 0,
            "absent_count": 0,
            "overtime_hours": 0,
            "normal_count": 0,
        }

        for record in records:
            if record.clock_in and record.clock_out:
                work_seconds = (record.clock_out - record.clock_in).total_seconds()
                work_hours = work_seconds / 3600
                stats["total_hours"] += work_hours

                # 지각/조퇴/야근 판정
                if record.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                    stats["late_count"] += 1
                if record.clock_out.time() < datetime.strptime("18:00", "%H:%M").time():
                    stats["early_leave_count"] += 1
                if work_hours > 8:
                    stats["overtime_hours"] += work_hours - 8
                else:
                    stats["normal_count"] += 1
            else:
                stats["absent_count"] += 1

        # HTML 템플릿 렌더링
        html = render_template(
            "reports/attendance_report_pdf.html",
            records=records,
            stats=stats,
            from_date=from_date,
            to_date=to_date,
            title=title,
        )

        # PDF 생성 시도
        try:
            import pdfkit

            options = {
                "page-size": "A4",
                "margin-top": "0.75in",
                "margin-right": "0.75in",
                "margin-bottom": "0.75in",
                "margin-left": "0.75in",
                "encoding": "UTF-8",
                "no-outline": None,
            }

            pdf = pdfkit.from_string(html, False, options=options)

            # 파일 저장
            filename = f"attendance_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            filepath = os.path.join("static", "reports", filename)

            # 디렉토리 생성
            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "wb") as f:
                f.write(bytes(pdf))

            flash(f"PDF 리포트가 생성되었습니다: {filename}", "success")
            return redirect(url_for("static", filename=f"reports/{filename}"))

        except ImportError:
            # pdfkit이 없는 경우 HTML 파일로 저장
            filename = f"attendance_report_{period}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            filepath = os.path.join("static", "reports", filename)

            os.makedirs(os.path.dirname(filepath), exist_ok=True)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)

            flash(f"HTML 리포트가 생성되었습니다: {filename}", "success")
            return redirect(url_for("static", filename=f"reports/{filename}"))

    except Exception as e:
        flash(f"리포트 생성 중 오류가 발생했습니다: {str(e)}", "error")
        return redirect(url_for("attendance.attendance_stats_simple"))


@attendance_bp.route("/admin/send_weekly_report")
@login_required
@admin_required
def send_weekly_report():
    """주간 리포트 이메일 발송"""
    try:
        import os
        import smtplib
        from datetime import date, timedelta
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # 관리자 목록 조회
        admins = User.query.filter_by(role="admin").all()

        if not admins:
            flash("발송할 관리자가 없습니다.", "warning")
            return redirect(url_for("attendance.attendance_stats_simple"))

        # 주간 데이터 생성
        end_date = date.today()
        start_date = end_date - timedelta(days=7)

        records = Attendance.query.filter(
            and_(Attendance.clock_in >= start_date, Attendance.clock_in <= end_date)
        ).all()

        # 통계 계산
        stats = {
            "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            "total_records": len(records),
            "total_hours": 0,
            "late_count": 0,
            "early_leave_count": 0,
            "absent_count": 0,
        }

        for record in records:
            if record.clock_in and record.clock_out:
                work_seconds = (record.clock_out - record.clock_in).total_seconds()
                work_hours = work_seconds / 3600
                stats["total_hours"] += work_hours

                if record.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                    stats["late_count"] += 1
                if record.clock_out.time() < datetime.strptime("18:00", "%H:%M").time():
                    stats["early_leave_count"] += 1
            else:
                stats["absent_count"] += 1

        # 이메일 본문 생성
        email_body = f"""
주간 근태 리포트

기간: {stats['period']}
총 기록: {stats['total_records']}건
총 근무시간: {round(stats['total_hours'], 2)}시간
지각: {stats['late_count']}건
조퇴: {stats['early_leave_count']}건
결근: {stats['absent_count']}건

감사합니다.
"""

        # 이메일 발송 (테스트용)
        success_count = 0
        for admin in admins:
            if admin.email:
                # 실제 환경에서는 SMTP 설정 필요
                logger.info(f"이메일 발송 테스트: {admin.email}")
                logger.info(f"제목: 주간 근태 리포트")
                logger.info(f"내용: {email_body}")
                success_count += 1

        flash(f"주간 리포트 발송 완료: {success_count}/{len(admins)}명", "success")

    except Exception as e:
        flash(f"리포트 발송 중 오류가 발생했습니다: {str(e)}", "error")

    return redirect(url_for("attendance.attendance_stats_simple"))


@attendance_bp.route("/admin/send_monthly_report")
@login_required
@admin_required
def send_monthly_report():
    """월간 리포트 이메일 발송"""
    try:
        import os
        import smtplib
        from datetime import date
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # 관리자 목록 조회
        admins = User.query.filter_by(role="admin").all()

        if not admins:
            flash("발송할 관리자가 없습니다.", "warning")
            return redirect(url_for("attendance.attendance_stats_simple"))

        # 월간 데이터 생성
        start_date = date.today().replace(day=1)
        end_date = date.today()

        records = Attendance.query.filter(
            and_(Attendance.clock_in >= start_date, Attendance.clock_in <= end_date)
        ).all()

        # 통계 계산
        stats = {
            "period": f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}",
            "total_records": len(records),
            "total_hours": 0,
            "late_count": 0,
            "early_leave_count": 0,
            "absent_count": 0,
        }

        for record in records:
            if record.clock_in and record.clock_out:
                work_seconds = (record.clock_out - record.clock_in).total_seconds()
                work_hours = work_seconds / 3600
                stats["total_hours"] += work_hours

                if record.clock_in.time() > datetime.strptime("09:00", "%H:%M").time():
                    stats["late_count"] += 1
                if record.clock_out.time() < datetime.strptime("18:00", "%H:%M").time():
                    stats["early_leave_count"] += 1
            else:
                stats["absent_count"] += 1

        # 이메일 본문 생성
        email_body = f"""
월간 근태 리포트

기간: {stats['period']}
총 기록: {stats['total_records']}건
총 근무시간: {round(stats['total_hours'], 2)}시간
지각: {stats['late_count']}건
조퇴: {stats['early_leave_count']}건
결근: {stats['absent_count']}건

감사합니다.
"""

        # 이메일 발송 (테스트용)
        success_count = 0
        for admin in admins:
            if admin.email:
                # 실제 환경에서는 SMTP 설정 필요
                logger.info(f"이메일 발송 테스트: {admin.email}")
                logger.info(f"제목: 월간 근태 리포트")
                logger.info(f"내용: {email_body}")
                success_count += 1

        flash(f"월간 리포트 발송 완료: {success_count}/{len(admins)}명", "success")

    except Exception as e:
        flash(f"리포트 발송 중 오류가 발생했습니다: {str(e)}", "error")

    return redirect(url_for("attendance.attendance_stats_simple"))


@attendance_bp.route("/test-email-weekly", methods=["POST"])
def test_weekly_email():
    """주간 이메일 발송 테스트"""
    try:
        # 관리자 계정 찾기
        admin = User.query.filter_by(role="admin").first()
        if not admin or not admin.email:
            return jsonify({"success": False, "message": "관리자 이메일이 없습니다."})
        
        # 주간 리포트 데이터 생성
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # 주간 근태 통계
        total_attendance = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).scalar() or 0
        
        present_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "present")
        ).scalar() or 0
        
        late_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "late")
        ).scalar() or 0
        
        absent_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "absent")
        ).scalar() or 0
        
        # 이메일 내용 생성
        if total_attendance > 0:
            email_body = f"""
주간 근태 리포트 ({start_date} ~ {end_date})

총 출근: {total_attendance}건
정상 출근: {present_count}건
지각: {late_count}건
결근: {absent_count}건

출근률: {round(present_count / total_attendance * 100, 1)}%
            """.strip()
        else:
            email_body = f"""
주간 근태 리포트 ({start_date} ~ {end_date})

데이터가 없습니다.
            """.strip()
        
        # 이메일 발송
        success = send_email(
            to_addr=admin.email,
            subject="주간 근태 리포트",
            body=email_body
        )
        
        if success:
            logger.info(f"이메일 발송 테스트: {admin.email}")
            logger.info(f"제목: 주간 근태 리포트")
            logger.info(f"내용: {email_body}")
            return jsonify({"success": True, "message": "주간 이메일 발송 완료"})
        else:
            return jsonify({"success": False, "message": "이메일 발송 실패"})
            
    except Exception as e:
        logger.error(f"주간 이메일 테스트 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@attendance_bp.route("/test-email-monthly", methods=["POST"])
def test_monthly_email():
    """월간 이메일 발송 테스트"""
    try:
        # 관리자 계정 찾기
        admin = User.query.filter_by(role="admin").first()
        if not admin or not admin.email:
            return jsonify({"success": False, "message": "관리자 이메일이 없습니다."})
        
        # 월간 리포트 데이터 생성
        end_date = datetime.now().date()
        start_date = end_date.replace(day=1)
        
        # 월간 근태 통계
        total_attendance = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).scalar() or 0
        
        present_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "present")
        ).scalar() or 0
        
        late_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "late")
        ).scalar() or 0
        
        absent_count = db.session.query(func.count(Attendance.id)).filter(
            func.date(Attendance.clock_in) >= start_date
        ).filter(
            func.date(Attendance.clock_in) <= end_date
        ).filter(
            cast(ColumnElement[bool], Attendance.status == "absent")
        ).scalar() or 0
        
        # 이메일 내용 생성
        if total_attendance > 0:
            email_body = f"""
월간 근태 리포트 ({start_date} ~ {end_date})

총 출근: {total_attendance}건
정상 출근: {present_count}건
지각: {late_count}건
결근: {absent_count}건

출근률: {round(present_count / total_attendance * 100, 1)}%
            """.strip()
        else:
            email_body = f"""
월간 근태 리포트 ({start_date} ~ {end_date})

데이터가 없습니다.
            """.strip()
        
        # 이메일 발송
        success = send_email(
            to_addr=admin.email,
            subject="월간 근태 리포트",
            body=email_body
        )
        
        if success:
            logger.info(f"이메일 발송 테스트: {admin.email}")
            logger.info(f"제목: 월간 근태 리포트")
            logger.info(f"내용: {email_body}")
            return jsonify({"success": True, "message": "월간 이메일 발송 완료"})
        else:
            return jsonify({"success": False, "message": "이메일 발송 실패"})
            
    except Exception as e:
        logger.error(f"월간 이메일 테스트 실패: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@attendance_bp.route("/api/attendance", methods=["POST"])
@login_required
@admin_required
def create_or_update_attendance():
    """근태 추가/수정 API"""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        date_str = data.get("date")
        clock_in_str = data.get("clock_in")
        clock_out_str = data.get("clock_out")
        
        if not user_id or not date_str:
            return jsonify({"success": False, "error": "필수 정보가 누락되었습니다."}), 400
        
        # 날짜 파싱
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"success": False, "error": "잘못된 날짜 형식입니다."}), 400
        
        # 시간 파싱
        clock_in = None
        clock_out = None
        
        if clock_in_str:
            try:
                clock_in = datetime.strptime(f"{date_str} {clock_in_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                return jsonify({"success": False, "error": "잘못된 출근 시간 형식입니다."}), 400
        
        if clock_out_str:
            try:
                clock_out = datetime.strptime(f"{date_str} {clock_out_str}", "%Y-%m-%d %H:%M")
            except ValueError:
                return jsonify({"success": False, "error": "잘못된 퇴근 시간 형식입니다."}), 400
        
        # 기존 근태 기록 확인
        existing_attendance = Attendance.query.filter(
            Attendance.user_id == user_id
        ).filter(
            func.date(Attendance.clock_in) == date_obj
        ).first()
        
        if existing_attendance:
            # 기존 기록 수정
            existing_attendance.clock_in = clock_in
            existing_attendance.clock_out = clock_out
            existing_attendance.updated_at = datetime.utcnow()
            attendance = existing_attendance
        else:
            # 새 기록 생성
            attendance = Attendance()
            attendance.user_id = user_id
            attendance.clock_in = clock_in
            attendance.clock_out = clock_out
            attendance.created_at = datetime.utcnow()
            attendance.updated_at = datetime.utcnow()
            db.session.add(attendance)
        
        db.session.commit()
        
        return jsonify({
            "success": True, 
            "message": "근태 정보가 저장되었습니다.",
            "attendance_id": attendance.id
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"근태 저장 실패: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_bp.route("/api/users", methods=["GET"])
@login_required
def get_users():
    """직원 목록 API - 근태 관리용 (통합 API 사용)"""
    try:
        # 통합 API로 리다이렉트
        from api.staff import get_staff_list
        return get_staff_list()
        
    except Exception as e:
        logger.error(f"직원 목록 조회 실패: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500
