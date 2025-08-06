"""
스케줄관리 플러그인 API 라우트
"""

from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, func
from extensions import db
from models_main import User
from .models import WorkSchedule, ScheduleTemplate, ScheduleRequest, ScheduleSettings, ScheduleStatus, RequestStatus
from plugins.schedule_management import schedule_bp

@schedule_bp.route('/schedules', methods=['GET'])
# @login_required  # 임시로 주석 처리
def get_schedules():
    """근무 스케줄 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        status = request.args.get('status')
        
        if not store_id:
            # 테스트용으로 기본 매장 ID 사용
            store_id = 1
        
        query = WorkSchedule.query.filter_by(store_id=store_id)
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if start_date:
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            query = query.filter(WorkSchedule.schedule_date >= start_datetime)
        
        if end_date:
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            query = query.filter(WorkSchedule.schedule_date <= end_datetime)
        
        if status:
            query = query.filter(WorkSchedule.status == ScheduleStatus(status))
        
        schedules = query.order_by(WorkSchedule.schedule_date, WorkSchedule.start_time).all()
        
        schedule_list = []
        for schedule in schedules:
            schedule_list.append({
                'id': schedule.id,
                'user_name': schedule.user.username,
                'schedule_date': schedule.schedule_date.strftime('%Y-%m-%d'),
                'shift_type': schedule.shift_type.value,
                'start_time': schedule.start_time,
                'end_time': schedule.end_time,
                'break_start': schedule.break_start,
                'break_end': schedule.break_end,
                'total_hours': schedule.total_hours,
                'status': schedule.status.value,
                'notes': schedule.notes,
                'created_by': schedule.created_user.username
            })
        
        return jsonify({
            'schedules': schedule_list,
            'total_count': len(schedule_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"근무 스케줄 목록 조회 오류: {str(e)}")
        return jsonify({'error': '근무 스케줄 목록 조회 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/schedules', methods=['POST'])
@login_required
def create_schedule():
    """근무 스케줄 생성"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        if not data.get('user_id'):
            return jsonify({'error': '직원 ID가 필요합니다.'}), 400
        
        if not data.get('schedule_date'):
            return jsonify({'error': '스케줄 날짜가 필요합니다.'}), 400
        
        if not data.get('start_time') or not data.get('end_time'):
            return jsonify({'error': '시작시간과 종료시간이 필요합니다.'}), 400
        
        # 스케줄 날짜 파싱
        schedule_date = datetime.strptime(data['schedule_date'], '%Y-%m-%d')
        
        # 기존 스케줄 확인
        existing_schedule = WorkSchedule.query.filter(
            and_(
                WorkSchedule.store_id == store_id,
                WorkSchedule.user_id == data['user_id'],
                func.date(WorkSchedule.schedule_date) == schedule_date.date()
            )
        ).first()
        
        if existing_schedule:
            return jsonify({'error': '해당 날짜에 이미 스케줄이 있습니다.'}), 400
        
        # 스케줄 생성
        schedule = WorkSchedule(
            store_id=store_id,
            user_id=data['user_id'],
            schedule_date=schedule_date,
            shift_type=ShiftType(data.get('shift_type', 'full_day')),
            start_time=data['start_time'],
            end_time=data['end_time'],
            break_start=data.get('break_start'),
            break_end=data.get('break_end'),
            notes=data.get('notes'),
            created_by=current_user.id
        )
        
        # 근무시간 계산
        schedule.calculate_hours()
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': '근무 스케줄이 생성되었습니다.',
            'schedule_id': schedule.id,
            'total_hours': schedule.total_hours
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"근무 스케줄 생성 오류: {str(e)}")
        return jsonify({'error': '근무 스케줄 생성 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@login_required
def update_schedule(schedule_id):
    """근무 스케줄 수정"""
    try:
        data = request.get_json()
        schedule = WorkSchedule.query.get_or_404(schedule_id)
        
        # 수정 가능한 필드들
        updatable_fields = [
            'shift_type', 'start_time', 'end_time', 'break_start', 
            'break_end', 'notes', 'status'
        ]
        
        for field in updatable_fields:
            if field in data:
                if field == 'shift_type':
                    setattr(schedule, field, ShiftType(data[field]))
                elif field == 'status':
                    setattr(schedule, field, ScheduleStatus(data[field]))
                else:
                    setattr(schedule, field, data[field])
        
        # 근무시간 재계산
        schedule.calculate_hours()
        
        db.session.commit()
        
        return jsonify({'message': '근무 스케줄이 수정되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"근무 스케줄 수정 오류: {str(e)}")
        return jsonify({'error': '근무 스케줄 수정 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@login_required
def delete_schedule(schedule_id):
    """근무 스케줄 삭제"""
    try:
        schedule = WorkSchedule.query.get_or_404(schedule_id)
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'message': '근무 스케줄이 삭제되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"근무 스케줄 삭제 오류: {str(e)}")
        return jsonify({'error': '근무 스케줄 삭제 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/templates', methods=['GET'])
# @login_required  # 임시로 주석 처리
def get_schedule_templates():
    """스케줄 템플릿 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        templates = ScheduleTemplate.query.filter_by(store_id=store_id, is_active=True).order_by(ScheduleTemplate.name).all()
        
        template_list = []
        for template in templates:
            template_list.append({
                'id': template.id,
                'name': template.name,
                'description': template.description,
                'shift_type': template.shift_type.value,
                'start_time': template.start_time,
                'end_time': template.end_time,
                'break_start': template.break_start,
                'break_end': template.break_end
            })
        
        return jsonify({
            'templates': template_list,
            'total_count': len(template_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"스케줄 템플릿 목록 조회 오류: {str(e)}")
        return jsonify({'error': '스케줄 템플릿 목록 조회 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/templates', methods=['POST'])
@login_required
def create_schedule_template():
    """스케줄 템플릿 생성"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        if not data.get('name'):
            return jsonify({'error': '템플릿명이 필요합니다.'}), 400
        
        if not data.get('start_time') or not data.get('end_time'):
            return jsonify({'error': '시작시간과 종료시간이 필요합니다.'}), 400
        
        template = ScheduleTemplate(
            store_id=store_id,
            name=data['name'],
            description=data.get('description'),
            shift_type=ShiftType(data.get('shift_type', 'full_day')),
            start_time=data['start_time'],
            end_time=data['end_time'],
            break_start=data.get('break_start'),
            break_end=data.get('break_end')
        )
        
        db.session.add(template)
        db.session.commit()
        
        return jsonify({
            'message': '스케줄 템플릿이 생성되었습니다.',
            'template_id': template.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"스케줄 템플릿 생성 오류: {str(e)}")
        return jsonify({'error': '스케줄 템플릿 생성 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/requests', methods=['GET'])
@login_required
def get_schedule_requests():
    """스케줄 변경 요청 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        status = request.args.get('status')
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        query = ScheduleRequest.query.join(WorkSchedule).filter(
            WorkSchedule.store_id == store_id
        )
        
        if status:
            query = query.filter(ScheduleRequest.status == RequestStatus(status))
        
        requests = query.order_by(ScheduleRequest.created_at.desc()).all()
        
        request_list = []
        for req in requests:
            request_list.append({
                'id': req.id,
                'user_name': req.user.username,
                'request_type': req.request_type,
                'requested_date': req.requested_date.strftime('%Y-%m-%d'),
                'requested_start_time': req.requested_start_time,
                'requested_end_time': req.requested_end_time,
                'reason': req.reason,
                'status': req.status.value,
                'approved_by': req.approved_user.username if req.approved_user else None,
                'rejection_reason': req.rejection_reason,
                'created_at': req.created_at.isoformat()
            })
        
        return jsonify({
            'requests': request_list,
            'total_count': len(request_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"스케줄 변경 요청 목록 조회 오류: {str(e)}")
        return jsonify({'error': '스케줄 변경 요청 목록 조회 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/requests', methods=['POST'])
@login_required
def create_schedule_request():
    """스케줄 변경 요청 생성"""
    try:
        data = request.get_json()
        schedule_id = data.get('schedule_id')
        request_type = data.get('request_type')
        reason = data.get('reason')
        
        if not all([schedule_id, request_type, reason]):
            return jsonify({'error': 'schedule_id, request_type, reason가 필요합니다.'}), 400
        
        # 스케줄 확인
        schedule = WorkSchedule.query.get_or_404(schedule_id)
        
        # 요청 생성
        request_obj = ScheduleRequest(
            user_id=current_user.id,
            schedule_id=schedule_id,
            request_type=request_type,
            requested_date=datetime.strptime(data['requested_date'], '%Y-%m-%d') if data.get('requested_date') else schedule.schedule_date,
            requested_start_time=data.get('requested_start_time'),
            requested_end_time=data.get('requested_end_time'),
            reason=reason
        )
        
        db.session.add(request_obj)
        db.session.commit()
        
        return jsonify({
            'message': '스케줄 변경 요청이 생성되었습니다.',
            'request_id': request_obj.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"스케줄 변경 요청 생성 오류: {str(e)}")
        return jsonify({'error': '스케줄 변경 요청 생성 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@login_required
def approve_schedule_request(request_id):
    """스케줄 변경 요청 승인"""
    try:
        request_obj = ScheduleRequest.query.get_or_404(request_id)
        
        if request_obj.status != RequestStatus.PENDING:
            return jsonify({'error': '대기 상태의 요청만 승인할 수 있습니다.'}), 400
        
        request_obj.status = RequestStatus.APPROVED
        request_obj.approved_by = current_user.id
        request_obj.approved_at = datetime.now()
        
        # 스케줄 업데이트
        schedule = request_obj.schedule
        if request_obj.requested_start_time:
            schedule.start_time = request_obj.requested_start_time
        if request_obj.requested_end_time:
            schedule.end_time = request_obj.requested_end_time
        if request_obj.requested_date:
            schedule.schedule_date = request_obj.requested_date
        
        schedule.calculate_hours()
        
        db.session.commit()
        
        return jsonify({'message': '스케줄 변경 요청이 승인되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"스케줄 변경 요청 승인 오류: {str(e)}")
        return jsonify({'error': '스케줄 변경 요청 승인 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_schedule_request(request_id):
    """스케줄 변경 요청 거절"""
    try:
        data = request.get_json()
        request_obj = ScheduleRequest.query.get_or_404(request_id)
        
        if request_obj.status != RequestStatus.PENDING:
            return jsonify({'error': '대기 상태의 요청만 거절할 수 있습니다.'}), 400
        
        request_obj.status = RequestStatus.REJECTED
        request_obj.approved_by = current_user.id
        request_obj.approved_at = datetime.now()
        request_obj.rejection_reason = data.get('rejection_reason', '')
        
        db.session.commit()
        
        return jsonify({'message': '스케줄 변경 요청이 거절되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"스케줄 변경 요청 거절 오류: {str(e)}")
        return jsonify({'error': '스케줄 변경 요청 거절 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/settings', methods=['GET'])
@login_required
def get_schedule_settings():
    """스케줄 관리 설정 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        settings = ScheduleSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            return jsonify({'error': '스케줄 관리 설정이 없습니다.'}), 404
        
        return jsonify({
            'default_shift_hours': settings.default_shift_hours,
            'break_time_minutes': settings.break_time_minutes,
            'overtime_threshold': settings.overtime_threshold,
            'auto_schedule_enabled': settings.auto_schedule_enabled,
            'max_consecutive_days': settings.max_consecutive_days,
            'min_rest_hours': settings.min_rest_hours,
            'schedule_publish_days': settings.schedule_publish_days
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"스케줄 설정 조회 오류: {str(e)}")
        return jsonify({'error': '스케줄 설정 조회 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/settings', methods=['PUT'])
@login_required
def update_schedule_settings():
    """스케줄 관리 설정 업데이트"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        data = request.get_json()
        settings = ScheduleSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            settings = ScheduleSettings(store_id=store_id)
            db.session.add(settings)
        
        # 설정 업데이트
        updatable_fields = [
            'default_shift_hours', 'break_time_minutes', 'overtime_threshold',
            'auto_schedule_enabled', 'max_consecutive_days', 'min_rest_hours',
            'schedule_publish_days'
        ]
        
        for field in updatable_fields:
            if field in data:
                setattr(settings, field, data[field])
        
        db.session.commit()
        
        return jsonify({'message': '스케줄 관리 설정이 업데이트되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"스케줄 설정 업데이트 오류: {str(e)}")
        return jsonify({'error': '스케줄 설정 업데이트 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/stats', methods=['GET'])
# @login_required  # 임시로 주석 처리
def get_schedule_stats():
    """스케줄 통계 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # 오늘 근무 중인 직원 수
        today_schedules = WorkSchedule.query.filter(
            and_(
                WorkSchedule.store_id == store_id,
                func.date(WorkSchedule.schedule_date) == today,
                WorkSchedule.status.in_([ScheduleStatus.PUBLISHED, ScheduleStatus.CONFIRMED])
            )
        ).count()
        
        # 오늘 총 근무 시간
        today_hours = db.session.query(func.sum(WorkSchedule.total_hours)).filter(
            and_(
                WorkSchedule.store_id == store_id,
                func.date(WorkSchedule.schedule_date) == today,
                WorkSchedule.status.in_([ScheduleStatus.PUBLISHED, ScheduleStatus.CONFIRMED])
            )
        ).scalar() or 0
        
        # 출근 완료한 직원 수 (임시로 오늘 스케줄이 있는 직원 수로 계산)
        completed_checkins = today_schedules
        
        # 이번 주 스케줄 수
        weekly_schedules = WorkSchedule.query.filter(
            and_(
                WorkSchedule.store_id == store_id,
                WorkSchedule.schedule_date >= week_start,
                WorkSchedule.schedule_date <= week_end
            )
        ).count()
        
        return jsonify({
            'todayWorking': today_schedules,
            'totalHours': round(today_hours, 1),
            'completedCheckins': completed_checkins,
            'weeklySchedules': weekly_schedules
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"스케줄 통계 조회 오류: {str(e)}")
        return jsonify({'error': '스케줄 통계 조회 중 오류가 발생했습니다.'}), 500

@schedule_bp.route('/employees', methods=['GET'])
# @login_required  # 임시로 주석 처리
def get_employees():
    """직원 목록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 해당 매장의 직원들 조회
        employees = User.query.filter_by(branch_id=store_id, status='approved').all()
        
        employee_list = []
        for employee in employees:
            employee_list.append({
                'id': employee.id,
                'username': employee.username,
                'role': employee.role,
                'position': employee.position,
                'department': employee.department
            })
        
        return jsonify({
            'employees': employee_list,
            'total_count': len(employee_list)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '직원 목록 조회 중 오류가 발생했습니다.'}), 500