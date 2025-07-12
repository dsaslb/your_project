"""
고도화된 플러그인 마켓플레이스 API
- 검색/필터/정렬, 상세 정보, 설치/업데이트/삭제, 리뷰/평점, 통계/추천
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
import logging

try:
    from core.backend.enhanced_marketplace import enhanced_marketplace
except ImportError:
    enhanced_marketplace = None

logger = logging.getLogger(__name__)

enhanced_marketplace_bp = Blueprint('enhanced_marketplace', __name__, url_prefix='/api/enhanced-marketplace')

@enhanced_marketplace_bp.route('/plugins', methods=['GET'])
def get_plugins():
    """플러그인 목록 조회 (검색/필터/정렬)"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        # 쿼리 파라미터
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'name')
        sort_order = request.args.get('sort_order', 'asc')
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        plugins = enhanced_marketplace.get_plugins(
            category=category if category else None,
            search=search if search else None,
            sort_by=sort_by,
            sort_order=sort_order,
            limit=limit,
            offset=offset
        )
        
        # JSON 직렬화
        data = []
        for plugin in plugins:
            data.append({
                'id': plugin.id,
                'name': plugin.name,
                'description': plugin.description,
                'version': plugin.version,
                'author': plugin.author,
                'category': plugin.category,
                'tags': plugin.tags,
                'price': plugin.price,
                'download_count': plugin.download_count,
                'rating': plugin.rating,
                'review_count': plugin.review_count,
                'size': plugin.size,
                'dependencies': plugin.dependencies,
                'compatibility': plugin.compatibility,
                'created_at': plugin.created_at.isoformat(),
                'updated_at': plugin.updated_at.isoformat(),
                'status': plugin.status,
                'license': plugin.license,
                'homepage': plugin.homepage,
                'repository': plugin.repository
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"플러그인 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'플러그인 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/plugins/<plugin_id>', methods=['GET'])
def get_plugin_detail(plugin_id: str):
    """플러그인 상세 정보 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        plugin = enhanced_marketplace.get_plugin(plugin_id)
        if not plugin:
            return jsonify({'success': False, 'message': '플러그인을 찾을 수 없습니다.'}), 404
        
        # 다운로드 통계 조회
        stats = enhanced_marketplace.get_download_stats(plugin_id)
        
        data = {
            'id': plugin.id,
            'name': plugin.name,
            'description': plugin.description,
            'version': plugin.version,
            'author': plugin.author,
            'category': plugin.category,
            'tags': plugin.tags,
            'price': plugin.price,
            'download_count': plugin.download_count,
            'rating': plugin.rating,
            'review_count': plugin.review_count,
            'size': plugin.size,
            'dependencies': plugin.dependencies,
            'compatibility': plugin.compatibility,
            'created_at': plugin.created_at.isoformat(),
            'updated_at': plugin.updated_at.isoformat(),
            'status': plugin.status,
            'license': plugin.license,
            'homepage': plugin.homepage,
            'repository': plugin.repository,
            'download_stats': {
                'total_downloads': stats.total_downloads if stats else 0,
                'daily_downloads': stats.daily_downloads if stats else 0,
                'weekly_downloads': stats.weekly_downloads if stats else 0,
                'monthly_downloads': stats.monthly_downloads if stats else 0,
                'last_download': stats.last_download.isoformat() if stats else None
            }
        }
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"플러그인 상세 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'플러그인 상세 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/plugins/<plugin_id>/download', methods=['POST'])
@login_required
def download_plugin(plugin_id: str):
    """플러그인 다운로드"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json() or {}
        version = data.get('version')
        user_id = current_user.id if current_user.is_authenticated else None
        
        success = enhanced_marketplace.download_plugin(plugin_id, str(user_id) if user_id else None, str(version) if version else None)
        
        if success:
            return jsonify({'success': True, 'message': '플러그인이 다운로드되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '플러그인 다운로드에 실패했습니다.'}), 500
            
    except Exception as e:
        logger.error(f"플러그인 다운로드 오류: {e}")
        return jsonify({'success': False, 'message': f'플러그인 다운로드 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/plugins/<plugin_id>/reviews', methods=['GET'])
def get_plugin_reviews(plugin_id: str):
    """플러그인 리뷰 목록 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        limit = request.args.get('limit', 20, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        reviews = enhanced_marketplace.get_reviews(plugin_id, limit, offset)
        
        data = []
        for review in reviews:
            data.append({
                'id': review.id,
                'plugin_id': review.plugin_id,
                'user_id': review.user_id,
                'rating': review.rating,
                'title': review.title,
                'content': review.content,
                'created_at': review.created_at.isoformat(),
                'helpful_count': review.helpful_count,
                'reported': review.reported
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"리뷰 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'리뷰 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/plugins/<plugin_id>/reviews', methods=['POST'])
@login_required
def add_plugin_review(plugin_id: str):
    """플러그인 리뷰 추가"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['rating', 'title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'필수 필드가 누락되었습니다: {field}'}), 400
        
        # 평점 범위 검증
        rating = data['rating']
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'success': False, 'message': '평점은 1-5 사이의 정수여야 합니다.'}), 400
        
        user_id = current_user.id if current_user.is_authenticated else 'anonymous'
        
        success = enhanced_marketplace.add_review(
            plugin_id=plugin_id,
            user_id=user_id,
            rating=rating,
            title=data['title'],
            content=data['content']
        )
        
        if success:
            return jsonify({'success': True, 'message': '리뷰가 추가되었습니다.'})
        else:
            return jsonify({'success': False, 'message': '리뷰 추가에 실패했습니다.'}), 500
            
    except Exception as e:
        logger.error(f"리뷰 추가 오류: {e}")
        return jsonify({'success': False, 'message': f'리뷰 추가 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/categories', methods=['GET'])
def get_categories():
    """카테고리 목록 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        categories = enhanced_marketplace.get_categories()
        return jsonify({'success': True, 'data': categories})
        
    except Exception as e:
        logger.error(f"카테고리 목록 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'카테고리 목록 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/popular', methods=['GET'])
def get_popular_plugins():
    """인기 플러그인 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        plugins = enhanced_marketplace.get_popular_plugins(limit)
        
        data = []
        for plugin in plugins:
            data.append({
                'id': plugin.id,
                'name': plugin.name,
                'description': plugin.description,
                'version': plugin.version,
                'author': plugin.author,
                'category': plugin.category,
                'tags': plugin.tags,
                'price': plugin.price,
                'download_count': plugin.download_count,
                'rating': plugin.rating,
                'review_count': plugin.review_count,
                'size': plugin.size,
                'status': plugin.status,
                'license': plugin.license
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"인기 플러그인 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'인기 플러그인 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/recommended', methods=['GET'])
def get_recommended_plugins():
    """추천 플러그인 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        limit = request.args.get('limit', 10, type=int)
        user_id = current_user.id if current_user.is_authenticated else None
        
        plugins = enhanced_marketplace.get_recommended_plugins(str(user_id) if user_id else None, limit)
        
        data = []
        for plugin in plugins:
            data.append({
                'id': plugin.id,
                'name': plugin.name,
                'description': plugin.description,
                'version': plugin.version,
                'author': plugin.author,
                'category': plugin.category,
                'tags': plugin.tags,
                'price': plugin.price,
                'download_count': plugin.download_count,
                'rating': plugin.rating,
                'review_count': plugin.review_count,
                'size': plugin.size,
                'status': plugin.status,
                'license': plugin.license
            })
        
        return jsonify({'success': True, 'data': data})
        
    except Exception as e:
        logger.error(f"추천 플러그인 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'추천 플러그인 조회 중 오류가 발생했습니다: {str(e)}'}), 500

@enhanced_marketplace_bp.route('/stats', methods=['GET'])
def get_marketplace_stats():
    """마켓플레이스 통계 조회"""
    if not enhanced_marketplace:
        return jsonify({'success': False, 'message': '마켓플레이스를 사용할 수 없습니다.'}), 503
    
    try:
        # 전체 플러그인 수
        all_plugins = enhanced_marketplace.get_plugins(limit=1000)
        total_plugins = len(all_plugins)
        
        # 카테고리별 통계
        categories = enhanced_marketplace.get_categories()
        category_stats = {}
        for category in categories:
            category_plugins = enhanced_marketplace.get_plugins(category=category)
            category_stats[category] = len(category_plugins)
        
        # 평균 평점
        total_rating = sum(p.rating for p in all_plugins)
        avg_rating = total_rating / total_plugins if total_plugins > 0 else 0
        
        # 총 다운로드 수
        total_downloads = sum(p.download_count for p in all_plugins)
        
        # 무료/유료 플러그인 수
        free_plugins = len([p for p in all_plugins if p.price == 0])
        paid_plugins = total_plugins - free_plugins
        
        stats = {
            'total_plugins': total_plugins,
            'total_downloads': total_downloads,
            'average_rating': round(avg_rating, 2),
            'free_plugins': free_plugins,
            'paid_plugins': paid_plugins,
            'categories': category_stats
        }
        
        return jsonify({'success': True, 'data': stats})
        
    except Exception as e:
        logger.error(f"마켓플레이스 통계 조회 오류: {e}")
        return jsonify({'success': False, 'message': f'마켓플레이스 통계 조회 중 오류가 발생했습니다: {str(e)}'}), 500 