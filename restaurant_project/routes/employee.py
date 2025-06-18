from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from restaurant_project.models import db, Attendance
from restaurant_project.utils.decorators import employee_required

employee_bp = Blueprint('employee', __name__, url_prefix='/employee')

@employee_bp.route('/attendance', methods=['GET', 'POST'])
@login_required
@employee_required
def attendance():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'clock_in':
            last = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.id.desc()).first()
            if not last or last.clock_out is not None:
                new_record = Attendance(user_id=current_user.id, clock_in=datetime.now())
                db.session.add(new_record)
                db.session.commit()
                flash("출근 기록 완료!", "success")
            else:
                flash("이전 퇴근이 처리되지 않았습니다. 퇴근부터 기록해주세요.", "warning")
        elif action == 'clock_out':
            last = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.id.desc()).first()
            if last and last.clock_out is None:
                last.clock_out = datetime.now()
                db.session.commit()
                flash("퇴근 기록 완료!", "success")
            else:
                flash("출근 기록이 없거나 이미 퇴근 처리됨.", "warning")
        return redirect(url_for('employee.attendance'))

    records = Attendance.query.filter_by(user_id=current_user.id).order_by(Attendance.clock_in.desc()).all()
    return render_template('employee_attendance_multi.html', records=records)
