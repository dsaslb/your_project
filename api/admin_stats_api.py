"""
통계/리포트 API (관리자 전용)
- /api/admin/stats/summary [GET]
- /api/admin/stats/timeseries [GET]
- /api/admin/stats/plugin [GET]
"""
from flask import Blueprint, request, jsonify
from middleware.security import admin_required
import random
from datetime import datetime, timedelta

bp = Blueprint('admin_stats_api', __name__, url_prefix='/api/admin/stats')

@bp.route('/summary', methods=['GET'])
@admin_required
def stats_summary():
    """주요 통계 요약 (매출, 사용자, 플러그인 등)"""
    # 실제 구현에서는 DB/서비스에서 집계
    return jsonify({
        'total_sales': 12345.67,
        'total_users': 2345,
        'active_users': 1234,
        'total_plugins': 12,
        'active_plugins': 8,
        'date': datetime.now().isoformat()
    })

@bp.route('/timeseries', methods=['GET'])
@admin_required
def stats_timeseries():
    """기간별 시계열 통계 (매출, 사용자 등)"""
    days = int(request.args.get('days', 30))
    now = datetime.now()
    sales = [
        {'date': (now - timedelta(days=i)).strftime('%Y-%m-%d'), 'sales': round(random.uniform(100, 1000), 2)}
        for i in reversed(range(days))
    ]
    users = [
        {'date': (now - timedelta(days=i)).strftime('%Y-%m-%d'), 'users': random.randint(10, 100)}
        for i in reversed(range(days))
    ]
    return jsonify({'sales': sales, 'users': users})

@bp.route('/plugin', methods=['GET'])
@admin_required
def stats_plugin():
    """플러그인별 사용/매출 통계"""
    # 실제 구현에서는 DB/서비스에서 집계
    plugins = [
        {'name': f'플러그인{i}', 'usage': random.randint(10, 100), 'sales': round(random.uniform(100, 1000), 2)}
        for i in range(1, 6)
    ]
    return jsonify({'plugins': plugins}) 