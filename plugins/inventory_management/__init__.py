"""
재고관리 플러그인
상품 재고 관리, 입출고 관리, 재고 알림 기능을 제공합니다.
"""

from flask import Blueprint

# 플러그인 블루프린트 생성
inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

# 플러그인 메타데이터
PLUGIN_INFO = {
    'name': 'inventory_management',
    'version': '1.0.0',
    'description': '상품 재고 관리 및 입출고 시스템',
    'author': 'Your Program',
    'category': 'Operations',
    'required_permissions': ['inventory_view', 'inventory_manage'],
    'dependencies': [],
    'settings': {
        'low_stock_threshold': 10,
        'auto_reorder_enabled': False,
        'reorder_quantity': 50,
        'stock_alert_email': True
    }
}

from . import routes, models 