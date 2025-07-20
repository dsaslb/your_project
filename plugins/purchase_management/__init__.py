"""
구매관리 플러그인
구매 주문, 공급업체 관리, 발주 관리 기능을 제공합니다.
"""

from flask import Blueprint

# 플러그인 블루프린트 생성
purchase_bp = Blueprint('purchase', __name__, url_prefix='/purchase')

# 플러그인 메타데이터
PLUGIN_INFO = {
    'name': 'purchase_management',
    'version': '1.0.0',
    'description': '구매 주문 및 공급업체 관리 시스템',
    'author': 'Your Program',
    'category': 'Operations',
    'required_permissions': ['purchase_view', 'purchase_manage'],
    'dependencies': ['inventory_management'],
    'settings': {
        'auto_approval_limit': 100000,  # 자동 승인 한도 (원)
        'default_payment_terms': 30,  # 기본 결제 조건 (일)
        'email_notifications': True
    }
}

from . import routes, models 