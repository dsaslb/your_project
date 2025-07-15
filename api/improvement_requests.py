from flask import Blueprint, jsonify, request, current_app
from sqlalchemy import and_, or_
from datetime import datetime
import json

from extensions import db
from models import User, ImprovementRequest, Brand, Branch
from utils.auth_decorators import jwt_required, role_required

improvement_requests_bp = Blueprint('improvement_requests', __name__)


@improvement_requests_bp.route('/requests', methods=['GET'])
@jwt_required
def get_improvement_requests():
    """개선 요청 목록 조회"""
    try:
        # 필터링 옵션
        status = request.args.get('status')
        priority = request.args.get('priority')
        category = request.args.get('category')
        brand_id = request.args.get('brand_id')
        store_id = request.args.get('store_id')
        
        query = ImprovementRequest.query
        current_user = getattr(request, 'current_user', None)
        # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 요청만 조회
        if current_user and hasattr(current_user, 'role') and current_user.role == 'brand_manager':
            query = query.filter_by(brand_id=current_user.brand_id)
        # 슈퍼관리자/총관리자는 전체 요청 조회
        elif current_user and hasattr(current_user, 'role') and current_user.role in ['admin', 'super_admin']:
            pass
        # 일반 사용자는 자신이 요청한 것만 조회
        elif current_user:
            query = query.filter_by(requester_id=current_user.id)
        
        if status:
            query = query.filter_by(status=status)
        if priority:
            query = query.filter_by(priority=priority)
        if category:
            query = query.filter_by(category=category)
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        if store_id:
            query = query.filter_by(store_id=store_id)
        
        requests = query.order_by(ImprovementRequest.created_at.desc()).all()
        
        request_list = []
        for req in requests:
            request_data = {
                'id': req.id,
                'title': req.title,
                'description': req.description,
                'category': req.category,
                'priority': req.priority,
                'status': req.status,
                'brand_name': req.brand.name if req.brand else None,
                'store_name': req.store.name if req.store else None,
                'requester_name': req.requester.name if req.requester else None,
                'reviewer_name': req.reviewer.name if req.reviewer else None,
                'created_at': req.created_at.isoformat() if req.created_at else None,
                'updated_at': req.updated_at.isoformat() if req.updated_at else None,
                'reviewed_at': req.reviewed_at.isoformat() if req.reviewed_at else None
            }
            request_list.append(request_data)
        
        return jsonify({
            'success': True,
            'requests': request_list,
            'total': len(request_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"개선 요청 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests/<int:request_id>', methods=['GET'])
@jwt_required
def get_improvement_request(request_id):
    """특정 개선 요청 상세 조회"""
    try:
        req = ImprovementRequest.query.get_or_404(request_id)
        
        # 권한 확인
        current_user = getattr(request, 'current_user', None)
        if current_user and current_user.role not in ['admin', 'super_admin']:
            if req.requester_id != current_user.id:
                return jsonify({'error': '권한이 없습니다.'}), 403
        
        request_data = {
            'id': req.id,
            'title': req.title,
            'description': req.description,
            'category': req.category,
            'priority': req.priority,
            'status': req.status,
            'brand_name': req.brand.name if req.brand else None,
            'store_name': req.store.name if req.store else None,
            'requester_name': req.requester.name if req.requester else None,
            'reviewer_name': req.reviewer.name if req.reviewer else None,
            'created_at': req.created_at.isoformat() if req.created_at else None,
            'updated_at': req.updated_at.isoformat() if req.updated_at else None,
            'reviewed_at': req.reviewed_at.isoformat() if req.reviewed_at else None,
            'admin_comment': req.admin_comment
        }
        
        return jsonify({
            'success': True,
            'request': request_data
        })
    
    except Exception as e:
        current_app.logger.error(f"개선 요청 상세 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests', methods=['POST'])
@jwt_required
def create_improvement_request():
    """개선 요청 생성"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '요청 데이터가 필요합니다.'}), 400
        
        # 필수 필드 검증
        required_fields = ['title', 'description', 'category', 'priority']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드가 필요합니다.'}), 400
        
        current_user = getattr(request, 'current_user', None)
        if not current_user:
            return jsonify({'error': '인증이 필요합니다.'}), 401
        
        # 새 개선 요청 생성
        new_request = ImprovementRequest()
        new_request.title = data['title']
        new_request.description = data['description']
        new_request.category = data['category']
        new_request.priority = data['priority']
        new_request.brand_id = data.get('brand_id')
        new_request.store_id = data.get('store_id')
        new_request.requester_id = current_user.id
        new_request.status = 'pending'
        
        db.session.add(new_request)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 생성되었습니다.',
            'request_id': new_request.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 생성 오류: {str(e)}")
        return jsonify({'error': '개선 요청 생성 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests/<int:request_id>', methods=['PUT'])
@jwt_required
@role_required(['admin', 'super_admin'])
def update_improvement_request(request_id):
    """개선 요청 수정 (관리자만)"""
    try:
        req = ImprovementRequest.query.get_or_404(request_id)
        data = request.get_json()
        
        if not data:
            return jsonify({'error': '수정 데이터가 필요합니다.'}), 400
        
        # 수정 가능한 필드들
        if 'title' in data:
            req.title = data['title']
        if 'description' in data:
            req.description = data['description']
        if 'category' in data:
            req.category = data['category']
        if 'priority' in data:
            req.priority = data['priority']
        if 'status' in data:
            req.status = data['status']
        if 'review_comments' in data:
            req.review_comments = data['review_comments']
        
        current_user = getattr(request, 'current_user', None)
        if current_user:
            req.reviewer_id = current_user.id
        req.reviewed_at = datetime.utcnow()
        req.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 수정되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 수정 오류: {str(e)}")
        return jsonify({'error': '개선 요청 수정 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests/<int:request_id>', methods=['DELETE'])
@jwt_required
@role_required(['admin', 'super_admin'])
def delete_improvement_request(request_id):
    """개선 요청 삭제 (관리자만)"""
    try:
        req = ImprovementRequest.query.get_or_404(request_id)
        
        db.session.delete(req)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 삭제되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 삭제 오류: {str(e)}")
        return jsonify({'error': '개선 요청 삭제 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests/<int:request_id>/approve', methods=['POST'])
@jwt_required
@role_required(['admin', 'super_admin'])
def approve_improvement_request(request_id):
    """개선 요청 승인"""
    try:
        req = ImprovementRequest.query.get_or_404(request_id)
        
        if req.status != 'pending':
            return jsonify({'error': '이미 처리된 요청입니다.'}), 400
        
        data = request.get_json()
        comments = data.get('comments', '')
        
        current_user = getattr(request, 'current_user', None)
        req.status = 'approved'
        if current_user:
            req.reviewer_id = current_user.id
        req.reviewed_at = datetime.utcnow()
        req.admin_comment = comments
        req.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 승인되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 승인 오류: {str(e)}")
        return jsonify({'error': '개선 요청 승인 중 오류가 발생했습니다.'}), 500


@improvement_requests_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
@jwt_required
@role_required(['admin', 'super_admin'])
def reject_improvement_request(request_id):
    """개선 요청 거절"""
    try:
        req = ImprovementRequest.query.get_or_404(request_id)
        
        if req.status != 'pending':
            return jsonify({'error': '이미 처리된 요청입니다.'}), 400
        
        data = request.get_json()
        comments = data.get('comments', '')
        
        current_user = getattr(request, 'current_user', None)
        req.status = 'rejected'
        if current_user:
            req.reviewer_id = current_user.id
        req.reviewed_at = datetime.utcnow()
        req.admin_comment = comments
        req.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 거절되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 거절 오류: {str(e)}")
        return jsonify({'error': '개선 요청 거절 중 오류가 발생했습니다.'}), 500 