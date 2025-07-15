from flask import Blueprint, request, jsonify, current_app
from functools import wraps
from models import Schedule, User, Attendance, db
from api.gateway import token_required, role_required
from datetime import datetime, timedelta
import json
from utils.role_required import role_required

schedule_management = Blueprint('schedule_management', __name__)

# 스케줄 생성
@schedule_management.route('/schedules', methods=['POST'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def create_schedule(current_user):
    """스케줄 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['user_id', 'date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'message': f'{field} 필드는 필수입니다'}), 400
        
        # 사용자 존재 확인
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'message': '존재하지 않는 사용자입니다'}), 404
        
        # 권한 확인
        if current_user.role != 'super_admin':
            if current_user.role == 'brand_manager' and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
            elif current_user.role == 'store_manager' and user.branch_id != current_user.branch_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        
        # 중복 스케줄 확인
        existing_schedule = Schedule.query.filter_by(
            user_id=data['user_id'],
            date=data['date']
        ).first()
        
        if existing_schedule:
            return jsonify({'message': '해당 날짜에 이미 스케줄이 존재합니다'}), 400
        
        # 스케줄 생성
        schedule = Schedule()
        schedule.user_id = data['user_id']
        schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        schedule.type = data.get('type', 'regular')
        schedule.memo = data.get('notes')
        schedule.manager_id = current_user.id
        
        db.session.add(schedule)
        db.session.commit()
        
        return jsonify({
            'message': '스케줄이 생성되었습니다',
            'schedule': {
                'id': schedule.id,
                'user_id': schedule.user_id,
                'date': schedule.date.isoformat(),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'type': schedule.type,
                'notes': schedule.notes
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Create schedule error: {str(e)}")
        return jsonify({'message': '스케줄 생성 중 오류가 발생했습니다'}), 500

# 스케줄 목록 조회
@schedule_management.route('/schedules', methods=['GET'])
@token_required
@role_required('admin', 'super_admin', 'brand_manager', 'store_manager', 'employee')
def get_schedules(current_user):
    """스케줄 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        schedule_type = request.args.get('type')
        
        query = Schedule.query
        # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 스케줄만 조회
        if current_user.role == 'brand_manager':
            query = query.filter(Schedule.brand_id == current_user.brand_id)
        # 슈퍼관리자는 전체 조회
        elif current_user.role == 'super_admin':
            pass
        # 일반 직원은 자신의 스케줄만 조회
        elif current_user.role == 'employee':
            query = query.filter(Schedule.user_id == current_user.id)
        # 매장 관리자는 자신의 매장 스케줄만 조회(기존 로직 유지)
        elif current_user.role == 'store_manager':
            query = query.join(User, Schedule.user_id == User.id).filter(User.branch_id == current_user.branch_id)
        # 사용자 필터
        if user_id:
            query = query.filter(Schedule.user_id == user_id)
        elif current_user.role not in ['super_admin', 'brand_manager', 'store_manager']:
            # 일반 직원은 자신의 스케줄만 조회
            query = query.filter(Schedule.user_id == current_user.id)
        elif current_user.role == 'brand_manager':
            # 브랜드 관리자는 자신의 브랜드 사용자 스케줄만 조회
            query = query.join(User, Schedule.user_id == User.id).filter(User.brand_id == current_user.brand_id)
        elif current_user.role == 'store_manager':
            # 매장 관리자는 자신의 매장 사용자 스케줄만 조회
            query = query.join(User, Schedule.user_id == User.id).filter(User.branch_id == current_user.branch_id)
        
        # 날짜 필터
        if start_date:
            query = query.filter(Schedule.date >= datetime.strptime(start_date, '%Y-%m-%d').date())
        if end_date:
            query = query.filter(Schedule.date <= datetime.strptime(end_date, '%Y-%m-%d').date())
        
        # 타입 필터
        if schedule_type:
            query = query.filter(Schedule.type == schedule_type)
        
        # 날짜순 정렬
        query = query.order_by(Schedule.date.desc(), Schedule.start_time)
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        schedules = []
        for schedule in pagination.items:
            user = User.query.get(schedule.user_id)
            schedules.append({
                'id': schedule.id,
                'user_id': schedule.user_id,
                'user_name': user.name if user else 'Unknown',
                'date': schedule.date.isoformat(),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'type': schedule.type,
                'notes': schedule.memo,
                'created_at': schedule.created_at.isoformat() if schedule.created_at else None
            })
        
        return jsonify({
            'schedules': schedules,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get schedules error: {str(e)}")
        return jsonify({'message': '스케줄 목록 조회 중 오류가 발생했습니다'}), 500

# 스케줄 상세 조회
@schedule_management.route('/schedules/<int:schedule_id>', methods=['GET'])
@token_required
def get_schedule(current_user, schedule_id):
    """스케줄 상세 조회"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        
        # 권한 확인
        if current_user.role not in ['super_admin', 'brand_manager', 'store_manager']:
            if schedule.user_id != current_user.id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        elif current_user.role == 'brand_manager':
            user = User.query.get(schedule.user_id)
            if user and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        elif current_user.role == 'store_manager':
            user = User.query.get(schedule.user_id)
            if user and user.branch_id != current_user.branch_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        
        user = User.query.get(schedule.user_id)
        
        return jsonify({
            'id': schedule.id,
            'user_id': schedule.user_id,
            'user_name': user.name if user else 'Unknown',
            'date': schedule.date.isoformat(),
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'type': schedule.type,
            'notes': schedule.memo,
            'created_at': schedule.created_at.isoformat() if schedule.created_at else None,
            'created_by': schedule.manager_id
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get schedule error: {str(e)}")
        return jsonify({'message': '스케줄 조회 중 오류가 발생했습니다'}), 500

# 스케줄 수정
@schedule_management.route('/schedules/<int:schedule_id>', methods=['PUT'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def update_schedule(current_user, schedule_id):
    """스케줄 수정"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        data = request.get_json()
        
        # 권한 확인
        if current_user.role == 'brand_manager':
            user = User.query.get(schedule.user_id)
            if user and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        elif current_user.role == 'store_manager':
            user = User.query.get(schedule.user_id)
            if user and user.store_id != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        
        # 수정 가능한 필드들
        if 'date' in data:
            schedule.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'start_time' in data:
            schedule.start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        if 'end_time' in data:
            schedule.end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        if 'type' in data:
            schedule.type = data['type']
        if 'notes' in data:
            schedule.notes = data['notes']
        
        db.session.commit()
        
        return jsonify({
            'message': '스케줄이 수정되었습니다',
            'schedule': {
                'id': schedule.id,
                'user_id': schedule.user_id,
                'date': schedule.date.isoformat(),
                'start_time': schedule.start_time.strftime('%H:%M'),
                'end_time': schedule.end_time.strftime('%H:%M'),
                'type': schedule.type,
                'notes': schedule.notes
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Update schedule error: {str(e)}")
        return jsonify({'message': '스케줄 수정 중 오류가 발생했습니다'}), 500

# 스케줄 삭제
@schedule_management.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@token_required
@role_required(['super_admin', 'brand_manager', 'store_manager'])
def delete_schedule(current_user, schedule_id):
    """스케줄 삭제"""
    try:
        schedule = Schedule.query.get_or_404(schedule_id)
        
        # 권한 확인
        if current_user.role == 'brand_manager':
            user = User.query.get(schedule.user_id)
            if user and user.brand_id != current_user.brand_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        elif current_user.role == 'store_manager':
            user = User.query.get(schedule.user_id)
            if user and user.store_id != current_user.store_id:
                return jsonify({'message': '접근 권한이 없습니다'}), 403
        
        db.session.delete(schedule)
        db.session.commit()
        
        return jsonify({'message': '스케줄이 삭제되었습니다'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Delete schedule error: {str(e)}")
        return jsonify({'message': '스케줄 삭제 중 오류가 발생했습니다'}), 500

# 스케줄 통계
@schedule_management.route('/schedules/stats', methods=['GET'])
@token_required
def get_schedule_stats(current_user):
    """스케줄 통계"""
    try:
        query = Schedule.query
        
        # 권한별 필터
        if current_user.role not in ['super_admin', 'brand_manager', 'store_manager']:
            query = query.filter(Schedule.user_id == current_user.id)
        elif current_user.role == 'brand_manager':
            query = query.join(User).filter(User.brand_id == current_user.brand_id)
        elif current_user.role == 'store_manager':
            query = query.join(User).filter(User.store_id == current_user.store_id)
        
        total_schedules = query.count()
        
        # 오늘 스케줄
        today = datetime.utcnow().date()
        today_schedules = query.filter(Schedule.date == today).count()
        
        # 이번 주 스케줄
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        week_schedules = query.filter(
            Schedule.date >= week_start,
            Schedule.date <= week_end
        ).count()
        
        # 타입별 통계
        type_stats = {}
        for schedule_type in ['regular', 'overtime', 'holiday', 'vacation']:
            count = query.filter(Schedule.type == schedule_type).count()
            type_stats[schedule_type] = count
        
        return jsonify({
            'total_schedules': total_schedules,
            'today_schedules': today_schedules,
            'week_schedules': week_schedules,
            'type_stats': type_stats
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Get schedule stats error: {str(e)}")
        return jsonify({'message': '스케줄 통계 조회 중 오류가 발생했습니다'}), 500 