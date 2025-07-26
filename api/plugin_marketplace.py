from flask import Blueprint, jsonify, request, current_app
from flask_cors import cross_origin
from datetime import datetime
import json
import os
import hashlib
from models.plugin_models import Plugin, PluginInstallation, PluginReview, PluginUpdate, PluginUsage
from models_main import db, Brand, Branch, User
import logging

# 로깅 설정
logger = logging.getLogger(__name__)

# Blueprint 생성
plugin_marketplace_bp = Blueprint('plugin_marketplace', __name__)

@plugin_marketplace_bp.route('/api/plugin/market', methods=['GET'])
@cross_origin()
def get_marketplace_plugins():
    """플러그인 마켓플레이스 목록 조회"""
    try:
        # 쿼리 파라미터 처리
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category = request.args.get('category', 'all')
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'download_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 기본 쿼리
        query = Plugin.query.filter(Plugin.is_active == True)
        
        # 카테고리 필터
        if category != 'all':
            query = query.filter(Plugin.category == category)
        
        # 검색 필터
        if search:
            query = query.filter(
                (Plugin.display_name.contains(search)) |
                (Plugin.description.contains(search)) |
                (Plugin.tags.contains([search]))
            )
        
        # 정렬
        if sort_by == 'download_count':
            query = query.order_by(Plugin.download_count.desc() if sort_order == 'desc' else Plugin.download_count.asc())
        elif sort_by == 'rating':
            query = query.order_by(Plugin.rating.desc() if sort_order == 'desc' else Plugin.rating.asc())
        elif sort_by == 'created_at':
            query = query.order_by(Plugin.created_at.desc() if sort_order == 'desc' else Plugin.created_at.asc())
        elif sort_by == 'name':
            query = query.order_by(Plugin.display_name.asc() if sort_order == 'asc' else Plugin.display_name.desc())
        
        # 페이지네이션
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        plugins = []
        for plugin in pagination.items:
            plugin_data = {
                'id': plugin.id,
                'name': plugin.name,
                'display_name': plugin.display_name,
                'description': plugin.description,
                'version': plugin.version,
                'author': plugin.author,
                'category': plugin.category,
                'tags': plugin.tags,
                'ui_schema': plugin.ui_schema,
                'icon': plugin.icon,
                'menu_position': plugin.menu_position,
                'is_installed': plugin.is_installed,
                'file_size': plugin.file_size,
                'download_count': plugin.download_count,
                'rating': plugin.rating,
                'review_count': plugin.review_count,
                'created_at': plugin.created_at.isoformat() if plugin.created_at else None,
                'updated_at': plugin.updated_at.isoformat() if plugin.updated_at else None
            }
            plugins.append(plugin_data)
        
        return jsonify({
            'success': True,
            'data': {
                'plugins': plugins,
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 마켓플레이스 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 목록을 불러오는 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/<int:plugin_id>', methods=['GET'])
@cross_origin()
def get_plugin_detail(plugin_id):
    """플러그인 상세 정보 조회"""
    try:
        plugin = Plugin.query.get_or_404(plugin_id)
        
        # 리뷰 조회
        reviews = PluginReview.query.filter_by(plugin_id=plugin_id).order_by(PluginReview.created_at.desc()).limit(10).all()
        reviews_data = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user_id': review.user_id,
                'rating': review.rating,
                'title': review.title,
                'content': review.content,
                'is_verified': review.is_verified,
                'created_at': review.created_at.isoformat() if review.created_at else None
            })
        
        # 설치 정보 조회
        installations = PluginInstallation.query.filter_by(plugin_id=plugin_id).all()
        installation_count = len(installations)
        
        # 최신 업데이트 정보
        latest_update = PluginUpdate.query.filter_by(plugin_id=plugin_id).order_by(PluginUpdate.created_at.desc()).first()
        update_info = None
        if latest_update:
            update_info = {
                'from_version': latest_update.from_version,
                'to_version': latest_update.to_version,
                'changelog': latest_update.changelog,
                'update_type': latest_update.update_type,
                'created_at': latest_update.created_at.isoformat() if latest_update.created_at else None
            }
        
        plugin_data = {
            'id': plugin.id,
            'name': plugin.name,
            'display_name': plugin.display_name,
            'description': plugin.description,
            'version': plugin.version,
            'author': plugin.author,
            'category': plugin.category,
            'tags': plugin.tags,
            'ui_schema': plugin.ui_schema,
            'icon': plugin.icon,
            'menu_position': plugin.menu_position,
            'is_installed': plugin.is_installed,
            'file_path': plugin.file_path,
            'file_size': plugin.file_size,
            'checksum': plugin.checksum,
            'download_count': plugin.download_count,
            'rating': plugin.rating,
            'review_count': plugin.review_count,
            'installation_count': installation_count,
            'reviews': reviews_data,
            'latest_update': update_info,
            'created_at': plugin.created_at.isoformat() if plugin.created_at else None,
            'updated_at': plugin.updated_at.isoformat() if plugin.updated_at else None
        }
        
        return jsonify({
            'success': True,
            'data': plugin_data
        })
        
    except Exception as e:
        logger.error(f"플러그인 상세 정보 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 정보를 불러오는 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/install', methods=['POST'])
@cross_origin()
def install_plugin():
    """플러그인 설치 - 임시 더미 데이터"""
    try:
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        brand_id = data.get('brand_id')
        branch_id = data.get('branch_id')
        user_id = data.get('user_id', 1)  # 임시로 기본값 사용
        
        if not plugin_id:
            return jsonify({
                'success': False,
                'error': '플러그인 ID가 필요합니다.'
            }), 400
        
        # 임시로 더미 응답 반환
        plugin_names = {
            1: 'AI 스케줄 최적화',
            2: '리뷰 자동 요약',
            3: 'QSC 자동 분석'
        }
        
        plugin_name = plugin_names.get(plugin_id, f'플러그인 {plugin_id}')
        installation_id = f'install_{plugin_id}_{12345}'
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin_name}이(가) 성공적으로 설치되었습니다.',
            'installation_id': installation_id
        })
        
    except Exception as e:
        logger.error(f"플러그인 설치 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 설치 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/uninstall', methods=['POST'])
@cross_origin()
def uninstall_plugin():
    """플러그인 제거"""
    try:
        data = request.get_json()
        installation_id = data.get('installation_id')
        user_id = data.get('user_id', 1)  # 임시로 기본값 사용
        
        if not installation_id:
            return jsonify({
                'success': False,
                'error': '설치 ID가 필요합니다.'
            }), 400
        
        # 설치 정보 조회
        installation = PluginInstallation.query.get_or_404(installation_id)
        plugin = Plugin.query.get(installation.plugin_id)
        
        # 설치 상태 변경
        installation.is_active = False
        installation.status = 'uninstalled'
        
        # 사용 기록 생성
        usage = PluginUsage(
            plugin_id=installation.plugin_id,
            installation_id=installation_id,
            action='uninstall',
            user_id=user_id,
            metadata={'brand_id': installation.brand_id, 'branch_id': installation.branch_id}
        )
        db.session.add(usage)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin.display_name}이(가) 성공적으로 제거되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"플러그인 제거 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 제거 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/update', methods=['POST'])
