"""
브랜드 온보딩 API
신규 브랜드 생성 후 초기 설정을 위한 온보딩 프로세스 관리
"""

import logging
import json
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import db, csrf
from models import Brand, BrandOnboarding, OnboardingTemplate, Branch, User, Industry

logger = logging.getLogger(__name__)

brand_onboarding_bp = Blueprint('brand_onboarding', __name__)

@brand_onboarding_bp.route('/api/brand-onboarding/start/<int:brand_id>', methods=['POST'])
@csrf.exempt
@login_required
def start_onboarding(brand_id):
    """브랜드 온보딩 시작"""
    try:
        # 브랜드 확인
        brand = Brand.query.get_or_404(brand_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 기존 온보딩 확인
        existing_onboarding = BrandOnboarding.query.filter_by(
            brand_id=brand_id, 
            user_id=current_user.id
        ).first()
        
        if existing_onboarding:
            return jsonify({
                'success': True,
                'message': '이미 진행 중인 온보딩이 있습니다.',
                'onboarding_id': existing_onboarding.id,
                'current_step': existing_onboarding.current_step,
                'progress': existing_onboarding.progress_percentage
            })
        
        # 새 온보딩 생성
        onboarding = BrandOnboarding(
            brand_id=brand_id,
            user_id=current_user.id,
            onboarding_data={}
        )
        
        db.session.add(onboarding)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드 온보딩이 시작되었습니다.',
            'onboarding_id': onboarding.id,
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"온보딩 시작 실패: {e}")
        return jsonify({'error': '온보딩 시작 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/status', methods=['GET'])
@csrf.exempt
@login_required
def get_onboarding_status(onboarding_id):
    """온보딩 상태 조회"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        return jsonify({
            'success': True,
            'data': {
                'onboarding_id': onboarding.id,
                'brand_id': onboarding.brand_id,
                'brand_name': onboarding.brand.name,
                'current_step': onboarding.current_step,
                'progress': onboarding.progress_percentage,
                'steps': {
                    'store': onboarding.step_store,
                    'employee': onboarding.step_employee,
                    'menu': onboarding.step_menu,
                    'settings': onboarding.step_settings
                },
                'started_at': onboarding.started_at.isoformat() if onboarding.started_at else None,
                'completed_at': onboarding.completed_at.isoformat() if onboarding.completed_at else None,
                'last_activity': onboarding.last_activity.isoformat() if onboarding.last_activity else None
            }
        })
        
    except Exception as e:
        logger.error(f"온보딩 상태 조회 실패: {e}")
        return jsonify({'error': '온보딩 상태 조회 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/store', methods=['POST'])
@csrf.exempt
@login_required
def complete_store_step(onboarding_id):
    """매장 추가 단계 완료"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 매장 생성
        store_data = data.get('store', {})
        new_store = Branch(
            name=store_data.get('name'),
            address=store_data.get('address'),
            phone=store_data.get('phone'),
            store_code=store_data.get('store_code'),
            store_type=store_data.get('store_type', 'franchise'),
            brand_id=onboarding.brand_id,
            business_hours=store_data.get('business_hours'),
            capacity=store_data.get('capacity'),
            status='active'
        )
        
        db.session.add(new_store)
        db.session.flush()  # ID 생성
        
        # 온보딩 데이터 업데이트
        if not onboarding.onboarding_data:
            onboarding.onboarding_data = {}
        
        onboarding.onboarding_data['store'] = {
            'store_id': new_store.id,
            'store_name': new_store.name,
            'store_address': new_store.address,
            'created_at': datetime.utcnow().isoformat()
        }
        
        onboarding.step_store = True
        onboarding.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '매장이 성공적으로 추가되었습니다.',
            'store_id': new_store.id,
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"매장 추가 실패: {e}")
        db.session.rollback()
        return jsonify({'error': '매장 추가 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/employee', methods=['POST'])
@csrf.exempt
@login_required
def complete_employee_step(onboarding_id):
    """직원 등록 단계 완료"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        employees_data = data.get('employees', [])
        
        created_employees = []
        
        for emp_data in employees_data:
            # 사용자명 중복 확인
            if User.query.filter_by(username=emp_data.get('username')).first():
                continue  # 중복된 사용자명은 건너뛰기
            
            # 새 직원 생성
            new_employee = User(
                username=emp_data.get('username'),
                name=emp_data.get('name'),
                email=emp_data.get('email'),
                role=emp_data.get('role', 'employee'),
                brand_id=onboarding.brand_id,
                branch_id=emp_data.get('branch_id'),
                status='approved'
            )
            new_employee.set_password(emp_data.get('password', '123456'))
            
            db.session.add(new_employee)
            created_employees.append({
                'id': new_employee.id,
                'username': new_employee.username,
                'name': new_employee.name,
                'role': new_employee.role
            })
        
        # 온보딩 데이터 업데이트
        if not onboarding.onboarding_data:
            onboarding.onboarding_data = {}
        
        onboarding.onboarding_data['employees'] = {
            'employees': created_employees,
            'count': len(created_employees),
            'created_at': datetime.utcnow().isoformat()
        }
        
        onboarding.step_employee = True
        onboarding.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(created_employees)}명의 직원이 등록되었습니다.',
            'employees': created_employees,
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"직원 등록 실패: {e}")
        db.session.rollback()
        return jsonify({'error': '직원 등록 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/menu', methods=['POST'])
@csrf.exempt
@login_required
def complete_menu_step(onboarding_id):
    """메뉴 구성 단계 완료"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        menu_data = data.get('menu', {})
        
        # 온보딩 데이터 업데이트
        if not onboarding.onboarding_data:
            onboarding.onboarding_data = {}
        
        onboarding.onboarding_data['menu'] = {
            'menu_data': menu_data,
            'created_at': datetime.utcnow().isoformat()
        }
        
        onboarding.step_menu = True
        onboarding.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '메뉴 구성이 완료되었습니다.',
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"메뉴 구성 실패: {e}")
        return jsonify({'error': '메뉴 구성 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/settings', methods=['POST'])
@csrf.exempt
@login_required
def complete_settings_step(onboarding_id):
    """운영 설정 단계 완료"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        settings_data = data.get('settings', {})
        
        # 온보딩 데이터 업데이트
        if not onboarding.onboarding_data:
            onboarding.onboarding_data = {}
        
        onboarding.onboarding_data['settings'] = {
            'settings_data': settings_data,
            'created_at': datetime.utcnow().isoformat()
        }
        
        onboarding.step_settings = True
        onboarding.step_completed = True
        onboarding.completed_at = datetime.utcnow()
        onboarding.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '브랜드 온보딩이 완료되었습니다!',
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"운영 설정 실패: {e}")
        return jsonify({'error': '운영 설정 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/<int:onboarding_id>/generate-sample-data', methods=['POST'])
@csrf.exempt
@login_required
def generate_sample_data(onboarding_id):
    """샘플 데이터 자동 생성"""
    try:
        onboarding = BrandOnboarding.query.get_or_404(onboarding_id)
        
        # 권한 확인
        if not current_user.has_permission('brand_management', 'manage') and current_user.brand_id != onboarding.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        brand = onboarding.brand
        
        # 샘플 매장 생성
        sample_store = Branch(
            name=f"{brand.name} 본점",
            address=brand.address or "서울시 강남구 테헤란로 123",
            phone=brand.contact_phone or "02-1234-5678",
            store_code=f"{brand.code}_MAIN",
            store_type='franchise',
            brand_id=brand.id,
            business_hours='09:00-18:00',
            capacity=50,
            status='active'
        )
        
        db.session.add(sample_store)
        db.session.flush()
        
        # 샘플 직원 생성
        sample_employees = [
            {
                'username': f'manager_{brand.code.lower()}',
                'name': '매장 관리자',
                'email': f'manager@{brand.code.lower()}.com',
                'role': 'store_manager',
                'password': '123456'
            },
            {
                'username': f'employee1_{brand.code.lower()}',
                'name': '직원 1',
                'email': f'emp1@{brand.code.lower()}.com',
                'role': 'employee',
                'password': '123456'
            },
            {
                'username': f'employee2_{brand.code.lower()}',
                'name': '직원 2',
                'email': f'emp2@{brand.code.lower()}.com',
                'role': 'employee',
                'password': '123456'
            }
        ]
        
        created_employees = []
        for emp_data in sample_employees:
            new_employee = User(
                username=emp_data['username'],
                name=emp_data['name'],
                email=emp_data['email'],
                role=emp_data['role'],
                brand_id=brand.id,
                branch_id=sample_store.id,
                status='approved'
            )
            new_employee.set_password(emp_data['password'])
            
            db.session.add(new_employee)
            created_employees.append({
                'id': new_employee.id,
                'username': new_employee.username,
                'name': new_employee.name,
                'role': new_employee.role
            })
        
        # 샘플 메뉴 데이터
        sample_menu = {
            'categories': [
                {
                    'name': '메인 메뉴',
                    'items': [
                        {'name': '시그니처 메뉴 1', 'price': 15000, 'description': '브랜드 대표 메뉴'},
                        {'name': '인기 메뉴 1', 'price': 12000, 'description': '고객들이 선호하는 메뉴'},
                        {'name': '신메뉴 1', 'price': 18000, 'description': '새로 출시된 메뉴'}
                    ]
                },
                {
                    'name': '사이드 메뉴',
                    'items': [
                        {'name': '사이드 1', 'price': 5000, 'description': '메인 메뉴와 함께 즐기는 사이드'},
                        {'name': '음료 1', 'price': 3000, 'description': '시원한 음료'}
                    ]
                }
            ]
        }
        
        # 샘플 설정 데이터
        sample_settings = {
            'business_hours': {
                'monday': {'open': '09:00', 'close': '18:00'},
                'tuesday': {'open': '09:00', 'close': '18:00'},
                'wednesday': {'open': '09:00', 'close': '18:00'},
                'thursday': {'open': '09:00', 'close': '18:00'},
                'friday': {'open': '09:00', 'close': '18:00'},
                'saturday': {'open': '10:00', 'close': '17:00'},
                'sunday': {'open': '10:00', 'close': '17:00'}
            },
            'notifications': {
                'email_notifications': True,
                'sms_notifications': False,
                'push_notifications': True
            },
            'work_rules': {
                'work_start_time': '09:00',
                'work_end_time': '18:00',
                'break_time': 60,
                'overtime_allowed': True
            }
        }
        
        # 온보딩 데이터 업데이트
        onboarding.onboarding_data = {
            'store': {
                'store_id': sample_store.id,
                'store_name': sample_store.name,
                'store_address': sample_store.address,
                'created_at': datetime.utcnow().isoformat()
            },
            'employees': {
                'employees': created_employees,
                'count': len(created_employees),
                'created_at': datetime.utcnow().isoformat()
            },
            'menu': {
                'menu_data': sample_menu,
                'created_at': datetime.utcnow().isoformat()
            },
            'settings': {
                'settings_data': sample_settings,
                'created_at': datetime.utcnow().isoformat()
            }
        }
        
        # 모든 단계 완료
        onboarding.step_store = True
        onboarding.step_employee = True
        onboarding.step_menu = True
        onboarding.step_settings = True
        onboarding.step_completed = True
        onboarding.completed_at = datetime.utcnow()
        onboarding.last_activity = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '샘플 데이터가 성공적으로 생성되었습니다!',
            'data': {
                'store': {
                    'id': sample_store.id,
                    'name': sample_store.name
                },
                'employees': created_employees,
                'menu_categories': len(sample_menu['categories']),
                'settings': '완료'
            },
            'current_step': onboarding.current_step,
            'progress': onboarding.progress_percentage
        })
        
    except Exception as e:
        logger.error(f"샘플 데이터 생성 실패: {e}")
        db.session.rollback()
        return jsonify({'error': '샘플 데이터 생성 중 오류가 발생했습니다.'}), 500

@brand_onboarding_bp.route('/api/brand-onboarding/templates', methods=['GET'])
@csrf.exempt
@login_required
def get_onboarding_templates():
    """온보딩 템플릿 목록 조회"""
    try:
        industry_id = request.args.get('industry_id', type=int)
        
        query = OnboardingTemplate.query.filter_by(is_active=True)
        if industry_id:
            query = query.filter_by(industry_id=industry_id)
        
        templates = query.all()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': template.id,
                    'name': template.name,
                    'description': template.description,
                    'industry_id': template.industry_id,
                    'is_default': template.is_default
                }
                for template in templates
            ]
        })
        
    except Exception as e:
        logger.error(f"온보딩 템플릿 조회 실패: {e}")
        return jsonify({'error': '온보딩 템플릿 조회 중 오류가 발생했습니다.'}), 500 