from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import json

from extensions import db
from models import Brand, Branch, User, AIDiagnosis, ImprovementRequest, AIImprovementSuggestion, SystemHealth, ApprovalWorkflow

ai_management_bp = Blueprint('ai_management', __name__)


@ai_management_bp.route('/diagnoses', methods=['GET'])
@login_required
def get_diagnoses():
    """AI 진단 결과 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 필터링 옵션
        brand_id = request.args.get('brand_id')
        store_id = request.args.get('store_id')
        status = request.args.get('status')
        diagnosis_type = request.args.get('type')
        severity = request.args.get('severity')
        
        query = AIDiagnosis.query
        
        # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 진단만 조회
        if current_user.role == 'brand_manager':
            query = query.filter_by(brand_id=current_user.brand_id)
        elif current_user.role in ['admin', 'super_admin']:
            pass
        else:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        if store_id:
            query = query.filter_by(store_id=store_id)
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
                'brand_id': diagnosis.brand_id,
                'brand_name': diagnosis.brand.name if diagnosis.brand else None,
                'store_id': diagnosis.store_id,
                'store_name': diagnosis.store.name if diagnosis.store else None,
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
        current_app.logger.error(f"AI 진단 결과 조회 오류: {str(e)}")
        return jsonify({'error': '진단 결과를 불러오는 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/diagnoses/<int:diagnosis_id>', methods=['GET'])
@login_required
def get_diagnosis(diagnosis_id):
    """특정 AI 진단 결과 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        diagnosis = AIDiagnosis.query.get_or_404(diagnosis_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 진단 결과만 조회 가능
        if current_user.role == 'brand_manager' and diagnosis.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        diagnosis_data = {
            'id': diagnosis.id,
            'title': diagnosis.title,
            'description': diagnosis.description,
            'diagnosis_type': diagnosis.diagnosis_type,
            'severity': diagnosis.severity,
            'status': diagnosis.status,
            'priority': diagnosis.priority,
            'findings': diagnosis.findings,
            'recommendations': diagnosis.recommendations,
            'brand_id': diagnosis.brand_id,
            'brand_name': diagnosis.brand.name if diagnosis.brand else None,
            'store_id': diagnosis.store_id,
            'store_name': diagnosis.store.name if diagnosis.store else None,
            'created_at': diagnosis.created_at.isoformat() if diagnosis.created_at else None,
            'updated_at': diagnosis.updated_at.isoformat() if diagnosis.updated_at else None,
            'reviewed_at': diagnosis.reviewed_at.isoformat() if diagnosis.reviewed_at else None,
            'implemented_at': diagnosis.implemented_at.isoformat() if diagnosis.implemented_at else None,
            'reviewer_name': diagnosis.reviewer.name if diagnosis.reviewer else None,
            'implementer_name': diagnosis.implementer.name if diagnosis.implementer else None
        }
        
        return jsonify({
            'success': True,
            'diagnosis': diagnosis_data
        })
    
    except Exception as e:
        current_app.logger.error(f"AI 진단 결과 상세 조회 오류: {str(e)}")
        return jsonify({'error': '진단 결과를 불러오는 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/diagnoses/<int:diagnosis_id>', methods=['PUT'])
@login_required
def update_diagnosis(diagnosis_id):
    """AI 진단 결과 상태 업데이트"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        diagnosis = AIDiagnosis.query.get_or_404(diagnosis_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 진단 결과만 수정 가능
        if current_user.role == 'brand_manager' and diagnosis.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        if 'status' in data:
            diagnosis.status = data['status']
            if data['status'] == 'reviewed':
                diagnosis.reviewed_at = datetime.utcnow()
                diagnosis.reviewed_by = current_user.id
            elif data['status'] == 'implemented':
                diagnosis.implemented_at = datetime.utcnow()
                diagnosis.implemented_by = current_user.id
        
        if 'priority' in data:
            diagnosis.priority = data['priority']
        
        diagnosis.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '진단 결과가 성공적으로 업데이트되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"AI 진단 결과 업데이트 오류: {str(e)}")
        return jsonify({'error': '진단 결과 업데이트 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/improvements', methods=['GET'])
@login_required
def get_improvements():
    """개선 요청 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 필터링 옵션
        brand_id = request.args.get('brand_id')
        store_id = request.args.get('store_id')
        status = request.args.get('status')
        category = request.args.get('category')
        priority = request.args.get('priority')
        
        query = ImprovementRequest.query
        
        # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 개선 요청만 조회
        if current_user.role == 'brand_manager':
            query = query.filter_by(brand_id=current_user.brand_id)
        elif current_user.role in ['admin', 'super_admin']:
            pass
        else:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        if store_id:
            query = query.filter_by(store_id=store_id)
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
                'brand_id': improvement.brand_id,
                'brand_name': improvement.brand.name if improvement.brand else None,
                'store_id': improvement.store_id,
                'store_name': improvement.store.name if improvement.store else None,
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
        current_app.logger.error(f"개선 요청 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/improvements', methods=['POST'])
@login_required
def create_improvement():
    """새 개선 요청 생성"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'create'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['title', 'description', 'category']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} 필드는 필수입니다.'}), 400
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드에만 개선 요청 생성 가능
        if current_user.role == 'brand_manager':
            if not data.get('brand_id') or data['brand_id'] != current_user.brand_id:
                return jsonify({'error': '자신이 관리하는 브랜드에만 개선 요청을 생성할 수 있습니다.'}), 403
        
        # 새 개선 요청 생성
        new_improvement = ImprovementRequest()
        new_improvement.brand_id = data.get('brand_id')
        new_improvement.store_id = data.get('store_id')
        new_improvement.requester_id = current_user.id
        new_improvement.category = data['category']
        new_improvement.title = data['title']
        new_improvement.description = data['description']
        new_improvement.current_issue = data.get('current_issue')
        new_improvement.proposed_solution = data.get('proposed_solution')
        new_improvement.expected_benefits = data.get('expected_benefits')
        new_improvement.priority = data.get('priority', 'normal')
        new_improvement.estimated_cost = data.get('estimated_cost')
        new_improvement.estimated_time = data.get('estimated_time')
        
        db.session.add(new_improvement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 생성되었습니다.',
            'improvement_id': new_improvement.id
        }), 201
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 생성 오류: {str(e)}")
        return jsonify({'error': '개선 요청 생성 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/improvements/<int:improvement_id>', methods=['GET'])
@login_required
def get_improvement(improvement_id):
    """특정 개선 요청 상세 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        improvement = ImprovementRequest.query.get_or_404(improvement_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 개선 요청만 조회 가능
        if current_user.role == 'brand_manager' and improvement.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        improvement_data = {
            'id': improvement.id,
            'title': improvement.title,
            'description': improvement.description,
            'category': improvement.category,
            'priority': improvement.priority,
            'status': improvement.status,
            'current_issue': improvement.current_issue,
            'proposed_solution': improvement.proposed_solution,
            'expected_benefits': improvement.expected_benefits,
            'estimated_cost': improvement.estimated_cost,
            'estimated_time': improvement.estimated_time,
            'brand_id': improvement.brand_id,
            'brand_name': improvement.brand.name if improvement.brand else None,
            'store_id': improvement.store_id,
            'store_name': improvement.store.name if improvement.store else None,
            'requester_name': improvement.requester.name if improvement.requester else None,
            'created_at': improvement.created_at.isoformat() if improvement.created_at else None,
            'updated_at': improvement.updated_at.isoformat() if improvement.updated_at else None,
            'reviewed_at': improvement.reviewed_at.isoformat() if improvement.reviewed_at else None,
            'admin_comment': improvement.admin_comment,
            'reviewer_name': improvement.reviewer.name if improvement.reviewer else None
        }
        
        return jsonify({
            'success': True,
            'improvement': improvement_data
        })
    
    except Exception as e:
        current_app.logger.error(f"개선 요청 상세 조회 오류: {str(e)}")
        return jsonify({'error': '개선 요청을 불러오는 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/improvements/<int:improvement_id>', methods=['PUT'])
@login_required
def update_improvement(improvement_id):
    """개선 요청 상태 업데이트"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        improvement = ImprovementRequest.query.get_or_404(improvement_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 개선 요청만 수정 가능
        if current_user.role == 'brand_manager' and improvement.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        if 'status' in data:
            improvement.status = data['status']
            if data['status'] in ['under_review', 'approved', 'rejected']:
                improvement.reviewed_at = datetime.utcnow()
                improvement.reviewed_by = current_user.id
        
        if 'admin_comment' in data:
            improvement.admin_comment = data['admin_comment']
        
        if 'priority' in data:
            improvement.priority = data['priority']
        
        improvement.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '개선 요청이 성공적으로 업데이트되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"개선 요청 업데이트 오류: {str(e)}")
        return jsonify({'error': '개선 요청 업데이트 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/suggestions', methods=['GET'])
@login_required
def get_ai_suggestions():
    """AI 개선 제안 목록 조회"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'view'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        # 필터링 옵션
        brand_id = request.args.get('brand_id')
        store_id = request.args.get('store_id')
        status = request.args.get('status')
        suggestion_type = request.args.get('type')
        
        query = AIImprovementSuggestion.query
        
        # [브랜드별 필터링] 브랜드 관리자는 자신의 브랜드 제안만 조회
        if current_user.role == 'brand_manager':
            query = query.filter_by(brand_id=current_user.brand_id)
        elif current_user.role in ['admin', 'super_admin']:
            pass
        else:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        
        if store_id:
            query = query.filter_by(store_id=store_id)
        if status:
            query = query.filter_by(status=status)
        if suggestion_type:
            query = query.filter_by(suggestion_type=suggestion_type)
        
        suggestions = query.order_by(AIImprovementSuggestion.created_at.desc()).all()
        
        suggestion_list = []
        for suggestion in suggestions:
            suggestion_data = {
                'id': suggestion.id,
                'title': suggestion.title,
                'suggestion_type': suggestion.suggestion_type,
                'status': suggestion.status,
                'estimated_effort': suggestion.estimated_effort,
                'estimated_roi': suggestion.estimated_roi,
                'confidence_score': suggestion.confidence_score,
                'brand_id': suggestion.brand_id,
                'brand_name': suggestion.brand.name if suggestion.brand else None,
                'store_id': suggestion.store_id,
                'store_name': suggestion.store.name if suggestion.store else None,
                'created_at': suggestion.created_at.isoformat() if suggestion.created_at else None
            }
            suggestion_list.append(suggestion_data)
        
        return jsonify({
            'success': True,
            'suggestions': suggestion_list,
            'total': len(suggestion_list)
        })
    
    except Exception as e:
        current_app.logger.error(f"AI 개선 제안 조회 오류: {str(e)}")
        return jsonify({'error': 'AI 개선 제안을 불러오는 중 오류가 발생했습니다.'}), 500


@ai_management_bp.route('/suggestions/<int:suggestion_id>', methods=['PUT'])
@login_required
def update_ai_suggestion(suggestion_id):
    """AI 개선 제안 상태 업데이트"""
    try:
        # 권한 확인
        if not current_user.has_permission('ai_management', 'edit'):
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        suggestion = AIImprovementSuggestion.query.get_or_404(suggestion_id)
        
        # 브랜드 매니저인 경우 자신이 관리하는 브랜드의 제안만 수정 가능
        if current_user.role == 'brand_manager' and suggestion.brand_id != current_user.brand_id:
            return jsonify({'error': '권한이 없습니다.'}), 403
        
        data = request.get_json()
        
        # 업데이트 가능한 필드들
        if 'status' in data:
            suggestion.status = data['status']
            if data['status'] in ['approved', 'rejected']:
                suggestion.reviewed_at = datetime.utcnow()
                suggestion.reviewed_by = current_user.id
        
        if 'admin_comment' in data:
            suggestion.admin_comment = data['admin_comment']
        
        suggestion.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'AI 개선 제안이 성공적으로 업데이트되었습니다.'
        })
    
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"AI 개선 제안 업데이트 오류: {str(e)}")
        return jsonify({'error': 'AI 개선 제안 업데이트 중 오류가 발생했습니다.'}), 500 