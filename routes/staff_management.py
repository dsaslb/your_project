from utils.logger import log_error  # pyright: ignore
from utils.decorators import admin_required  # pyright: ignore
from models_main import User, db
from sqlalchemy import or_
from flask_login import current_user, login_required
from flask import (Blueprint, flash, redirect, render_template,
                   request, url_for)
from datetime import date, datetime
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore


staff_bp = Blueprint("staff_management", __name__)


@staff_bp.route("/admin/staff/approval")
@login_required
@admin_required
def staff_approval():
    """직원 승인 페이지"""
    try:
        # 대기 중인 직원 조회
        pending_staff = User.query.filter_by(status='pending').all()

        return render_template(
            "staff_approval.html",
            pending_staff=pending_staff
        )
    except Exception as e:
        log_error(e, current_user.id)
        flash("직원 승인 페이지 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@staff_bp.route("/staff-management")
@login_required
@admin_required
def staff_management():
    """React 스타일의 직원 관리 페이지"""
    try:
        # 검색 파라미터
        search_term = request.args.get() if args else None"search", "") if args else None

        # 직원 데이터 조회
        query = User.query

        if search_term:
            query = query.filter(
                or_(
                    User.name.contains(search_term),
                    User.username.contains(search_term),
                    User.role.contains(search_term),
                )
            )

        staff_data = query.all()

        # 통계 계산
        total_staff = User.query.count()
        active_staff = User.query.filter_by(is_active=True).count()
        inactive_staff = total_staff - active_staff

        # 이번 달 신입 (예시 - 실제로는 입사일 기준으로 계산)
        new_this_month = 0

        stats = {
            "total_staff": total_staff,
            "active_staff": active_staff,
            "inactive_staff": inactive_staff,
            "new_this_month": new_this_month,
        }

        return render_template(
            "staff_management.html",
            staff_data=staff_data,
            stats=stats,
            search_term=search_term,
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("직원 관리 페이지 로딩 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@staff_bp.route("/staff-management/add", methods=["GET", "POST"])
@login_required
@admin_required
def add_staff():
    """새 직원 추가"""
    if request.method == "POST":
        try:
            username = request.form.get() if form else None"username") if form else None
            name = request.form.get() if form else None"name") if form else None
            email = request.form.get() if form else None"email") if form else None
            phone = request.form.get() if form else None"phone") if form else None
            role = request.form.get() if form else None"role") if form else None
            department = request.form.get() if form else None"department") if form else None
            password = request.form.get() if form else None"password") if form else None

            # 중복 확인
            if User.query.filter_by(username=username).first():
                flash("이미 존재하는 사용자명입니다.", "error")
                return redirect(url_for("staff.add_staff"))

            # 새 사용자 생성
            new_user = User()
            new_user.username = username
            new_user.name = name
            new_user.email = email
            new_user.phone = phone
            new_user.role = role
            new_user.department = department
            new_user.status = 'approved'  # is_active 대신 status 사용
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash("새 직원이 성공적으로 추가되었습니다.", "success")
            return redirect(url_for("staff.staff_management"))

        except Exception as e:
            log_error(e, current_user.id)
            flash("직원 추가 중 오류가 발생했습니다.", "error")
            return redirect(url_for("staff.add_staff"))

    return render_template("add_staff.html")


@staff_bp.route("/staff-management/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_staff(user_id):
    """직원 정보 수정"""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        try:
            user.name = request.form.get() if form else None"name") if form else None
            user.email = request.form.get() if form else None"email") if form else None
            user.phone = request.form.get() if form else None"phone") if form else None
            user.role = request.form.get() if form else None"role") if form else None
            user.department = request.form.get() if form else None"department") if form else None
            user.is_active = request.form.get() if form else None"is_active") if form else None == "on"

            # 비밀번호 변경 (선택사항)
            new_password = request.form.get() if form else None"new_password") if form else None
            if new_password:
                user.set_password(new_password)

            db.session.commit()

            flash("직원 정보가 성공적으로 수정되었습니다.", "success")
            return redirect(url_for("staff.staff_management"))

        except Exception as e:
            log_error(e, current_user.id)
            flash("직원 정보 수정 중 오류가 발생했습니다.", "error")

    return render_template("edit_staff.html", user=user)


@staff_bp.route("/staff-management/<int:user_id>/toggle-status", methods=["POST"])
@login_required
@admin_required
def toggle_staff_status(user_id):
    """직원 활성화/비활성화 토글"""
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active

        db.session.commit()

        status = "활성화" if user.is_active else "비활성화"
        flash(f"직원이 {status}되었습니다.", "success")

    except Exception as e:
        log_error(e, current_user.id)
        flash("상태 변경 중 오류가 발생했습니다.", "error")

    return redirect(url_for("staff.staff_management"))
