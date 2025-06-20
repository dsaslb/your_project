from flask import Blueprint, render_template, send_file, flash, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import datetime, time
from sqlalchemy import extract, func
import os

from extensions import db
from models import User, Attendance
from utils.decorators import admin_required
from utils.report import generate_attendance_report_pdf, generate_monthly_summary_pdf
from utils.logger import log_action, log_error

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/admin/attendance_report_pdf/<int:user_id>')
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
        attendances = Attendance.query.filter(
            Attendance.user_id == user_id,
            extract('year', Attendance.clock_in) == year,
            extract('month', Attendance.clock_in) == month,
            Attendance.clock_out.isnot(None)
        ).order_by(Attendance.clock_in).all()

        # 통계 계산
        lateness = early_leave = night_work = 0
        for att in attendances:
            if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                lateness += 1
            if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                early_leave += 1
            if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                night_work += 1

        # PDF 파일 생성
        filename = f"attendance_report_{user.username}_{year}_{month}.pdf"
        filepath = os.path.join('static', 'reports', filename)
        
        # reports 디렉토리 생성
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        generate_attendance_report_pdf(filepath, user, month, year, lateness, early_leave, night_work, attendances)
        
        log_action(current_user.id, 'PDF_REPORT_GENERATED', f'Generated attendance report for {user.username}')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('PDF 생성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard'))

@reports_bp.route('/admin/monthly_summary_pdf')
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
        users = User.query.filter_by(status='approved').all()

        for user in users:
            attendances = Attendance.query.filter(
                Attendance.user_id == user.id,
                extract('year', Attendance.clock_in) == year,
                extract('month', Attendance.clock_in) == month,
                Attendance.clock_out.isnot(None)
            ).all()

            lateness = early_leave = night_work = 0
            total_hours = 0

            for att in attendances:
                if att.clock_in and att.clock_in.time() > STANDARD_CLOCKIN:
                    lateness += 1
                if att.clock_out and att.clock_out.time() < STANDARD_CLOCKOUT:
                    early_leave += 1
                if att.clock_out and att.clock_out.time() > NIGHT_WORK_START:
                    night_work += 1
                total_hours += att.work_hours

            users_data.append({
                'user': user,
                'lateness': lateness,
                'early_leave': early_leave,
                'night_work': night_work,
                'total_hours': total_hours
            })

        # PDF 파일 생성
        filename = f"monthly_summary_{year}_{month}.pdf"
        filepath = os.path.join('static', 'reports', filename)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        generate_monthly_summary_pdf(filepath, users_data, month, year)
        
        log_action(current_user.id, 'PDF_SUMMARY_GENERATED', f'Generated monthly summary for {year}/{month}')
        
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        log_error(e, current_user.id)
        flash('PDF 생성 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('admin_dashboard')) 