@cross_origin()
def update_plugin():
    """플러그인 업데이트"""
    try:
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        installation_id = data.get('installation_id')
        user_id = data.get('user_id', 1)  # 임시로 기본값 사용
        
        if not plugin_id or not installation_id:
            return jsonify({
                'success': False,
                'error': '플러그인 ID와 설치 ID가 필요합니다.'
            }), 400
        
        # 플러그인과 설치 정보 조회
        plugin = Plugin.query.get_or_404(plugin_id)
        installation = PluginInstallation.query.get_or_404(installation_id)
        
        # 최신 업데이트 정보 조회
        latest_update = PluginUpdate.query.filter_by(plugin_id=plugin_id).order_by(PluginUpdate.created_at.desc()).first()
        
        if not latest_update:
            return jsonify({
                'success': False,
                'error': '업데이트 정보를 찾을 수 없습니다.'
            }), 404
        
        # 버전 업데이트
        old_version = installation.version
        installation.version = latest_update.to_version
        
        # 사용 기록 생성
        usage = PluginUsage(
            plugin_id=plugin_id,
            installation_id=installation_id,
            action='update',
            user_id=user_id,
            metadata={
                'from_version': old_version,
                'to_version': latest_update.to_version,
                'update_type': latest_update.update_type
            }
        )
        db.session.add(usage)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'플러그인 {plugin.display_name}이(가) {latest_update.to_version}으로 업데이트되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"플러그인 업데이트 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '플러그인 업데이트 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/review', methods=['POST'])
