import io
from datetime import datetime

import pandas as pd
import pdfkit
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, send_file, url_for)
from flask_login import current_user, login_required

from app import Attendance, AttendanceReport, User, db

admin_dashboard_export_bp = Blueprint("admin_dashboard_export", __name__)


@admin_dashboard_export_bp.route("/admin_dashboard/export_excel")
@login_required
def export_admin_dashboard_excel():
    if not current_user.is_admin() and not current_user.is_teamlead():
        flash("관리자/팀장 권한이 필요합니다.", "error")
        return redirect(url_for("dashboard"))

    # 기존 필터 파라미터 재사용
    team = request.args.get("team")
    user_id = request.args.get("user_id")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    q = Attendance.query
    if team:
        q = q.join(User).filter(User.team == team)
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    records = q.order_by(Attendance.date.desc()).limit(100).all()

    data = [
        {
            "일자": r.date,
            "직원": r.user.name or r.user.username,
            "팀": r.user.team or "",
            "사유": r.reason or "",
            "출근시간": r.clock_in.strftime("%H:%M") if r.clock_in else "",
            "퇴근시간": r.clock_out.strftime("%H:%M") if r.clock_out else "",
            "상태": r.status or "",
        }
        for r in records
    ]

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="근태데이터")

        # 통계 시트 추가
        stats_data = []
        if records:
            total_records = len(records)
            late_count = len([r for r in records if "지각" in (r.reason or "")])
            absent_count = len([r for r in records if "결근" in (r.reason or "")])

            stats_data = [
                {"구분": "총 기록수", "수량": total_records},
                {"구분": "지각", "수량": late_count},
                {"구분": "결근", "수량": absent_count},
                {"구분": "정상출근", "수량": total_records - late_count - absent_count},
            ]

        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, index=False, sheet_name="통계")

    output.seek(0)
    return send_file(output, download_name="dashboard_export.xlsx", as_attachment=True)


@admin_dashboard_export_bp.route("/admin_dashboard/export_pdf")
@login_required
def export_admin_dashboard_pdf():
    if not current_user.is_admin() and not current_user.is_teamlead():
        flash("관리자/팀장 권한이 필요합니다.", "error")
        return redirect(url_for("dashboard"))

    # 기존 필터 파라미터 재사용
    team = request.args.get("team")
    user_id = request.args.get("user_id")
    date_from = request.args.get("from")
    date_to = request.args.get("to")

    q = Attendance.query
    if team:
        q = q.join(User).filter(User.team == team)
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    records = q.order_by(Attendance.date.desc()).limit(100).all()

    # 통계 계산
    stats = {}
    if records:
        stats["total_records"] = len(records)
        stats["late_count"] = len([r for r in records if "지각" in (r.reason or "")])
        stats["absent_count"] = len([r for r in records if "결근" in (r.reason or "")])
        stats["normal_count"] = (
            stats["total_records"] - stats["late_count"] - stats["absent_count"]
        )

    html = render_template(
        "admin_dashboard_pdf.html",
        records=records,
        stats=stats,
        team=team,
        user_id=user_id,
        date_from=date_from,
        date_to=date_to,
    )
    pdf = pdfkit.from_string(html, False)
    return send_file(
        io.BytesIO(pdf), download_name="dashboard_export.pdf", as_attachment=True
    )
