from typing import Optional
from extensions import db
from models_main import User, Brand, Branch, SystemLog, db
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, time
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
출퇴근 관리 모듈
직원별 출근/퇴근/지각/초과근무 기록, 통계, 알림 관리
"""


logger = logging.getLogger(__name__)

attendance_management_bp = Blueprint('attendance_management', __name__, url_prefix='/api/attendance')

# 메모리 기반 임시 저장소 (실제로는 DB 테이블 사용)
attendance_records = {}
attendance_settings = {}
attendance_notifications = {}


class AttendanceRecord:
    """출퇴근 기록 클래스"""

    def __init__(self, user_id: int, date: str, clock_in: Optional[str] = None,
                 clock_out: str = None, work_type: str = "정규",
                 note: str = "", is_late: bool = False,
                 is_early_leave: bool = False, overtime_hours: float = 0.0):
        self.id = f"{user_id}_{date}"
        self.user_id = user_id
        self.date = date
        self.clock_in = clock_in
        self.clock_out = clock_out
        self.work_type = work_type
        self.note = note
        self.is_late = is_late
        self.is_early_leave = is_early_leave
        self.overtime_hours = overtime_hours
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any] if Dict is not None else None:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'date': self.date,
            'clock_in': self.clock_in,
            'clock_out': self.clock_out,
            'work_type': self.work_type,
            'note': self.note,
            'is_late': self.is_late,
            'is_early_leave': self.is_early_leave,
            'overtime_hours': self.overtime_hours,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class AttendanceSettings:
    """출퇴근 설정 클래스"""

    def __init__(self,  brand_id: int, date=None):
        self.brand_id = brand_id
        self.branch_id = branch_id
        self.work_start_time = "09:00"
        self.work_end_time = "18:00"
        self.late_threshold_minutes = 10
        self.overtime_threshold_hours = 8
        self.auto_notification = True
        self.notification_interval = 5  # 분
        self.work_types = ["정규", "시급", "파트타임", "인턴"]
        self.is_active = True

    def to_dict(self) -> Dict[str, Any] if Dict is not None else None:
        return {
            'brand_id': self.brand_id,
            'branch_id': self.branch_id,
            'work_start_time': self.work_start_time,
            'work_end_time': self.work_end_time,
            'late_threshold_minutes': self.late_threshold_minutes,
            'overtime_threshold_hours': self.overtime_threshold_hours,
            'auto_notification': self.auto_notification,
            'notification_interval': self.notification_interval,
            'work_types': self.work_types,
            'is_active': self.is_active
        }


def get_user_hierarchy() -> Dict[str, Any]:
    """사용자 계층 정보 반환"""
    user = User.query.get(current_user.id)
    if not user:
        return None

    brand = Brand.query.get(user.brand_id) if user.brand_id else None
    branch = Branch.query.get(user.branch_id) if user.branch_id else None

    return {
        'user_id': user.id,
        'brand_id': user.brand_id,
        'branch_id': user.branch_id,
        'role': user.role,
        'brand_name': brand.name if brand else None,
        'branch_name': branch.name if branch else None
    }


def can_manage_attendance(target_user_id: int) -> bool:
    """출퇴근 관리 권한 확인"""
    hierarchy = get_user_hierarchy()
    if not hierarchy:
        return False

    # 관리자는 모든 직원 관리 가능
    if hierarchy['role'] in ['admin', 'brand_manager', 'branch_manager']:
        return True

    # 일반 직원은 본인만 관리 가능
    return current_user.id == target_user_id


def get_attendance_settings(brand_id: int, branch_id: Optional[int] = None) -> AttendanceSettings:
    """출퇴근 설정 조회"""
    key = f"{brand_id}_{branch_id}" if branch_id else f"{brand_id}_global"

    if key not in attendance_settings:
        # 기본 설정 생성
        settings = AttendanceSettings(brand_id, branch_id)
        attendance_settings[key] = settings

    return attendance_settings[key]


def calculate_work_hours(clock_in: str, clock_out: str) -> float:
    """근무 시간 계산"""
    try:
        start = datetime.strptime(clock_in, "%H:%M")
        end = datetime.strptime(clock_out, "%H:%M")

        # 날짜가 다른 경우 처리
        if end < start:
            end += timedelta(days=1)

        diff = end - start
        return diff.total_seconds() / 3600  # 시간 단위
    except:
        return 0.0


def check_late_status(clock_in: str, settings: AttendanceSettings) -> bool:
    """지각 여부 확인"""
    try:
        actual_time = datetime.strptime(clock_in, "%H:%M")
        expected_time = datetime.strptime(settings.work_start_time, "%H:%M")

        diff = actual_time - expected_time
        return diff.total_seconds() / 60 > settings.late_threshold_minutes
    except:
        return False


def check_early_leave_status(clock_out: str, settings: AttendanceSettings) -> bool:
    """조퇴 여부 확인"""
    try:
        actual_time = datetime.strptime(clock_out, "%H:%M")
        expected_time = datetime.strptime(settings.work_end_time, "%H:%M")

        return actual_time < expected_time
    except:
        return False


def calculate_overtime_hours(work_hours: float, settings: AttendanceSettings) -> float:
    """초과근무 시간 계산"""
    overtime = work_hours - settings.overtime_threshold_hours
    return max(0, overtime)


def create_notification(user_id: int, type: str, message: str):
    """알림 생성"""
    notification = {
        'id': f"{user_id}_{datetime.now().isoformat()}",
        'user_id': user_id,
        'type': type,
        'message': message,
        'created_at': datetime.now().isoformat(),
        'is_read': False
    }

    if user_id not in attendance_notifications:
        attendance_notifications[user_id] = []

    attendance_notifications[user_id].append(notification)

    # 시스템 로그 기록
    log = SystemLog()
    log.user_id = current_user.id  # pyright: ignore
    log.action = 'attendance_notification'  # pyright: ignore
    log.detail = f'출퇴근 알림: {type} - {message}'  # pyright: ignore
    log.ip_address = request.remote_addr  # pyright: ignore
    db.session.add(log)


@attendance_management_bp.route('/clock-in', methods=['POST'])
@login_required
def clock_in():
    """출근 기록"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', current_user.id)

        # 권한 확인
        if not can_manage_attendance(user_id):
            return jsonify({'error': '권한이 없습니다.'}), 403

        hierarchy = get_user_hierarchy()
        settings = get_attendance_settings(hierarchy['brand_id'], hierarchy['branch_id'])

        # 이미 출근 기록이 있는지 확인
        today = datetime.now().strftime('%Y-%m-%d')
        record_key = f"{user_id}_{today}"

        if record_key in attendance_records:
            return jsonify({'error': '이미 출근 기록이 있습니다.'}), 400

        # 출근 시간 기록
        clock_in_time = datetime.now().strftime('%H:%M')
        is_late = check_late_status(clock_in_time, settings)

        record = AttendanceRecord(
            user_id=user_id,
            date=today,
            clock_in=clock_in_time,
            work_type=data.get('work_type', '정규'),
            note=data.get('note', ''),
            is_late=is_late
        )

        attendance_records[record_key] = record

        # 지각 알림 생성
        if is_late and settings.auto_notification:
            user = User.query.get(user_id)
            create_notification(
                user_id=user_id,
                type='late',
                message=f'{user.name}님이 지각했습니다. (출근시간: {clock_in_time})'
            )

        # 시스템 로그 기록
        log = SystemLog()
        log.user_id = current_user.id  # pyright: ignore
        log.action = 'attendance_clock_in'  # pyright: ignore
        log.detail = f'출근 기록: {user_id} - {clock_in_time}'  # pyright: ignore
        log.ip_address = request.remote_addr  # pyright: ignore
        db.session.add(log)

        return jsonify({
            'success': True,
            'message': '출근이 기록되었습니다.',
            'record': record.to_dict()
        })

    except Exception as e:
        logger.error(f"출근 기록 오류: {str(e)}")
        return jsonify({'error': '출근 기록 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/clock-out', methods=['POST'])
@login_required
def clock_out():
    """퇴근 기록"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', current_user.id)

        # 권한 확인
        if not can_manage_attendance(user_id):
            return jsonify({'error': '권한이 없습니다.'}), 403

        hierarchy = get_user_hierarchy()
        settings = get_attendance_settings(hierarchy['brand_id'], hierarchy['branch_id'])

        # 출근 기록 확인
        today = datetime.now().strftime('%Y-%m-%d')
        record_key = f"{user_id}_{today}"

        if record_key not in attendance_records:
            return jsonify({'error': '출근 기록이 없습니다.'}), 400

        record = attendance_records[record_key]
        if record.clock_out:
            return jsonify({'error': '이미 퇴근 기록이 있습니다.'}), 400

        # 퇴근 시간 기록
        clock_out_time = datetime.now().strftime('%H:%M')
        record.clock_out = clock_out_time
        record.updated_at = datetime.now().isoformat()

        # 근무 시간 계산
        work_hours = calculate_work_hours(record.clock_in, clock_out_time)
        record.overtime_hours = calculate_overtime_hours(work_hours, settings)
        record.is_early_leave = check_early_leave_status(clock_out_time, settings)

        # 조퇴 알림 생성
        if record.is_early_leave and settings.auto_notification:
            user = User.query.get(user_id)
            create_notification(
                user_id=user_id,
                type='early_leave',
                message=f'{user.name}님이 조퇴했습니다. (퇴근시간: {clock_out_time})'
            )

        # 시스템 로그 기록
        log = SystemLog()
        log.user_id = current_user.id  # pyright: ignore
        log.action = 'attendance_clock_out'  # pyright: ignore
        log.detail = f'퇴근 기록: {user_id} - {clock_out_time}'  # pyright: ignore
        log.ip_address = request.remote_addr  # pyright: ignore
        db.session.add(log)

        return jsonify({
            'success': True,
            'message': '퇴근이 기록되었습니다.',
            'record': record.to_dict()
        })

    except Exception as e:
        logger.error(f"퇴근 기록 오류: {str(e)}")
        return jsonify({'error': '퇴근 기록 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/records', methods=['GET'])
@login_required
def get_attendance_records():
    """출퇴근 기록 조회"""
    try:
        # 쿼리 파라미터
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)

        # 권한 확인
        if user_id and not can_manage_attendance(user_id):
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 조회할 사용자 목록 결정
        hierarchy = get_user_hierarchy()
        if hierarchy['role'] in ['admin', 'brand_manager', 'branch_manager']:
            # 관리자는 모든 직원 조회 가능
            if user_id:
                target_users = [user_id]
            else:
                # 브랜드/매장의 모든 직원
                query = User.query.filter_by(brand_id=hierarchy['brand_id'])
                if hierarchy['branch_id']:
                    query = query.filter_by(branch_id=hierarchy['branch_id'])
                target_users = [user.id for user in query.all()]
        else:
            # 일반 직원은 본인만 조회
            target_users = [current_user.id]

        # 기록 필터링
        filtered_records = []
        for record_key, record in attendance_records.items():
            record_user_id = int(record_key.split('_')[0])

            if record_user_id not in target_users:
                continue

            if start_date and record.date < start_date:
                continue

            if end_date and record.date > end_date:
                continue

            filtered_records.append(record)

        # 정렬 (최신순)
        filtered_records.sort(key=lambda x: x.date, reverse=True)

        # 페이지네이션
        total = len(filtered_records)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_records = filtered_records[start_idx:end_idx]

        # 사용자 정보 추가
        result_records = []
        for record in paginated_records:
            user = User.query.get(record.user_id)
            record_dict = record.to_dict()
            record_dict['user_name'] = user.name if user else '알 수 없음'
            record_dict['user_position'] = user.position if user else '알 수 없음'
            result_records.append(record_dict)

        return jsonify({
            'success': True,
            'records': result_records,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        })

    except Exception as e:
        logger.error(f"출퇴근 기록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/statistics', methods=['GET'])
@login_required
def get_attendance_statistics():
    """출퇴근 통계"""
    try:
        user_id = request.args.get('user_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        # 권한 확인
        if user_id and not can_manage_attendance(user_id):
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 조회할 사용자 목록 결정
        hierarchy = get_user_hierarchy()
        if hierarchy['role'] in ['admin', 'brand_manager', 'branch_manager']:
            if user_id:
                target_users = [user_id]
            else:
                query = User.query.filter_by(brand_id=hierarchy['brand_id'])
                if hierarchy['branch_id']:
                    query = query.filter_by(branch_id=hierarchy['branch_id'])
                target_users = [user.id for user in query.all()]
        else:
            target_users = [current_user.id]

        # 통계 계산
        total_records = 0
        total_work_hours = 0.0
        late_count = 0
        early_leave_count = 0
        absent_count = 0
        overtime_hours = 0.0

        for record_key, record in attendance_records.items():
            record_user_id = int(record_key.split('_')[0])

            if record_user_id not in target_users:
                continue

            if start_date and record.date < start_date:
                continue

            if end_date and record.date > end_date:
                continue

            total_records += 1

            if record.clock_in and record.clock_out:
                work_hours = calculate_work_hours(record.clock_in, record.clock_out)
                total_work_hours += work_hours
                overtime_hours += record.overtime_hours

            if record.is_late:
                late_count += 1

            if record.is_early_leave:
                early_leave_count += 1

        # 평균 계산
        avg_work_hours = total_work_hours / total_records if total_records > 0 else 0

        return jsonify({
            'success': True,
            'statistics': {
                'total_records': total_records,
                'total_work_hours': round(total_work_hours, 2),
                'avg_work_hours': round(avg_work_hours, 2),
                'late_count': late_count,
                'early_leave_count': early_leave_count,
                'absent_count': absent_count,
                'overtime_hours': round(overtime_hours, 2)
            }
        })

    except Exception as e:
        logger.error(f"출퇴근 통계 조회 오류: {str(e)}")
        return jsonify({'error': '통계 조회 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/settings', methods=['GET'])
@login_required
def get_attendance_settings_api():
    """출퇴근 설정 조회"""
    try:
        hierarchy = get_user_hierarchy()
        if not hierarchy:
            return jsonify({'error': '사용자 정보를 찾을 수 없습니다.'}), 404

        settings = get_attendance_settings(hierarchy['brand_id'], hierarchy['branch_id'])

        return jsonify({
            'success': True,
            'settings': settings.to_dict()
        })

    except Exception as e:
        logger.error(f"출퇴근 설정 조회 오류: {str(e)}")
        return jsonify({'error': '설정 조회 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/settings', methods=['PUT'])
@login_required
def update_attendance_settings():
    """출퇴근 설정 업데이트"""
    try:
        # 관리자 권한 확인
        hierarchy = get_user_hierarchy()
        if hierarchy['role'] not in ['admin', 'brand_manager', 'branch_manager']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        settings = get_attendance_settings(hierarchy['brand_id'], hierarchy['branch_id'])

        # 설정 업데이트
        if 'work_start_time' in data:
            settings.work_start_time = data['work_start_time']
        if 'work_end_time' in data:
            settings.work_end_time = data['work_end_time']
        if 'late_threshold_minutes' in data:
            settings.late_threshold_minutes = data['late_threshold_minutes']
        if 'overtime_threshold_hours' in data:
            settings.overtime_threshold_hours = data['overtime_threshold_hours']
        if 'auto_notification' in data:
            settings.auto_notification = data['auto_notification']
        if 'notification_interval' in data:
            settings.notification_interval = data['notification_interval']
        if 'work_types' in data:
            settings.work_types = data['work_types']
        if 'is_active' in data:
            settings.is_active = data['is_active']

        # 시스템 로그 기록
        log = SystemLog()
        log.user_id = current_user.id  # pyright: ignore
        log.action = 'attendance_settings_update'  # pyright: ignore
        log.detail = f'출퇴근 설정 업데이트: {hierarchy["brand_id"]}'  # pyright: ignore
        log.ip_address = request.remote_addr  # pyright: ignore
        db.session.add(log)

        return jsonify({
            'success': True,
            'message': '설정이 업데이트되었습니다.',
            'settings': settings.to_dict()
        })

    except Exception as e:
        logger.error(f"출퇴근 설정 업데이트 오류: {str(e)}")
        return jsonify({'error': '설정 업데이트 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/notifications', methods=['GET'])
@login_required
def get_attendance_notifications():
    """출퇴근 알림 조회"""
    try:
        user_id = current_user.id
        notifications = attendance_notifications.get(user_id, [])

        # 최신순 정렬
        notifications.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            'success': True,
            'notifications': notifications
        })

    except Exception as e:
        logger.error(f"출퇴근 알림 조회 오류: {str(e)}")
        return jsonify({'error': '알림 조회 중 오류가 발생했습니다.'}), 500


@attendance_management_bp.route('/test-data', methods=['POST'])
@login_required
def generate_test_data():
    """테스트 데이터 생성"""
    try:
        # 관리자 권한 확인
        hierarchy = get_user_hierarchy()
        if hierarchy['role'] not in ['admin', 'brand_manager']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        days = data.get('days', 30)

        # 브랜드의 모든 직원 조회
        users = User.query.filter_by(brand_id=hierarchy['brand_id']).all()

        generated_count = 0
        today = datetime.now()

        for user in users:
            for i in range(days):
                date = today - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                record_key = f"{user.id}_{date_str}"

                # 이미 기록이 있으면 스킵
                if record_key in attendance_records:
                    continue

                # 랜덤 출퇴근 시간 생성
                import random

                # 출근 시간 (8:00 ~ 10:00)
                clock_in_hour = random.randint(8, 10)
                clock_in_minute = random.randint(0, 59)
                clock_in = f"{clock_in_hour:02d}:{clock_in_minute:02d}"

                # 퇴근 시간 (17:00 ~ 22:00)
                clock_out_hour = random.randint(17, 22)
                clock_out_minute = random.randint(0, 59)
                clock_out = f"{clock_out_hour:02d}:{clock_out_minute:02d}"

                # 근무 유형
                work_types = ["정규", "시급", "파트타임"]
                work_type = random.choice(work_types)

                # 지각/조퇴 여부
                is_late = clock_in_hour > 9
                is_early_leave = clock_out_hour < 18

                # 초과근무 시간
                work_hours = calculate_work_hours(clock_in, clock_out)
                overtime_hours = max(0, work_hours - 8)

                record = AttendanceRecord(
                    user_id=user.id,
                    date=date_str,
                    clock_in=clock_in,
                    clock_out=clock_out,
                    work_type=work_type,
                    note=f"테스트 데이터 - {date_str}",
                    is_late=is_late,
                    is_early_leave=is_early_leave,
                    overtime_hours=overtime_hours
                )

                attendance_records[record_key] = record
                generated_count += 1

        return jsonify({
            'success': True,
            'message': f'{generated_count}개의 테스트 데이터가 생성되었습니다.',
            'generated_count': generated_count
        })

    except Exception as e:
        logger.error(f"테스트 데이터 생성 오류: {str(e)}")
        return jsonify({'error': '테스트 데이터 생성 중 오류가 발생했습니다.'}), 500
