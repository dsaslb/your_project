from flask import Blueprint, request, jsonify, render_template
from models import Attendance, User, db
from datetime import datetime, date
from sqlalchemy import extract, func
from flask_login import login_required, current_user
from functools import wraps

attendance_bp = Blueprint('attendance', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "관리자 권한이 필요합니다"}), 403
        return f(*args, **kwargs)
    return decorated_function

@attendance_bp.route('/api/attendance_stats', methods=['GET'])
@login_required
def attendance_stats():
    """근태 통계 API - 간소화 버전"""
    try:
        # 쿼리 파라미터
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int)
        
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
            q = q.filter(extract('year', Attendance.clock_in) == year)
            q = q.filter(extract('month', Attendance.clock_in) == month)
        else:
            q = q.filter(extract('year', Attendance.clock_in) == year)
        
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
            if att.clock_in and att.clock_in.time() > datetime.strptime('09:00', '%H:%M').time():
                is_late = True
            if att.clock_out and att.clock_out.time() < datetime.strptime('18:00', '%H:%M').time():
                is_early_leave = True
            
            result.append({
                "id": att.id,
                "user_id": att.user_id,
                "user_name": att.user.name or att.user.username,
                "date": att.clock_in.date().isoformat() if att.clock_in else None,
                "clock_in": att.clock_in.strftime("%H:%M") if att.clock_in else None,
                "clock_out": att.clock_out.strftime("%H:%M") if att.clock_out else None,
                "work_hours": round(work_hours, 2),
                "is_late": is_late,
                "is_early_leave": is_early_leave,
                "is_absent": att.clock_in is None,
                "overtime_hours": max(0, work_hours - 8) if work_hours > 8 else 0
            })
        
        return jsonify({
            "success": True,
            "data": result,
            "total_count": len(result)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@attendance_bp.route('/api/attendance_summary', methods=['GET'])
@login_required
def attendance_summary():
    """근태 통계 요약 API"""
    try:
        user_id = request.args.get('user_id', type=int)
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int)
        
        # 기본 쿼리
        q = db.session.query(Attendance)
        
        if user_id:
            q = q.filter(Attendance.user_id == user_id)
        if month:
            q = q.filter(extract('year', Attendance.clock_in) == year)
            q = q.filter(extract('month', Attendance.clock_in) == month)
        else:
            q = q.filter(extract('year', Attendance.clock_in) == year)
        
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
                if att.clock_in.time() > datetime.strptime('09:00', '%H:%M').time():
                    late_count += 1
                if att.clock_out.time() < datetime.strptime('18:00', '%H:%M').time():
                    early_leave_count += 1
                if work_hours > 8:
                    overtime_hours += work_hours - 8
            else:
                absent_count += 1
        
        # 예상 급여 계산 (시급 12,000원)
        estimated_wage = int(total_hours * 12000)
        
        return jsonify({
            "success": True,
            "summary": {
                "total_days": total_days,
                "total_hours": round(total_hours, 2),
                "late_count": late_count,
                "early_leave_count": early_leave_count,
                "absent_count": absent_count,
                "overtime_hours": round(overtime_hours, 2),
                "estimated_wage": estimated_wage,
                "avg_hours_per_day": round(total_hours / total_days, 2) if total_days > 0 else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@attendance_bp.route('/attendance_stats_simple')
@login_required
@admin_required
def attendance_stats_simple():
    """간소화된 근태 통계 페이지"""
    # 사용자 목록
    users = User.query.filter(User.deleted_at == None).order_by(User.username).all()
    
    # 기본 통계 데이터
    year = request.args.get('year', type=int) or datetime.now().year
    month = request.args.get('month', type=int)
    user_id = request.args.get('user_id', type=int)
    
    return render_template('admin/attendance_stats_simple.html',
                         users=users,
                         year=year,
                         month=month,
                         user_id=user_id) 