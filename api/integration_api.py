from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
import json
import logging
from datetime import datetime, timedelta
import traceback

# 통합 모듈 import
from integration.workflow_engine import WorkflowEngine, WorkflowStatus, TaskType
from integration.event_bus import EventBus, EventPriority
from integration.api_gateway import ApiGateway, RequestMethod, AuthType
from integration.microservice_integration import MicroserviceIntegration, ServiceStatus

# Blueprint 생성
integration_api = Blueprint('integration_api', __name__, url_prefix='/api/integration')

# 로깅 설정
logger = logging.getLogger(__name__)

# 통합 모듈 인스턴스
workflow_engine = WorkflowEngine()
event_bus = EventBus()
api_gateway = ApiGateway()
microservice_integration = MicroserviceIntegration()

# 워크플로우 API 엔드포인트
@integration_api.route('/workflows', methods=['GET'])
@login_required
def get_workflows():
    """워크플로우 목록 조회"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        
        # 상태 필터링
        workflow_status = None
        if status:
            workflow_status = WorkflowStatus(status)
        
        workflows = workflow_engine.get_workflow_instances(
            status=workflow_status,
            limit=per_page,
            offset=(page - 1) * per_page
        )
        
        return jsonify({
            'success': True,
            'workflows': [asdict(wf) for wf in workflows],
            'page': page,
            'per_page': per_page
        })
        
    except Exception as e:
        logger.error(f"워크플로우 목록 조회 오류: {str(e)}")
        return jsonify({'error': '워크플로우 목록 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/workflows', methods=['POST'])
@login_required
def create_workflow():
    """워크플로우 정의 생성"""
    try:
        data = request.get_json()
        
        workflow_id = workflow_engine.create_workflow_definition(
            name=data.get('name'),
            description=data.get('description'),
            tasks=data.get('tasks', []),
            variables=data.get('variables', {}),
            triggers=data.get('triggers', []),
            timeout=data.get('timeout', 3600),
            retry_count=data.get('retry_count', 3),
            retry_delay=data.get('retry_delay', 60)
        )
        
        return jsonify({
            'success': True,
            'workflow_id': workflow_id,
            'message': '워크플로우가 생성되었습니다'
        })
        
    except Exception as e:
        logger.error(f"워크플로우 생성 오류: {str(e)}")
        return jsonify({'error': '워크플로우 생성 중 오류가 발생했습니다'}), 500

@integration_api.route('/workflows/<workflow_id>/start', methods=['POST'])
@login_required
def start_workflow(workflow_id):
    """워크플로우 실행 시작"""
    try:
        data = request.get_json() or {}
        
        instance_id = workflow_engine.start_workflow(
            workflow_id=workflow_id,
            variables=data.get('variables', {}),
            created_by=current_user.id if current_user else 'system'
        )
        
        return jsonify({
            'success': True,
            'instance_id': instance_id,
            'message': '워크플로우가 시작되었습니다'
        })
        
    except Exception as e:
        logger.error(f"워크플로우 시작 오류: {str(e)}")
        return jsonify({'error': '워크플로우 시작 중 오류가 발생했습니다'}), 500

@integration_api.route('/workflows/instances/<instance_id>', methods=['GET'])
@login_required
def get_workflow_instance(instance_id):
    """워크플로우 인스턴스 조회"""
    try:
        # 워크플로우 인스턴스 조회 로직 구현
        instances = workflow_engine.get_workflow_instances()
        instance = next((inst for inst in instances if inst.id == instance_id), None)
        
        if not instance:
            return jsonify({'error': '워크플로우 인스턴스를 찾을 수 없습니다'}), 404
        
        return jsonify({
            'success': True,
            'instance': asdict(instance)
        })
        
    except Exception as e:
        logger.error(f"워크플로우 인스턴스 조회 오류: {str(e)}")
        return jsonify({'error': '워크플로우 인스턴스 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/workflows/instances/<instance_id>/cancel', methods=['POST'])
@login_required
def cancel_workflow(instance_id):
    """워크플로우 취소"""
    try:
        success = workflow_engine.cancel_workflow(instance_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '워크플로우가 취소되었습니다'
            })
        else:
            return jsonify({'error': '워크플로우를 취소할 수 없습니다'}), 400
        
    except Exception as e:
        logger.error(f"워크플로우 취소 오류: {str(e)}")
        return jsonify({'error': '워크플로우 취소 중 오류가 발생했습니다'}), 500

@integration_api.route('/workflows/statistics', methods=['GET'])
@login_required
def get_workflow_statistics():
    """워크플로우 통계 조회"""
    try:
        stats = workflow_engine.get_workflow_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"워크플로우 통계 조회 오류: {str(e)}")
        return jsonify({'error': '워크플로우 통계 조회 중 오류가 발생했습니다'}), 500

# 이벤트 버스 API 엔드포인트
@integration_api.route('/events', methods=['POST'])
@login_required
def publish_event():
    """이벤트 발행"""
    try:
        data = request.get_json()
        
        event_id = event_bus.publish_event(
            event_type=data.get('type'),
            source=data.get('source'),
            data=data.get('data', {}),
            target=data.get('target'),
            priority=EventPriority(data.get('priority', 'normal')),
            expires_at=datetime.fromisoformat(data.get('expires_at')) if data.get('expires_at') else None,
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'success': True,
            'event_id': event_id,
            'message': '이벤트가 발행되었습니다'
        })
        
    except Exception as e:
        logger.error(f"이벤트 발행 오류: {str(e)}")
        return jsonify({'error': '이벤트 발행 중 오류가 발생했습니다'}), 500

@integration_api.route('/events', methods=['GET'])
@login_required
def get_events():
    """이벤트 목록 조회"""
    try:
        event_type = request.args.get('type')
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        events = event_bus.get_events(
            event_type=event_type,
            limit=limit,
            offset=offset
        )
        
        return jsonify({
            'success': True,
            'events': [asdict(event) for event in events]
        })
        
    except Exception as e:
        logger.error(f"이벤트 목록 조회 오류: {str(e)}")
        return jsonify({'error': '이벤트 목록 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/events/statistics', methods=['GET'])
@login_required
def get_event_statistics():
    """이벤트 통계 조회"""
    try:
        stats = event_bus.get_event_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"이벤트 통계 조회 오류: {str(e)}")
        return jsonify({'error': '이벤트 통계 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/events/broadcast', methods=['POST'])
@login_required
def broadcast_message():
    """브로드캐스트 메시지 전송"""
    try:
        data = request.get_json()
        
        event_bus.broadcast_message(
            message=data.get('message'),
            message_type=data.get('type', 'info'),
            target_connections=data.get('target_connections')
        )
        
        return jsonify({
            'success': True,
            'message': '브로드캐스트 메시지가 전송되었습니다'
        })
        
    except Exception as e:
        logger.error(f"브로드캐스트 메시지 전송 오류: {str(e)}")
        return jsonify({'error': '브로드캐스트 메시지 전송 중 오류가 발생했습니다'}), 500

# API 게이트웨이 API 엔드포인트
@integration_api.route('/gateway/routes', methods=['GET'])
@login_required
def get_gateway_routes():
    """게이트웨이 라우트 목록 조회"""
    try:
        # 라우트 목록 조회 로직 구현
        routes = list(api_gateway.routes.values())
        
        return jsonify({
            'success': True,
            'routes': [asdict(route) for route in routes]
        })
        
    except Exception as e:
        logger.error(f"게이트웨이 라우트 조회 오류: {str(e)}")
        return jsonify({'error': '게이트웨이 라우트 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/gateway/routes', methods=['POST'])
@login_required
def create_gateway_route():
    """게이트웨이 라우트 생성"""
    try:
        data = request.get_json()
        
        route_id = api_gateway.add_route(
            path=data.get('path'),
            method=RequestMethod(data.get('method')),
            target_url=data.get('target_url'),
            auth_type=AuthType(data.get('auth_type', 'none')),
            rate_limit=data.get('rate_limit', 100),
            timeout=data.get('timeout', 30),
            retry_count=data.get('retry_count', 3),
            headers=data.get('headers', {}),
            parameters=data.get('parameters', {})
        )
        
        return jsonify({
            'success': True,
            'route_id': route_id,
            'message': '게이트웨이 라우트가 생성되었습니다'
        })
        
    except Exception as e:
        logger.error(f"게이트웨이 라우트 생성 오류: {str(e)}")
        return jsonify({'error': '게이트웨이 라우트 생성 중 오류가 발생했습니다'}), 500

@integration_api.route('/gateway/api-keys', methods=['POST'])
@login_required
def create_api_key():
    """API 키 생성"""
    try:
        data = request.get_json()
        
        api_key = api_gateway.create_api_key(
            name=data.get('name'),
            user_id=data.get('user_id'),
            permissions=data.get('permissions', []),
            rate_limit=data.get('rate_limit', 1000),
            expires_at=datetime.fromisoformat(data.get('expires_at')) if data.get('expires_at') else None
        )
        
        return jsonify({
            'success': True,
            'api_key': api_key,
            'message': 'API 키가 생성되었습니다'
        })
        
    except Exception as e:
        logger.error(f"API 키 생성 오류: {str(e)}")
        return jsonify({'error': 'API 키 생성 중 오류가 발생했습니다'}), 500

@integration_api.route('/gateway/statistics', methods=['GET'])
@login_required
def get_gateway_statistics():
    """게이트웨이 통계 조회"""
    try:
        stats = api_gateway.get_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"게이트웨이 통계 조회 오류: {str(e)}")
        return jsonify({'error': '게이트웨이 통계 조회 중 오류가 발생했습니다'}), 500

# 마이크로서비스 통합 API 엔드포인트
@integration_api.route('/microservices', methods=['GET'])
@login_required
def get_microservices():
    """마이크로서비스 목록 조회"""
    try:
        services = list(microservice_integration.services.values())
        
        return jsonify({
            'success': True,
            'services': [asdict(service) for service in services]
        })
        
    except Exception as e:
        logger.error(f"마이크로서비스 목록 조회 오류: {str(e)}")
        return jsonify({'error': '마이크로서비스 목록 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/microservices', methods=['POST'])
@login_required
def register_microservice():
    """마이크로서비스 등록"""
    try:
        data = request.get_json()
        
        service_id = microservice_integration.register_service(
            name=data.get('name'),
            version=data.get('version'),
            description=data.get('description'),
            endpoints=data.get('endpoints', []),
            health_check_interval=data.get('health_check_interval', 30),
            timeout=data.get('timeout', 10),
            retry_count=data.get('retry_count', 3),
            circuit_breaker_config=data.get('circuit_breaker_config', {}),
            load_balancer_config=data.get('load_balancer_config', {})
        )
        
        return jsonify({
            'success': True,
            'service_id': service_id,
            'message': '마이크로서비스가 등록되었습니다'
        })
        
    except Exception as e:
        logger.error(f"마이크로서비스 등록 오류: {str(e)}")
        return jsonify({'error': '마이크로서비스 등록 중 오류가 발생했습니다'}), 500

@integration_api.route('/microservices/<service_name>/instances', methods=['POST'])
@login_required
def register_service_instance(service_name):
    """서비스 인스턴스 등록"""
    try:
        data = request.get_json()
        
        instance_id = microservice_integration.register_instance(
            service_name=service_name,
            host=data.get('host'),
            port=data.get('port'),
            protocol=data.get('protocol', 'http'),
            health_check_url=data.get('health_check_url'),
            metadata=data.get('metadata', {})
        )
        
        return jsonify({
            'success': True,
            'instance_id': instance_id,
            'message': '서비스 인스턴스가 등록되었습니다'
        })
        
    except Exception as e:
        logger.error(f"서비스 인스턴스 등록 오류: {str(e)}")
        return jsonify({'error': '서비스 인스턴스 등록 중 오류가 발생했습니다'}), 500

@integration_api.route('/microservices/<service_name>/status', methods=['GET'])
@login_required
def get_service_status(service_name):
    """서비스 상태 조회"""
    try:
        status = microservice_integration.get_service_status(service_name)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"서비스 상태 조회 오류: {str(e)}")
        return jsonify({'error': '서비스 상태 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/microservices/status', methods=['GET'])
@login_required
def get_all_services_status():
    """모든 서비스 상태 조회"""
    try:
        status = microservice_integration.get_all_services_status()
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        logger.error(f"전체 서비스 상태 조회 오류: {str(e)}")
        return jsonify({'error': '전체 서비스 상태 조회 중 오류가 발생했습니다'}), 500

@integration_api.route('/microservices/<service_name>/call', methods=['POST'])
@login_required
def call_service(service_name):
    """서비스 호출"""
    try:
        data = request.get_json()
        
        result = microservice_integration.call_service(
            service_name=service_name,
            endpoint=data.get('endpoint'),
            method=data.get('method', 'GET'),
            data=data.get('data'),
            headers=data.get('headers'),
            timeout=data.get('timeout')
        )
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"서비스 호출 오류: {str(e)}")
        return jsonify({'error': f'서비스 호출 중 오류가 발생했습니다: {str(e)}'}), 500

@integration_api.route('/microservices/mesh', methods=['POST'])
@login_required
def add_service_mesh_config():
    """서비스 메시 설정 추가"""
    try:
        data = request.get_json()
        
        microservice_integration.add_service_mesh_config(
            service_name=data.get('service_name'),
            mesh_config=data.get('mesh_config', {}),
            routing_rules=data.get('routing_rules', []),
            security_policies=data.get('security_policies', [])
        )
        
        return jsonify({
            'success': True,
            'message': '서비스 메시 설정이 추가되었습니다'
        })
        
    except Exception as e:
        logger.error(f"서비스 메시 설정 추가 오류: {str(e)}")
        return jsonify({'error': '서비스 메시 설정 추가 중 오류가 발생했습니다'}), 500

# 통합 시스템 전체 통계
@integration_api.route('/statistics', methods=['GET'])
@login_required
def get_integration_statistics():
    """통합 시스템 전체 통계 조회"""
    try:
        # 각 시스템의 통계 수집
        workflow_stats = workflow_engine.get_workflow_statistics()
        event_stats = event_bus.get_event_statistics()
        gateway_stats = api_gateway.get_statistics()
        microservice_stats = microservice_integration.get_all_services_status()
        
        # 전체 통계 계산
        total_stats = {
            'workflows': workflow_stats,
            'events': event_stats,
            'gateway': gateway_stats,
            'microservices': microservice_stats,
            'summary': {
                'total_workflows': workflow_stats.get('total_workflows', 0),
                'total_events': event_stats.get('total_events', 0),
                'total_requests': gateway_stats.get('total_requests', 0),
                'total_services': microservice_stats.get('summary', {}).get('total_services', 0),
                'overall_health': 'healthy'  # 간단한 헬스 체크
            }
        }
        
        return jsonify({
            'success': True,
            'statistics': total_stats
        })
        
    except Exception as e:
        logger.error(f"통합 시스템 통계 조회 오류: {str(e)}")
        return jsonify({'error': '통합 시스템 통계 조회 중 오류가 발생했습니다'}), 500

# 시스템 정리 API
@integration_api.route('/cleanup', methods=['POST'])
@login_required
def cleanup_systems():
    """시스템 정리"""
    try:
        data = request.get_json() or {}
        days = data.get('days', 30)
        
        # 각 시스템 정리
        workflow_cleaned = workflow_engine.cleanup_old_workflows(days)
        event_cleaned = event_bus.cleanup_old_events(days)
        gateway_cleaned = api_gateway.cleanup_old_logs(days)
        microservice_cleaned = microservice_integration.cleanup_old_instances(days)
        
        return jsonify({
            'success': True,
            'cleanup_results': {
                'workflows': workflow_cleaned,
                'events': event_cleaned,
                'gateway_logs': gateway_cleaned,
                'microservice_instances': microservice_cleaned
            },
            'message': '시스템 정리가 완료되었습니다'
        })
        
    except Exception as e:
        logger.error(f"시스템 정리 오류: {str(e)}")
        return jsonify({'error': '시스템 정리 중 오류가 발생했습니다'}), 500

# 에러 핸들러
@integration_api.errorhandler(404)
def not_found(error):
    return jsonify({'error': '요청한 리소스를 찾을 수 없습니다'}), 404

@integration_api.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '내부 서버 오류가 발생했습니다'}), 500
