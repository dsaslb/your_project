from flask import Blueprint, request, jsonify
from gateway.gateway_manager import GatewayManager, GatewayConfig
import os
from datetime import datetime
import sqlite3

# 게이트웨이 관리자 초기화
gateway_config = GatewayConfig(
    data_dir="data/gateway",
    jwt_secret="your-secret-key-change-in-production",
    rate_limit_window=3600,
    rate_limit_max_requests=1000,
    enable_rate_limiting=True,
    enable_logging=True
)

gateway_manager = GatewayManager(gateway_config)

# Blueprint 생성
gateway_bp = Blueprint('gateway', __name__, url_prefix='/api/gateway')

@gateway_bp.route('/health', methods=['GET'])
def health_check():
    """게이트웨이 시스템 상태 확인"""
    try:
        stats = gateway_manager.get_gateway_stats()
        return jsonify({
            'status': 'success',
            'message': '게이트웨이 시스템이 정상적으로 작동합니다',
            'data': {
                'total_routes': stats.get('total_routes', 0),
                'active_routes': stats.get('active_routes', 0),
                'total_metrics': stats.get('total_metrics', 0)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'게이트웨이 시스템 상태 확인 실패: {str(e)}'
        }), 500

@gateway_bp.route('/stats', methods=['GET'])
def get_gateway_stats():
    """게이트웨이 통계 조회"""
    try:
        stats = gateway_manager.get_gateway_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'게이트웨이 통계 조회 실패: {str(e)}'
        }), 500

@gateway_bp.route('/routes', methods=['GET'])
def get_routes():
    """API 라우트 조회"""
    try:
        routes_data = []
        for route in gateway_manager.routes.values():
            route_dict = {
                'route_id': route.route_id,
                'name': route.name,
                'path': route.path,
                'method': route.method,
                'target_url': route.target_url,
                'service_name': route.service_name,
                'is_active': route.is_active,
                'requires_auth': route.requires_auth,
                'created_at': route.created_at.isoformat()
            }
            routes_data.append(route_dict)
        
        return jsonify({
            'status': 'success',
            'data': routes_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 라우트 조회 실패: {str(e)}'
        }), 500

@gateway_bp.route('/routes', methods=['POST'])
def create_route():
    """API 라우트 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'path', 'method', 'target_url', 'service_name']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} 필드가 필요합니다'
                }), 400
        
        route_id = gateway_manager.create_route(
            name=data['name'],
            path=data['path'],
            method=data['method'],
            target_url=data['target_url'],
            service_name=data['service_name'],
            is_active=data.get('is_active', True),
            requires_auth=data.get('requires_auth', True)
        )
        
        return jsonify({
            'status': 'success',
            'message': f'API 라우트 {data["name"]}이(가) 생성되었습니다',
            'data': {
                'route_id': route_id
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 라우트 생성 실패: {str(e)}'
        }), 500

@gateway_bp.route('/routes/<route_id>', methods=['PUT'])
def update_route(route_id):
    """API 라우트 수정"""
    try:
        if route_id not in gateway_manager.routes:
            return jsonify({
                'status': 'error',
                'message': f'라우트를 찾을 수 없습니다: {route_id}'
            }), 404
        
        data = request.get_json()
        route = gateway_manager.routes[route_id]
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            route.name = data['name']
        if 'path' in data:
            route.path = data['path']
        if 'method' in data:
            route.method = data['method']
        if 'target_url' in data:
            route.target_url = data['target_url']
        if 'service_name' in data:
            route.service_name = data['service_name']
        if 'is_active' in data:
            route.is_active = data['is_active']
        if 'requires_auth' in data:
            route.requires_auth = data['requires_auth']
        
        route.updated_at = datetime.utcnow()
        gateway_manager._save_route(route)
        
        return jsonify({
            'status': 'success',
            'message': f'API 라우트 {route.name}이(가) 업데이트되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 라우트 수정 실패: {str(e)}'
        }), 500

@gateway_bp.route('/routes/<route_id>', methods=['DELETE'])
def delete_route(route_id):
    """API 라우트 삭제"""
    try:
        if route_id not in gateway_manager.routes:
            return jsonify({
                'status': 'error',
                'message': f'라우트를 찾을 수 없습니다: {route_id}'
            }), 404
        
        route = gateway_manager.routes[route_id]
        route_name = route.name
        
        del gateway_manager.routes[route_id]
        
        # 데이터베이스에서도 삭제
        db_path = os.path.join(gateway_manager.config.data_dir, 'gateway.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM api_routes WHERE route_id = ?', (route_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'API 라우트 {route_name}이(가) 삭제되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 라우트 삭제 실패: {str(e)}'
        }), 500

@gateway_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """API 메트릭 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        route_id = request.args.get('route_id')
        
        metrics = gateway_manager.metrics[:limit]
        
        if route_id:
            metrics = [m for m in metrics if m.route_id == route_id]
        
        metrics_data = []
        for metric in metrics:
            metric_dict = {
                'metric_id': metric.metric_id,
                'route_id': metric.route_id,
                'method': metric.method,
                'path': metric.path,
                'status_code': metric.status_code,
                'response_time': metric.response_time,
                'ip_address': metric.ip_address,
                'timestamp': metric.timestamp.isoformat()
            }
            metrics_data.append(metric_dict)
        
        return jsonify({
            'status': 'success',
            'data': metrics_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 메트릭 조회 실패: {str(e)}'
        }), 500