@cross_origin()
def add_plugin_review():
    """플러그인 리뷰 추가/수정"""
    try:
        data = request.get_json()
        plugin_id = data.get('plugin_id')
        user_id = data.get('user_id', 1)  # 임시로 기본값 사용
        rating = data.get('rating')
        title = data.get('title')
        content = data.get('content')
        
        if not plugin_id or not rating:
            return jsonify({
                'success': False,
                'error': '플러그인 ID와 평점이 필요합니다.'
            }), 400
        
        # 기존 리뷰 확인
        existing_review = PluginReview.query.filter_by(
            plugin_id=plugin_id,
            user_id=user_id
        ).first()
        
        if existing_review:
            # 기존 리뷰 수정
            existing_review.rating = rating
            existing_review.title = title
            existing_review.content = content
            existing_review.updated_at = datetime.utcnow()
        else:
            # 새 리뷰 생성
            review = PluginReview(
                plugin_id=plugin_id,
                user_id=user_id,
                rating=rating,
                title=title,
                content=content
            )
            db.session.add(review)
        
        # 플러그인 평점 업데이트
        plugin = Plugin.query.get(plugin_id)
        if plugin:
            reviews = PluginReview.query.filter_by(plugin_id=plugin_id).all()
            if reviews:
                total_rating = sum(review.rating for review in reviews)
                plugin.rating = total_rating / len(reviews)
                plugin.review_count = len(reviews)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '리뷰가 성공적으로 저장되었습니다.'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"플러그인 리뷰 추가 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '리뷰 저장 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/installed', methods=['GET'])
@cross_origin()
def get_installed_plugins():
    """설치된 플러그인 목록 조회"""
    try:
        brand_id = request.args.get('brand_id', type=int)
        branch_id = request.args.get('branch_id', type=int)
        
        query = PluginInstallation.query.filter_by(is_active=True)
        
        if brand_id:
            query = query.filter_by(brand_id=brand_id)
        if branch_id:
            query = query.filter_by(branch_id=branch_id)
        
        installations = query.all()
        
        installed_plugins = []
        for installation in installations:
            plugin = Plugin.query.get(installation.plugin_id)
            if plugin:
                plugin_data = {
                    'id': plugin.id,
                    'name': plugin.name,
                    'display_name': plugin.display_name,
                    'description': plugin.description,
                    'version': installation.version,
                    'author': plugin.author,
                    'category': plugin.category,
                    'ui_schema': plugin.ui_schema,
                    'icon': plugin.icon,
                    'installation_id': installation.id,
                    'installed_at': installation.installed_at.isoformat() if installation.installed_at else None,
                    'settings': installation.settings,
                    'permissions': installation.permissions,
                    'status': installation.status,
                    'last_used': installation.last_used.isoformat() if installation.last_used else None,
                    'usage_count': installation.usage_count
                }
                installed_plugins.append(plugin_data)
        
        return jsonify({
            'success': True,
            'data': {
                'plugins': installed_plugins
            }
        })
        
    except Exception as e:
        logger.error(f"설치된 플러그인 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '설치된 플러그인 목록을 불러오는 중 오류가 발생했습니다.'
        }), 500

@plugin_marketplace_bp.route('/api/plugin/categories', methods=['GET'])
@cross_origin()
def get_plugin_categories():
    """플러그인 카테고리 목록 조회 - 임시 더미 데이터"""
    try:
        # 임시로 더미 데이터 반환
        category_list = [
            {
                'id': 'scheduling',
                'name': '스케줄링',
                'description': '직원 스케줄 및 근무 관리 플러그인',
                'icon': 'fas fa-calendar-alt',
                'plugin_count': 1
            },
            {
                'id': 'customer_management',
                'name': '고객 관리',
                'description': '고객 리뷰 및 피드백 관리 플러그인',
                'icon': 'fas fa-users',
                'plugin_count': 1
            },
            {
                'id': 'quality_management',
                'name': '품질 관리',
                'description': 'QSC 및 품질 관리 플러그인',
                'icon': 'fas fa-clipboard-check',
                'plugin_count': 1
            },
            {
                'id': 'contract_management',
                'name': '계약 관리',
                'description': '계약 및 문서 관리 플러그인',
                'icon': 'fas fa-file-contract',
                'plugin_count': 0
            },
            {
                'id': 'inventory_management',
                'name': '재고 관리',
                'description': '재고 및 발주 관리 플러그인',
                'icon': 'fas fa-boxes',
                'plugin_count': 0
            }
        ]
        
        return jsonify({
            'success': True,
            'data': {
                'categories': category_list
            }
        })
        
    except Exception as e:
        logger.error(f"플러그인 카테고리 조회 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '카테고리 목록을 불러오는 중 오류가 발생했습니다.'
        }), 500 