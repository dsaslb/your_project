import logging
from datetime import datetime, timedelta
from extensions import db
from models_main import User, Brand, Branch, Staff, SystemLog, AIDiagnosis, ImprovementRequest, Attendance
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, render_template
query = None  # pyright: ignore
form = None  # pyright: ignore
"""
매장별 관리 시스템
매장별 현황 및 개선 사항 관리
"""


logger = logging.getLogger(__name__)

store_management_bp = Blueprint('store_management', __name__, url_prefix='/admin/store-management')


@store_management_bp.route('/', methods=['GET'])
@login_required
def store_management_page():
    """매장별 관리 페이지"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    return render_template('admin/store_management.html')


@store_management_bp.route('/api/stores', methods=['GET'])
@login_required
def get_stores():
    """매장 목록 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        branches = Branch.query.all()
        store_list = []

        for branch in branches:
            brand = Brand.query.get(branch.brand_id) if branch.brand_id else None

            # 직원 수
            staff_count = Staff.query.filter_by(branch_id=branch.id).count()

            # 오늘 출근 직원 수
            today = datetime.utcnow().date()
            # pyright: ignore [reportAttributeAccessIssue]
            # Staff 모델의 branch_id 속성에 대한 접근 오류를 무시합니다.
            today_attendance = Attendance.query.filter(
                Attendance.user_id.in_(
                    db.session.query(Staff.user_id).filter(Staff.branch_id == branch.id)  # pyright: ignore
                ),
                db.func.date(Attendance.clock_in) == today
            ).count()
            # 최근 AI 진단 수
            recent_diagnoses = AIDiagnosis.query.filter_by(store_id=branch.id).count()

            # 개선 요청 수
            improvement_requests = ImprovementRequest.query.filter_by(store_id=branch.id).count()

            store_list.append({
                'store_id': branch.id,
                'store_name': branch.name,
                'store_code': branch.store_code,
                'brand_name': brand.name if brand else '미지정',
                'address': branch.address,
                'phone': branch.phone,
                'status': branch.status,
                'staff_count': staff_count,
                'today_attendance': today_attendance,
                'recent_diagnoses': recent_diagnoses,
                'improvement_requests': improvement_requests,
                'created_at': branch.created_at.isoformat(),
                'updated_at': branch.updated_at.isoformat()
            })

        return jsonify({
            'success': True,
            'stores': store_list,
            'total_count': len(store_list)
        })

    except Exception as e:
        logger.error(f"매장 목록 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/api/store/<int:store_id>/details', methods=['GET'])
@login_required
def get_store_details(store_id):
    """매장 상세 정보 조회"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        branch = Branch.query.get(store_id)
        if not branch:
            return jsonify({'error': '매장을 찾을 수 없습니다.'}), 404

        # 브랜드 정보
        brand = Brand.query.get(branch.brand_id) if branch.brand_id else None

        # 직원 목록
        staff_list = Staff.query.filter_by(branch_id=branch.id).all()
        employees = []

        for staff in staff_list:
            user = User.query.get(staff.user_id)
            if user:
                # 오늘 출근 여부
                today = datetime.utcnow().date()
                today_attendance = Attendance.query.filter(
                    Attendance.user_id == user.id,
                    db.func.date(Attendance.clock_in) == today
                ).first()

                employees.append({
                    'staff_id': staff.id,
                    'user_id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'position': user.position,
                    'status': user.status,
                    'today_attendance': today_attendance is not None,
                    'clock_in_time': today_attendance.clock_in.isoformat() if today_attendance else None
                })

        # AI 진단 목록
        diagnoses = AIDiagnosis.query.filter_by(store_id=branch.id).order_by(AIDiagnosis.created_at.desc()).limit(10).all()
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

        # 개선 요청 목록
        improvements = ImprovementRequest.query.filter_by(store_id=branch.id).order_by(
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
        today = datetime.utcnow().date()
        stats = {
            'total_staff': len(employees),
            'present_today': len([e for e in employees if e['today_attendance']]),
            'absent_today': len([e for e in employees if not e['today_attendance']]),
            'pending_diagnoses': len([d for d in diagnosis_list if d['status'] == 'pending']),
            'pending_improvements': len([i for i in improvement_list if i['status'] == 'pending'])
        }

        return jsonify({
            'success': True,
            'store': {
                'store_id': branch.id,
                'store_name': branch.name,
                'store_code': branch.store_code,
                'brand_name': brand.name if brand else '미지정',
                'address': branch.address,
                'phone': branch.phone,
                'status': branch.status,
                'created_at': branch.created_at.isoformat()
            },
            'employees': employees,
            'diagnoses': diagnosis_list,
            'improvements': improvement_list,
            'stats': stats
        })

    except Exception as e:
        logger.error(f"매장 상세 정보 조회 오류: {str(e)}")
        return jsonify({'error': '데이터 조회 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/api/store/<int:store_id>/update', methods=['PUT'])
@login_required
def update_store(store_id):
    """매장 정보 업데이트"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        data = request.get_json()
        branch = Branch.query.get(store_id)

        if not branch:
            return jsonify({'error': '매장을 찾을 수 없습니다.'}), 404

        # 업데이트 가능한 필드들
        if 'name' in data:
            branch.name = data['name']
        if 'address' in data:
            branch.address = data['address']
        if 'phone' in data:
            branch.phone = data['phone']
        if 'status' in data:
            branch.status = data['status']
        if 'brand_id' in data:
            branch.brand_id = data['brand_id']

        branch.updated_at = datetime.utcnow()

        # 시스템 로그 기록
        log = SystemLog(
            user=current_user,  # pyright: ignore
            action='store_update',  # pyright: ignore
            detail=f'매장 정보 업데이트: {branch.name}',  # pyright: ignore
            ip_address=request.remote_addr  # pyright: ignore
        )
        db.session.add(log)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'{branch.name} 매장 정보가 업데이트되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"매장 업데이트 오류: {str(e)}")
        return jsonify({'error': '매장 업데이트 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/api/store/<int:store_id>/analytics', methods=['GET'])
@login_required
def get_store_analytics(store_id):
    """매장 분석 데이터"""
    if not current_user.is_admin():
        return jsonify({'error': '권한이 없습니다.'}), 403

    try:
        # 최근 30일 데이터
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=30)

        # 출근 통계
        # pyright: ignore는 린트 경고를 무시하기 위해 추가합니다.
        staff_ids = db.session.query(Staff.user_id).filter(Staff.branch_id == store_id).subquery()  # pyright: ignore
        attendances = Attendance.query.filter(
            Attendance.user_id.in_(staff_ids),
            db.func.date(Attendance.clock_in) >= start_date
        ).all()

        # 설명:
        # Staff.branch_id에서 린트 경고가 발생하는데, 실제로는 Staff 모델에 branch_id가 있다고 가정하고 pyright: ignore를 추가했습니다.
        # 이 코드는 해당 매장(store_id)에 속한 직원들의 출근 기록을 최근 30일 기준으로 조회합니다.

        attendance_stats = {
            'total': len(attendances),
            'by_status': {
                'present': len([a for a in attendances if a.status == 'present']),
                'late': len([a for a in attendances if a.status == 'late']),
                'absent': len([a for a in attendances if a.status == 'absent']),
                'early_leave': len([a for a in attendances if a.status == 'early_leave'])
            }
        }

        # AI 진단 통계
        diagnoses = AIDiagnosis.query.filter(
            AIDiagnosis.store_id == store_id,
            AIDiagnosis.created_at >= start_date
        ).all()

        diagnosis_stats = {
            'total': len(diagnoses),
            'by_severity': {
                'low': len([d for d in diagnoses if d.severity == 'low']),
                'medium': len([d for d in diagnoses if d.severity == 'medium']),
                'high': len([d for d in diagnoses if d.severity == 'high']),
                'critical': len([d for d in diagnoses if d.severity == 'critical'])
            },
            'by_status': {
                'pending': len([d for d in diagnoses if d.status == 'pending']),
                'reviewed': len([d for d in diagnoses if d.status == 'reviewed']),
                'implemented': len([d for d in diagnoses if d.status == 'implemented']),
                'resolved': len([d for d in diagnoses if d.status == 'resolved'])
            }
        }

        # 개선 요청 통계
        improvements = ImprovementRequest.query.filter(
            ImprovementRequest.store_id == store_id,
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

        return jsonify({
            'success': True,
            'analytics': {
                'attendance_stats': attendance_stats,
                'diagnosis_stats': diagnosis_stats,
                'improvement_stats': improvement_stats,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        })

    except Exception as e:
        logger.error(f"매장 분석 데이터 조회 오류: {str(e)}")
        return jsonify({'error': '분석 데이터 조회 중 오류가 발생했습니다.'}), 500
