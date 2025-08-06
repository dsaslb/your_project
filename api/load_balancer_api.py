from flask import Blueprint, request, jsonify
from load_balancer.load_balancer_manager import LoadBalancerManager, LoadBalancerConfig, LoadBalancingAlgorithm, ServerStatus
import os
from datetime import datetime
import sqlite3

# 로드 밸런서 관리자 초기화
load_balancer_config = LoadBalancerConfig(
    data_dir="data/load_balancer",
    health_check_interval=30,
    health_check_timeout=5,
    max_failures=3,
    enable_sticky_sessions=True,
    session_timeout=1800
)

load_balancer_manager = LoadBalancerManager(load_balancer_config)

# Blueprint 생성
load_balancer_bp = Blueprint('load_balancer', __name__, url_prefix='/api/load-balancer')

@load_balancer_bp.route('/health', methods=['GET'])
def health_check():
    """로드 밸런서 시스템 상태 확인"""
    try:
        stats = load_balancer_manager.get_load_balancer_stats()
        return jsonify({
            'status': 'success',
            'message': '로드 밸런서 시스템이 정상적으로 작동합니다',
            'data': {
                'total_groups': stats.get('total_groups', 0),
                'total_servers': stats.get('total_servers', 0),
                'healthy_servers': stats.get('healthy_servers', 0),
                'total_connections': stats.get('total_connections', 0)
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'로드 밸런서 시스템 상태 확인 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/stats', methods=['GET'])
def get_load_balancer_stats():
    """로드 밸런서 통계 조회"""
    try:
        stats = load_balancer_manager.get_load_balancer_stats()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'로드 밸런서 통계 조회 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/groups', methods=['GET'])
def get_server_groups():
    """서버 그룹 조회"""
    try:
        groups_data = []
        for group in load_balancer_manager.server_groups.values():
            group_dict = {
                'group_id': group.group_id,
                'name': group.name,
                'algorithm': group.algorithm.value,
                'is_active': group.is_active,
                'created_at': group.created_at.isoformat(),
                'updated_at': group.updated_at.isoformat(),
                'servers': []
            }
            
            for server in group.servers:
                server_dict = {
                    'server_id': server.server_id,
                    'name': server.name,
                    'host': server.host,
                    'port': server.port,
                    'protocol': server.protocol,
                    'weight': server.weight,
                    'max_connections': server.max_connections,
                    'is_active': server.is_active,
                    'status': server.status.value,
                    'health_check_url': server.health_check_url,
                    'created_at': server.created_at.isoformat(),
                    'updated_at': server.updated_at.isoformat()
                }
                group_dict['servers'].append(server_dict)
            
            groups_data.append(group_dict)
        
        return jsonify({
            'status': 'success',
            'data': groups_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 그룹 조회 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/groups', methods=['POST'])
def create_server_group():
    """서버 그룹 생성"""
    try:
        data = request.get_json()
        
        required_fields = ['name', 'algorithm']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} 필드가 필요합니다'
                }), 400
        
        # 알고리즘 검증
        try:
            algorithm = LoadBalancingAlgorithm(data['algorithm'])
        except ValueError:
            return jsonify({
                'status': 'error',
                'message': f'유효하지 않은 알고리즘: {data["algorithm"]}'
            }), 400
        
        group_id = load_balancer_manager.create_server_group(
            name=data['name'],
            algorithm=algorithm,
            servers=data.get('servers', [])
        )
        
        return jsonify({
            'status': 'success',
            'message': f'서버 그룹 {data["name"]}이(가) 생성되었습니다',
            'data': {
                'group_id': group_id
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 그룹 생성 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/groups/<group_id>', methods=['PUT'])
def update_server_group(group_id):
    """서버 그룹 수정"""
    try:
        if group_id not in load_balancer_manager.server_groups:
            return jsonify({
                'status': 'error',
                'message': f'서버 그룹을 찾을 수 없습니다: {group_id}'
            }), 404
        
        data = request.get_json()
        group = load_balancer_manager.server_groups[group_id]
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            group.name = data['name']
        if 'algorithm' in data:
            try:
                group.algorithm = LoadBalancingAlgorithm(data['algorithm'])
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': f'유효하지 않은 알고리즘: {data["algorithm"]}'
                }), 400
        if 'is_active' in data:
            group.is_active = data['is_active']
        
        group.updated_at = datetime.utcnow()
        load_balancer_manager._save_server_group(group)
        
        return jsonify({
            'status': 'success',
            'message': f'서버 그룹 {group.name}이(가) 업데이트되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 그룹 수정 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/groups/<group_id>', methods=['DELETE'])
def delete_server_group(group_id):
    """서버 그룹 삭제"""
    try:
        if group_id not in load_balancer_manager.server_groups:
            return jsonify({
                'status': 'error',
                'message': f'서버 그룹을 찾을 수 없습니다: {group_id}'
            }), 404
        
        group = load_balancer_manager.server_groups[group_id]
        group_name = group.name
        
        # 그룹의 모든 서버 삭제
        for server in group.servers:
            del load_balancer_manager.servers[server.server_id]
            if server.server_id in load_balancer_manager.health_check_results:
                del load_balancer_manager.health_check_results[server.server_id]
        
        # 그룹 삭제
        del load_balancer_manager.server_groups[group_id]
        
        # 데이터베이스에서 삭제
        db_path = os.path.join(load_balancer_manager.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM servers WHERE group_id = ?', (group_id,))
        cursor.execute('DELETE FROM server_groups WHERE group_id = ?', (group_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'서버 그룹 {group_name}이(가) 삭제되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 그룹 삭제 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/groups/<group_id>/servers', methods=['POST'])
def add_server_to_group(group_id):
    """서버 그룹에 서버 추가"""
    try:
        if group_id not in load_balancer_manager.server_groups:
            return jsonify({
                'status': 'error',
                'message': f'서버 그룹을 찾을 수 없습니다: {group_id}'
            }), 404
        
        data = request.get_json()
        
        required_fields = ['name', 'host', 'port']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'{field} 필드가 필요합니다'
                }), 400
        
        server_id = load_balancer_manager.add_server_to_group(
            group_id=group_id,
            name=data['name'],
            host=data['host'],
            port=data['port'],
            protocol=data.get('protocol', 'http'),
            weight=data.get('weight', 100),
            max_connections=data.get('max_connections', 1000),
            health_check_url=data.get('health_check_url', '/health')
        )
        
        return jsonify({
            'status': 'success',
            'message': f'서버 {data["name"]}이(가) 추가되었습니다',
            'data': {
                'server_id': server_id
            }
        }), 201
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 추가 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/servers/<server_id>', methods=['PUT'])
def update_server(server_id):
    """서버 정보 수정"""
    try:
        if server_id not in load_balancer_manager.servers:
            return jsonify({
                'status': 'error',
                'message': f'서버를 찾을 수 없습니다: {server_id}'
            }), 404
        
        data = request.get_json()
        server = load_balancer_manager.servers[server_id]
        
        # 업데이트 가능한 필드들
        if 'name' in data:
            server.name = data['name']
        if 'host' in data:
            server.host = data['host']
        if 'port' in data:
            server.port = data['port']
        if 'protocol' in data:
            server.protocol = data['protocol']
        if 'weight' in data:
            server.weight = data['weight']
        if 'max_connections' in data:
            server.max_connections = data['max_connections']
        if 'is_active' in data:
            server.is_active = data['is_active']
        if 'health_check_url' in data:
            server.health_check_url = data['health_check_url']
        
        server.updated_at = datetime.utcnow()
        
        # 그룹 ID 찾기
        group_id = None
        for group in load_balancer_manager.server_groups.values():
            if any(s.server_id == server_id for s in group.servers):
                group_id = group.group_id
                break
        
        load_balancer_manager._save_server(server, group_id)
        
        return jsonify({
            'status': 'success',
            'message': f'서버 {server.name}이(가) 업데이트되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 수정 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/servers/<server_id>', methods=['DELETE'])
def delete_server(server_id):
    """서버 삭제"""
    try:
        if server_id not in load_balancer_manager.servers:
            return jsonify({
                'status': 'error',
                'message': f'서버를 찾을 수 없습니다: {server_id}'
            }), 404
        
        server = load_balancer_manager.servers[server_id]
        server_name = server.name
        
        # 서버 그룹에서 제거
        for group in load_balancer_manager.server_groups.values():
            group.servers = [s for s in group.servers if s.server_id != server_id]
        
        # 서버 삭제
        del load_balancer_manager.servers[server_id]
        if server_id in load_balancer_manager.health_check_results:
            del load_balancer_manager.health_check_results[server_id]
        
        # 데이터베이스에서 삭제
        db_path = os.path.join(load_balancer_manager.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM servers WHERE server_id = ?', (server_id,))
        cursor.execute('DELETE FROM health_check_results WHERE server_id = ?', (server_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': f'서버 {server_name}이(가) 삭제되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 삭제 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/servers/<server_id>/health', methods=['GET'])
def get_server_health(server_id):
    """서버 헬스 체크 결과 조회"""
    try:
        if server_id not in load_balancer_manager.health_check_results:
            return jsonify({
                'status': 'error',
                'message': f'서버를 찾을 수 없습니다: {server_id}'
            }), 404
        
        result = load_balancer_manager.health_check_results[server_id]
        
        health_data = {
            'server_id': result.server_id,
            'status': result.status.value,
            'response_time': result.response_time,
            'status_code': result.status_code,
            'last_check': result.last_check.isoformat(),
            'consecutive_failures': result.consecutive_failures
        }
        
        return jsonify({
            'status': 'success',
            'data': health_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 헬스 체크 조회 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/servers/<server_id>/health', methods=['POST'])
def perform_health_check(server_id):
    """수동 헬스 체크 수행"""
    try:
        if server_id not in load_balancer_manager.servers:
            return jsonify({
                'status': 'error',
                'message': f'서버를 찾을 수 없습니다: {server_id}'
            }), 404
        
        server = load_balancer_manager.servers[server_id]
        load_balancer_manager._perform_health_check(server)
        
        return jsonify({
            'status': 'success',
            'message': f'서버 {server.name} 헬스 체크가 수행되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'헬스 체크 수행 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/metrics', methods=['GET'])
def get_metrics():
    """로드 밸런서 메트릭 조회"""
    try:
        limit = request.args.get('limit', 100, type=int)
        server_id = request.args.get('server_id')
        group_id = request.args.get('group_id')
        
        metrics = load_balancer_manager.metrics[:limit]
        
        if server_id:
            metrics = [m for m in metrics if m.server_id == server_id]
        if group_id:
            metrics = [m for m in metrics if m.group_id == group_id]
        
        metrics_data = []
        for metric in metrics:
            metric_dict = {
                'metric_id': metric.metric_id,
                'server_id': metric.server_id,
                'group_id': metric.group_id,
                'request_count': metric.request_count,
                'response_time': metric.response_time,
                'status_code': metric.status_code,
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
            'message': f'메트릭 조회 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/select-server/<group_id>', methods=['POST'])
def select_server(group_id):
    """로드 밸런싱 알고리즘에 따라 서버 선택"""
    try:
        data = request.get_json() or {}
        client_ip = data.get('client_ip')
        session_id = data.get('session_id')
        
        selected_server = load_balancer_manager.select_server(
            group_id=group_id,
            client_ip=client_ip,
            session_id=session_id
        )
        
        if selected_server:
            server_data = {
                'server_id': selected_server.server_id,
                'name': selected_server.name,
                'host': selected_server.host,
                'port': selected_server.port,
                'protocol': selected_server.protocol,
                'weight': selected_server.weight,
                'status': selected_server.status.value
            }
            
            return jsonify({
                'status': 'success',
                'data': server_data
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': '사용 가능한 서버가 없습니다'
            }), 503
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'서버 선택 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/config', methods=['GET'])
def get_config():
    """로드 밸런서 설정 조회"""
    try:
        config_data = {
            'data_dir': load_balancer_manager.config.data_dir,
            'health_check_interval': load_balancer_manager.config.health_check_interval,
            'health_check_timeout': load_balancer_manager.config.health_check_timeout,
            'max_failures': load_balancer_manager.config.max_failures,
            'enable_sticky_sessions': load_balancer_manager.config.enable_sticky_sessions,
            'session_timeout': load_balancer_manager.config.session_timeout
        }
        
        return jsonify({
            'status': 'success',
            'data': config_data
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 조회 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/config', methods=['PUT'])
def update_config():
    """로드 밸런서 설정 수정"""
    try:
        data = request.get_json()
        
        # 업데이트 가능한 설정들
        if 'health_check_interval' in data:
            load_balancer_manager.config.health_check_interval = data['health_check_interval']
        if 'health_check_timeout' in data:
            load_balancer_manager.config.health_check_timeout = data['health_check_timeout']
        if 'max_failures' in data:
            load_balancer_manager.config.max_failures = data['max_failures']
        if 'enable_sticky_sessions' in data:
            load_balancer_manager.config.enable_sticky_sessions = data['enable_sticky_sessions']
        if 'session_timeout' in data:
            load_balancer_manager.config.session_timeout = data['session_timeout']
        
        return jsonify({
            'status': 'success',
            'message': '로드 밸런서 설정이 업데이트되었습니다'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'설정 수정 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/sessions/clear', methods=['POST'])
def clear_sessions():
    """세션 매핑 정리"""
    try:
        load_balancer_manager.session_mapping.clear()
        
        return jsonify({
            'status': 'success',
            'message': '세션 매핑이 정리되었습니다',
            'data': {
                'cleared_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'세션 정리 실패: {str(e)}'
        }), 500

@load_balancer_bp.route('/connections/clear', methods=['POST'])
def clear_connections():
    """연결 수 카운터 정리"""
    try:
        load_balancer_manager.connection_counts.clear()
        
        return jsonify({
            'status': 'success',
            'message': '연결 수 카운터가 정리되었습니다',
            'data': {
                'cleared_at': datetime.utcnow().isoformat()
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'연결 수 정리 실패: {str(e)}'
        }), 500 