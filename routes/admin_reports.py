"""
신고/이의제기 관리 라우트
"""

import io
import json
from collections import Counter
from datetime import datetime, timedelta

import pandas as pd
from flask import (Blueprint, flash, jsonify, redirect, render_template,
                   request, send_file, url_for)
from flask_login import current_user, login_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from sqlalchemy import and_, func, or_

from extensions import db
from models import (Attendance, AttendanceReport, Notification, Order,
                    SystemLog, User)
from utils.decorators import admin_required, require_permission
from utils.logger import log_action, log_error
from utils.notify import send_notification_enhanced

admin_reports_bp = Blueprint("admin_reports", __name__)


@admin_reports_bp.route("/admin_dashboard/reports")
@login_required
@admin_required
def admin_reports():
    """신고/이의제기 관리 대시보드"""
    try:
        # 필터 파라미터
        status = request.args.get("status", "")
        user_id = request.args.get("user_id", "")
        dispute_type = request.args.get("dispute_type", "")
        date_from = request.args.get("date_from", "")
        date_to = request.args.get("date_to", "")

        # 쿼리 구성
        query = AttendanceReport.query

        if status:
            query = query.filter(AttendanceReport.status == status)
        if user_id:
            query = query.filter(AttendanceReport.user_id == int(user_id))
        if dispute_type:
            query = query.filter(AttendanceReport.dispute_type == dispute_type)
        if date_from:
            query = query.filter(
                AttendanceReport.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                AttendanceReport.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )

        # 정렬 및 제한
        reports = query.order_by(AttendanceReport.created_at.desc()).limit(100).all()

        # 통계 계산
        total_count = AttendanceReport.query.count()
        pending_count = AttendanceReport.query.filter_by(status="pending").count()
        processing_count = AttendanceReport.query.filter_by(status="processing").count()
        resolved_count = AttendanceReport.query.filter_by(status="resolved").count()

        # 사용자 목록 (필터용)
        users = User.query.filter_by(is_active=True).order_by(User.name).all()

        # 상태별 통계
        status_stats = (
            db.session.query(AttendanceReport.status, func.count(AttendanceReport.id))
            .group_by(AttendanceReport.status)
            .all()
        )

        context = {
            "reports": reports,
            "users": users,
            "total_count": total_count,
            "pending_count": pending_count,
            "processing_count": processing_count,
            "resolved_count": resolved_count,
            "status_stats": dict(status_stats),
            "filters": {
                "status": status,
                "user_id": user_id,
                "dispute_type": dispute_type,
                "date_from": date_from,
                "date_to": date_to,
            },
        }

        return render_template("admin/reports.html", **context)

    except Exception as e:
        log_error(e, current_user.id)
        flash("신고/이의제기 목록을 불러오는 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_dashboard"))


@admin_reports_bp.route("/admin_dashboard/report_timeline")
@login_required
@admin_required
def report_timeline():
    """신고/이의제기 타임라인 뷰"""
    try:
        # 필터 파라미터
        user_id = request.args.get("user_id", "")
        status = request.args.get("status", "")
        date_from = request.args.get("from", "")
        date_to = request.args.get("to", "")
        keyword = request.args.get("q", "")

        # 쿼리 구성
        query = AttendanceReport.query

        if user_id:
            query = query.filter(AttendanceReport.user_id == int(user_id))
        if status:
            query = query.filter(AttendanceReport.status == status)
        if date_from:
            query = query.filter(
                AttendanceReport.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                AttendanceReport.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )
        if keyword:
            query = query.filter(
                or_(
                    AttendanceReport.reason.contains(keyword),
                    AttendanceReport.admin_reply.contains(keyword),
                    User.name.contains(keyword),
                )
            ).join(User, AttendanceReport.user_id == User.id)

        # 정렬 및 제한
        reports = query.order_by(AttendanceReport.created_at.desc()).limit(200).all()

        # 사용자 목록 (필터용)
        users = User.query.filter_by(is_active=True).order_by(User.name).all()

        # AI 자동 요약
        summary = ai_summarize_reports(reports)

        context = {
            "reports": reports,
            "users": users,
            "summary": summary,
            "filters": {
                "user_id": user_id,
                "status": status,
                "date_from": date_from,
                "date_to": date_to,
                "keyword": keyword,
            },
        }

        return render_template("admin/report_timeline.html", **context)

    except Exception as e:
        log_error(e, current_user.id)
        flash("타임라인을 불러오는 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.admin_reports"))


