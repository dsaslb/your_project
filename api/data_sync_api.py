#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
데이터 동기화 API
industry-admin과 hierarchy-management 간의 데이터 일치성 보장
"""

import logging
from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from models_main import *
from api.hierarchical_dashboard import dashboard_manager

logger = logging.getLogger(__name__)

data_sync_bp = Blueprint('data_sync', __name__, url_prefix='/api/data-sync')

@data_sync_bp.route('/industry-admins', methods=['GET'])
@login_required
def get_synced_industry_admins():
    """업종별 관리자 통합 데이터 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        result = []
        
        # 1. IndustryAdmin 테이블에서 기본 데이터 조회
        industry_admins = IndustryAdmin.query.all()
        
        for admin in industry_admins:
            # 2. User 테이블에서 해당 사용자의 계층 정보 조회
            user = User.query.filter_by(id=admin.user_id).first()
            
            if user:
                # 3. 계층 관리자에서 상세 정보 조회
                hierarchy_info = dashboard_manager.get_user_hierarchy(user)
                
                # 4. 통합 데이터 구성
                admin_data = {
                    'id': admin.id,
                    'user_id': admin.user_id,
                    'industry_id': admin.industry_id,
                    'status': admin.status,
                    'created_at': admin.created_at.isoformat() if admin.created_at else None,
                    
                    # User 정보
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'brand_id': user.brand_id,
                    'branch_id': user.branch_id,
                    
                    # 계층 정보
                    'hierarchy_level': hierarchy_info.get('hierarchy_level'),
                    'permissions': hierarchy_info.get('permissions', {}),
                    'dashboard_access': hierarchy_info.get('dashboard_access', []),
                    'subordinates_count': len(hierarchy_info.get('subordinates', [])),
                    
                    # 업종 정보
                    'industry_name': admin.industry.name if admin.industry else None,
                    'industry_code': admin.industry.code if admin.industry else None,
                }
                
                result.append(admin_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result),
            'synced_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"업종별 관리자 통합 데이터 조회 오류: {e}")
        return jsonify({'error': '데이터 조회에 실패했습니다.'}), 500

@data_sync_bp.route('/hierarchy-admins', methods=['GET'])
@login_required
def get_synced_hierarchy_admins():
    """계층 관리 통합 데이터 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        result = []
        
        # 1. 관리자 역할을 가진 모든 사용자 조회
        admin_users = User.query.filter(
            User.role.in_(['admin', 'brand_admin', 'store_admin', 'manager'])
        ).all()
        
        for user in admin_users:
            # 2. 계층 정보 조회
            hierarchy_info = dashboard_manager.get_user_hierarchy(user)
            
            # 3. IndustryAdmin 테이블에서 업종 관리자 정보 확인
            industry_admin = IndustryAdmin.query.filter_by(user_id=user.id).first()
            
            # 4. 통합 데이터 구성
            admin_data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'brand_id': user.brand_id,
                'branch_id': user.branch_id,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                
                # 계층 정보
                'hierarchy_level': hierarchy_info.get('hierarchy_level'),
                'permissions': hierarchy_info.get('permissions', {}),
                'dashboard_access': hierarchy_info.get('dashboard_access', []),
                'subordinates': hierarchy_info.get('subordinates', []),
                'subordinates_count': len(hierarchy_info.get('subordinates', [])),
                
                # 업종 관리자 정보
                'is_industry_admin': industry_admin is not None,
                'industry_admin_id': industry_admin.id if industry_admin else None,
                'industry_id': industry_admin.industry_id if industry_admin else None,
                'industry_admin_status': industry_admin.status if industry_admin else None,
                'industry_name': industry_admin.industry.name if (industry_admin and industry_admin.industry) else None,
                
                # 브랜드/매장 정보
                'brand_name': user.brand.name if user.brand else None,
                'branch_name': user.branch.name if user.branch else None,
            }
            
            result.append(admin_data)
        
        return jsonify({
            'success': True,
            'data': result,
            'total': len(result),
            'synced_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"계층 관리 통합 데이터 조회 오류: {e}")
        return jsonify({'error': '데이터 조회에 실패했습니다.'}), 500

@data_sync_bp.route('/sync-check', methods=['GET'])
@login_required
def check_data_sync():
    """데이터 동기화 상태 확인"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        # 1. IndustryAdmin 테이블의 총 레코드 수
        industry_admin_count = IndustryAdmin.query.count()
        
        # 2. User 테이블의 관리자 역할 사용자 수
        hierarchy_admin_count = User.query.filter(
            User.role.in_(['admin', 'brand_admin', 'store_admin', 'manager'])
        ).count()
        
        # 3. 동기화되지 않은 사용자 찾기
        industry_admin_users = {ia.user_id for ia in IndustryAdmin.query.all()}
        hierarchy_admin_users = {u.id for u in User.query.filter(
            User.role.in_(['admin', 'brand_admin', 'store_admin', 'manager'])
        ).all()}
        
        # 4. 불일치 항목
        missing_in_industry = hierarchy_admin_users - industry_admin_users
        missing_in_hierarchy = industry_admin_users - hierarchy_admin_users
        
        sync_status = {
            'industry_admin_count': industry_admin_count,
            'hierarchy_admin_count': hierarchy_admin_count,
            'is_synced': len(missing_in_industry) == 0 and len(missing_in_hierarchy) == 0,
            'missing_in_industry_admin': len(missing_in_industry),
            'missing_in_hierarchy': len(missing_in_hierarchy),
            'sync_issues': {
                'users_not_in_industry_admin': list(missing_in_industry),
                'industry_admins_not_in_users': list(missing_in_hierarchy)
            },
            'checked_at': datetime.now().isoformat()
        }
        
        return jsonify({
            'success': True,
            'sync_status': sync_status
        }), 200
        
    except Exception as e:
        logger.error(f"데이터 동기화 상태 확인 오류: {e}")
        return jsonify({'error': '동기화 상태 확인에 실패했습니다.'}), 500

@data_sync_bp.route('/auto-sync', methods=['POST'])
@login_required
def auto_sync_data():
    """자동 데이터 동기화"""
    try:
        # 권한 확인
        if not current_user.has_permission('system_management', 'admin'):
            return jsonify({'error': '권한이 없습니다.'}), 403

        sync_results = {
            'created_industry_admins': 0,
            'updated_user_roles': 0,
            'errors': []
        }
        
        # 1. 관리자 역할 사용자 중 IndustryAdmin에 없는 사용자들을 추가
        admin_users = User.query.filter(
            User.role.in_(['admin', 'brand_admin', 'store_admin', 'manager'])
        ).all()
        
        existing_industry_admins = {ia.user_id for ia in IndustryAdmin.query.all()}
        
        for user in admin_users:
            if user.id not in existing_industry_admins:
                try:
                    # 기본 업종 ID 설정 (첫 번째 업종 또는 기본값)
                    default_industry = Industry.query.first()
                    if default_industry:
                        new_industry_admin = IndustryAdmin(
                            user_id=user.id,
                            industry_id=default_industry.id,
                            status='approved',  # 기본 승인 상태
                            created_at=datetime.now()
                        )
                        db.session.add(new_industry_admin)
                        sync_results['created_industry_admins'] += 1
                except Exception as e:
                    sync_results['errors'].append(f"사용자 {user.id} 동기화 실패: {str(e)}")
        
        # 2. 변경사항 저장
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '데이터 동기화가 완료되었습니다.',
            'results': sync_results,
            'synced_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"자동 데이터 동기화 오류: {e}")
        return jsonify({'error': '데이터 동기화에 실패했습니다.'}), 500