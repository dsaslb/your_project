from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func
from models import db, Attendance, User

chart_api = Blueprint('chart_api', __name__)

@chart_api.route('/admin_dashboard/stats_data')
@login_required
def admin_dashboard_stats_data():
    """관리자/팀장 대시보드 차트용 데이터 API"""
    if not current_user.is_admin() and not current_user.is_teamlead():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    team = request.args.get('team')
    user_id = request.args.get('user_id')
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    q = Attendance.query
    if team:
        q = q.join(User).filter(User.team == team)
    if user_id:
        q = q.filter_by(user_id=int(user_id))
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    
    # 일자별 지각/결근/정상 카운트
    data = q.with_entities(
        Attendance.date,
        func.sum(func.case([(Attendance.reason.like('%지각%'), 1)], else_=0)).label('late'),
        func.sum(func.case([(Attendance.reason.like('%결근%'), 1)], else_=0)).label('absent'),
        func.count().label('total')
    ).group_by(Attendance.date).order_by(Attendance.date.asc()).all()
    
    result = {
        'labels': [d.strftime('%m-%d') for d, *_ in data],
        'late': [late for _, late, _, _ in data],
        'absent': [absent for _, _, absent, _ in data],
        'total': [total for _, _, _, total in data]
    }
    return jsonify(result)

@chart_api.route('/admin_dashboard/team_stats')
@login_required
def admin_dashboard_team_stats():
    """팀별 출결 통계 데이터 API"""
    if not current_user.is_admin() and not current_user.is_teamlead():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    q = Attendance.query.join(User)
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    
    # 팀별 지각/결근/정상 카운트
    data = q.with_entities(
        User.team,
        func.sum(func.case([(Attendance.reason.like('%지각%'), 1)], else_=0)).label('late'),
        func.sum(func.case([(Attendance.reason.like('%결근%'), 1)], else_=0)).label('absent'),
        func.count().label('total')
    ).group_by(User.team).all()
    
    result = {
        'labels': [team or '미지정' for team, *_ in data],
        'late': [late for _, late, _, _ in data],
        'absent': [absent for _, _, absent, _ in data],
        'total': [total for _, _, _, total in data]
    }
    return jsonify(result)

@chart_api.route('/admin_dashboard/reason_stats')
@login_required
def admin_dashboard_reason_stats():
    """사유별 출결 통계 데이터 API (파이 차트용)"""
    if not current_user.is_admin() and not current_user.is_teamlead():
        return jsonify({'error': '권한이 없습니다.'}), 403
    
    date_from = request.args.get('from')
    date_to = request.args.get('to')
    
    q = Attendance.query
    if date_from:
        q = q.filter(Attendance.date >= date_from)
    if date_to:
        q = q.filter(Attendance.date <= date_to)
    
    # 사유별 카운트 (상위 10개)
    data = q.with_entities(
        Attendance.reason,
        func.count().label('count')
    ).group_by(Attendance.reason).order_by(func.count().desc()).limit(10).all()
    
    result = {
        'labels': [reason or '사유 없음' for reason, _ in data],
        'data': [count for _, count in data]
    }
    return jsonify(result) 