def ai_summarize_reports(reports):
    """AI 자동 요약/코멘트 생성"""
    try:
        if not reports:
            return "신고/이의제기 데이터가 없습니다."

        # 상태별 통계
        status_cnt = Counter([r.status for r in reports])
        pending_count = status_cnt.get("pending", 0)
        resolved_count = status_cnt.get("resolved", 0)
        processing_count = status_cnt.get("processing", 0)

        # 가장 많은 사유
        reason_counter = Counter([r.reason for r in reports if r.reason])
        most_common_reason = reason_counter.most_common(1)
        top_reason = most_common_reason[0][0] if most_common_reason else "N/A"

        # 기간 분석
        if reports:
            latest_date = max(r.created_at for r in reports)
            earliest_date = min(r.created_at for r in reports)
            period_days = (latest_date - earliest_date).days + 1
        else:
            period_days = 0

        # AI 분석 결과
        summary_parts = []

        # 기본 통계
        summary_parts.append(f"총 {len(reports)}건의 신고/이의제기")

        if period_days > 0:
            summary_parts.append(f"기간: {period_days}일")

        # 상태별 분석
        if pending_count > 0:
            summary_parts.append(f"미처리 {pending_count}건")
        if processing_count > 0:
            summary_parts.append(f"처리중 {processing_count}건")
        if resolved_count > 0:
            summary_parts.append(f"처리완료 {resolved_count}건")

        # 사유 분석
        if top_reason != "N/A":
            summary_parts.append(f"주요 사유: {top_reason}")

        # AI 권장사항
        recommendations = []
        if pending_count > len(reports) * 0.3:  # 30% 이상 미처리
            recommendations.append("미처리 건수가 많아 신속한 처리 필요")

        if reason_counter and len(reason_counter) <= 3:
            recommendations.append("사유가 단조로워 정책 검토 필요")

        if recommendations:
            summary_parts.append(f"권장사항: {'; '.join(recommendations)}")

        return " | ".join(summary_parts)

    except Exception as e:
        log_error(e, current_user.id)
        return "AI 요약 생성 중 오류가 발생했습니다."


@admin_reports_bp.route("/admin_dashboard/report_timeline/export_pdf")
@login_required
@admin_required
def report_timeline_export_pdf():
    """타임라인 PDF 내보내기"""
    try:
        # 필터 파라미터 (타임라인과 동일)
        user_id = request.args.get("user_id", "")
        status = request.args.get("status", "")
        date_from = request.args.get("from", "")
        date_to = request.args.get("to", "")
        keyword = request.args.get("q", "")

        # 쿼리 구성
        query = AttendanceReport.query

        if user_id:
            query = query.filter(AttendanceReport.user_id == int(user_id))
        if status:
            query = query.filter(AttendanceReport.status == status)
        if date_from:
            query = query.filter(
                AttendanceReport.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                AttendanceReport.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )
        if keyword:
            query = query.filter(
                or_(
                    AttendanceReport.reason.contains(keyword),
                    AttendanceReport.admin_reply.contains(keyword),
                    User.name.contains(keyword),
                )
            ).join(User, AttendanceReport.user_id == User.id)

        reports = query.order_by(AttendanceReport.created_at.desc()).limit(200).all()

        # AI 요약
        summary = ai_summarize_reports(reports)

        # PDF 생성
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)

        # 제목
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "신고/이의제기 타임라인 리포트")

        # 생성 정보
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, 760, f"총 건수: {len(reports)}건")

        # AI 요약
        if summary:
            c.drawString(50, 740, f"AI 요약: {summary}")

        # 필터 정보
        filter_info = []
        if user_id:
            user = User.query.get(int(user_id))
            if user:
                filter_info.append(f"직원: {user.name}")
        if status:
            filter_info.append(f"상태: {status}")
        if date_from:
            filter_info.append(f"시작일: {date_from}")
        if date_to:
            filter_info.append(f"종료일: {date_to}")
        if keyword:
            filter_info.append(f"키워드: {keyword}")

        if filter_info:
            c.drawString(50, 720, f"필터: {' | '.join(filter_info)}")

        # 타임라인 데이터
        y_position = 680
        c.setFont("Helvetica", 9)

        for i, report in enumerate(reports):
            if y_position < 50:  # 페이지 끝 도달 시 새 페이지
                c.showPage()
                y_position = 750
                c.setFont("Helvetica", 9)

            # 타임라인 항목
            timestamp = report.created_at.strftime("%m-%d %H:%M")
            user_name = report.user.name or report.user.username
            reason = (
                report.reason[:50] + "..." if len(report.reason) > 50 else report.reason
            )

            # 메인 내용
            c.setFont("Helvetica-Bold", 9)
            c.drawString(50, y_position, f"[{timestamp}] {user_name}:")

            y_position -= 15
            c.setFont("Helvetica", 8)
            c.drawString(60, y_position, reason)

            y_position -= 12
            c.drawString(60, y_position, f"상태: {report.status}")

            # 출결 정보
            if report.attendance:
                attendance_info = (
                    f"출결: {report.attendance.clock_in.strftime('%Y-%m-%d')}"
                )
                if report.attendance.reason:
                    attendance_info += f" ({report.attendance.reason})"
                c.drawString(60, y_position - 12, attendance_info)
                y_position -= 12

            # 답변 정보
            if report.admin_reply:
                y_position -= 12
                c.setFont("Helvetica-Bold", 8)
                c.drawString(60, y_position, "답변:")
                y_position -= 10
                c.setFont("Helvetica", 8)
                reply_text = (
                    report.admin_reply[:60] + "..."
                    if len(report.admin_reply) > 60
                    else report.admin_reply
                )
                c.drawString(70, y_position, reply_text)

            y_position -= 20  # 다음 항목과의 간격

        c.save()
        output.seek(0)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"신고이의제기_타임라인_{timestamp}.pdf"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/pdf",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("PDF 내보내기 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.report_timeline"))


