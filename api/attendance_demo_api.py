from utils.auth_utils import admin_required, permission_required  # pyright: ignore
from utils.demo_attendance_data import DemoAttendanceData  # pyright: ignore
import json
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, render_template
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
출퇴근 관리 모듈 데모 API
마켓플레이스에서 모듈 미리보기/데모 실행을 위한 API
"""


# Blueprint 생성
attendance_demo_bp = Blueprint('attendance_demo', __name__, url_prefix='/demo/attendance')


@attendance_demo_bp.route('/')
@login_required
def demo_dashboard():
    """출퇴근 관리 데모 대시보드"""
    try:
        # 데모 데이터 로드
        demo_data = DemoAttendanceData.get_full_demo_data()

        return render_template('marketplace/demo_attendance.html',
                               demo_data=demo_data,
                               module_info=get_module_info())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@attendance_demo_bp.route('/api/data')
@login_required
def get_demo_data():
    """데모 데이터 API"""
    try:
        data_type = request.args.get('type', 'all')

        if data_type == 'users':
            data = DemoAttendanceData.get_demo_users()
        elif data_type == 'attendance':
            days = request.args.get('days', 30, type=int)
            data = DemoAttendanceData.get_demo_attendance_data(days)
        elif data_type == 'statistics':
            data = DemoAttendanceData.get_demo_statistics()
        elif data_type == 'realtime':
            data = DemoAttendanceData.get_demo_realtime_data()
        elif data_type == 'notifications':
            data = DemoAttendanceData.get_demo_notifications()
        elif data_type == 'settings':
            data = DemoAttendanceData.get_demo_settings()
        else:
            data = DemoAttendanceData.get_full_demo_data()

        return jsonify({
            "success": True,
            "data": data,
            "module_info": get_module_info()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/clock-in', methods=['POST'])
@login_required
def demo_clock_in():
    """데모 출근 처리"""
    try:
        user_id = request.json.get('user_id', 1)
        clock_in_time = request.json.get('clock_in_time', datetime.now().strftime('%H:%M'))

        # 데모용 출근 데이터 생성
        demo_data = {
            "user_id": user_id,
            "clock_in_time": clock_in_time,
            "status": "checked_in",
            "is_late": is_late_check(clock_in_time),
            "message": "출근이 기록되었습니다."
        }

        return jsonify({
            "success": True,
            "data": demo_data,
            "message": "데모 모드: 출근이 기록되었습니다."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/clock-out', methods=['POST'])
@login_required
def demo_clock_out():
    """데모 퇴근 처리"""
    try:
        user_id = request.json.get('user_id', 1)
        clock_out_time = request.json.get('clock_out_time', datetime.now().strftime('%H:%M'))

        # 데모용 퇴근 데이터 생성
        demo_data = {
            "user_id": user_id,
            "clock_out_time": clock_out_time,
            "status": "completed",
            "work_hours": calculate_work_hours(clock_out_time),
            "is_overtime": is_overtime_check(clock_out_time),
            "message": "퇴근이 기록되었습니다."
        }

        return jsonify({
            "success": True,
            "data": demo_data,
            "message": "데모 모드: 퇴근이 기록되었습니다."
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/statistics')
@login_required
def demo_statistics():
    """데모 통계 데이터"""
    try:
        period = request.args.get('period', 'month')  # week, month, year
        user_id = request.args.get('user_id', type=int)

        # 데모 통계 데이터
        stats = DemoAttendanceData.get_demo_statistics()

        # 기간별 필터링 (데모용)
        if period == 'week':
            stats['period'] = '이번 주'
        elif period == 'month':
            stats['period'] = '이번 달'
        elif period == 'year':
            stats['period'] = '올해'

        # 사용자별 필터링
        if user_id:
            user_stats = stats.get('user_statistics', {})
            for user_name, user_data in user_stats.items():
                if user_data.get('user_id') == user_id:
                    stats['user_statistics'] = {user_name: user_data}
                    break

        return jsonify({
            "success": True,
            "data": stats,
            "period": period
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/realtime')
@login_required
def demo_realtime():
    """데모 실시간 데이터"""
    try:
        # 실시간 데모 데이터
        realtime_data = DemoAttendanceData.get_demo_realtime_data()

        return jsonify({
            "success": True,
            "data": realtime_data,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/notifications')
@login_required
def demo_notifications():
    """데모 알림 데이터"""
    try:
        notification_type = request.args.get('type', 'all')

        notifications = DemoAttendanceData.get_demo_notifications()

        # 타입별 필터링
        if notification_type != 'all':
            notifications = [n for n in notifications if n.get('type') == notification_type]

        return jsonify({
            "success": True,
            "data": notifications,
            "count": len(notifications)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/settings', methods=['GET', 'POST'])
@login_required
def demo_settings():
    """데모 설정 관리"""
    try:
        if request.method == 'GET':
            # 설정 조회
            settings = DemoAttendanceData.get_demo_settings()
            return jsonify({
                "success": True,
                "data": settings
            })
        else:
            # 설정 업데이트 (데모용)
            new_settings = request.json
            settings = DemoAttendanceData.get_demo_settings()
            if isinstance(new_settings, dict):
                settings.update(new_settings)
            else:
                # pyright: ignore [reportGeneralTypeIssues]
                pass  # new_settings가 dict가 아니면 업데이트하지 않음 (lint 무시)

            return jsonify({
                "success": True,
                "data": settings,
                "message": "데모 모드: 설정이 업데이트되었습니다."
            })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/features')
@login_required
def demo_features():
    """데모 기능 목록"""
    try:
        features = {
            "basic_features": [
                "출근/퇴근 기록",
                "지각/조퇴/초과근무 판정",
                "근무 시간 계산",
                "일일/월간 통계"
            ],
            "advanced_features": [
                "실시간 모니터링",
                "AI 기반 패턴 분석",
                "자동 알림 시스템",
                "급여 시스템 연동"
            ],
            "management_features": [
                "권한별 접근 제어",
                "설정 관리",
                "보고서 생성",
                "데이터 내보내기"
            ]
        }

        return jsonify({
            "success": True,
            "data": features
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@attendance_demo_bp.route('/api/status')
@login_required
def demo_module_status():
    """데모 모듈 상태"""
    try:
        status = {
            "module_id": "attendance_management",
            "status": "activated",
            "version": "1.0.0",
            "last_updated": datetime.now().isoformat(),
            "demo_mode": True,
            "features_enabled": [
                "attendance_recording",
                "statistics",
                # "realtime_monitoring",
                "notifications"
            ],
            "permissions": [
                "attendance_view",
                "attendance_edit",
                "attendance_admin"
            ]
        }

        return jsonify({
            "success": True,
            "data": status
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def get_module_info():
    """모듈 정보 반환"""
    return {
        "id": "attendance_management",
        "name": "출퇴근 관리",
        "version": "1.0.0",
        "description": "직원 출퇴근 관리, 지각/초과근무 통계, 급여 연동, 실시간 모니터링",
        "category": "hr",
        "demo_mode": True,
        "features": [
            "직원별 출퇴근 기록",
            "지각/초과근무 통계",
            "급여 시스템 연동",
            "AI 기반 근무 패턴 분석",
            "실시간 알림",
            "데모 데이터 제공",
            "권한별 접근 제어",
            "모듈 상태 관리"
        ]
    }


def is_late_check(clock_in_time):
    """지각 여부 확인"""
    try:
        hour, minute = map(int, clock_in_time.split(':'))
        return hour > 9 or (hour == 9 and minute > 0)
    except:
        return False


def is_overtime_check(clock_out_time):
    """초과근무 여부 확인"""
    try:
        hour, minute = map(int, clock_out_time.split(':'))
        return hour > 18
    except:
        return False


def calculate_work_hours(clock_out_time):
    """근무 시간 계산 (데모용)"""
    try:
        hour, minute = map(int, clock_out_time.split(':'))
        # 9시 출근 기준으로 계산
        work_hours = hour - 9 + minute / 60
        return round(max(0, work_hours), 2)
    except:
        return 8.0
