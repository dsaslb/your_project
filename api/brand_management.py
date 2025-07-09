from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import json

from extensions import db
from models import Brand, Branch, User, AIDiagnosis, ImprovementRequest, AIImprovementSuggestion, SystemHealth, ApprovalWorkflow

brand_management_bp = Blueprint('brand_management', __name__)


@brand_management_bp.route('/brands', methods=['GET'])
@login_required
def get_brands():
    """브랜드 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 조회
        if current_user.role == 'brand_manager':
            brands = Brand.query.filter_by(id=current_user.brand_id).all()
        else:
            brands = Brand.query.all()
        
        brand_list = []
        for brand in brands:
            brand_data = {
                'id': brand.id,
                'name': brand.name,
                'description': brand.description,
                'logo_url': brand.logo_url,
                'website': brand.website,
                'contact_email': brand.contact_email,
                'contact_phone': brand.contact_phone,
                'address': brand.address,
                'status': brand.status,
                'store_count': len(brand.stores),
                'created_at': brand.created_at.isoformat() if brand.created_at else None
            }
            brand_list.append(brand_data)
        
        return jsonify({
            'success': True,
            'brands': brand_list,
            'total': len(brand_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"브랜드 목록 조회 오류: {str(e)}")
        return jsonify({'error': '브랜드 목록을 불러오는 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands', methods=['POST'])
@login_required
def create_brand():
    """새 브랜드 생성"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 브랜드명 중복 확인
        existing_brand = Brand.query.filter_by(name=data['name']).first()
        if existing_brand:
            return jsonify({'error': '이미 존재하는 브랜드명입니다.'}), 400
        
        # 새 브랜드 생성
        new_brand = Brand()
        new_brand.name = data['name']
        new_brand.description = data.get('description')
        new_brand.logo_url = data.get('logo_url')
        new_brand.website = data.get('website')
        new_brand.contact_email = data.get('contact_email')
        new_brand.contact_phone = data.get('contact_phone')
        new_brand.address = data.get('address')
        new_brand.status = data.get('status', 'active')
        
        db.session.add(new_brand)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드가 성공적으로 생성되었습니다.',
            'brand_id': new_brand.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"브랜드 생성 오류: {str(e)}")
        return jsonify({'error': '브랜드 생성 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>', methods=['GET'])
@login_required
def get_brand(brand_id):
    """특정 브랜드 상세 정보 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 조회 가능
        if current_user.role == 'brand_manager' and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 브랜드 정보
        brand_data = {
            'id': brand.id,
            'name': brand.name,
            'description': brand.description,
            'logo_url': brand.logo_url,
            'website': brand.website,
            'contact_email': brand.contact_email,
            'contact_phone': brand.contact_phone,
            'address': brand.address,
            'status': brand.status,
            'created_at': brand.created_at.isoformat() if brand.created_at else None,
            'updated_at': brand.updated_at.isoformat() if brand.updated_at else None
        }
        
        # 매장 목록
        stores = []
        for store in brand.stores:
            store_data = {
                'id': store.id,
                'name': store.name,
                'address': store.address,
                'phone': store.phone,
                'store_code': store.store_code,
                'store_type': store.store_type,
                'status': store.status,
                'employee_count': len(store.users)
            }
            stores.append(store_data)
        
        # 최근 AI 진단 결과
        recent_diagnoses = AIDiagnosis.query.filter_by(brand_id=brand_id).order_by(AIDiagnosis.created_at.desc()).limit(5).all()
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
        latest_health = SystemHealth.query.filter_by(brand_id=brand_id).order_by(SystemHealth.health_date.desc()).first()
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
            'brand': brand_data,
            'stores': stores,
            'recent_diagnoses': diagnoses,
            'system_health': health_data
        })
    
    except Exception as e:
        current_app.logger.error(f"브랜드 상세 조회 오류: {str(e)}")
        return jsonify({'error': '브랜드 정보를 불러오는 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>', methods=['PUT'])
@login_required
def update_brand(brand_id):
    """브랜드 정보 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('brand_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 수정 가능
        if current_user.role == 'brand_manager' and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        updatable_fields = ['description', 'logo_url', 'website', 'contact_email', 'contact_phone', 'address', 'status']
        
        for field in updatable_fields:
            if field in data:
                setattr(brand, field, data[field])
        
        brand.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드 정보가 성공적으로 수정되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"브랜드 수정 오류: {str(e)}")
        return jsonify({'error': '브랜드 수정 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>/stores', methods=['GET'])
@login_required
def get_brand_stores(brand_id):
    """브랜드의 매장 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('store_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 조회 가능
        if current_user.role == 'brand_manager' and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        stores = []
        for store in brand.stores:
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
                'employee_count': employee_count,
                'active_employees': active_employees,
                'created_at': store.created_at.isoformat() if store.created_at else None
            }
            stores.append(store_data)
        
        return jsonify({
            'success': True,
            'stores': stores,
            'total': len(stores)
        })
    
    except Exception as e:
        current_app.logger.error(f"브랜드 매장 목록 조회 오류: {str(e)}")
        return jsonify({'error': '매장 목록을 불러오는 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>/diagnoses', methods=['GET'])
@login_required
def get_brand_diagnoses(brand_id):
    """브랜드의 AI 진단 결과 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 조회 가능
        if current_user.role == 'brand_manager' and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 필터링 옵션
        status = request.args.get('status')
        diagnosis_type = request.args.get('type')
        severity = request.args.get('severity')
        
        query = AIDiagnosis.query.filter_by(brand_id=brand_id)
        
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
        current_app.logger.error(f"브랜드 진단 결과 조회 오류: {str(e)}")
        return jsonify({'error': '진단 결과를 불러오는 중 오류가 발생했습니다.'}), 500


@brand_management_bp.route('/brands/<int:brand_id>/improvements', methods=['GET'])
@login_required
def get_brand_improvements(brand_id):
    """브랜드의 개선 요청 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = Brand.query.get_or_404(brand_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드만 조회 가능
        if current_user.role == 'brand_manager' and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 필터링 옵션
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        query = ImprovementRequest.query.filter_by(brand_id=brand_id)
        
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
        current_app.logger.error(f"브랜드 개선 요청 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500 