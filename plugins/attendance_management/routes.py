"""
출근관리 플러그인 API 라우트
"""

from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, func
from extensions import db
from models_main import AttendanceRecord, AttendanceSettings
from plugins.attendance_management import attendance_bp

@attendance_bp.route('/check-in', methods=['POST'])
@login_required
def check_in():
    """출근 체크인"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 오늘 날짜의 출근 기록 확인
        today = datetime.now().date()
        existing_record = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.store_id == store_id,
                func.date(AttendanceRecord.date) == today
            )
        ).first()
        
        if existing_record and existing_record.check_in_time:
            return jsonify({'error': '이미 출근 처리되었습니다.'}), 400
        
        # 출근 설정 가져오기
        settings = AttendanceSettings.query.filter_by(store_id=store_id).first()
        if not settings:
            settings = AttendanceSettings(store_id=store_id)
            db.session.add(settings)
        
        # 출근 기록 생성 또는 업데이트
        if existing_record:
            record = existing_record
        else:
            record = AttendanceRecord(
                user_id=current_user.id,
                store_id=store_id,
                date=datetime.now()
            )
            db.session.add(record)
        
        record.check_in_time = datetime.now()
        
        # 지각 여부 확인
        work_start = datetime.strptime(settings.work_start_time, '%H:%M').time()
        current_time = datetime.now().time()
        
        if current_time > work_start and (current_time.hour * 60 + current_time.minute) - (work_start.hour * 60 + work_start.minute) > settings.late_threshold:
            record.status = 'late'
        else:
            record.status = 'present'
        
        db.session.commit()
        
        return jsonify({
            'message': '출근 처리되었습니다.',
            'check_in_time': record.check_in_time.isoformat(),
            'status': record.status
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"출근 체크인 오류: {str(e)}")
        return jsonify({'error': '출근 처리 중 오류가 발생했습니다.'}), 500

@attendance_bp.route('/check-out', methods=['POST'])
@login_required
def check_out():
    """퇴근 체크아웃"""
    try:
        data = request.get_json()
        store_id = data.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 오늘 날짜의 출근 기록 확인
        today = datetime.now().date()
        record = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.store_id == store_id,
                func.date(AttendanceRecord.date) == today
            )
        ).first()
        
        if not record or not record.check_in_time:
            return jsonify({'error': '출근 기록이 없습니다.'}), 400
        
        if record.check_out_time:
            return jsonify({'error': '이미 퇴근 처리되었습니다.'}), 400
        
        # 퇴근 시간 기록
        record.check_out_time = datetime.now()
        
        # 근무시간 계산
        work_hours = record.calculate_work_hours()
        
        # 출근 설정 가져오기
        settings = AttendanceSettings.query.filter_by(store_id=store_id).first()
        if settings:
            # 초과근무 계산
            if work_hours > settings.overtime_threshold:
                record.overtime_hours = work_hours - settings.overtime_threshold
            
            # 조퇴 여부 확인
            work_end = datetime.strptime(settings.work_end_time, '%H:%M').time()
            check_out_time = record.check_out_time.time()
            
            if check_out_time < work_end and (work_end.hour * 60 + work_end.minute) - (check_out_time.hour * 60 + check_out_time.minute) > settings.early_leave_threshold:
                record.status = 'early_leave'
        
        db.session.commit()
        
        return jsonify({
            'message': '퇴근 처리되었습니다.',
            'check_out_time': record.check_out_time.isoformat(),
            'work_hours': work_hours,
            'overtime_hours': record.overtime_hours
        }), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"퇴근 체크아웃 오류: {str(e)}")
        return jsonify({'error': '퇴근 처리 중 오류가 발생했습니다.'}), 500

@attendance_bp.route('/status', methods=['GET'])
@login_required
def get_attendance_status():
    """오늘 출근 상태 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 오늘 날짜의 출근 기록 확인
        today = datetime.now().date()
        record = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.store_id == store_id,
                func.date(AttendanceRecord.date) == today
            )
        ).first()
        
        if not record:
            return jsonify({
                'status': 'not_checked_in',
                'message': '출근하지 않았습니다.'
            }), 200
        
        return jsonify({
            'status': record.status,
            'check_in_time': record.check_in_time.isoformat() if record.check_in_time else None,
            'check_out_time': record.check_out_time.isoformat() if record.check_out_time else None,
            'work_hours': record.work_hours,
            'overtime_hours': record.overtime_hours
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"출근 상태 조회 오류: {str(e)}")
        return jsonify({'error': '출근 상태 조회 중 오류가 발생했습니다.'}), 500

@attendance_bp.route('/history', methods=['GET'])
@login_required
def get_attendance_history():
    """출근 기록 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        # 날짜 범위 설정
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        
        if not end_date:
            end_date = datetime.now().date()
        else:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # 출근 기록 조회
        records = AttendanceRecord.query.filter(
            and_(
                AttendanceRecord.user_id == current_user.id,
                AttendanceRecord.store_id == store_id,
                func.date(AttendanceRecord.date) >= start_date,
                func.date(AttendanceRecord.date) <= end_date
            )
        ).order_by(AttendanceRecord.date.desc()).all()
        
        history = []
        for record in records:
            history.append({
                'id': record.id,
                'date': record.date.strftime('%Y-%m-%d'),
                'check_in_time': record.check_in_time.isoformat() if record.check_in_time else None,
                'check_out_time': record.check_out_time.isoformat() if record.check_out_time else None,
                'work_hours': record.work_hours,
                'overtime_hours': record.overtime_hours,
                'status': record.status,
                'notes': record.notes
            })
        
        return jsonify({
            'history': history,
            'total_records': len(history)
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"출근 기록 조회 오류: {str(e)}")
        return jsonify({'error': '출근 기록 조회 중 오류가 발생했습니다.'}), 500

@attendance_bp.route('/settings', methods=['GET'])
@login_required
def get_attendance_settings():
    """출근 설정 조회"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        settings = AttendanceSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            return jsonify({'error': '출근 설정이 없습니다.'}), 404
        
        return jsonify({
            'work_start_time': settings.work_start_time,
            'work_end_time': settings.work_end_time,
            'break_time': settings.break_time,
            'overtime_threshold': settings.overtime_threshold,
            'late_threshold': settings.late_threshold,
            'early_leave_threshold': settings.early_leave_threshold,
            'flexible_work': settings.flexible_work
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"출근 설정 조회 오류: {str(e)}")
        return jsonify({'error': '출근 설정 조회 중 오류가 발생했습니다.'}), 500

@attendance_bp.route('/settings', methods=['PUT'])
@login_required
def update_attendance_settings():
    """출근 설정 업데이트"""
    try:
        store_id = request.args.get('store_id', current_user.store_id if hasattr(current_user, 'store_id') else None)
        
        if not store_id:
            return jsonify({'error': '매장 ID가 필요합니다.'}), 400
        
        data = request.get_json()
        settings = AttendanceSettings.query.filter_by(store_id=store_id).first()
        
        if not settings:
            settings = AttendanceSettings(store_id=store_id)
            db.session.add(settings)
        
        # 설정 업데이트
        if 'work_start_time' in data:
            settings.work_start_time = data['work_start_time']
        if 'work_end_time' in data:
            settings.work_end_time = data['work_end_time']
        if 'break_time' in data:
            settings.break_time = data['break_time']
        if 'overtime_threshold' in data:
            settings.overtime_threshold = data['overtime_threshold']
        if 'late_threshold' in data:
            settings.late_threshold = data['late_threshold']
        if 'early_leave_threshold' in data:
            settings.early_leave_threshold = data['early_leave_threshold']
        if 'flexible_work' in data:
            settings.flexible_work = data['flexible_work']
        
        db.session.commit()
        
        return jsonify({'message': '출근 설정이 업데이트되었습니다.'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"출근 설정 업데이트 오류: {str(e)}")
        return jsonify({'error': '출근 설정 업데이트 중 오류가 발생했습니다.'}), 500 