@admin_reports_bp.route(
    "/admin_dashboard/report/<int:report_id>/reply", methods=["POST"]
)
@login_required
@admin_required
def admin_report_reply(report_id):
    """신고/이의제기 답변 처리"""
    try:
        dispute = AttendanceReport.query.get_or_404(report_id)

        # 답변 내용
        reply = request.form.get("reply", "").strip()
        new_status = request.form.get("status", "resolved")

        if not reply:
            flash("답변 내용을 입력해주세요.", "error")
            return redirect(url_for("admin_reports.admin_reports"))

        # 상태 업데이트
        dispute.admin_reply = reply
        dispute.status = new_status
        dispute.admin_id = current_user.id
        dispute.updated_at = datetime.utcnow()

        db.session.commit()

        # 사용자에게 알림 발송
        send_notification_enhanced(
            user_id=dispute.user_id,
            content=f"신고/이의제기에 답변이 등록되었습니다. (상태: {new_status})",
            category="신고/이의제기",
            link=f"/attendance/dispute/{dispute.id}",
        )

        # 로그 기록
        log_action(
            user_id=current_user.id,
            action=f"신고/이의제기 답변 처리",
            details=f"신고ID: {dispute.id}, 상태: {new_status}, 답변: {reply[:50]}...",
        )

        flash("답변이 성공적으로 등록되었습니다.", "success")
        return redirect(url_for("admin_reports.admin_reports"))

    except Exception as e:
        log_error(e, current_user.id)
        flash("답변 처리 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.admin_reports"))


@admin_reports_bp.route("/admin_dashboard/reports/export_excel")
@login_required
@admin_required
def export_reports_excel():
    """신고/이의제기 엑셀 내보내기"""
    try:
        # 필터 파라미터 (목록과 동일)
        status = request.args.get("status", "")
        user_id = request.args.get("user_id", "")
        dispute_type = request.args.get("dispute_type", "")
        date_from = request.args.get("date_from", "")
        date_to = request.args.get("date_to", "")

        # 쿼리 구성
        query = AttendanceReport.query

        if status:
            query = query.filter(AttendanceReport.status == status)
        if user_id:
            query = query.filter(AttendanceReport.user_id == int(user_id))
        if dispute_type:
            query = query.filter(AttendanceReport.dispute_type == dispute_type)
        if date_from:
            query = query.filter(
                AttendanceReport.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                AttendanceReport.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )

        reports = query.order_by(AttendanceReport.created_at.desc()).all()

        # 엑셀 데이터 구성
        data = []
        for r in reports:
            data.append(
                {
                    "신고일시": r.created_at.strftime("%Y-%m-%d %H:%M"),
                    "직원명": r.user.name or r.user.username,
                    "출결일": (
                        r.attendance.clock_in.strftime("%Y-%m-%d")
                        if r.attendance
                        else ""
                    ),
                    "신고유형": "신고" if r.dispute_type == "report" else "이의제기",
                    "신고내용": r.reason,
                    "상태": r.status,
                    "관리자답변": r.admin_reply or "",
                    "답변일시": (
                        r.updated_at.strftime("%Y-%m-%d %H:%M") if r.admin_reply else ""
                    ),
                    "처리관리자": r.admin.name if r.admin else "",
                }
            )

        # DataFrame 생성 및 엑셀 저장
        df = pd.DataFrame(data)
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="신고이의제기", index=False)

            # 워크시트 가져오기
            worksheet = writer.sheets["신고이의제기"]

            # 열 너비 자동 조정
            for i, col in enumerate(df.columns):
                max_len = max(df[col].astype(str).apply(len).max(), len(col))
                worksheet.set_column(i, i, max_len + 2)

        output.seek(0)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"신고이의제기_내보내기_{timestamp}.xlsx"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("엑셀 내보내기 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.admin_reports"))


@admin_reports_bp.route("/admin_dashboard/reports/export_pdf")
@login_required
@admin_required
def export_reports_pdf():
    """신고/이의제기 PDF 내보내기"""
    try:
        # 필터 파라미터 (목록과 동일)
        status = request.args.get("status", "")
        user_id = request.args.get("user_id", "")
        dispute_type = request.args.get("dispute_type", "")
        date_from = request.args.get("date_from", "")
        date_to = request.args.get("date_to", "")

        # 쿼리 구성
        query = AttendanceReport.query

        if status:
            query = query.filter(AttendanceReport.status == status)
        if user_id:
            query = query.filter(AttendanceReport.user_id == int(user_id))
        if dispute_type:
            query = query.filter(AttendanceReport.dispute_type == dispute_type)
        if date_from:
            query = query.filter(
                AttendanceReport.created_at >= datetime.strptime(date_from, "%Y-%m-%d")
            )
        if date_to:
            query = query.filter(
                AttendanceReport.created_at
                <= datetime.strptime(date_to, "%Y-%m-%d") + timedelta(days=1)
            )

        reports = query.order_by(AttendanceReport.created_at.desc()).all()

        # PDF 생성
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)

        # 제목
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "신고/이의제기 관리 리포트")

        # 생성 정보
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(50, 760, f"총 건수: {len(reports)}건")

        # 테이블 헤더
        y_position = 720
        headers = ["신고일시", "직원명", "신고유형", "상태", "신고내용"]
        x_positions = [50, 120, 200, 280, 350]

        c.setFont("Helvetica-Bold", 9)
        for i, header in enumerate(headers):
            c.drawString(x_positions[i], y_position, header)

        # 데이터 행
        y_position -= 20
        c.setFont("Helvetica", 8)

        for report in reports:
            if y_position < 50:  # 페이지 끝 도달 시 새 페이지
                c.showPage()
                y_position = 750
                c.setFont("Helvetica", 8)

            row_data = [
                report.created_at.strftime("%m-%d %H:%M"),
                report.user.name or report.user.username,
                "신고" if report.dispute_type == "report" else "이의제기",
                report.status,
                (
                    report.reason[:30] + "..."
                    if len(report.reason) > 30
                    else report.reason
                ),
            ]

            for i, data in enumerate(row_data):
                c.drawString(x_positions[i], y_position, str(data))

            y_position -= 15

        c.save()
        output.seek(0)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"신고이의제기_리포트_{timestamp}.pdf"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/pdf",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("PDF 내보내기 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.admin_reports"))


