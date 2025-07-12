from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import extract, func

from extensions import db
from models import ActionLog, Attendance, User
from utils.decorators import admin_required
from utils.logger import log_action, log_error
from utils.notify import notify_salary_payment
from utils.pay_transfer import transfer_salary, validate_bank_account

payroll_bp = Blueprint("payroll", __name__)


@payroll_bp.route("/admin/bulk_transfer")
@login_required
@admin_required
def bulk_transfer():
    """일괄 급여 이체 실행"""
    try:
        year, month = datetime.utcnow().year, datetime.utcnow().month
        users = User.query.filter(
            User.role.in_(['employee', 'manager']),
            User.status.in_(['approved', 'active'])
        ).order_by(User.name).all()

        transfer_results = []

        for user in users:
            # 해당 월 근무시간 계산
            total_seconds = (
                db.session.query(
                    func.sum(
                        func.strftime("%s", Attendance.clock_out)
                        - func.strftime("%s", Attendance.clock_in)
                    )
                )
                .filter(
                    Attendance.user_id == user.id,
                    extract("year", Attendance.clock_in) == year,
                    extract("month", Attendance.clock_in) == month,
                    Attendance.clock_out.isnot(None),
                )
                .scalar()
                or 0
            )

            total_hours = int(total_seconds // 3600)
            wage = total_hours * 12000  # 시간당 12,000원

            # 계좌 정보 검증
            is_valid, error_msg = validate_bank_account(user)
            if not is_valid:
                transfer_results.append(
                    {
                        "user_id": user.id,
                        "user_name": user.name or user.username,
                        "amount": wage,
                        "success": False,
                        "message": error_msg,
                    }
                )
                continue

            # 급여 이체 실행
            result = transfer_salary(user, wage)
            if isinstance(result, tuple):
                success, message = result
            else:
                success, message = result, ""

            transfer_results.append(
                {
                    "user_id": user.id,
                    "user_name": user.name or user.username,
                    "amount": wage,
                    "success": success,
                    "message": message,
                }
            )

            # 성공 시 알림 발송
            if success:
                notify_salary_payment(user, wage, year, month)

        # 결과 요약
        success_count = sum(1 for r in transfer_results if r["success"])
        total_count = len(transfer_results)

        log_action(
            current_user.id,
            "BULK_TRANSFER_EXECUTED",
            f"Transferred salary for {success_count}/{total_count} users",
        )

        flash(
            f"일괄 급여 이체 완료! 성공: {success_count}명, 실패: {total_count - success_count}명",
            "success",
        )

        return redirect(url_for("admin_dashboard"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("급여 이체 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@payroll_bp.route("/admin/transfer_history")
@login_required
@admin_required
def transfer_history():
    """이체 이력 조회"""
    try:
        # 최근 이체 이력 조회
        recent_transfers = (
            ActionLog.query.filter(ActionLog.action.like("SALARY_TRANSFER_%"))
            .order_by(ActionLog.created_at.desc())
            .limit(50)
            .all()
        )

        return render_template(
            "admin/transfer_history.html", transfers=recent_transfers
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("이체 이력 조회 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@payroll_bp.route("/admin/individual_transfer/<int:user_id>")
@login_required
@admin_required
def individual_transfer(user_id):
    """개별 급여 이체"""
    try:
        user = User.query.get_or_404(user_id)
        year, month = datetime.utcnow().year, datetime.utcnow().month

        # 해당 월 근무시간 계산
        total_seconds = (
            db.session.query(
                func.sum(
                    func.strftime("%s", Attendance.clock_out)
                    - func.strftime("%s", Attendance.clock_in)
                )
            )
            .filter(
                Attendance.user_id == user.id,
                extract("year", Attendance.clock_in) == year,
                extract("month", Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None),
            )
            .scalar()
            or 0
        )

        total_hours = int(total_seconds // 3600)
        wage = total_hours * 12000

        # 계좌 정보 검증
        is_valid, error_msg = validate_bank_account(user)
        if not is_valid:
            flash(f"계좌 정보 오류: {error_msg}", "error")
            return redirect(url_for("admin_users"))

        # 급여 이체 실행
        result = transfer_salary(user, wage)
        if isinstance(result, tuple):
            success, message = result
        else:
            success, message = result, ""

        if success:
            notify_salary_payment(user, wage, year, month)
            flash(
                f"{user.name or user.username}님 급여 {wage:,}원 이체 완료!", "success"
            )
        else:
            flash(f"급여 이체 실패: {message}", "error")

        log_action(
            current_user.id,
            "INDIVIDUAL_TRANSFER",
            f"Transferred {wage:,} won to {user.username}",
        )

        return redirect(url_for("admin_users"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("급여 이체 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_users"))
