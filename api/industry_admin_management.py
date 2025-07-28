# -*- coding: utf-8 -*-
"""
업종별 관리자 관리 API
업종별 관리자 생성/수정/삭제/승인/목록 관리
"""

import logging
from datetime import datetime
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import and_, or_
import re

from extensions import db, csrf
from models_main import IndustryAdmin, User, Industry, ActionLog

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
industry_admin_bp = Blueprint('industry_admin', __name__)

def validate_email(email):
    """이메일 유효성 검사"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """전화번호 유효성 검사"""
    pattern = r'^[0-9-+\s()]{10,20}$'
    return re.match(pattern, phone) is not None

def validate_business_license(license_number):
    """사업자등록번호 유효성 검사"""
    if not license_number:
        return True
    pattern = r'^[0-9]{10}$'
    return re.match(pattern, license_number) is not None

@industry_admin_bp.route('/api/industry-admin', methods=['GET'])
@login_required
def get_industry_admins():
    """업종별 관리자 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'view'):
            return jsonify({'error': '업종별 관리자 조회 권한이 없습니다.'}), 403
        
        # 쿼리 파라미터
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        industry_id = request.args.get('industry_id', type=int)
        search = request.args.get('search')
        
        # 기본 쿼리
        query = db.session.query(IndustryAdmin).join(User).join(Industry)
        
        # 필터링
        if status:
            query = query.filter(IndustryAdmin.status == status)
        if industry_id:
            query = query.filter(IndustryAdmin.industry_id == industry_id)
        if search:
            search_filter = or_(
                IndustryAdmin.full_name.ilike(f'%{search}%'),
                IndustryAdmin.contact_email.ilike(f'%{search}%'),
                IndustryAdmin.company_name.ilike(f'%{search}%'),
                Industry.name.ilike(f'%{search}%')
            )
            query = query.filter(search_filter)
        
        # 정렬 (최신순)
        query = query.order_by(IndustryAdmin.created_at.desc())
        
        # 페이징
        pagination = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # 결과 데이터 구성
        industry_admins = []
        for admin in pagination.items:
            admin_data = {
                'id': admin.id,
                'user_id': admin.user_id,
                'industry_id': admin.industry_id,
                'industry_name': admin.industry.name if admin.industry else None,
                'full_name': admin.full_name,
                'contact_email': admin.contact_email,
                'contact_phone': admin.contact_phone,
                'business_license': admin.business_license,
                'company_name': admin.company_name,
                'status': admin.status,
                'approval_date': admin.approval_date.isoformat() if admin.approval_date else None,
                'approved_by': admin.approved_by,
                'rejection_reason': admin.rejection_reason,
                'last_activity': admin.last_activity.isoformat() if admin.last_activity else None,
                'login_count': admin.login_count,
                'two_factor_enabled': admin.two_factor_enabled,
                'created_at': admin.created_at.isoformat(),
                'updated_at': admin.updated_at.isoformat(),
                'user_status': admin.user.status if admin.user else None,
                'user_role': admin.user.role if admin.user else None
            }
            industry_admins.append(admin_data)
        
        return jsonify({
            'industry_admins': industry_admins,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"업종별 관리자 목록 조회 실패: {e}")
        return jsonify({'error': '업종별 관리자 목록 조회에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin', methods=['POST'])
@login_required
@csrf.exempt
def create_industry_admin():
    """업종별 관리자 생성"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'create'):
            return jsonify({'error': '업종별 관리자 생성 권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['industry_id', 'full_name', 'contact_email', 'contact_phone', 'username', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 이메일 유효성 검사
        if not validate_email(data['contact_email']):
            return jsonify({'error': '유효하지 않은 이메일 형식입니다.'}), 400
        
        # 전화번호 유효성 검사
        if not validate_phone(data['contact_phone']):
            return jsonify({'error': '유효하지 않은 전화번호 형식입니다.'}), 400
        
        # 사업자등록번호 유효성 검사
        if data.get('business_license') and not validate_business_license(data['business_license']):
            return jsonify({'error': '유효하지 않은 사업자등록번호 형식입니다.'}), 400
        
        # 업종 존재 확인
        industry = Industry.query.get(data['industry_id'])
        if not industry:
            return jsonify({'error': '존재하지 않는 업종입니다.'}), 404
        
        # 이메일 중복 확인
        if IndustryAdmin.query.filter_by(contact_email=data['contact_email']).first():
            return jsonify({'error': '이미 등록된 이메일입니다.'}), 409
        
        # 사용자명 중복 확인
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': '이미 사용 중인 사용자명입니다.'}), 409
        
        # 사용자 생성
        user = User(
            username=data['username'],
            email=data['contact_email'],
            role='industry_admin',
            status='pending',
            industry_id=data['industry_id']
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.flush()  # ID 생성
        
        # 업종별 관리자 생성
        industry_admin = IndustryAdmin(
            user_id=user.id,
            industry_id=data['industry_id'],
            full_name=data['full_name'],
            contact_email=data['contact_email'],
            contact_phone=data['contact_phone'],
            business_license=data.get('business_license'),
            company_name=data.get('company_name'),
            status='pending'
        )
        
        db.session.add(industry_admin)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='create_industry_admin',
            message=f'업종별 관리자 생성: {data["full_name"]} ({industry.name})',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 생성 완료: {data['full_name']} (ID: {industry_admin.id})")
        
        return jsonify({
            'message': '업종별 관리자가 성공적으로 생성되었습니다.',
            'industry_admin_id': industry_admin.id,
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 생성 실패: {e}")
        return jsonify({'error': '업종별 관리자 생성에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>', methods=['GET'])
@login_required
def get_industry_admin_detail(admin_id):
    """업종별 관리자 상세 정보 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'view'):
            return jsonify({'error': '업종별 관리자 조회 권한이 없습니다.'}), 403
        
        industry_admin = db.session.query(IndustryAdmin).join(User).join(Industry).filter(
            IndustryAdmin.id == admin_id
        ).first()
        
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        # 상세 정보 구성
        admin_data = {
            'id': industry_admin.id,
            'user_id': industry_admin.user_id,
            'industry_id': industry_admin.industry_id,
            'industry_name': industry_admin.industry.name if industry_admin.industry else None,
            'industry_code': industry_admin.industry.code if industry_admin.industry else None,
            'full_name': industry_admin.full_name,
            'contact_email': industry_admin.contact_email,
            'contact_phone': industry_admin.contact_phone,
            'business_license': industry_admin.business_license,
            'company_name': industry_admin.company_name,
            'status': industry_admin.status,
            'approval_date': industry_admin.approval_date.isoformat() if industry_admin.approval_date else None,
            'approved_by': industry_admin.approved_by,
            'approver_name': industry_admin.approver.username if industry_admin.approver else None,
            'rejection_reason': industry_admin.rejection_reason,
            'last_activity': industry_admin.last_activity.isoformat() if industry_admin.last_activity else None,
            'login_count': industry_admin.login_count,
            'two_factor_enabled': industry_admin.two_factor_enabled,
            'ip_whitelist': industry_admin.ip_whitelist,
            'session_timeout': industry_admin.session_timeout,
            'created_at': industry_admin.created_at.isoformat(),
            'updated_at': industry_admin.updated_at.isoformat(),
            'user': {
                'id': industry_admin.user.id,
                'username': industry_admin.user.username,
                'email': industry_admin.user.email,
                'role': industry_admin.user.role,
                'status': industry_admin.user.status,
                'last_login': industry_admin.user.last_login.isoformat() if industry_admin.user.last_login else None,
                'created_at': industry_admin.user.created_at.isoformat()
            }
        }
        
        return jsonify(admin_data)
        
    except Exception as e:
        logger.error(f"업종별 관리자 상세 조회 실패: {e}")
        return jsonify({'error': '업종별 관리자 상세 조회에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>', methods=['PUT'])
@login_required
@csrf.exempt
def update_industry_admin(admin_id):
    """업종별 관리자 정보 수정"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'edit'):
            return jsonify({'error': '업종별 관리자 수정 권한이 없습니다.'}), 403
        
        industry_admin = IndustryAdmin.query.get(admin_id)
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        data = request.get_json()
        
        # 수정 가능한 필드들
        updatable_fields = [
            'full_name', 'contact_phone', 'business_license', 'company_name',
            'two_factor_enabled', 'ip_whitelist', 'session_timeout'
        ]
        
        # 필드 업데이트
        for field in updatable_fields:
            if field in data:
                setattr(industry_admin, field, data[field])
        
        # 전화번호 유효성 검사
        if 'contact_phone' in data and not validate_phone(data['contact_phone']):
            return jsonify({'error': '유효하지 않은 전화번호 형식입니다.'}), 400
        
        # 사업자등록번호 유효성 검사
        if 'business_license' in data and data['business_license'] and not validate_business_license(data['business_license']):
            return jsonify({'error': '유효하지 않은 사업자등록번호 형식입니다.'}), 400
        
        industry_admin.updated_at = datetime.utcnow()
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='update_industry_admin',
            message=f'업종별 관리자 정보 수정: {industry_admin.full_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 정보 수정 완료: {industry_admin.full_name} (ID: {admin_id})")
        
        return jsonify({'message': '업종별 관리자 정보가 성공적으로 수정되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 정보 수정 실패: {e}")
        return jsonify({'error': '업종별 관리자 정보 수정에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>/approve', methods=['POST'])
@login_required
@csrf.exempt
def approve_industry_admin(admin_id):
    """업종별 관리자 승인"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'approve'):
            return jsonify({'error': '업종별 관리자 승인 권한이 없습니다.'}), 403
        
        industry_admin = IndustryAdmin.query.get(admin_id)
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        if industry_admin.is_approved:
            return jsonify({'error': '이미 승인된 업종별 관리자입니다.'}), 400
        
        data = request.get_json()
        approval_notes = data.get('approval_notes')
        
        # 승인 처리
        industry_admin.approve(current_user.id, approval_notes)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='approve_industry_admin',
            message=f'업종별 관리자 승인: {industry_admin.full_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 승인 완료: {industry_admin.full_name} (ID: {admin_id})")
        
        return jsonify({'message': '업종별 관리자가 성공적으로 승인되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 승인 실패: {e}")
        return jsonify({'error': '업종별 관리자 승인에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>/reject', methods=['POST'])
@login_required
@csrf.exempt
def reject_industry_admin(admin_id):
    """업종별 관리자 거절"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'approve'):
            return jsonify({'error': '업종별 관리자 거절 권한이 없습니다.'}), 403
        
        industry_admin = IndustryAdmin.query.get(admin_id)
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        if not industry_admin.is_pending:
            return jsonify({'error': '승인 대기 중인 업종별 관리자만 거절할 수 있습니다.'}), 400
        
        data = request.get_json()
        rejection_reason = data.get('rejection_reason')
        
        if not rejection_reason:
            return jsonify({'error': '거절 사유를 입력해주세요.'}), 400
        
        # 거절 처리
        industry_admin.reject(current_user.id, rejection_reason)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='reject_industry_admin',
            message=f'업종별 관리자 거절: {industry_admin.full_name} - {rejection_reason}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 거절 완료: {industry_admin.full_name} (ID: {admin_id})")
        
        return jsonify({'message': '업종별 관리자가 성공적으로 거절되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 거절 실패: {e}")
        return jsonify({'error': '업종별 관리자 거절에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>/deactivate', methods=['POST'])
@login_required
@csrf.exempt
def deactivate_industry_admin(admin_id):
    """업종별 관리자 비활성화"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'delete'):
            return jsonify({'error': '업종별 관리자 비활성화 권한이 없습니다.'}), 403
        
        industry_admin = IndustryAdmin.query.get(admin_id)
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        if industry_admin.is_inactive:
            return jsonify({'error': '이미 비활성화된 업종별 관리자입니다.'}), 400
        
        data = request.get_json()
        deactivation_reason = data.get('deactivation_reason')
        
        # 비활성화 처리
        industry_admin.deactivate(current_user.id, deactivation_reason)
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='deactivate_industry_admin',
            message=f'업종별 관리자 비활성화: {industry_admin.full_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 비활성화 완료: {industry_admin.full_name} (ID: {admin_id})")
        
        return jsonify({'message': '업종별 관리자가 성공적으로 비활성화되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 비활성화 실패: {e}")
        return jsonify({'error': '업종별 관리자 비활성화에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/<int:admin_id>', methods=['DELETE'])
@login_required
@csrf.exempt
def delete_industry_admin(admin_id):
    """업종별 관리자 삭제"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'delete'):
            return jsonify({'error': '업종별 관리자 삭제 권한이 없습니다.'}), 403
        
        industry_admin = IndustryAdmin.query.get(admin_id)
        if not industry_admin:
            return jsonify({'error': '존재하지 않는 업종별 관리자입니다.'}), 404
        
        # 관련 사용자도 함께 삭제
        user = industry_admin.user
        admin_name = industry_admin.full_name
        
        # 활동 로그 기록
        action_log = ActionLog(
            user_id=current_user.id,
            action='delete_industry_admin',
            message=f'업종별 관리자 삭제: {admin_name}',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(action_log)
        
        # 삭제
        db.session.delete(industry_admin)
        if user:
            db.session.delete(user)
        
        db.session.commit()
        
        logger.info(f"업종별 관리자 삭제 완료: {admin_name} (ID: {admin_id})")
        
        return jsonify({'message': '업종별 관리자가 성공적으로 삭제되었습니다.'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"업종별 관리자 삭제 실패: {e}")
        return jsonify({'error': '업종별 관리자 삭제에 실패했습니다.'}), 500

@industry_admin_bp.route('/api/industry-admin/stats', methods=['GET'])
@login_required
def get_industry_admin_stats():
    """업종별 관리자 통계"""
    try:
        # 권한 확인
        if not current_user.has_permission('industry_management', 'view'):
            return jsonify({'error': '업종별 관리자 통계 조회 권한이 없습니다.'}), 403
        
        # 전체 통계
        total_count = IndustryAdmin.query.count()
        pending_count = IndustryAdmin.query.filter_by(status='pending').count()
        approved_count = IndustryAdmin.query.filter_by(status='approved').count()
        rejected_count = IndustryAdmin.query.filter_by(status='rejected').count()
        inactive_count = IndustryAdmin.query.filter_by(status='inactive').count()
        
        # 업종별 통계
        industry_stats = db.session.query(
            Industry.name,
            db.func.count(IndustryAdmin.id).label('count')
        ).join(IndustryAdmin).group_by(Industry.id, Industry.name).all()
        
        # 최근 활동 통계
        recent_activity = db.session.query(
            IndustryAdmin.full_name,
            IndustryAdmin.last_activity,
            Industry.name.label('industry_name')
        ).join(Industry).filter(
            IndustryAdmin.last_activity.isnot(None)
        ).order_by(IndustryAdmin.last_activity.desc()).limit(10).all()
        
        stats = {
            'total_count': total_count,
            'pending_count': pending_count,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'inactive_count': inactive_count,
            'approval_rate': round((approved_count / total_count * 100), 2) if total_count > 0 else 0,
            'industry_stats': [
                {
                    'industry_name': stat.name,
                    'count': stat.count
                } for stat in industry_stats
            ],
            'recent_activity': [
                {
                    'full_name': activity.full_name,
                    'last_activity': activity.last_activity.isoformat() if activity.last_activity else None,
                    'industry_name': activity.industry_name
                } for activity in recent_activity
            ]
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"업종별 관리자 통계 조회 실패: {e}")
        return jsonify({'error': '업종별 관리자 통계 조회에 실패했습니다.'}), 500 