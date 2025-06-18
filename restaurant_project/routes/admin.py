from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from restaurant_project.models import db, User, Attendance
from restaurant_project.utils.decorators import admin_or_manager_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@login_required
@admin_or_manager_required
def dashboard():
    return render_template('admin_dashboard.html')

@admin_bp.route('/attendances')
@login_required
@admin_or_manager_required
def attendances():
    attendances = Attendance.query.order_by(Attendance.clock_in.desc()).all()
    users = {u.id: u.username for u in User.query.all()}
    stats = {}
    for att in attendances:
        if att.user_id not in stats:
            stats[att.user_id] = {'total_minutes': 0, 'count': 0}
        if att.clock_in and att.clock_out:
            stats[att.user_id]['total_minutes'] += int((att.clock_out - att.clock_in).total_seconds() // 60)
            stats[att.user_id]['count'] += 1
    return render_template('admin_attendance_list.html', attendances=attendances, users=users, stats=stats)
