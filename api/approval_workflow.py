from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import json

from extensions import db
from models import User, ApprovalWorkflow, ImprovementRequest, AIImprovementSuggestion

approval_workflow_bp = Blueprint('approval_workflow', __name__)


@approval_workflow_bp.route('/workflows', methods=['GET'])
@login_required
def get_workflows():
    """승인 워크플로우 목록 조회"""
    try:
        # 필터링 옵션
        workflow_type = request.args.get('type')
        status = request.args.get('status')
        target_type = request.args.get('target_type')
        
        query = ApprovalWorkflow.query
        
        # 사용자별 필터링
        if current_user.role in ['admin', 'super_admin']:
            # 관리자는 모든 워크플로우 조회 가능
            pass
        elif current_user.role == 'brand_manager':
            # 브랜드 매니저는 자신이 관련된 워크플로우만 조회
            query = query.filter(
                or_(
                    ApprovalWorkflow.requester_id == current_user.id,
                    ApprovalWorkflow.approver_id == current_user.id
                )
            )
        else:
            # 일반 사용자는 자신이 요청한 워크플로우만 조회
            query = query.filter_by(requester_id=current_user.id)
        
        if workflow_type:
            query = query.filter_by(workflow_type=workflow_type)
        if status:
            query = query.filter_by(status=status)
        if target_type:
            query = query.filter_by(target_type=target_type)
        
        workflows = query.order_by(ApprovalWorkflow.created_at.desc()).all()
        
        workflow_list = []
        for workflow in workflows:
            workflow_data = {
                'id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'target_type': workflow.target_type,
                'target_id': workflow.target_id,
                'status': workflow.status,
                'requester_name': workflow.requester.name if workflow.requester else None,
                'approver_name': workflow.approver.name if workflow.approver else None,
                'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
                'approved_at': workflow.approved_at.isoformat() if workflow.approved_at else None,
                'rejected_at': workflow.rejected_at.isoformat() if workflow.rejected_at else None
            }
            workflow_list.append(workflow_data)
        
        return jsonify({
            'success': True,
            'workflows': workflow_list,
            'total': len(workflow_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"승인 워크플로우 조회 오류: {str(e)}")
        return jsonify({'error': '승인 워크플로우를 불러오는 중 오류가 발생했습니다.'}), 500


@approval_workflow_bp.route('/workflows/<int:workflow_id>', methods=['GET'])
@login_required
def get_workflow(workflow_id):
    """특정 승인 워크플로우 상세 조회"""
    try:
        workflow = ApprovalWorkflow.query.get_or_404(workflow_id)
        
        # 권한 확인
        if current_user.role not in ['admin', 'super_admin']:
            if workflow.requester_id != current_user.id and workflow.approver_id != current_user.id:
                return jsonify({'error': '권한이 없습니다.'}), 403
        
        workflow_data = {
            'id': workflow.id,
            'workflow_type': workflow.workflow_type,
            'target_type': workflow.target_type,
            'target_id': workflow.target_id,
            'status': workflow.status,
            'request_data': workflow.request_data,
            'approval_data': workflow.approval_data,
            'comments': workflow.comments,
            'requester_name': workflow.requester.name if workflow.requester else None,
            'approver_name': workflow.approver.name if workflow.approver else None,
            'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
            'updated_at': workflow.updated_at.isoformat() if workflow.updated_at else None,
            'approved_at': workflow.approved_at.isoformat() if workflow.approved_at else None,
            'rejected_at': workflow.rejected_at.isoformat() if workflow.rejected_at else None
        }
        
        return jsonify({
            'success': True,
            'workflow': workflow_data
        })
    
    except Exception as e:
        current_app.logger.error(f"승인 워크플로우 상세 조회 오류: {str(e)}")
        return jsonify({'error': '승인 워크플로우를 불러오는 중 오류가 발생했습니다.'}), 500


@approval_workflow_bp.route('/workflows/<int:workflow_id>/approve', methods=['POST'])
@login_required
def approve_workflow(workflow_id):
    """승인 워크플로우 승인"""
    try:
        workflow = ApprovalWorkflow.query.get_or_404(workflow_id)
        
        # 권한 확인
        if current_user.role not in ['admin', 'super_admin']:
            if workflow.approver_id != current_user.id:
                return jsonify({'error': '승인 권한이 없습니다.'}), 403
        
        # 상태 확인
        if workflow.status != 'pending':
            return jsonify({'error': '이미 처리된 워크플로우입니다.'}), 400
        
        data = request.get_json()
        comments = data.get('comments', '')
        
        # 워크플로우 승인
        workflow.status = 'approved'
        workflow.approval_data = {
            'approved_by': current_user.id,
            'approved_at': datetime.utcnow().isoformat(),
            'comments': comments
        }
        workflow.approved_at = datetime.utcnow()
        workflow.comments = comments
        
        # 대상 객체 상태 업데이트
        if workflow.target_type == 'user':
            user = User.query.get(workflow.target_id)
            if user:
                user.status = 'approved'
        elif workflow.target_type == 'improvement_request':
            improvement = ImprovementRequest.query.get(workflow.target_id)
            if improvement:
                improvement.status = 'approved'
                improvement.reviewed_at = datetime.utcnow()
                improvement.reviewed_by = current_user.id
        elif workflow.target_type == 'ai_suggestion':
            suggestion = AIImprovementSuggestion.query.get(workflow.target_id)
            if suggestion:
                suggestion.status = 'approved'
                suggestion.reviewed_at = datetime.utcnow()
                suggestion.reviewed_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '워크플로우가 성공적으로 승인되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"워크플로우 승인 오류: {str(e)}")
        return jsonify({'error': '워크플로우 승인 중 오류가 발생했습니다.'}), 500


@approval_workflow_bp.route('/workflows/<int:workflow_id>/reject', methods=['POST'])
@login_required
def reject_workflow(workflow_id):
    """승인 워크플로우 거절"""
    try:
        workflow = ApprovalWorkflow.query.get_or_404(workflow_id)
        
        # 권한 확인
        if current_user.role not in ['admin', 'super_admin']:
            if workflow.approver_id != current_user.id:
                return jsonify({'error': '거절 권한이 없습니다.'}), 403
        
        # 상태 확인
        if workflow.status != 'pending':
            return jsonify({'error': '이미 처리된 워크플로우입니다.'}), 400
        
        data = request.get_json()
        comments = data.get('comments', '')
        
        # 워크플로우 거절
        workflow.status = 'rejected'
        workflow.approval_data = {
            'rejected_by': current_user.id,
            'rejected_at': datetime.utcnow().isoformat(),
            'comments': comments
        }
        workflow.rejected_at = datetime.utcnow()
        workflow.comments = comments
        
        # 대상 객체 상태 업데이트
        if workflow.target_type == 'user':
            user = User.query.get(workflow.target_id)
            if user:
                user.status = 'rejected'
        elif workflow.target_type == 'improvement_request':
            improvement = ImprovementRequest.query.get(workflow.target_id)
            if improvement:
                improvement.status = 'rejected'
                improvement.reviewed_at = datetime.utcnow()
                improvement.reviewed_by = current_user.id
        elif workflow.target_type == 'ai_suggestion':
            suggestion = AIImprovementSuggestion.query.get(workflow.target_id)
            if suggestion:
                suggestion.status = 'rejected'
                suggestion.reviewed_at = datetime.utcnow()
                suggestion.reviewed_by = current_user.id
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '워크플로우가 성공적으로 거절되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"워크플로우 거절 오류: {str(e)}")
        return jsonify({'error': '워크플로우 거절 중 오류가 발생했습니다.'}), 500


@approval_workflow_bp.route('/workflows', methods=['POST'])
@login_required
def create_workflow():
    """새 승인 워크플로우 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['workflow_type', 'target_type', 'target_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 대상 객체 존재 확인
        if data['target_type'] == 'user':
            target = User.query.get(data['target_id'])
        elif data['target_type'] == 'improvement_request':
            target = ImprovementRequest.query.get(data['target_id'])
        elif data['target_type'] == 'ai_suggestion':
            target = AIImprovementSuggestion.query.get(data['target_id'])
        else:
            return jsonify({'error': '지원하지 않는 대상 타입입니다.'}), 400
        
        if not target:
            return jsonify({'error': '대상 객체를 찾을 수 없습니다.'}), 404
        
        # 승인자 설정
        approver_id = data.get('approver_id')
        if not approver_id:
            # 기본 승인자 설정 (관리자 중 첫 번째)
            approver = User.query.filter_by(role='admin').first()
            if approver:
                approver_id = approver.id
            else:
                return jsonify({'error': '승인자를 찾을 수 없습니다.'}), 400
        
        # 새 워크플로우 생성
        new_workflow = ApprovalWorkflow()
        new_workflow.workflow_type = data['workflow_type']
        new_workflow.target_type = data['target_type']
        new_workflow.target_id = data['target_id']
        new_workflow.requester_id = current_user.id
        new_workflow.approver_id = approver_id
        new_workflow.request_data = data.get('request_data', {})
        new_workflow.status = 'pending'
        
        db.session.add(new_workflow)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '승인 워크플로우가 성공적으로 생성되었습니다.',
            'workflow_id': new_workflow.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"승인 워크플로우 생성 오류: {str(e)}")
        return jsonify({'error': '승인 워크플로우 생성 중 오류가 발생했습니다.'}), 500


@approval_workflow_bp.route('/workflows/pending', methods=['GET'])
@login_required
def get_pending_workflows():
    """대기 중인 승인 워크플로우 조회"""
    try:
        query = ApprovalWorkflow.query.filter_by(status='pending')
        
        # 사용자별 필터링
        if current_user.role in ['admin', 'super_admin']:
            # 관리자는 모든 대기 중인 워크플로우 조회 가능
            pass
        else:
            # 일반 사용자는 자신이 승인해야 할 워크플로우만 조회
            query = query.filter_by(approver_id=current_user.id)
        
        workflows = query.order_by(ApprovalWorkflow.created_at.asc()).all()
        
        workflow_list = []
        for workflow in workflows:
            workflow_data = {
                'id': workflow.id,
                'workflow_type': workflow.workflow_type,
                'target_type': workflow.target_type,
                'target_id': workflow.target_id,
                'requester_name': workflow.requester.name if workflow.requester else None,
                'created_at': workflow.created_at.isoformat() if workflow.created_at else None,
                'request_data': workflow.request_data
            }
            workflow_list.append(workflow_data)
        
        return jsonify({
            'success': True,
            'workflows': workflow_list,
            'total': len(workflow_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"대기 중인 워크플로우 조회 오류: {str(e)}")
        return jsonify({'error': '대기 중인 워크플로우를 불러오는 중 오류가 발생했습니다.'}), 500 