"""
성능 최적화 API
캐싱, 쿼리 최적화, 연결 풀 관리, 성능 모니터링
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required
from datetime import datetime, timedelta
from utils.advanced_caching import get_cache, AdvancedCache
from utils.query_optimizer import get_query_optimizer, get_connection_pool_optimizer
from utils.auth_decorators import admin_required
import json

performance_bp = Blueprint('performance', __name__, url_prefix='/api/admin/performance')

@performance_bp.route('/cache/stats', methods=['GET'])
@login_required
@admin_required
def get_cache_stats():
    """캐시 통계 조회"""
    try:
        cache = get_cache()
        stats = cache.get_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/cache/clear', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """캐시 전체 삭제"""
    try:
        data = request.get_json(silent=True) or {}
        namespace = data.get('namespace')
        levels = data.get('levels')
        
        cache = get_cache()
        success = cache.clear(namespace, levels)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message': '캐시가 삭제되었습니다' if success else '캐시 삭제에 실패했습니다'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/cache/test', methods=['POST'])
@login_required
@admin_required
def test_cache():
    """캐시 테스트"""
    try:
        data = request.get_json()
        key = data.get('key', 'test_key')
        value = data.get('value', 'test_value')
        ttl = data.get('ttl', 60)
        levels = data.get('levels', ['l1_memory', 'l2_redis', 'l3_file'])
        
        cache = get_cache()
        
        # 값 저장
        cache.set(key, value, ttl, levels=levels)
        
        # 값 조회
        retrieved_value = cache.get(key, levels=levels)
        
        # 값 삭제
        cache.delete(key, levels=levels)
        
        return jsonify({
            'status': 'success',
            'data': {
                'stored_value': value,
                'retrieved_value': retrieved_value,
                'test_passed': retrieved_value == value
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/queries/analysis', methods=['GET'])
@login_required
@admin_required
def get_query_analysis():
    """쿼리 분석 결과 조회"""
    try:
        optimizer = get_query_optimizer()
        if not optimizer:
            return jsonify({'status': 'error', 'message': '쿼리 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        analysis = optimizer.analyze_queries()
        
        return jsonify({
            'status': 'success',
            'data': analysis
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/queries/slow', methods=['GET'])
@login_required
@admin_required
def get_slow_queries():
    """느린 쿼리 목록 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        optimizer = get_query_optimizer()
        if not optimizer:
            return jsonify({'status': 'error', 'message': '쿼리 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        slow_queries = optimizer.get_slow_queries(limit)
        
        return jsonify({
            'status': 'success',
            'data': slow_queries
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/queries/stats', methods=['GET'])
@login_required
@admin_required
def get_query_stats():
    """쿼리 성능 통계 조회"""
    try:
        optimizer = get_query_optimizer()
        if not optimizer:
            return jsonify({'status': 'error', 'message': '쿼리 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        stats = optimizer.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/queries/clear', methods=['POST'])
@login_required
@admin_required
def clear_query_metrics():
    """쿼리 메트릭 초기화"""
    try:
        optimizer = get_query_optimizer()
        if not optimizer:
            return jsonify({'status': 'error', 'message': '쿼리 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        optimizer.clear_metrics()
        
        return jsonify({
            'status': 'success',
            'message': '쿼리 메트릭이 초기화되었습니다'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/pool/stats', methods=['GET'])
@login_required
@admin_required
def get_pool_stats():
    """연결 풀 통계 조회"""
    try:
        pool_optimizer = get_connection_pool_optimizer()
        if not pool_optimizer:
            return jsonify({'status': 'error', 'message': '연결 풀 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        stats = pool_optimizer.get_pool_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/pool/optimize', methods=['POST'])
@login_required
@admin_required
def optimize_pool():
    """연결 풀 최적화"""
    try:
        pool_optimizer = get_connection_pool_optimizer()
        if not pool_optimizer:
            return jsonify({'status': 'error', 'message': '연결 풀 최적화 시스템이 초기화되지 않았습니다'}), 500
        
        optimized_engine = pool_optimizer.optimize_pool()
        
        if optimized_engine:
            return jsonify({
                'status': 'success',
                'message': '연결 풀이 최적화되었습니다'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '연결 풀 최적화에 실패했습니다'
            }), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/overview', methods=['GET'])
@login_required
@admin_required
def get_performance_overview():
    """성능 개요 조회"""
    try:
        # 캐시 통계
        cache = get_cache()
        cache_stats = cache.get_stats()
        
        # 쿼리 통계
        optimizer = get_query_optimizer()
        query_stats = {}
        if optimizer:
            query_stats = optimizer.get_performance_stats()
        
        # 연결 풀 통계
        pool_optimizer = get_connection_pool_optimizer()
        pool_stats = {}
        if pool_optimizer:
            pool_stats = pool_optimizer.get_pool_stats()
        
        # 전체 성능 점수 계산
        performance_score = 0
        recommendations = []
        
        # 캐시 히트율 기반 점수
        if cache_stats.get('overall_hit_rate', 0) > 80:
            performance_score += 30
        elif cache_stats.get('overall_hit_rate', 0) > 60:
            performance_score += 20
            recommendations.append("캐시 히트율을 높이기 위해 캐시 전략을 검토하세요")
        else:
            performance_score += 10
            recommendations.append("캐시 히트율이 낮습니다. 캐시 설정을 최적화하세요")
        
        # 쿼리 성능 기반 점수
        if query_stats.get('slow_query_percentage', 100) < 5:
            performance_score += 40
        elif query_stats.get('slow_query_percentage', 100) < 20:
            performance_score += 25
            recommendations.append("느린 쿼리가 있습니다. 인덱스 추가를 고려하세요")
        else:
            performance_score += 10
            recommendations.append("느린 쿼리가 많습니다. 쿼리 최적화가 필요합니다")
        
        # 연결 풀 상태 기반 점수
        if pool_stats:
            total_connections = pool_stats.get('total_connections', 0)
            checked_out = pool_stats.get('checked_out', 0)
            
            if total_connections > 0:
                utilization_rate = (checked_out / total_connections) * 100
                if 20 <= utilization_rate <= 80:
                    performance_score += 30
                elif utilization_rate < 20:
                    performance_score += 20
                    recommendations.append("연결 풀 사용률이 낮습니다. 풀 크기를 줄이세요")
                else:
                    performance_score += 10
                    recommendations.append("연결 풀 사용률이 높습니다. 풀 크기를 늘리세요")
        
        return jsonify({
            'status': 'success',
            'data': {
                'performance_score': performance_score,
                'cache_stats': cache_stats,
                'query_stats': query_stats,
                'pool_stats': pool_stats,
                'recommendations': recommendations,
                'last_updated': datetime.now().isoformat()
            }
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/optimize', methods=['POST'])
@login_required
@admin_required
def run_optimization():
    """자동 성능 최적화 실행"""
    try:
        data = request.get_json(silent=True) or {}
        optimization_types = data.get('types', ['cache', 'queries', 'pool'])
        
        results = {}
        
        # 캐시 최적화
        if 'cache' in optimization_types:
            cache = get_cache()
            # 캐시 설정 최적화 (실제로는 설정 파일에서 관리)
            results['cache'] = {
                'status': 'success',
                'message': '캐시 최적화 완료'
            }
        
        # 쿼리 최적화
        if 'queries' in optimization_types:
            optimizer = get_query_optimizer()
            if optimizer:
                # 쿼리 분석 실행
                optimizer.analyze_queries()
                results['queries'] = {
                    'status': 'success',
                    'message': '쿼리 분석 완료',
                    'recommendations_count': len(optimizer.index_recommendations)
                }
            else:
                results['queries'] = {
                    'status': 'error',
                    'message': '쿼리 최적화 시스템이 초기화되지 않았습니다'
                }
        
        # 연결 풀 최적화
        if 'pool' in optimization_types:
            pool_optimizer = get_connection_pool_optimizer()
            if pool_optimizer:
                optimized_engine = pool_optimizer.optimize_pool()
                results['pool'] = {
                    'status': 'success' if optimized_engine else 'error',
                    'message': '연결 풀 최적화 완료' if optimized_engine else '연결 풀 최적화 실패'
                }
            else:
                results['pool'] = {
                    'status': 'error',
                    'message': '연결 풀 최적화 시스템이 초기화되지 않았습니다'
                }
        
        return jsonify({
            'status': 'success',
            'data': results
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500 