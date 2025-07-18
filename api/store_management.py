from models_main import Brand, Branch, User, AIDiagnosis, ImprovementRequest, AIImprovementSuggestion, SystemHealth, ApprovalWorkflow
from extensions import db
import json
from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
form = None  # pyright: ignore


store_management_bp = Blueprint('store_management', __name__)


@store_management_bp.route('/stores', methods=['GET'])
@login_required
def get_stores():
    """매장 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('store_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 필터링 옵션
        brand_id = request.args.get('brand_id')
        status = request.args.get('status')
        store_type = request.args.get('store_type')

        query = Branch.query

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 조회
        if current_user.role == 'brand_manager':
            query = query.filter_by(brand_id=current_user.brand_id)
        elif brand_id:
            query = query.filter_by(brand_id=brand_id)

        if status:
            query = query.filter_by(status=status)
        if store_type:
            query = query.filter_by(store_type=store_type)

        stores = query.all()

        store_list = []
        for store in stores:
            # 매장별 통계 정보
            employee_count = len(store.users)
            active_employees = len([u for u in store.users if u.status == 'approved'])

            store_data = {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'store_code': store.store_code,
                'store_type': store.store_type,
                'status': store.status,
                'brand_id': store.brand_id,
                'brand_name': store.brand.name if store.brand else None,
                'employee_count': employee_count,
                'active_employees': active_employees,
                'created_at': store.created_at.isoformat() if store.created_at else None
            }
            store_list.append(store_data)

        return jsonify({
            'success': True,
            'stores': store_list,
            'total': len(store_list)
        })

    except Exception as e:
        current_app.logger.error(f"매장 목록 조회 오류: {str(e)}")
        return jsonify({'error': '매장 목록을 불러오는 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores', methods=['POST'])
@login_required
def create_store():
    """새 매장 생성"""
    try:
        # 권한 확인
        if not current_user.has_permission('store_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()

        # 필수 필드 검증
        required_fields = ['name', 'address']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드에만 매장 생성 가능
        if current_user.role == 'brand_manager':
            if not data.get('brand_id') or data['brand_id'] != current_user.brand_id:
                return jsonify({'error': '자신이 관리하는 브랜드에만 매장을 생성할 수 있습니다.'}), 403

        # 매장 코드 중복 확인
        if data.get('store_code'):
            existing_store = Branch.query.filter_by(store_code=data['store_code']).first()
            if existing_store:
                return jsonify({'error': '이미 존재하는 매장 코드입니다.'}), 400

        # 새 매장 생성
        new_store = Branch()
        new_store.name = data['name']
        new_store.address = data['address']
        new_store.phone = data.get('phone')
        new_store.store_code = data.get('store_code')
        new_store.store_type = data.get('store_type', 'franchise')
        new_store.brand_id = data.get('brand_id')
        new_store.business_hours = data.get('business_hours')
        new_store.capacity = data.get('capacity')
        new_store.status = data.get('status', 'active')
        new_store.processing_time_standard = data.get('processing_time_standard', 15)

        db.session.add(new_store)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 생성되었습니다.',
            'store_id': new_store.id
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매장 생성 오류: {str(e)}")
        return jsonify({'error': '매장 생성 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores/<int:store_id>', methods=['GET'])
@login_required
def get_store(store_id):
    """특정 매장 상세 정보 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('store_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        store = Branch.query.get_or_404(store_id)

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 조회 가능
        if current_user.role == 'brand_manager' and store.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 매장 정보
        store_data = {
            'id': store.id,
            'name': store.name,
            'address': store.address,
            'phone': store.phone,
            'store_code': store.store_code,
            'store_type': store.store_type,
            'status': store.status,
            'brand_id': store.brand_id,
            'brand_name': store.brand.name if store.brand else None,
            'business_hours': store.business_hours,
            'capacity': store.capacity,
            'processing_time_standard': store.processing_time_standard,
            'created_at': store.created_at.isoformat() if store.created_at else None,
            'updated_at': store.updated_at.isoformat() if store.updated_at else None
        }

        # 직원 목록
        employees = []
        for user in store.users:
            employee_data = {
                'id': user.id,
                'name': user.name,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'position': user.position,
                'department': user.department,
                'status': user.status,
                'created_at': user.created_at.isoformat() if user.created_at else None
            }
            employees.append(employee_data)

        # 최근 AI 진단 결과
        recent_diagnoses = AIDiagnosis.query.filter_by(store_id=store_id).order_by(
            AIDiagnosis.created_at.desc()).limit(5).all()
        diagnoses = []
        for diagnosis in recent_diagnoses:
            diagnosis_data = {
                'id': diagnosis.id,
                'title': diagnosis.title,
                'diagnosis_type': diagnosis.diagnosis_type,
                'severity': diagnosis.severity,
                'status': diagnosis.status,
                'created_at': diagnosis.created_at.isoformat() if diagnosis.created_at else None
            }
            diagnoses.append(diagnosis_data)

        # 시스템 건강도
        latest_health = SystemHealth.query.filter_by(store_id=store_id).order_by(SystemHealth.health_date.desc()).first()
        health_data = None
        if latest_health:
            health_data = {
                'overall_score': latest_health.overall_score,
                'performance_score': latest_health.performance_score,
                'quality_score': latest_health.quality_score,
                'efficiency_score': latest_health.efficiency_score,
                'safety_score': latest_health.safety_score,
                'customer_satisfaction_score': latest_health.customer_satisfaction_score,
                'health_date': latest_health.health_date.isoformat() if latest_health.health_date else None
            }

        return jsonify({
            'success': True,
            'store': store_data,
            'employees': employees,
            'recent_diagnoses': diagnoses,
            'system_health': health_data
        })

    except Exception as e:
        current_app.logger.error(f"매장 상세 조회 오류: {str(e)}")
        return jsonify({'error': '매장 정보를 불러오는 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores/<int:store_id>', methods=['PUT'])
@login_required
def update_store(store_id):
    """매장 정보 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('store_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        store = Branch.query.get_or_404(store_id)

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 수정 가능
        if current_user.role == 'brand_manager' and store.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()

        # 업데이트 가능한 필드들
        updatable_fields = ['name', 'address', 'phone', 'store_code', 'store_type',
                            'business_hours', 'capacity', 'status', 'processing_time_standard']

        for field in updatable_fields:
            if field in data:
                setattr(store, field, data[field] if data is not None else None)

        store.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': '매장 정보가 성공적으로 수정되었습니다.'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"매장 수정 오류: {str(e)}")
        return jsonify({'error': '매장 수정 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores/<int:store_id>/employees', methods=['GET'])
@login_required
def get_store_employees(store_id):
    """매장의 직원 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('employee_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        store = Branch.query.get_or_404(store_id)

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 조회 가능
        if current_user.role == 'brand_manager' and store.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 필터링 옵션
        status = request.args.get('status')
        role = request.args.get('role')
        department = request.args.get('department')

        query = User.query.filter_by(branch_id=store_id)

        if status:
            query = query.filter_by(status=status)
        if role:
            query = query.filter_by(role=role)
        if department:
            query = query.filter_by(department=department)

        employees = query.all()

        employee_list = []
        for employee in employees:
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'username': employee.username,
                'email': employee.email,
                'role': employee.role,
                'position': employee.position,
                'department': employee.department,
                'status': employee.status,
                'phone': employee.phone,
                'created_at': employee.created_at.isoformat() if employee.created_at else None,
                'last_login': employee.last_login.isoformat() if employee.last_login else None
            }
            employee_list.append(employee_data)

        return jsonify({
            'success': True,
            'employees': employee_list,
            'total': len(employee_list)
        })

    except Exception as e:
        current_app.logger.error(f"매장 직원 목록 조회 오류: {str(e)}")
        return jsonify({'error': '직원 목록을 불러오는 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores/<int:store_id>/diagnoses', methods=['GET'])
@login_required
def get_store_diagnoses(store_id):
    """매장의 AI 진단 결과 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        store = Branch.query.get_or_404(store_id)

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 조회 가능
        if current_user.role == 'brand_manager' and store.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 필터링 옵션
        status = request.args.get('status')
        diagnosis_type = request.args.get('type')
        severity = request.args.get('severity')

        query = AIDiagnosis.query.filter_by(store_id=store_id)

        if status:
            query = query.filter_by(status=status)
        if diagnosis_type:
            query = query.filter_by(diagnosis_type=diagnosis_type)
        if severity:
            query = query.filter_by(severity=severity)

        diagnoses = query.order_by(AIDiagnosis.created_at.desc()).all()

        diagnosis_list = []
        for diagnosis in diagnoses:
            diagnosis_data = {
                'id': diagnosis.id,
                'title': diagnosis.title,
                'description': diagnosis.description,
                'diagnosis_type': diagnosis.diagnosis_type,
                'severity': diagnosis.severity,
                'status': diagnosis.status,
                'priority': diagnosis.priority,
                'created_at': diagnosis.created_at.isoformat() if diagnosis.created_at else None,
                'reviewed_at': diagnosis.reviewed_at.isoformat() if diagnosis.reviewed_at else None
            }
            diagnosis_list.append(diagnosis_data)

        return jsonify({
            'success': True,
            'diagnoses': diagnosis_list,
            'total': len(diagnosis_list)
        })

    except Exception as e:
        current_app.logger.error(f"매장 진단 결과 조회 오류: {str(e)}")
        return jsonify({'error': '진단 결과를 불러오는 중 오류가 발생했습니다.'}), 500


@store_management_bp.route('/stores/<int:store_id>/improvements', methods=['GET'])
@login_required
def get_store_improvements(store_id):
    """매장의 개선 요청 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        store = Branch.query.get_or_404(store_id)

        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 매장만 조회 가능
        if current_user.role == 'brand_manager' and store.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 필터링 옵션
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')

        query = ImprovementRequest.query.filter_by(store_id=store_id)

        if status:
            query = query.filter_by(status=status)
        if category:
            query = query.filter_by(category=category)
        if priority:
            query = query.filter_by(priority=priority)

        improvements = query.order_by(ImprovementRequest.created_at.desc()).all()

        improvement_list = []
        for improvement in improvements:
            improvement_data = {
                'id': improvement.id,
                'title': improvement.title,
                'category': improvement.category,
                'priority': improvement.priority,
                'status': improvement.status,
                'requester_name': improvement.requester.name if improvement.requester else None,
                'estimated_cost': improvement.estimated_cost,
                'estimated_time': improvement.estimated_time,
                'created_at': improvement.created_at.isoformat() if improvement.created_at else None
            }
            improvement_list.append(improvement_data)

        return jsonify({
            'success': True,
            'improvements': improvement_list,
            'total': len(improvement_list)
        })

    except Exception as e:
        current_app.logger.error(f"매장 개선 요청 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500
