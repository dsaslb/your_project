from flask import Blueprint

# 플러그인 관리 블루프린트 생성
plugin_management = Blueprint('plugin_management', __name__, url_prefix='/api/plugin-management')

# 플러그인 메타데이터
PLUGIN_METADATA = {
    'id': 'plugin_management',
    'name': '플러그인 관리',
    'description': '플러그인 활성화/비활성화 및 권한 분배 관리',
    'version': '1.0.0',
    'author': 'System',
    'category': 'system',
    'icon': 'settings',
    'permissions': {
        'view': ['admin', 'brand_admin'],
        'manage': ['admin'],
        'test': ['admin', 'brand_admin']
    }
}

# 라우트 등록
from . import routes 