"""
모듈 마켓플레이스 API
사용자가 모듈을 검색, 구매, 다운로드할 수 있는 마켓플레이스
"""

# type: ignore
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime
import json
import os
import shutil
from typing import Dict, List, Any
import logging

# 데코레이터 import
from utils.auth_decorators import admin_required, manager_required

logger = logging.getLogger(__name__)

module_marketplace_bp = Blueprint('module_marketplace', __name__)

# 마켓플레이스 모듈 데이터 (실제로는 데이터베이스에서 관리)
marketplace_modules = {
    'qsc_system': {
        'id': 'qsc_system',
        'name': 'QSC 점검 시스템',
        'description': '품질(Quality), 서비스(Service), 청결(Cleanliness) 점검을 체계적으로 관리하는 시스템',
        'category': 'quality_management',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,  # 무료
        'rating': 4.8,
        'downloads': 1250,
        'tags': ['품질관리', '점검', 'QSC', '표준화'],
        'features': [
            '실시간 QSC 점검 기록',
            '점검 항목 커스터마이징',
            '점검 결과 통계 및 리포트',
            '알림 및 경고 시스템',
            '모바일 지원'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy'],
            'permissions': ['qsc_management']
        },
        'screenshots': [
            '/static/marketplace/qsc_system_1.png',
            '/static/marketplace/qsc_system_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    },
    'checklist_system': {
        'id': 'checklist_system',
        'name': '업무 체크리스트 시스템',
        'description': '일일 업무 체크리스트를 관리하고 완료율을 추적하는 시스템',
        'category': 'task_management',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,
        'rating': 4.6,
        'downloads': 980,
        'tags': ['체크리스트', '업무관리', '할일관리', '진행률'],
        'features': [
            '일일/주간/월간 체크리스트',
            '업무별 체크리스트 템플릿',
            '완료율 추적 및 통계',
            '팀별 업무 할당',
            '알림 및 리마인더'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy'],
            'permissions': ['checklist_management']
        },
        'screenshots': [
            '/static/marketplace/checklist_system_1.png',
            '/static/marketplace/checklist_system_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    },
    'cooktime_system': {
        'id': 'cooktime_system',
        'name': '조리 예상시간 시스템',
        'description': '메뉴별 조리 시간을 예측하고 실제 시간과 비교하여 효율성을 분석하는 시스템',
        'category': 'kitchen_management',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,
        'rating': 4.7,
        'downloads': 1100,
        'tags': ['조리시간', '예측', '효율성', '주방관리'],
        'features': [
            '메뉴별 조리시간 예측',
            '실제 조리시간 기록',
            '효율성 분석 및 통계',
            '요리사 경험별 조정',
            '메뉴 커스터마이징 시간 계산'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy'],
            'permissions': ['cooktime_management']
        },
        'screenshots': [
            '/static/marketplace/cooktime_system_1.png',
            '/static/marketplace/cooktime_system_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    },
    'kitchen_monitor': {
        'id': 'kitchen_monitor',
        'name': '주방 모니터링 시스템',
        'description': '주방 설비의 상태를 실시간으로 모니터링하고 유지보수를 관리하는 시스템',
        'category': 'equipment_management',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,
        'rating': 4.9,
        'downloads': 850,
        'tags': ['주방모니터링', '설비관리', '유지보수', 'IoT'],
        'features': [
            '실시간 설비 상태 모니터링',
            '온도, 효율성 등 지표 추적',
            '유지보수 일정 관리',
            '알림 및 경고 시스템',
            '설비 제어 기능'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy'],
            'permissions': ['kitchen_monitor_management']
        },
        'screenshots': [
            '/static/marketplace/kitchen_monitor_1.png',
            '/static/marketplace/kitchen_monitor_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    },
    'ai_diagnosis': {
        'id': 'ai_diagnosis',
        'name': 'AI 진단 및 개선안 시스템',
        'description': 'AI를 활용하여 업무 효율성을 분석하고 개선안을 제시하는 시스템',
        'category': 'ai_analytics',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,
        'rating': 4.5,
        'downloads': 650,
        'tags': ['AI', '진단', '분석', '개선안', '최적화'],
        'features': [
            '업무 효율성 AI 분석',
            '개선안 자동 생성',
            '성능 지표 대시보드',
            '예측 분석',
            '개선 효과 추적'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy', 'pandas', 'numpy'],
            'permissions': ['ai_management']
        },
        'screenshots': [
            '/static/marketplace/ai_diagnosis_1.png',
            '/static/marketplace/ai_diagnosis_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    },
    'plugin_registration': {
        'id': 'plugin_registration',
        'name': '플러그인 등록 시스템',
        'description': '사용자 정의 플러그인을 등록하고 관리할 수 있는 시스템',
        'category': 'development',
        'version': '1.0.0',
        'author': 'System Admin',
        'price': 0,
        'rating': 4.4,
        'downloads': 420,
        'tags': ['플러그인', '개발', '확장', '커스터마이징'],
        'features': [
            '플러그인 등록 및 검증',
            '플러그인 버전 관리',
            '보안 검사 및 승인',
            '플러그인 마켓플레이스 연동',
            '개발자 도구'
        ],
        'requirements': {
            'python_version': '3.8+',
            'dependencies': ['flask', 'sqlalchemy', 'gitpython'],
            'permissions': ['plugin_management']
        },
        'screenshots': [
            '/static/marketplace/plugin_registration_1.png',
            '/static/marketplace/plugin_registration_2.png'
        ],
        'status': 'approved',
        'created_at': '2024-01-15T10:00:00Z',
        'updated_at': '2024-01-15T10:00:00Z'
    }
}

# 사용자별 설치된 모듈 (실제로는 데이터베이스에서 관리)
user_installed_modules = {}

@module_marketplace_bp.route('/api/marketplace/modules', methods=['GET'])
@login_required
def get_marketplace_modules():
    """마켓플레이스 모듈 목록 조회"""
    try:
        # 필터링 옵션
        category = request.args.get('category')
        search = request.args.get('search')
        sort_by = request.args.get('sort_by', 'downloads')  # downloads, rating, name, price
        order = request.args.get('order', 'desc')  # asc, desc
        
        # 기본 모듈 목록
        modules = list(marketplace_modules.values())
        
        # 카테고리 필터링
        if category:
            modules = [m for m in modules if m['category'] == category]
        
        # 검색 필터링
        if search:
            search_lower = search.lower()
            modules = [
                m for m in modules 
                if search_lower in str(m['name']).lower() or 
                   search_lower in str(m['description']).lower() or
                   any(search_lower in str(tag).lower() for tag in (m.get('tags', []) if isinstance(m.get('tags'), list) else []))  # type: ignore
            ]
        
        # 정렬
        reverse_order = order == 'desc'
        if sort_by == 'downloads':
            modules.sort(key=lambda x: int(x.get('downloads', 0)), reverse=reverse_order)  # type: ignore
        elif sort_by == 'rating':
            modules.sort(key=lambda x: float(x.get('rating', 0.0)), reverse=reverse_order)  # type: ignore
        elif sort_by == 'name':
            modules.sort(key=lambda x: str(x.get('name', '')).lower(), reverse=reverse_order)  # type: ignore
        elif sort_by == 'price':
            modules.sort(key=lambda x: float(x.get('price', 0.0)), reverse=reverse_order)  # type: ignore
        
        # 페이지네이션
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paginated_modules = modules[start_idx:end_idx]
        
        # 카테고리 목록
        categories = list(set(m['category'] for m in marketplace_modules.values()))
        
        return jsonify({
            'success': True,
            'modules': paginated_modules,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(modules),
                'pages': (len(modules) + per_page - 1) // per_page
            },
            'categories': categories,
            'total_modules': len(marketplace_modules)
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '마켓플레이스 모듈 목록 조회에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/modules/<module_id>', methods=['GET'])
@login_required
def get_module_detail(module_id: str):
    """모듈 상세 정보 조회"""
    try:
        if module_id not in marketplace_modules:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        module = marketplace_modules[module_id]
        
        # 사용자의 설치 여부 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        is_installed = module_id in user_modules
        
        # 리뷰 정보 (실제로는 데이터베이스에서 조회)
        reviews = [
            {
                'id': 1,
                'user_name': '김철수',
                'rating': 5,
                'comment': '정말 유용한 모듈입니다!',
                'created_at': '2024-01-10T15:30:00Z'
            },
            {
                'id': 2,
                'user_name': '이영희',
                'rating': 4,
                'comment': '기능이 잘 구현되어 있어요.',
                'created_at': '2024-01-08T12:15:00Z'
            }
        ]
        
        return jsonify({
            'success': True,
            'module': module,
            'is_installed': is_installed,
            'reviews': reviews,
            'related_modules': [
                m for m in marketplace_modules.values()
                if m['category'] == module['category'] and m['id'] != module_id
            ][:4]  # 같은 카테고리의 다른 모듈 4개
        })
        
    except Exception as e:
        logger.error(f"모듈 상세 정보 조회 실패: {e}")
        return jsonify({'error': '모듈 상세 정보 조회에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/modules/<module_id>/install', methods=['POST'])
@login_required
def install_module(module_id: str):
    """모듈 설치"""
    try:
        if module_id not in marketplace_modules:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        module = marketplace_modules[module_id]
        
        # 이미 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id in user_modules:
            return jsonify({'error': '이미 설치된 모듈입니다.'}), 400
        
        # 권한 확인
        required_permissions = module['requirements'].get('permissions', [])
        for permission in required_permissions:
            if not current_user.has_permission(permission, 'view'):
                return jsonify({'error': f'모듈 설치 권한이 없습니다: {permission}'}), 403
        
        # 모듈 설치 (실제로는 파일 복사, 데이터베이스 설정 등)
        if current_user.id not in user_installed_modules:
            user_installed_modules[current_user.id] = []
        
        user_installed_modules[current_user.id].append(module_id)
        
        # 다운로드 수 증가
        marketplace_modules[module_id]['downloads'] += 1
        
        # 설치 로그 기록
        logger.info(f"모듈 설치: {current_user.username} -> {module_id}")
        
        return jsonify({
            'success': True,
            'message': f"{module['name']}이(가) 성공적으로 설치되었습니다.",
            'module': module
        })
        
    except Exception as e:
        logger.error(f"모듈 설치 실패: {e}")
        return jsonify({'error': '모듈 설치에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/modules/<module_id>/uninstall', methods=['POST'])
@login_required
def uninstall_module(module_id: str):
    """모듈 제거"""
    try:
        if module_id not in marketplace_modules:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        module = marketplace_modules[module_id]
        
        # 설치된 모듈인지 확인
        user_modules = user_installed_modules.get(current_user.id, [])
        if module_id not in user_modules:
            return jsonify({'error': '설치되지 않은 모듈입니다.'}), 400
        
        # 모듈 제거
        user_installed_modules[current_user.id].remove(module_id)
        
        # 제거 로그 기록
        logger.info(f"모듈 제거: {current_user.username} -> {module_id}")
        
        return jsonify({
            'success': True,
            'message': f"{module['name']}이(가) 성공적으로 제거되었습니다."
        })
        
    except Exception as e:
        logger.error(f"모듈 제거 실패: {e}")
        return jsonify({'error': '모듈 제거에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/modules/<module_id>/review', methods=['POST'])
@login_required
def add_module_review(module_id: str):
    """모듈 리뷰 작성"""
    try:
        if module_id not in marketplace_modules:
            return jsonify({'error': '모듈을 찾을 수 없습니다.'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': '요청 데이터가 없습니다.'}), 400
        
        rating = data.get('rating')
        comment = data.get('comment', '')
        
        if not rating or not isinstance(rating, int) or rating < 1 or rating > 5:
            return jsonify({'error': '유효하지 않은 평점입니다.'}), 400
        
        # 리뷰 저장 (실제로는 데이터베이스에 저장)
        review = {
            'id': len(marketplace_modules[module_id].get('reviews', [])) + 1,
            'user_name': current_user.username,
            'rating': rating,
            'comment': comment,
            'created_at': datetime.now().isoformat()
        }
        
        # 모듈의 평균 평점 업데이트
        if 'reviews' not in marketplace_modules[module_id]:
            marketplace_modules[module_id]['reviews'] = []
        
        marketplace_modules[module_id]['reviews'].append(review)
        
        # 평균 평점 계산
        ratings = [r['rating'] for r in marketplace_modules[module_id]['reviews']]
        marketplace_modules[module_id]['rating'] = sum(ratings) / len(ratings)
        
        return jsonify({
            'success': True,
            'message': '리뷰가 성공적으로 등록되었습니다.',
            'review': review
        })
        
    except Exception as e:
        logger.error(f"모듈 리뷰 작성 실패: {e}")
        return jsonify({'error': '모듈 리뷰 작성에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/categories', methods=['GET'])
@login_required
def get_marketplace_categories():
    """마켓플레이스 카테고리 목록"""
    try:
        categories = {}
        
        for module in marketplace_modules.values():
            category = module['category']
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'count': 0,
                    'modules': []
                }
            
            categories[category]['count'] += 1
            categories[category]['modules'].append({
                'id': module['id'],
                'name': module['name'],
                'rating': module['rating'],
                'downloads': module['downloads']
            })
        
        return jsonify({
            'success': True,
            'categories': list(categories.values())
        })
        
    except Exception as e:
        logger.error(f"마켓플레이스 카테고리 조회 실패: {e}")
        return jsonify({'error': '마켓플레이스 카테고리 조회에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/installed', methods=['GET'])
@login_required
def get_installed_modules():
    """사용자가 설치한 모듈 목록"""
    try:
        user_modules = user_installed_modules.get(current_user.id, [])
        installed_modules = []
        
        for module_id in user_modules:
            if module_id in marketplace_modules:
                module = marketplace_modules[module_id].copy()
                module['installed_at'] = datetime.now().isoformat()  # 실제로는 설치 시간 저장
                installed_modules.append(module)
        
        return jsonify({
            'success': True,
            'modules': installed_modules,
            'total_installed': len(installed_modules)
        })
        
    except Exception as e:
        logger.error(f"설치된 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '설치된 모듈 목록 조회에 실패했습니다.'}), 500

@module_marketplace_bp.route('/api/marketplace/trending', methods=['GET'])
@login_required
def get_trending_modules():
    """인기 모듈 목록"""
    try:
        # 다운로드 수 기준으로 정렬
        trending_modules = sorted(
            marketplace_modules.values(),
            key=lambda x: x['downloads'],
            reverse=True
        )[:8]  # 상위 8개
        
        return jsonify({
            'success': True,
            'modules': trending_modules
        })
        
    except Exception as e:
        logger.error(f"인기 모듈 목록 조회 실패: {e}")
        return jsonify({'error': '인기 모듈 목록 조회에 실패했습니다.'}), 500 