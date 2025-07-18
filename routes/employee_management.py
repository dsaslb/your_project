import logging
from datetime import datetime, timedelta
from extensions import db
from models_main import User, Brand, Branch, Staff, SystemLog, AIDiagnosis, ImprovementRequest, Attendance
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, render_template
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
직원별 관리 시스템
직원별 현황 및 개선 사항 관리
"""


logger = logging.getLogger(__name__)

employee_management_bp = Blueprint('employee_management', __name__, url_prefix='/admin/employee-management')


@employee_management_bp.route('/', methods=['GET'])
@login_required
def employee_management_page():
    """직원별 관리 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    return render_template('admin/employee_management.html')


@employee_management_bp.route('/api/employees', methods=['GET'])
@login_required
def get_employees():
    """직원 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        users = User.query.filter(User.role != 'admin').all()
        employee_list = []

        for user in users:
            brand = Brand.query.get(user.brand_id) if user.brand_id else None
            branch = Branch.query.get(user.branch_id) if user.branch_id else None

            # 오늘 출근 여부
            today = datetime.utcnow().date()
            today_attendance = Attendance.query.filter(
                Attendance.user_id == user.id,
                db.func.date(Attendance.clock_in) == today
            ).first()

            # 최근 30일 출근 일수
            thirty_days_ago = today - timedelta(days=30)
            attendance_count = Attendance.query.filter(
                Attendance.user_id == user.id,
                db.func.date(Attendance.clock_in) >= thirty_days_ago
            ).count()

            employee_list.append({
                'user_id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'position': user.position,
                'status': user.status,
                'brand_name': brand.name if brand else '미지정',
                'store_name': branch.name if branch else '미지정',
                'today_attendance': today_attendance is not None,
                'clock_in_time': today_attendance.clock_in.isoformat() if today_attendance else None,
                'attendance_count_30days': attendance_count,
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            })

        return jsonify({
            'success': True,
            'employees': employee_list,
            'total_count': len(employee_list)
        })

    except Exception as e:
        logger.error(f"직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@employee_management_bp.route('/api/employee/<int:user_id>/details', methods=['GET'])
@login_required
def get_employee_details(user_id):
    """직원 상세 정보 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404

        # 브랜드 정보
        brand = Brand.query.get(user.brand_id) if user.brand_id else None

        # 매장 정보
        branch = Branch.query.get(user.branch_id) if user.branch_id else None

        # 최근 30일 출근 기록
        today = datetime.utcnow().date()
        thirty_days_ago = today - timedelta(days=30)
        attendances = Attendance.query.filter(
            Attendance.user_id == user.id,
            db.func.date(Attendance.clock_in) >= thirty_days_ago
        ).order_by(Attendance.clock_in.desc()).all()

        attendance_list = []
        for attendance in attendances:
            attendance_list.append({
                'date': attendance.clock_in.date().isoformat(),
                'clock_in': attendance.clock_in.isoformat(),
                'clock_out': attendance.clock_out.isoformat() if attendance.clock_out else None,
                'status': attendance.status,
                'work_hours': attendance.work_hours if attendance.clock_out else None
            })

        # AI 진단 목록 (해당 직원이 관련된 것들)
        diagnoses = AIDiagnosis.query.filter(
            (AIDiagnosis.brand_id == user.brand_id) | (AIDiagnosis.store_id == user.branch_id)
        ).order_by(AIDiagnosis.created_at.desc()).limit(10).all()

        diagnosis_list = []
        for diagnosis in diagnoses:
            diagnosis_list.append({
                'diagnosis_id': diagnosis.id,
                'title': diagnosis.title,
                'diagnosis_type': diagnosis.diagnosis_type,
                'severity': diagnosis.severity,
                'status': diagnosis.status,
                'priority': diagnosis.priority,
                'created_at': diagnosis.created_at.isoformat()
            })

        # 개선 요청 목록 (해당 직원이 요청한 것들)
        improvements = ImprovementRequest.query.filter_by(requester_id=user.id).order_by(
            ImprovementRequest.created_at.desc()).limit(10).all()
        improvement_list = []

        for improvement in improvements:
            improvement_list.append({
                'request_id': improvement.id,
                'title': improvement.title,
                'category': improvement.category,
                'priority': improvement.priority,
                'status': improvement.status,
                'created_at': improvement.created_at.isoformat()
            })

        # 통계 정보
        stats = {
            'total_attendance_30days': len(attendance_list),
            'present_days': len([a for a in attendance_list if a['status'] == 'present']),
            'late_days': len([a for a in attendance_list if a['status'] == 'late']),
            'absent_days': len([a for a in attendance_list if a['status'] == 'absent']),
            'pending_diagnoses': len([d for d in diagnosis_list if d['status'] == 'pending']),
            'pending_improvements': len([i for i in improvement_list if i['status'] == 'pending'])
        }

        return jsonify({
            'success': True,
            'employee': {
                'user_id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'position': user.position,
                'status': user.status,
                'brand_name': brand.name if brand else '미지정',
                'store_name': branch.name if branch else '미지정',
                'created_at': user.created_at.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None
            },
            'attendances': attendance_list,
            'diagnoses': diagnosis_list,
            'improvements': improvement_list,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"직원 상세 정보 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@employee_management_bp.route('/api/employee/<int:user_id>/update', methods=['PUT'])
@login_required
def update_employee(user_id):
    """직원 정보 업데이트"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        data = request.get_json()
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': '직원을 찾을 수 없습니다.'}), 404

        # 업데이트 가능한 필드들
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'position' in data:
            user.position = data['position']
        if 'status' in data:
            user.status = data['status']
        if 'branch_id' in data:
            user.branch_id = data['branch_id']
        if 'brand_id' in data:
            user.brand_id = data['brand_id']

        user.updated_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog(
            user=current_user,  # pyright: ignore
            action='employee_update',  # pyright: ignore
            detail=f'직원 정보 업데이트: {user.name}',  # pyright: ignore
            ip=request.remote_addr  # pyright: ignore
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{user.name} 직원 정보가 업데이트되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"직원 업데이트 오류: {str(e)}")
        return jsonify({'error': '직원 업데이트 중 오류가 발생했습니다.'}), 500


@employee_management_bp.route('/api/employee/<int:user_id>/analytics', methods=['GET'])
@login_required
def get_employee_analytics(user_id):
    """직원 분석 데이터"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 최근 90일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=90)

        # 출근 통계
        attendances = Attendance.query.filter(
            Attendance.user_id == user_id,
            db.func.date(Attendance.clock_in) >= start_date
        ).all()

        attendance_stats = {
            'total': len(attendances),
            'by_status': {
                'present': len([a for a in attendances if a.status == 'present']),
                'late': len([a for a in attendances if a.status == 'late']),
                'absent': len([a for a in attendances if a.status == 'absent']),
                'early_leave': len([a for a in attendances if a.status == 'early_leave'])
            }
        }

        # 개선 요청 통계
        improvements = ImprovementRequest.query.filter(
            ImprovementRequest.requester_id == user_id,
            ImprovementRequest.created_at >= start_date
        ).all()

        improvement_stats = {
            'total': len(improvements),
            'by_category': {
                'system': len([i for i in improvements if i.category == 'system']),
                'process': len([i for i in improvements if i.category == 'process']),
                'equipment': len([i for i in improvements if i.category == 'equipment']),
                'training': len([i for i in improvements if i.category == 'training']),
                'other': len([i for i in improvements if i.category == 'other'])
            },
            'by_status': {
                'pending': len([i for i in improvements if i.status == 'pending']),
                'under_review': len([i for i in improvements if i.status == 'under_review']),
                'approved': len([i for i in improvements if i.status == 'approved']),
                'rejected': len([i for i in improvements if i.status == 'rejected']),
                'implemented': len([i for i in improvements if i.status == 'implemented'])
            }
        }

        # 월별 출근 추이
        monthly_attendance = {}
        for attendance in attendances:
            month_key = attendance.clock_in.strftime('%Y-%m')
            if month_key not in monthly_attendance:
                monthly_attendance[month_key] = 0
            monthly_attendance[month_key] += 1

        return jsonify({
            'success': True,
            'analytics': {
                'attendance_stats': attendance_stats,
                'improvement_stats': improvement_stats,
                'monthly_attendance': monthly_attendance,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        })

    except Exception as e:
        logger.error(f"직원 분석 데이터 조회 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 조회 중 오류가 발생했습니다.'}), 500