@admin_reports_bp.route("/admin_dashboard/reports/stats")
@login_required
@admin_required
def reports_stats():
    """신고/이의제기 통계 API"""
    try:
        # 기간별 통계
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # 전체 통계
        total_reports = AttendanceReport.query.count()
        pending_reports = AttendanceReport.query.filter_by(status="pending").count()
        processing_reports = AttendanceReport.query.filter_by(
            status="processing"
        ).count()
        resolved_reports = AttendanceReport.query.filter_by(status="resolved").count()

        # 최근 7일 통계
        recent_week = AttendanceReport.query.filter(
            AttendanceReport.created_at >= week_ago
        ).count()

        # 최근 30일 통계
        recent_month = AttendanceReport.query.filter(
            AttendanceReport.created_at >= month_ago
        ).count()

        # 유형별 통계
        report_type_stats = (
            db.session.query(
                AttendanceReport.dispute_type, func.count(AttendanceReport.id)
            )
            .group_by(AttendanceReport.dispute_type)
            .all()
        )

        # 상태별 통계
        status_stats = (
            db.session.query(AttendanceReport.status, func.count(AttendanceReport.id))
            .group_by(AttendanceReport.status)
            .all()
        )

        # 일별 통계 (최근 7일)
        daily_stats = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = AttendanceReport.query.filter(
                func.date(AttendanceReport.created_at) == date
            ).count()
            daily_stats.append({"date": date.strftime("%m-%d"), "count": count})

        daily_stats.reverse()  # 오래된 순으로 정렬

        return jsonify(
            {
                "success": True,
                "stats": {
                    "total": total_reports,
                    "pending": pending_reports,
                    "processing": processing_reports,
                    "resolved": resolved_reports,
                    "recent_week": recent_week,
                    "recent_month": recent_month,
                    "type_stats": dict(report_type_stats),
                    "status_stats": dict(status_stats),
                    "daily_stats": daily_stats,
                },
            }
        )

    except Exception as e:
        log_error(e, current_user.id)
        return jsonify({"success": False, "error": str(e)}), 500


