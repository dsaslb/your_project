"""
플러그인 성능 최적화 자동화 API
- 최적화 제안 조회, 실행, 이력 조회
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
import logging

try:
    from core.backend.plugin_optimization_engine import plugin_optimization_engine
except ImportError:
    plugin_optimization_engine = None

logger = logging.getLogger(__name__)

plugin_optimization_bp = Blueprint('plugin_optimization', __name__, url_prefix='/api/plugin-optimization')

@plugin_optimization_bp.route('/suggestions', methods=['GET'])
@login_required
def get_suggestions():
    """최적화 제안 목록 조회"""
    if not plugin_optimization_engine:
        return jsonify({'success': False, 'message': '최적화 엔진을 사용할 수 없습니다.'}), 503
    plugin_id = request.args.get('plugin_id')
    suggestions = plugin_optimization_engine.get_suggestions(plugin_id)
    data = [
        {
            'id': idx,
            'plugin_id': s.plugin_id,
            'suggestion_type': s.suggestion_type,
            'description': s.description,
            'created_at': s.created_at.isoformat(),
            'details': s.details,
            'executed': s.executed,
            'executed_at': s.executed_at.isoformat() if s.executed_at else None,
            'result': s.result
        }
        for idx, s in enumerate(suggestions)
    ]
    return jsonify({'success': True, 'data': data})

@plugin_optimization_bp.route('/execute/<int:suggestion_id>', methods=['POST'])
@login_required
def execute_suggestion(suggestion_id):
    """최적화 제안 실행"""
    if not plugin_optimization_engine:
        return jsonify({'success': False, 'message': '최적화 엔진을 사용할 수 없습니다.'}), 503
    ok = plugin_optimization_engine.execute_suggestion(suggestion_id)
    if ok:
        return jsonify({'success': True, 'message': '최적화 제안이 실행되었습니다.'})
    else:
        return jsonify({'success': False, 'message': '최적화 제안 실행에 실패했습니다.'}), 500

@plugin_optimization_bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """최적화 실행 이력 조회"""
    if not plugin_optimization_engine:
        return jsonify({'success': False, 'message': '최적화 엔진을 사용할 수 없습니다.'}), 503
    plugin_id = request.args.get('plugin_id')
    history = plugin_optimization_engine.get_history(plugin_id)
    data = [
        {
            'plugin_id': h.plugin_id,
            'suggestion_type': h.suggestion.suggestion_type,
            'description': h.suggestion.description,
            'executed_at': h.executed_at.isoformat(),
            'result': h.result
        }
        for h in history
    ]
    return jsonify({'success': True, 'data': data}) 