@gateway_bp.route('/metrics/summary', methods=['GET'])
def get_metrics_summary():
    """API 메트릭 요약 조회"""
    try:
        from datetime import datetime, timedelta
        
        # 시간 범위 설정
        hours = request.args.get('hours', 24, type=int)
        since = datetime.utcnow() - timedelta(hours=hours)
        
        # 해당 시간 범위의 메트릭 필터링
        recent_metrics = [m for m in gateway_manager.metrics if m.timestamp > since]
        
        if not recent_metrics:
            return jsonify({
                'status': 'success',
                'data': {
                    'total_requests': 0,
                    'avg_response_time': 0,
                    'success_rate': 0,
                    'status_code_distribution': {},
                    'top_routes': []
                }
            }), 200
        
        # 통계 계산
        total_requests = len(recent_metrics)
        avg_response_time = sum(m.response_time for m in recent_metrics) / total_requests
        success_requests = len([m for m in recent_metrics if 200 <= m.status_code < 400])
        success_rate = (success_requests / total_requests) * 100
        
        # 상태 코드 분포
        status_distribution = {}
        for metric in recent_metrics:
            status_group = f"{metric.status_code // 100}xx"
            status_distribution[status_group] = status_distribution.get(status_group, 0) + 1
        
        # 상위 라우트
        route_counts = {}
        for metric in recent_metrics:
            if metric.route_id:
                route_counts[metric.route_id] = route_counts.get(metric.route_id, 0) + 1
        
        top_routes = []
        for route_id, count in sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            route = gateway_manager.routes.get(route_id)
            if route:
                top_routes.append({
                    'name': route.name,
                    'path': route.path,
                    'count': count
                })
        
        summary = {
            'total_requests': total_requests,
            'avg_response_time': round(avg_response_time, 3),
            'success_rate': round(success_rate, 2),
            'status_code_distribution': status_distribution,
            'top_routes': top_routes
        }
        
        return jsonify({
            'status': 'success',
            'data': summary
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'API 메트릭 요약 조회 실패: {str(e)}'
        }), 500

@gateway_bp.route('/proxy/<path:subpath>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(subpath):
    """프록시 요청 처리"""
    try:
        # 전체 경로 구성
        full_path = f"/{subpath}"
        
        # 게이트웨이를 통해 요청 라우팅
        response, status_code = gateway_manager.route_request(request)
        
        # 응답이 튜플인 경우 (에러 응답)
        if isinstance(response, tuple):
            return jsonify(response[0]), response[1]
        
        # 일반 응답
        return response, status_code
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'프록시 요청 처리 실패: {str(e)}'
        }), 500

@gateway_bp.route('/config', methods=['GET'])
def get_config():
    """게이트웨이 설정 조회"""
    try:
        config_data = {
            'data_dir': gateway_manager.config.data_dir,
            'rate_limit_window': gateway_manager.config.rate_limit_window,
            'rate_limit_max_requests': gateway_manager.config.rate_limit_max_requests,
            'enable_rate_limiting': gateway_manager.config.enable_rate_limiting,
            'enable_logging': gateway_manager.config.enable_logging
        }
        
        return jsonify({
            'status': 'success',
            'data': config_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'게이트웨이 설정 조회 실패: {str(e)}'
        }), 500

@gateway_bp.route('/config', methods=['PUT'])
def update_config():
    """게이트웨이 설정 수정"""
    try:
        data = request.get_json()
        
        # 업데이트 가능한 설정들
        if 'rate_limit_window' in data:
            gateway_manager.config.rate_limit_window = data['rate_limit_window']
        if 'rate_limit_max_requests' in data:
            gateway_manager.config.rate_limit_max_requests = data['rate_limit_max_requests']
        if 'enable_rate_limiting' in data:
            gateway_manager.config.enable_rate_limiting = data['enable_rate_limiting']
        if 'enable_logging' in data:
            gateway_manager.config.enable_logging = data['enable_logging']
        
        return jsonify({
            'status': 'success',
            'message': '게이트웨이 설정이 업데이트되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'게이트웨이 설정 수정 실패: {str(e)}'
        }), 500

@gateway_bp.route('/cache/clear', methods=['POST'])
def clear_cache():
    """캐시 정리"""
    try:
        gateway_manager.cache.clear()
        
        return jsonify({
            'status': 'success',
            'message': '게이트웨이 캐시가 정리되었습니다',
            'data': {
                'cleared_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'캐시 정리 실패: {str(e)}'
        }), 500

@gateway_bp.route('/rate-limit/clear', methods=['POST'])
def clear_rate_limit():
    """속도 제한 데이터 정리"""
    try:
        gateway_manager._rate_limit_store.clear()
        
        return jsonify({
            'status': 'success',
            'message': '속도 제한 데이터가 정리되었습니다',
            'data': {
                'cleared_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'속도 제한 데이터 정리 실패: {str(e)}'
        }), 500 