@admin_reports_bp.route("/admin_dashboard/report_stats")
@login_required
@admin_required
def report_stats():
    """누적 신고/이의 패턴 AI 분석"""
    try:
        # 1. 직원별/팀별 누적 신고/이의 건수
        report_counts = (
            db.session.query(
                User.name, User.id, func.count(AttendanceReport.id).label("count")
            )
            .join(AttendanceReport, AttendanceReport.user_id == User.id)
            .group_by(User.id, User.name)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        # 2. 사유별(패턴) 건수
        reason_counts = (
            db.session.query(
                AttendanceReport.reason,
                func.count(AttendanceReport.id).label("count"),
            )
            .group_by(AttendanceReport.reason)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        # 3. 반복 신고(3회 이상) 직원 자동 경고 감지
        flagged_users = []
        for name, user_id, count in report_counts:
            if count >= 3:
                flagged_users.append({"name": name, "user_id": user_id, "count": count})

        # 4. 월별/주별 트렌드
        monthly_stats = (
            db.session.query(
                func.date_format(AttendanceReport.created_at, "%Y-%m").label("month"),
                func.count(AttendanceReport.id).label("count"),
            )
            .group_by(func.date_format(AttendanceReport.created_at, "%Y-%m"))
            .order_by(func.date_format(AttendanceReport.created_at, "%Y-%m").desc())
            .limit(12)
            .all()
        )

        # 5. 팀별 통계 (팀 정보가 있는 경우)
        team_stats = []
        try:
            team_stats = (
                db.session.query(
                    User.team, func.count(AttendanceReport.id).label("count")
                )
                .join(AttendanceReport, AttendanceReport.user_id == User.id)
                .filter(User.team.isnot(None))
                .group_by(User.team)
                .order_by(func.count(AttendanceReport.id).desc())
                .all()
            )
        except:
            pass  # 팀 컬럼이 없는 경우 무시

        # 6. AI 분석 결과
        ai_analysis = {
            "high_risk_users": flagged_users,
            "most_common_reasons": reason_counts[:5],  # 상위 5개 사유
            "trend_analysis": (
                "증가"
                if len(monthly_stats) >= 2
                and monthly_stats[0].count > monthly_stats[1].count
                else "감소"
            ),
            "recommendations": [],
        }

        # AI 권장사항 생성
        if flagged_users:
            ai_analysis["recommendations"].append(
                f"반복 신고자 {len(flagged_users)}명에 대한 개별 면담 필요"
            )

        if reason_counts:
            top_reason = reason_counts[0]
            ai_analysis["recommendations"].append(
                f"가장 많은 사유 '{top_reason.reason}'에 대한 정책 검토 필요"
            )

        # 7. 자동 경고 발송 (새로운 경고만)
        for flagged_user in flagged_users:
            # 이미 경고를 받았는지 확인 (간단한 로직)
            recent_warnings = (
                db.session.query(AttendanceReport)
                .filter(
                    and_(
                        AttendanceReport.user_id == flagged_user["user_id"],
                        AttendanceReport.reason.like("%AI 경고%"),
                        AttendanceReport.created_at
                        >= datetime.now() - timedelta(days=7),
                    )
                )
                .count()
            )

            if recent_warnings == 0:
                # 새로운 AI 경고 생성
                ai_warning = AttendanceReport(
                    attendance_id=None,  # 특정 출결에 대한 것이 아님
                    user_id=flagged_user["user_id"],
                    dispute_type="ai_warning",
                    reason=f"AI 분석: 반복 신고/이의제기 감지 (총 {flagged_user['count']}건)",
                    status="pending",
                    admin_reply="자동 생성된 AI 경고입니다. 관리자 검토 필요.",
                    admin_id=None,
                )
                db.session.add(ai_warning)

                # 사용자에게 알림
                send_notification_enhanced(
                    user_id=flagged_user["user_id"],
                    content=f"반복 신고/이의제기 패턴이 감지되어 관리자에게 자동 경고가 발송되었습니다.",
                    category="AI경고",
                )

        db.session.commit()

        context = {
            "report_counts": report_counts,
            "reason_counts": reason_counts,
            "flagged_users": flagged_users,
            "monthly_stats": monthly_stats,
            "team_stats": team_stats,
            "ai_analysis": ai_analysis,
            "total_reports": sum(count for _, _, count in report_counts),
            "unique_users": len(report_counts),
        }

        return render_template("admin/report_stats.html", **context)

    except Exception as e:
        log_error(e, current_user.id)
        flash("AI 분석 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.admin_reports"))


@admin_reports_bp.route("/admin_dashboard/report_stats/export_pdf")
@login_required
@admin_required
def export_report_stats_pdf():
    """AI 분석 리포트 PDF 내보내기"""
    try:
        # AI 분석 데이터 조회 (위와 동일)
        report_counts = (
            db.session.query(User.name, func.count(AttendanceReport.id).label("count"))
            .join(AttendanceReport, AttendanceReport.user_id == User.id)
            .group_by(User.id, User.name)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        reason_counts = (
            db.session.query(
                AttendanceReport.reason,
                func.count(AttendanceReport.id).label("count"),
            )
            .group_by(AttendanceReport.reason)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        flagged_users = [name for name, count in report_counts if count >= 3]

        # PDF 생성
        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)

        # 제목
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, 800, "신고/이의제기 AI 분석 리포트")

        # 생성 정보
        c.setFont("Helvetica", 10)
        c.drawString(50, 780, f"생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.drawString(
            50, 760, f"총 신고건수: {sum(count for _, count in report_counts)}건"
        )
        c.drawString(50, 740, f"신고자 수: {len(report_counts)}명")

        # AI 경고 섹션
        y_position = 700
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "⚠️ AI 분석 경고")

        y_position -= 20
        c.setFont("Helvetica", 10)
        if flagged_users:
            c.drawString(50, y_position, f"반복 신고자: {', '.join(flagged_users)}")
        else:
            c.drawString(50, y_position, "반복 신고자 없음")

        # 상위 신고자
        y_position -= 40
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "상위 신고자")

        y_position -= 20
        c.setFont("Helvetica", 10)
        for i, (name, count) in enumerate(report_counts[:10]):  # 상위 10명
            if y_position < 50:
                c.showPage()
                y_position = 750
                c.setFont("Helvetica", 10)

            warning_text = " [AI 경고]" if name in flagged_users else ""
            c.drawString(50, y_position, f"{i+1}. {name} ({count}건){warning_text}")
            y_position -= 15

        # 사유별 통계
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "사유별 신고 통계")

        y_position -= 20
        c.setFont("Helvetica", 10)
        for reason, count in reason_counts[:10]:  # 상위 10개 사유
            if y_position < 50:
                c.showPage()
                y_position = 750
                c.setFont("Helvetica", 10)

            c.drawString(50, y_position, f"• {reason}: {count}건")
            y_position -= 15

        c.save()
        output.seek(0)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"신고이의제기_AI분석_{timestamp}.pdf"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/pdf",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("PDF 내보내기 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.report_stats"))


