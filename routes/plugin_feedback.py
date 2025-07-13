#!/usr/bin/env python3
"""
플러그인 피드백 시스템 API
리뷰, 버그 리포트, 기능 요청 관리
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime
from models import db, PluginReview, PluginBugReport, PluginFeatureRequest, Module, User
from sqlalchemy import desc
import json

plugin_feedback_bp = Blueprint('plugin_feedback', __name__)

# ==================== 플러그인 리뷰 API ====================

@plugin_feedback_bp.route('/plugins/<plugin_id>/reviews', methods=['GET'])
@login_required
def get_plugin_reviews(plugin_id):
    """플러그인 리뷰 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        rating_filter = request.args.get('rating', type=int)
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 쿼리 구성
        query = PluginReview.query.filter_by(plugin_id=plugin_id, status='active')
        
        # 평점 필터
        if rating_filter:
            query = query.filter_by(rating=rating_filter)
        
        # 정렬
        if sort_by == 'rating':
            order_column = PluginReview.rating
        elif sort_by == 'helpful_count':
            order_column = PluginReview.helpful_count
        else:
            order_column = PluginReview.created_at
            
        if sort_order == 'asc':
            query = query.order_by(order_column)
        else:
            query = query.order_by(desc(order_column))
        
        # 페이지네이션
        reviews = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # 통계 계산
        total_reviews = PluginReview.query.filter_by(plugin_id=plugin_id, status='active').count()
        avg_rating = db.session.query(db.func.avg(PluginReview.rating)).filter_by(
            plugin_id=plugin_id, status='active'
        ).scalar() or 0
        
        rating_distribution = db.session.query(
            PluginReview.rating, db.func.count(PluginReview.id)
        ).filter_by(plugin_id=plugin_id, status='active').group_by(PluginReview.rating).all()
        
        return jsonify({
            'success': True,
            'data': {
                'reviews': [{
                    'id': review.id,
                    'user_name': review.user.username,
                    'rating': review.rating,
                    'title': review.title,
                    'content': review.content,
                    'helpful_count': review.helpful_count,
                    'created_at': review.created_at.isoformat(),
                    'is_public': review.is_public
                } for review in reviews.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': reviews.total,
                    'pages': reviews.pages
                },
                'stats': {
                    'total_reviews': total_reviews,
                    'average_rating': round(float(avg_rating), 1),
                    'rating_distribution': dict(rating_distribution)
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"리뷰 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/plugins/<plugin_id>/reviews', methods=['POST'])
@login_required
def create_plugin_review(plugin_id):
    """플러그인 리뷰 작성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['rating', 'title', 'content']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400
        
        # 평점 범위 검증
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'error': '평점은 1-5 사이의 정수여야 합니다'}), 400
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 기존 리뷰 확인 (사용자당 하나만)
        existing_review = PluginReview.query.filter_by(
            plugin_id=plugin_id, user_id=current_user.id
        ).first()
        
        if existing_review:
            return jsonify({'success': False, 'error': '이미 리뷰를 작성했습니다'}), 400
        
        # 리뷰 생성
        review = PluginReview(
            plugin_id=plugin_id,
            user_id=current_user.id,
            version=plugin.version,
            rating=rating,
            title=data['title'],
            content=data['content'],
            is_public=data.get('is_public', True)
        )
        
        db.session.add(review)
        db.session.commit()
        
        # 플러그인 평점 업데이트
        update_plugin_rating(plugin_id)
        
        return jsonify({
            'success': True,
            'message': '리뷰가 작성되었습니다',
            'data': {
                'id': review.id,
                'rating': review.rating,
                'title': review.title,
                'content': review.content,
                'created_at': review.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"리뷰 작성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/reviews/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    """리뷰 도움됨 표시"""
    try:
        review = PluginReview.query.get(review_id)
        if not review:
            return jsonify({'success': False, 'error': '리뷰를 찾을 수 없습니다'}), 404
        
        # 도움됨 카운트 증가
        review.helpful_count += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '도움됨으로 표시되었습니다',
            'helpful_count': review.helpful_count
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"리뷰 도움됨 표시 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 플러그인 버그 리포트 API ====================

@plugin_feedback_bp.route('/plugins/<plugin_id>/bugs', methods=['GET'])
@login_required
def get_plugin_bugs(plugin_id):
    """플러그인 버그 리포트 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        severity_filter = request.args.get('severity')
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 쿼리 구성
        query = PluginBugReport.query.filter_by(plugin_id=plugin_id)
        
        # 필터 적용
        if status_filter:
            query = query.filter_by(status=status_filter)
        if severity_filter:
            query = query.filter_by(severity=severity_filter)
        
        # 관리자가 아닌 경우 자신의 버그 리포트만 조회
        if not current_user.is_admin():
            query = query.filter_by(reporter_id=current_user.id)
        
        # 정렬 (최신순)
        query = query.order_by(desc(PluginBugReport.created_at))
        
        # 페이지네이션
        bugs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'bugs': [{
                    'id': bug.id,
                    'title': bug.title,
                    'severity': bug.severity,
                    'status': bug.status,
                    'priority': bug.priority,
                    'reporter_name': bug.reporter.username,
                    'created_at': bug.created_at.isoformat(),
                    'updated_at': bug.updated_at.isoformat(),
                    'is_public': bug.is_public
                } for bug in bugs.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': bugs.total,
                    'pages': bugs.pages
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"버그 리포트 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/plugins/<plugin_id>/bugs', methods=['POST'])
@login_required
def create_plugin_bug(plugin_id):
    """플러그인 버그 리포트 작성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['title', 'description', 'severity']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400
        
        # 심각도 검증
        severity = data['severity']
        if severity not in ['low', 'medium', 'high', 'critical']:
            return jsonify({'success': False, 'error': '유효하지 않은 심각도입니다'}), 400
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 버그 리포트 생성
        bug = PluginBugReport(
            plugin_id=plugin_id,
            reporter_id=current_user.id,
            version=plugin.version,
            title=data['title'],
            description=data['description'],
            severity=severity,
            priority=data.get('priority', 'normal'),
            steps_to_reproduce=data.get('steps_to_reproduce'),
            expected_behavior=data.get('expected_behavior'),
            actual_behavior=data.get('actual_behavior'),
            environment=data.get('environment'),
            attachments=data.get('attachments', []),
            is_public=data.get('is_public', False)
        )
        
        db.session.add(bug)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '버그 리포트가 작성되었습니다',
            'data': {
                'id': bug.id,
                'title': bug.title,
                'severity': bug.severity,
                'status': bug.status,
                'created_at': bug.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"버그 리포트 작성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/bugs/<int:bug_id>', methods=['GET'])
@login_required
def get_plugin_bug(bug_id):
    """플러그인 버그 리포트 상세 조회"""
    try:
        bug = PluginBugReport.query.get(bug_id)
        if not bug:
            return jsonify({'success': False, 'error': '버그 리포트를 찾을 수 없습니다'}), 404
        
        # 권한 확인 (관리자이거나 작성자만 조회 가능)
        if not current_user.is_admin() and bug.reporter_id != current_user.id:
            return jsonify({'success': False, 'error': '접근 권한이 없습니다'}), 403
        
        return jsonify({
            'success': True,
            'data': {
                'id': bug.id,
                'plugin_id': bug.plugin_id,
                'title': bug.title,
                'description': bug.description,
                'severity': bug.severity,
                'status': bug.status,
                'priority': bug.priority,
                'steps_to_reproduce': bug.steps_to_reproduce,
                'expected_behavior': bug.expected_behavior,
                'actual_behavior': bug.actual_behavior,
                'environment': bug.environment,
                'attachments': bug.attachments,
                'reporter_name': bug.reporter.username,
                'created_at': bug.created_at.isoformat(),
                'updated_at': bug.updated_at.isoformat(),
                'resolved_at': bug.resolved_at.isoformat() if bug.resolved_at else None
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"버그 리포트 상세 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 플러그인 기능 요청 API ====================

@plugin_feedback_bp.route('/plugins/<plugin_id>/features', methods=['GET'])
@login_required
def get_plugin_features(plugin_id):
    """플러그인 기능 요청 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        status_filter = request.args.get('status')
        sort_by = request.args.get('sort_by', 'votes')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 쿼리 구성
        query = PluginFeatureRequest.query.filter_by(plugin_id=plugin_id)
        
        # 상태 필터
        if status_filter:
            query = query.filter_by(status=status_filter)
        
        # 정렬
        if sort_by == 'votes':
            order_column = PluginFeatureRequest.votes
        elif sort_by == 'created_at':
            order_column = PluginFeatureRequest.created_at
        else:
            order_column = PluginFeatureRequest.votes
            
        if sort_order == 'asc':
            query = query.order_by(order_column)
        else:
            query = query.order_by(desc(order_column))
        
        # 페이지네이션
        features = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'features': [{
                    'id': feature.id,
                    'title': feature.title,
                    'description': feature.description,
                    'status': feature.status,
                    'priority': feature.priority,
                    'votes': feature.votes,
                    'requester_name': feature.requester.username,
                    'created_at': feature.created_at.isoformat(),
                    'updated_at': feature.updated_at.isoformat(),
                    'is_public': feature.is_public
                } for feature in features.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': features.total,
                    'pages': features.pages
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"기능 요청 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/plugins/<plugin_id>/features', methods=['POST'])
@login_required
def create_plugin_feature(plugin_id):
    """플러그인 기능 요청 작성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['title', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'error': f'{field}은 필수입니다'}), 400
        
        # 플러그인 존재 확인
        plugin = Module.query.get(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'error': '플러그인을 찾을 수 없습니다'}), 404
        
        # 기능 요청 생성
        feature = PluginFeatureRequest(
            plugin_id=plugin_id,
            requester_id=current_user.id,
            title=data['title'],
            description=data['description'],
            priority=data.get('priority', 'normal'),
            is_public=data.get('is_public', True)
        )
        
        db.session.add(feature)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '기능 요청이 작성되었습니다',
            'data': {
                'id': feature.id,
                'title': feature.title,
                'status': feature.status,
                'votes': feature.votes,
                'created_at': feature.created_at.isoformat()
            }
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"기능 요청 작성 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/features/<int:feature_id>/vote', methods=['POST'])
@login_required
def vote_feature_request(feature_id):
    """기능 요청 투표"""
    try:
        feature = PluginFeatureRequest.query.get(feature_id)
        if not feature:
            return jsonify({'success': False, 'error': '기능 요청을 찾을 수 없습니다'}), 404
        
        # 투표 수 증가
        feature.votes += 1
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '투표가 완료되었습니다',
            'votes': feature.votes
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"기능 요청 투표 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 관리자 API ====================

@plugin_feedback_bp.route('/admin/bugs', methods=['GET'])
@login_required
def admin_get_all_bugs():
    """관리자용 전체 버그 리포트 조회"""
    try:
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': '관리자 권한이 필요합니다'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')
        severity_filter = request.args.get('severity')
        plugin_filter = request.args.get('plugin_id')
        
        query = PluginBugReport.query
        
        # 필터 적용
        if status_filter:
            query = query.filter_by(status=status_filter)
        if severity_filter:
            query = query.filter_by(severity=severity_filter)
        if plugin_filter:
            query = query.filter_by(plugin_id=plugin_filter)
        
        # 정렬 (최신순)
        query = query.order_by(desc(PluginBugReport.created_at))
        
        # 페이지네이션
        bugs = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'success': True,
            'data': {
                'bugs': [{
                    'id': bug.id,
                    'plugin_id': bug.plugin_id,
                    'plugin_name': bug.plugin.name if bug.plugin else 'Unknown',
                    'title': bug.title,
                    'severity': bug.severity,
                    'status': bug.status,
                    'priority': bug.priority,
                    'reporter_name': bug.reporter.username,
                    'created_at': bug.created_at.isoformat(),
                    'updated_at': bug.updated_at.isoformat()
                } for bug in bugs.items],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': bugs.total,
                    'pages': bugs.pages
                }
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"관리자 버그 리포트 조회 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@plugin_feedback_bp.route('/admin/bugs/<int:bug_id>/status', methods=['PUT'])
@login_required
def admin_update_bug_status(bug_id):
    """관리자용 버그 리포트 상태 업데이트"""
    try:
        if not current_user.is_admin():
            return jsonify({'success': False, 'error': '관리자 권한이 필요합니다'}), 403
        
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': '상태는 필수입니다'}), 400
        
        if new_status not in ['open', 'in_progress', 'resolved', 'closed']:
            return jsonify({'success': False, 'error': '유효하지 않은 상태입니다'}), 400
        
        bug = PluginBugReport.query.get(bug_id)
        if not bug:
            return jsonify({'success': False, 'error': '버그 리포트를 찾을 수 없습니다'}), 404
        
        # 상태 업데이트
        bug.status = new_status
        if new_status == 'resolved':
            bug.resolved_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '상태가 업데이트되었습니다',
            'status': bug.status
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"버그 리포트 상태 업데이트 오류: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ==================== 유틸리티 함수 ====================

def update_plugin_rating(plugin_id):
    """플러그인 평점 업데이트"""
    try:
        # 평균 평점 계산
        avg_rating = db.session.query(db.func.avg(PluginReview.rating)).filter_by(
            plugin_id=plugin_id, status='active'
        ).scalar()
        
        if avg_rating:
            # 플러그인 정보 업데이트
            plugin = Module.query.get(plugin_id)
            if plugin:
                # 플러그인 메타데이터에 평점 정보 추가
                if not hasattr(plugin, 'metadata') or not plugin.metadata:
                    plugin.metadata = {}
                
                plugin.metadata['rating'] = round(float(avg_rating), 1)
                plugin.metadata['rating_count'] = PluginReview.query.filter_by(
                    plugin_id=plugin_id, status='active'
                ).count()
                
                db.session.commit()
                
    except Exception as e:
        current_app.logger.error(f"플러그인 평점 업데이트 오류: {e}")
        db.session.rollback() 