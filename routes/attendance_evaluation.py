from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
from models import (
    AttendanceEvaluation, AttendanceReport, Excuse, ExcuseResponse, 
    User, Notification, db
)
from datetime import datetime, date, timedelta
from sqlalchemy import extract, func, and_
from flask_login import login_required, current_user
from functools import wraps
from utils.notification_automation import send_notification

evaluation_bp = Blueprint('evaluation', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "관리자 권한이 필요합니다"}), 403
        return f(*args, **kwargs)
    return decorated_function

def manager_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_admin or current_user.is_manager):
            return jsonify({"error": "관리자 또는 매니저 권한이 필요합니다"}), 403
        return f(*args, **kwargs)
    return decorated_function

@evaluation_bp.route('/staff/<int:user_id>/attendance_report/eval', methods=['POST'])
@login_required
@manager_required
def eval_attendance(user_id):
    """근태 평가 저장 및 등급별 경고/알림"""
    try:
        # 평가 입력/저장 로직(점수, 등급 등)
        score = int(request.form.get('score', 0))
        grade = request.form.get('grade')
        comment = request.form.get('comment', '')
        period_from = datetime.strptime(request.form.get('period_from'), '%Y-%m-%d').date()
        period_to = datetime.strptime(request.form.get('period_to'), '%Y-%m-%d').date()
        
        # 기존 평가 확인
        existing_report = AttendanceReport.query.filter(
            and_(
                AttendanceReport.user_id == user_id,
                AttendanceReport.period_from == period_from,
                AttendanceReport.period_to == period_to
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
            report = AttendanceReport(
                user_id=user_id,
                period_from=period_from,
                period_to=period_to,
                score=score,
                grade=grade,
                comment=comment,
                created_by=current_user.id
            )
            db.session.add(report)
        
        db.session.commit()
        
        # 등급별 경고/알림/소명 요청
        warning_sent = False
        if grade in ('D', 'F') or score < 70:
            warning_sent = True
            # 경고 알림 발송
            send_notification(
                user_id=user_id,
                content=f"최근 근태평가 등급이 '{grade}'(점수: {score}점)입니다. 소명서를 제출해주세요.",
                category="근태경고",
                priority="중요",
                link=url_for('evaluation.submit_excuse', user_id=user_id)
            )
            
            # 관리자에게도 알림
            admins = User.query.filter(User.role == 'admin').all()
            for admin in admins:
                send_notification(
                    user_id=admin.id,
                    content=f"{report.user.name or report.user.username}님의 근태평가 등급이 '{grade}'로 경고 상태입니다.",
                    category="근태관리",
                    priority="중요",
                    link=url_for('evaluation.admin_excuse_list')
                )
        
        flash('평가 결과가 저장되었습니다.' + (' 경고 알림이 발송되었습니다.' if warning_sent else ''), 'success')
        return redirect(url_for('evaluation.staff_attendance_report', user_id=user_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'평가 저장 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('evaluation.staff_attendance_report', user_id=user_id))

@evaluation_bp.route('/staff/<int:user_id>/attendance_report')
@login_required
def staff_attendance_report(user_id):
    """직원 근태 리포트 페이지"""
    user = User.query.get_or_404(user_id)
    
    # 최근 평가 조회
    recent_reports = AttendanceReport.query.filter(
        AttendanceReport.user_id == user_id
    ).order_by(AttendanceReport.created_at.desc()).limit(5).all()
    
    # 소명 요청 조회
    pending_excuses = Excuse.query.filter(
        and_(
            Excuse.user_id == user_id,
            Excuse.status == 'pending'
        )
    ).order_by(Excuse.created_at.desc()).all()
    
    return render_template('attendance/staff_attendance_report.html',
                         user=user,
                         recent_reports=recent_reports,
                         pending_excuses=pending_excuses)

@evaluation_bp.route('/staff/<int:user_id>/attendance_excuse', methods=['GET', 'POST'])
@login_required
def submit_excuse(user_id):
    """소명(이의제기) 제출 폼"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            title = request.form.get('title', '').strip()
            content = request.form.get('content', '').strip()
            category = request.form.get('category', '근태평가')
            priority = request.form.get('priority', '일반')
            
            if not title or not content:
                flash('제목과 내용을 모두 입력해주세요.', 'error')
                return render_template('attendance/attendance_excuse_form.html', user=user)
            
            # 소명서 생성
            excuse = Excuse(
                user_id=user_id,
                title=title,
                content=content,
                category=category,
                priority=priority
            )
            db.session.add(excuse)
            db.session.commit()
            
            # 관리자에게 알림
            admins = User.query.filter(User.role == 'admin').all()
            for admin in admins:
                send_notification(
                    user_id=admin.id,
                    content=f"{user.name or user.username}님이 소명서를 제출했습니다: {title}",
                    category="소명관리",
                    priority="중요" if priority == "긴급" else "일반",
                    link=url_for('evaluation.admin_excuse_list')
                )
            
            flash('소명서가 제출되었습니다.', 'success')
            return redirect(url_for('evaluation.staff_attendance_report', user_id=user_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'소명서 제출 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return render_template('attendance/attendance_excuse_form.html', user=user)

@evaluation_bp.route('/admin/attendance_excuses')
@login_required
@admin_required
def admin_excuse_list():
    """관리자 소명 목록 및 검토 화면"""
    # 필터링 옵션
    status = request.args.get('status', 'all')
    priority = request.args.get('priority', 'all')
    category = request.args.get('category', 'all')
    
    # 쿼리 구성
    query = db.session.query(Excuse).join(User, Excuse.user_id == User.id)
    
    if status != 'all':
        query = query.filter(Excuse.status == status)
    if priority != 'all':
        query = query.filter(Excuse.priority == priority)
    if category != 'all':
        query = query.filter(Excuse.category == category)
    
    excuses = query.order_by(Excuse.created_at.desc()).all()
    
    # 통계
    stats = {
        'total': len(excuses),
        'pending': len([e for e in excuses if e.status == 'pending']),
        'reviewed': len([e for e in excuses if e.status == 'reviewed']),
        'accepted': len([e for e in excuses if e.status == 'accepted']),
        'rejected': len([e for e in excuses if e.status == 'rejected'])
    }
    
    return render_template('admin/excuse_list.html',
                         excuses=excuses,
                         stats=stats,
                         current_status=status,
                         current_priority=priority,
                         current_category=category)

@evaluation_bp.route('/admin/excuse/<int:excuse_id>')
@login_required
@admin_required
def admin_excuse_detail(excuse_id):
    """소명 상세 보기"""
    excuse = Excuse.query.get_or_404(excuse_id)
    responses = ExcuseResponse.query.filter(
        ExcuseResponse.excuse_id == excuse_id
    ).order_by(ExcuseResponse.created_at).all()
    
    return render_template('admin/excuse_detail.html',
                         excuse=excuse,
                         responses=responses)

@evaluation_bp.route('/admin/excuse/<int:excuse_id>/review', methods=['POST'])
@login_required
@admin_required
def review_excuse(excuse_id):
    """소명 검토 및 답변"""
    try:
        excuse = Excuse.query.get_or_404(excuse_id)
        action = request.form.get('action')  # accept/reject
        admin_comment = request.form.get('admin_comment', '').strip()
        response_content = request.form.get('response_content', '').strip()
        
        if action not in ['accept', 'reject']:
            flash('잘못된 액션입니다.', 'error')
            return redirect(url_for('evaluation.admin_excuse_detail', excuse_id=excuse_id))
        
        # 소명 상태 업데이트
        excuse.status = 'accepted' if action == 'accept' else 'rejected'
        excuse.reviewed_at = datetime.utcnow()
        excuse.reviewed_by = current_user.id
        excuse.admin_comment = admin_comment
        
        # 답변 추가
        if response_content:
            response = ExcuseResponse(
                excuse_id=excuse_id,
                responder_id=current_user.id,
                content=response_content,
                response_type='decision'
            )
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
            link=url_for('evaluation.staff_attendance_report', user_id=excuse.user_id)
        )
        
        flash(f'소명서가 {"승인" if action == "accept" else "거절"}되었습니다.', 'success')
        return redirect(url_for('evaluation.admin_excuse_list'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'소명 검토 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('evaluation.admin_excuse_detail', excuse_id=excuse_id))

@evaluation_bp.route('/admin/excuse/<int:excuse_id>/response', methods=['POST'])
@login_required
@admin_required
def add_excuse_response(excuse_id):
    """소명에 답변 추가"""
    try:
        content = request.form.get('content', '').strip()
        response_type = request.form.get('response_type', 'comment')
        
        if not content:
            flash('답변 내용을 입력해주세요.', 'error')
            return redirect(url_for('evaluation.admin_excuse_detail', excuse_id=excuse_id))
        
        response = ExcuseResponse(
            excuse_id=excuse_id,
            responder_id=current_user.id,
            content=content,
            response_type=response_type
        )
        db.session.add(response)
        db.session.commit()
        
        # 사용자에게 알림
        excuse = Excuse.query.get(excuse_id)
        send_notification(
            user_id=excuse.user_id,
            content=f"소명서 '{excuse.title}'에 관리자 답변이 추가되었습니다.",
            category="소명답변",
            link=url_for('evaluation.staff_attendance_report', user_id=excuse.user_id)
        )
        
        flash('답변이 추가되었습니다.', 'success')
        return redirect(url_for('evaluation.admin_excuse_detail', excuse_id=excuse_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'답변 추가 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('evaluation.admin_excuse_detail', excuse_id=excuse_id))

@evaluation_bp.route('/api/attendance_evaluation_stats')
@login_required
@admin_required
def attendance_evaluation_stats():
    """근태 평가 통계 API"""
    try:
        year = request.args.get('year', type=int) or datetime.now().year
        month = request.args.get('month', type=int)
        
        # 평가 데이터 조회
        query = db.session.query(AttendanceReport)
        
        if month:
            query = query.filter(
                and_(
                    extract('year', AttendanceReport.created_at) == year,
                    extract('month', AttendanceReport.created_at) == month
                )
            )
        else:
            query = query.filter(extract('year', AttendanceReport.created_at) == year)
        
        reports = query.all()
        
        # 통계 계산
        grade_stats = {}
        score_ranges = {'90-100': 0, '80-89': 0, '70-79': 0, '60-69': 0, '0-59': 0}
        warning_count = 0
        
        for report in reports:
            # 등급별 통계
            grade = report.grade
            if grade not in grade_stats:
                grade_stats[grade] = 0
            grade_stats[grade] += 1
            
            # 점수 범위별 통계
            score = report.score
            if score >= 90:
                score_ranges['90-100'] += 1
            elif score >= 80:
                score_ranges['80-89'] += 1
            elif score >= 70:
                score_ranges['70-79'] += 1
            elif score >= 60:
                score_ranges['60-69'] += 1
            else:
                score_ranges['0-59'] += 1
            
            # 경고 통계
            if report.grade in ('D', 'F') or report.score < 70:
                warning_count += 1
        
        return jsonify({
            "success": True,
            "stats": {
                "total_reports": len(reports),
                "grade_stats": grade_stats,
                "score_ranges": score_ranges,
                "warning_count": warning_count,
                "avg_score": sum(r.score for r in reports) / len(reports) if reports else 0
            }
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500 