@admin_reports_bp.route("/admin_dashboard/report_stats/export_excel")
@login_required
@admin_required
def export_report_stats_excel():
    """AI 분석 리포트 엑셀 내보내기"""
    try:
        # AI 분석 데이터 조회
        report_counts = (
            db.session.query(User.name, func.count(AttendanceReport.id).label("count"))
            .join(AttendanceReport, AttendanceReport.user_id == User.id)
            .group_by(User.id, User.name)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        reason_counts = (
            db.session.query(
                AttendanceReport.reason,
                func.count(AttendanceReport.id).label("count"),
            )
            .group_by(AttendanceReport.reason)
            .order_by(func.count(AttendanceReport.id).desc())
            .all()
        )

        flagged_users = [name for name, count in report_counts if count >= 3]

        # 엑셀 데이터 구성
        output = io.BytesIO()

        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            # 1. 직원별 신고 통계
            user_data = []
            for name, count in report_counts:
                user_data.append(
                    {
                        "직원명": name,
                        "신고건수": count,
                        "AI경고": "Y" if name in flagged_users else "N",
                    }
                )

            df_users = pd.DataFrame(user_data)
            df_users.to_excel(writer, sheet_name="직원별통계", index=False)

            # 2. 사유별 통계
            reason_data = []
            for reason, count in reason_counts:
                reason_data.append({"사유": reason, "건수": count})

            df_reasons = pd.DataFrame(reason_data)
            df_reasons.to_excel(writer, sheet_name="사유별통계", index=False)

            # 3. AI 분석 요약
            summary_data = [
                {
                    "분석항목": "총 신고건수",
                    "값": sum(count for _, count in report_counts),
                },
                {"분석항목": "신고자 수", "값": len(report_counts)},
                {"분석항목": "반복 신고자 수", "값": len(flagged_users)},
                {
                    "분석항목": "AI 경고 대상자",
                    "값": ", ".join(flagged_users) if flagged_users else "없음",
                },
            ]

            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name="AI분석요약", index=False)

            # 워크시트 스타일링
            for sheet_name in writer.sheets:
                worksheet = writer.sheets[sheet_name]
                for i, col in enumerate(
                    df_users.columns
                    if sheet_name == "직원별통계"
                    else (
                        df_reasons.columns
                        if sheet_name == "사유별통계"
                        else df_summary.columns
                    )
                ):
                    max_len = max(
                        (
                            df_users[col].astype(str).apply(len).max()
                            if sheet_name == "직원별통계"
                            else (
                                df_reasons[col].astype(str).apply(len).max()
                                if sheet_name == "사유별통계"
                                else df_summary[col].astype(str).apply(len).max()
                            )
                        ),
                        len(col),
                    )
                    worksheet.set_column(i, i, max_len + 2)

        output.seek(0)

        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"신고이의제기_AI분석_{timestamp}.xlsx"

        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    except Exception as e:
        log_error(e, current_user.id)
        flash("엑셀 내보내기 중 오류가 발생했습니다.", "error")
        return redirect(url_for("admin_reports.report_stats"))


@admin_reports_bp.route("/admin/permissions")
@login_required
@require_permission("employee_management", "assign_roles")
def manage_permissions():
    """권한 관리 페이지"""
    users = User.query.filter(User.deleted_at.is_(None)).all()

    # 권한 모듈 정의
    permission_modules = {
        "dashboard": "대시보드",
        "employee_management": "직원 관리",
        "schedule_management": "스케줄 관리",
        "order_management": "발주 관리",
        "inventory_management": "재고 관리",
        "notification_management": "알림 관리",
        "system_management": "시스템 관리",
        "reports": "보고서",
    }

    permission_actions = {
        "view": "조회",
        "create": "생성",
        "edit": "편집",
        "delete": "삭제",
        "approve": "승인",
        "assign_roles": "권한 부여",
    }

    return render_template(
        "admin/permissions.html",
        users=users,
        permission_modules=permission_modules,
        permission_actions=permission_actions,
    )


@admin_reports_bp.route(
    "/admin/permissions/user/<int:user_id>", methods=["GET", "POST"]
)
@login_required
@require_permission("employee_management", "assign_roles")
def user_permissions(user_id):
    """사용자별 권한 관리"""
    user = User.query.get_or_404(user_id)

    if request.method == "POST":
        try:
            # 기존 권한 백업
            old_permissions = user.permissions.copy() if user.permissions else {}

            # 새로운 권한 설정
            new_permissions = {}
            for module in request.form.getlist("modules"):
                actions = request.form.getlist(f"actions_{module}")
                new_permissions[module] = {
                    "view": "view" in actions,
                    "create": "create" in actions,
                    "edit": "edit" in actions,
                    "delete": "delete" in actions,
                    "approve": "approve" in actions,
                    "assign_roles": "assign_roles" in actions,
                    "admin_only": request.form.get(f"admin_only_{module}") == "on",
                }

            # 권한 업데이트
            user.permissions = new_permissions
            db.session.commit()

            flash(f"{user.username}의 권한이 성공적으로 업데이트되었습니다.", "success")
            return redirect(url_for("admin_reports.manage_permissions"))

        except Exception as e:
            db.session.rollback()
            flash(f"권한 업데이트 중 오류가 발생했습니다: {str(e)}", "error")

    return render_template("admin/user_permissions.html", user=user)


# 권한 템플릿 기능은 User.permissions 기반으로 단순화되어 제거됨


# 권한 템플릿 적용 기능은 User.permissions 기반으로 단순화되어 제거됨


@admin_reports_bp.route("/admin/permissions/logs")
@login_required
@require_permission("employee_management", "view")
def permission_logs():
    """권한 변경 로그 - User.permissions 기반으로 단순화됨"""
    # 권한 변경 로그는 SystemLog에서 확인
    page = request.args.get("page", 1, type=int)
    logs = SystemLog.query.filter(
        SystemLog.action.contains("permission")
    ).order_by(SystemLog.created_at.desc()).paginate(page=page, per_page=50, error_out=False)

    return render_template("admin/permission_logs.html", logs=logs)


@admin_reports_bp.route("/api/permissions/check")
@login_required
def check_permissions():
    """권한 체크 API"""
    module = request.args.get("module")
    action = request.args.get("action", "view")

    if not module:
        return jsonify({"error": "모듈이 지정되지 않았습니다."}), 400

    has_perm = current_user.has_permission(module, action)
    return jsonify(
        {
            "module": module,
            "action": action,
            "has_permission": has_perm,
            "user_role": current_user.role,
        }
    )


@admin_reports_bp.route("/api/permissions/summary")
@login_required
def permission_summary():
    """권한 요약 정보 API"""
    summary = current_user.get_permission_summary()
    return jsonify(summary)


@admin_reports_bp.route("/admin/dashboard/charts")
@login_required
@require_permission("dashboard", "view")
def dashboard_charts():
    """관리자 대시보드 차트 데이터"""
    # 기간 설정
    days = request.args.get("days", 30, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 출근 데이터 (일별)
    attendance_data = (
        db.session.query(
            func.date(Attendance.clock_in).label("date"),
            func.count(Attendance.id).label("count"),
        )
        .filter(
            and_(Attendance.clock_in >= start_date, Attendance.clock_in <= end_date)
        )
        .group_by(func.date(Attendance.clock_in))
        .all()
    )

    # 알림 데이터 (일별)
    notification_data = (
        db.session.query(
            func.date(Notification.created_at).label("date"),
            func.count(Notification.id).label("count"),
        )
        .filter(
            and_(
                Notification.created_at >= start_date,
                Notification.created_at <= end_date,
            )
        )
        .group_by(func.date(Notification.created_at))
        .all()
    )

    # 발주 데이터 (일별)
    order_data = (
        db.session.query(
            func.date(Order.created_at).label("date"),
            func.count(Order.id).label("count"),
        )
        .filter(and_(Order.created_at >= start_date, Order.created_at <= end_date))
        .group_by(func.date(Order.created_at))
        .all()
    )

    # 시스템 로그 데이터 (일별)
    system_log_data = (
        db.session.query(
            func.date(SystemLog.created_at).label("date"),
            func.count(SystemLog.id).label("count"),
        )
        .filter(
            and_(SystemLog.created_at >= start_date, SystemLog.created_at <= end_date)
        )
        .group_by(func.date(SystemLog.created_at))
        .all()
    )

    # 데이터 포맷팅
    def format_chart_data(data, label):
        dates = []
        counts = []
        for item in data:
            dates.append(item.date.strftime("%Y-%m-%d"))
            counts.append(item.count)
        return {
            "labels": dates,
            "datasets": [
                {
                    "label": label,
                    "data": counts,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "tension": 0.1,
                }
            ],
        }

    return jsonify(
        {
            "attendance": format_chart_data(attendance_data, "출근"),
            "notifications": format_chart_data(notification_data, "알림"),
            "orders": format_chart_data(order_data, "발주"),
            "system_logs": format_chart_data(system_log_data, "시스템 로그"),
        }
    )


@admin_reports_bp.route("/admin/dashboard/stats")
@login_required
@require_permission("dashboard", "view")
def dashboard_stats():
    """관리자 대시보드 통계 데이터"""
    today = datetime.now().date()
    this_month = datetime.now().replace(day=1)

    # 오늘 통계
    today_stats = {
        "attendance": Attendance.query.filter(
            func.date(Attendance.clock_in) == today
        ).count(),
        "notifications": Notification.query.filter(
            func.date(Notification.created_at) == today
        ).count(),
        "orders": Order.query.filter(func.date(Order.created_at) == today).count(),
        "system_logs": SystemLog.query.filter(
            func.date(SystemLog.created_at) == today
        ).count(),
    }

    # 이번 달 통계
    month_stats = {
        "attendance": Attendance.query.filter(
            Attendance.clock_in >= this_month
        ).count(),
        "notifications": Notification.query.filter(
            Notification.created_at >= this_month
        ).count(),
        "orders": Order.query.filter(Order.created_at >= this_month).count(),
        "system_logs": SystemLog.query.filter(
            SystemLog.created_at >= this_month
        ).count(),
    }

    # 사용자 통계
    user_stats = {
        "total_users": User.query.filter(User.deleted_at.is_(None)).count(),
        "active_users": User.query.filter(
            and_(User.deleted_at.is_(None), User.status == "approved")
        ).count(),
        "pending_users": User.query.filter(
            and_(User.deleted_at.is_(None), User.status == "pending")
        ).count(),
        "admin_users": User.query.filter(
            and_(User.deleted_at.is_(None), User.role == "admin")
        ).count(),
    }

    return jsonify({"today": today_stats, "month": month_stats, "users": user_stats})


@admin_reports_bp.route("/admin/dashboard/realtime")
@login_required
@require_permission("dashboard", "view")
def realtime_dashboard():
    """실시간 대시보드"""
    # 최근 1시간 데이터
    one_hour_ago = datetime.now() - timedelta(hours=1)

    # 실시간 통계
    realtime_stats = {
        "recent_attendance": Attendance.query.filter(
            Attendance.clock_in >= one_hour_ago
        ).count(),
        "recent_notifications": Notification.query.filter(
            Notification.created_at >= one_hour_ago
        ).count(),
        "recent_orders": Order.query.filter(Order.created_at >= one_hour_ago).count(),
        "recent_logs": SystemLog.query.filter(
            SystemLog.created_at >= one_hour_ago
        ).count(),
    }

    # 최근 활동
    recent_activities = []

    # 최근 출근
    recent_attendance = (
        Attendance.query.filter(Attendance.clock_in >= one_hour_ago)
        .order_by(Attendance.clock_in.desc())
        .limit(5)
        .all()
    )

    for attendance in recent_attendance:
        recent_activities.append(
            {
                "type": "attendance",
                "user": attendance.user.username,
                "action": "출근",
                "time": attendance.clock_in.strftime("%H:%M"),
                "icon": "fas fa-sign-in-alt",
            }
        )

    # 최근 알림
    recent_notifications = (
        Notification.query.filter(Notification.created_at >= one_hour_ago)
        .order_by(Notification.created_at.desc())
        .limit(5)
        .all()
    )

    for notification in recent_notifications:
        recent_activities.append(
            {
                "type": "notification",
                "user": notification.user.username,
                "action": notification.title or "알림",
                "time": notification.created_at.strftime("%H:%M"),
                "icon": "fas fa-bell",
            }
        )

    # 시간순 정렬
    recent_activities.sort(key=lambda x: x["time"], reverse=True)

    return jsonify(
        {"stats": realtime_stats, "activities": recent_activities[:10]}  # 최대 10개
    )


@admin_reports_bp.route("/admin/logs")
@login_required
@require_permission("system_management", "monitoring")
def system_logs():
    """시스템 로그 뷰어"""
    # 로그 레벨 필터
    level = request.args.get("level", "all")
    # 페이지네이션
    page = request.args.get("page", 1, type=int)

    # 로그 쿼리
    query = SystemLog.query

    if level != "all":
        query = query.filter(SystemLog.action.contains(level.upper()))

    logs = query.order_by(SystemLog.created_at.desc()).paginate(
        page=page, per_page=100, error_out=False
    )

    return render_template("admin/system_logs.html", logs=logs, level=level)


@admin_reports_bp.route("/admin/logs/realtime")
@login_required
@require_permission("system_management", "monitoring")
def realtime_logs():
    """실시간 로그 스트리밍"""
    return render_template("admin/realtime_logs.html")


@admin_reports_bp.route("/api/logs/stream")
@login_required
@require_permission("system_management", "monitoring")
def log_stream():
    """로그 스트림 API"""
    import time

    from flask import Response, stream_with_context

    def generate():
        last_id = 0

        while True:
            try:
                # 새로운 로그 조회
                new_logs = (
                    SystemLog.query.filter(SystemLog.id > last_id)
                    .order_by(SystemLog.created_at.desc())
                    .limit(10)
                    .all()
                )

                if new_logs:
                    for log in new_logs:
                        last_id = max(last_id, log.id)

                        log_data = {
                            "id": log.id,
                            "action": log.action,
                            "detail": log.detail,
                            "user": log.user.username if log.user else "시스템",
                            "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                            "ip_address": log.ip_address,
                        }

                        yield f"data: {json.dumps(log_data, ensure_ascii=False)}\n\n"

                time.sleep(2)  # 2초마다 체크

            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
                time.sleep(5)

    return Response(stream_with_context(generate()), mimetype="text/event-stream")


@admin_reports_bp.route("/api/logs/recent")
@login_required
@require_permission("system_management", "monitoring")
def recent_logs():
    """최근 로그 조회 API"""
    limit = request.args.get("limit", 50, type=int)
    level = request.args.get("level", "all")

    query = SystemLog.query

    if level != "all":
        query = query.filter(SystemLog.action.contains(level.upper()))

    logs = query.order_by(SystemLog.created_at.desc()).limit(limit).all()

    log_list = []
    for log in logs:
        log_list.append(
            {
                "id": log.id,
                "action": log.action,
                "detail": log.detail,
                "user": log.user.username if log.user else "시스템",
                "created_at": log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": log.ip_address,
            }
        )

    return jsonify(log_list)


@admin_reports_bp.route("/admin/logs/export")
@login_required
@require_permission("system_management", "monitoring")
def export_logs():
    """로그 내보내기"""
    from datetime import datetime, timedelta

    # 기간 설정
    days = request.args.get("days", 7, type=int)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # 로그 조회
    logs = (
        SystemLog.query.filter(
            and_(SystemLog.created_at >= start_date, SystemLog.created_at <= end_date)
        )
        .order_by(SystemLog.created_at.desc())
        .all()
    )

    # CSV 생성
    import csv
    from io import StringIO

    output = StringIO()
    writer = csv.writer(output)

    # 헤더
    writer.writerow(["ID", "액션", "상세내용", "사용자", "IP주소", "생성일시"])

    # 데이터
    for log in logs:
        writer.writerow(
            [
                log.id,
                log.action,
                log.detail,
                log.user.username if log.user else "시스템",
                log.ip_address,
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    output.seek(0)

    from flask import send_file

    return send_file(
        StringIO(output.getvalue()),
        mimetype="text/csv",
        as_attachment=True,
        download_name=f'system_logs_{datetime.now().strftime("%Y%m%d")}.csv',
    )
