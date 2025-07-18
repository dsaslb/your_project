from core.backend.plugin_microservice_manager import (  # pyright: ignore
    PluginMicroserviceManager, ServiceConfig, ServiceType, ServiceStatus
)
from concurrent.futures import ThreadPoolExecutor  # pyright: ignore
import threading
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import logging
import json
from flask_cors import cross_origin
from flask import Blueprint, request, jsonify, current_app
args = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
environ = None  # pyright: ignore
"""
플러그인 마이크로서비스 관리 API
고도화된 마이크로서비스 아키텍처 REST API 제공
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
plugin_microservice_bp = Blueprint('plugin_microservice', __name__, url_prefix='/api/plugin-microservice')

# 전역 마이크로서비스 매니저 인스턴스
microservice_manager = PluginMicroserviceManager()

# 비동기 실행을 위한 스레드 풀
executor = ThreadPoolExecutor(max_workers=10)


def run_async(coro):
    """비동기 함수를 동기적으로 실행"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@plugin_microservice_bp.route('/services', methods=['GET'])
@cross_origin()
def list_services():
    """서비스 목록 조회"""
    try:
        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id')
        status = request.args.get('status')

        # 상태 필터링
        status_filter = None
        if status:
            try:
                status_filter = ServiceStatus(status)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '유효하지 않은 상태값입니다.',
                    'message': f'유효한 상태: {", ".join([s.value for s in ServiceStatus])}'
                }), 400

        services = run_async(microservice_manager.list_services(plugin_id,  status_filter))

        return jsonify({
            'success': True,
            'data': services,
            'message': f'{len(services)}개의 서비스를 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 목록 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>', methods=['GET'])
@cross_origin()
def get_service(service_id):
    """특정 서비스 조회"""
    try:
        service = run_async(microservice_manager.get_service(service_id))

        if not service:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

        return jsonify({
            'success': True,
            'data': service.to_dict(),
            'message': '서비스 정보를 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services', methods=['POST'])
@cross_origin()
def create_service():
    """새 서비스 생성"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '요청 데이터가 없습니다.',
                'message': '서비스 생성에 필요한 데이터를 제공해주세요.'
            }), 400

        # 필수 필드 검증
        required_fields = ['plugin_id', 'name', 'service_type', 'port']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 없습니다: {field}',
                    'message': f'서비스 생성에 필요한 {field} 필드를 제공해주세요.'
                }), 400

        # 서비스 타입 검증
        try:
            service_type = ServiceType(data['service_type'])
        except ValueError:
            return jsonify({
                'success': False,
                'error': f'유효하지 않은 서비스 타입입니다: {data["service_type"]}',
                'message': f'유효한 서비스 타입: {", ".join([t.value for t in ServiceType])}'
            }), 400

        # ServiceConfig 생성
        config = ServiceConfig(
            name=data['name'],
            plugin_id=data['plugin_id'],
            service_type=service_type,
            port=data['port'],
            host=data.get('host', '0.0.0.0'),
            environment=data.get('environment', {}),
            volumes=data.get('volumes', []),
            networks=data.get('networks', ['plugin_network']),
            depends_on=data.get('depends_on', []),
            health_check=data.get('health_check'),
            resource_limits=data.get('resource_limits'),
            restart_policy=data.get('restart_policy', 'unless-stopped'),
            version=data.get('version', 'latest')
        )

        # 서비스 생성
        service_id = run_async(microservice_manager.create_service(data['plugin_id'],  config))

        return jsonify({
            'success': True,
            'data': {'service_id': service_id},
            'message': '서비스가 성공적으로 생성되었습니다.'
        }), 201

    except Exception as e:
        logger.error(f"서비스 생성 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 생성 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/stop', methods=['POST'])
@cross_origin()
def stop_service(service_id):
    """서비스 중지"""
    try:
        success = run_async(microservice_manager.stop_service(service_id))

        if success:
            return jsonify({
                'success': True,
                'data': {'service_id': service_id},
                'message': '서비스가 성공적으로 중지되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

    except Exception as e:
        logger.error(f"서비스 중지 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 중지 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/start', methods=['POST'])
@cross_origin()
def start_service(service_id):
    """서비스 시작"""
    try:
        success = run_async(microservice_manager.restart_service(service_id))

        if success:
            return jsonify({
                'success': True,
                'data': {'service_id': service_id},
                'message': '서비스가 성공적으로 시작되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

    except Exception as e:
        logger.error(f"서비스 시작 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 시작 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/restart', methods=['POST'])
@cross_origin()
def restart_service(service_id):
    """서비스 재시작"""
    try:
        success = run_async(microservice_manager.restart_service(service_id))

        if success:
            return jsonify({
                'success': True,
                'data': {'service_id': service_id},
                'message': '서비스가 성공적으로 재시작되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

    except Exception as e:
        logger.error(f"서비스 재시작 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 재시작 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>', methods=['DELETE'])
@cross_origin()
def delete_service(service_id):
    """서비스 삭제"""
    try:
        success = run_async(microservice_manager.delete_service(service_id))

        if success:
            return jsonify({
                'success': True,
                'data': {'service_id': service_id},
                'message': '서비스가 성공적으로 삭제되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

    except Exception as e:
        logger.error(f"서비스 삭제 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 삭제 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/logs', methods=['GET'])
@cross_origin()
def get_service_logs(service_id):
    """서비스 로그 조회"""
    try:
        lines = int(request.args.get('lines', 100))
        logs = run_async(microservice_manager.get_service_logs(service_id,  lines))

        return jsonify({
            'success': True,
            'data': logs,
            'message': f'{len(logs)}개의 로그 항목을 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 로그 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 로그 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/metrics', methods=['GET'])
@cross_origin()
def get_service_metrics(service_id):
    """서비스 메트릭 조회"""
    try:
        metrics = run_async(microservice_manager.get_service_metrics(service_id))

        if not metrics:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

        return jsonify({
            'success': True,
            'data': metrics,
            'message': '서비스 메트릭을 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 메트릭 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 메트릭 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/services/<service_id>/scale', methods=['POST'])
@cross_origin()
def scale_service(service_id):
    """서비스 스케일링"""
    try:
        data = request.get_json()

        if not data or 'replicas' not in data:
            return jsonify({
                'success': False,
                'error': 'replicas 필드가 필요합니다.',
                'message': '스케일링할 replica 수를 지정해주세요.'
            }), 400

        replicas = int(data['replicas'])
        if replicas < 0:
            return jsonify({
                'success': False,
                'error': 'replicas는 0 이상이어야 합니다.',
                'message': '올바른 replica 수를 입력해주세요.'
            }), 400

        success = run_async(microservice_manager.scale_service(service_id,  replicas))

        if success:
            return jsonify({
                'success': True,
                'data': {
                    'service_id': service_id,
                    'replicas': replicas
                },
                'message': f'서비스가 {replicas}개 replica로 스케일링되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '서비스를 찾을 수 없습니다.',
                'message': f'서비스 ID {service_id}가 존재하지 않습니다.'
            }), 404

    except Exception as e:
        logger.error(f"서비스 스케일링 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 스케일링 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/discovery', methods=['GET'])
@cross_origin()
def get_service_discovery():
    """서비스 디스커버리 정보 조회"""
    try:
        discovery_info = run_async(microservice_manager.get_service_discovery_info())

        return jsonify({
            'success': True,
            'data': discovery_info,
            'message': '서비스 디스커버리 정보를 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 디스커버리 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 디스커버리 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/cleanup', methods=['POST'])
@cross_origin()
def cleanup_resources():
    """사용하지 않는 리소스 정리"""
    try:
        cleanup_stats = run_async(microservice_manager.cleanup_unused_resources())

        return jsonify({
            'success': True,
            'data': cleanup_stats,
            'message': '리소스 정리가 완료되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"리소스 정리 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '리소스 정리 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """헬스 체크"""
    try:
        # 마이크로서비스 매니저 상태 확인
        discovery_info = run_async(microservice_manager.get_service_discovery_info())

        total_services = discovery_info['total_services'] if discovery_info is not None else None
        healthy_services = discovery_info['healthy_services'] if discovery_info is not None else None
        unhealthy_services = discovery_info['unhealthy_services'] if discovery_info is not None else None

        health_status = 'healthy' if unhealthy_services == 0 else 'degraded'

        return jsonify({
            'success': True,
            'data': {
                'status': health_status,
                'total_services': total_services,
                'healthy_services': healthy_services,
                'unhealthy_services': unhealthy_services,
                'timestamp': datetime.now().isoformat()
            },
            'message': '플러그인 마이크로서비스 시스템이 정상적으로 작동 중입니다.'
        }), 200

    except Exception as e:
        logger.error(f"헬스 체크 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '시스템 상태 확인 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/templates', methods=['GET'])
@cross_origin()
def get_service_templates():
    """서비스 템플릿 목록 조회"""
    try:
        templates = [
            {
                "id": "rest_api_basic",
                "name": "기본 REST API 서비스",
                "description": "Flask 기반 기본 REST API 서비스",
                "service_type": "rest_api",
                "port": 8080,
                "template": {
                    "name": "rest_api_service",
                    "service_type": "rest_api",
                    "port": 8080,
                    "environment": {
                        "FLASK_ENV": "production",
                        "FLASK_DEBUG": "false"
                    },
                    "health_check": {
                        "url": "http://localhost:8080/health",
                        "interval": 30,
                        "timeout": 10,
                        "retries": 3
                    },
                    "resource_limits": {
                        "memory": "512m",
                        "cpu": "0.5"
                    }
                }
            },
            {
                "id": "websocket_service",
                "name": "WebSocket 서비스",
                "description": "실시간 통신을 위한 WebSocket 서비스",
                "service_type": "websocket",
                "port": 8081,
                "template": {
                    "name": "websocket_service",
                    "service_type": "websocket",
                    "port": 8081,
                    "environment": {
                        "WS_HOST": "0.0.0.0",
                        "WS_PORT": "8081"
                    },
                    "health_check": {
                        "url": "http://localhost:8081/health",
                        "interval": 30,
                        "timeout": 10,
                        "retries": 3
                    },
                    "resource_limits": {
                        "memory": "256m",
                        "cpu": "0.3"
                    }
                }
            },
            {
                "id": "background_worker",
                "name": "백그라운드 워커",
                "description": "비동기 작업 처리를 위한 백그라운드 워커",
                "service_type": "background",
                "port": 8082,
                "template": {
                    "name": "background_worker",
                    "service_type": "background",
                    "port": 8082,
                    "environment": {
                        "WORKER_POOL_SIZE": "4",
                        "TASK_TIMEOUT": "300"
                    },
                    "health_check": {
                        "url": "http://localhost:8082/health",
                        "interval": 60,
                        "timeout": 15,
                        "retries": 2
                    },
                    "resource_limits": {
                        "memory": "1g",
                        "cpu": "1.0"
                    }
                }
            },
            {
                "id": "scheduler_service",
                "name": "스케줄러 서비스",
                "description": "정기적인 작업 스케줄링을 위한 서비스",
                "service_type": "scheduler",
                "port": 8083,
                "template": {
                    "name": "scheduler_service",
                    "service_type": "scheduler",
                    "port": 8083,
                    "environment": {
                        "SCHEDULER_INTERVAL": "60",
                        "MAX_JOBS": "100"
                    },
                    "health_check": {
                        "url": "http://localhost:8083/health",
                        "interval": 60,
                        "timeout": 15,
                        "retries": 2
                    },
                    "resource_limits": {
                        "memory": "256m",
                        "cpu": "0.2"
                    }
                }
            }
        ]

        return jsonify({
            'success': True,
            'data': templates,
            'message': f'{len(templates)}개의 서비스 템플릿을 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"서비스 템플릿 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '서비스 템플릿 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_microservice_bp.route('/templates/<template_id>/create', methods=['POST'])
@cross_origin()
def create_service_from_template(template_id):
    """템플릿을 사용하여 서비스 생성"""
    try:
        data = request.get_json()

        if not data or 'plugin_id' not in data:
            return jsonify({
                'success': False,
                'error': 'plugin_id 필드가 필요합니다.',
                'message': '플러그인 ID를 지정해주세요.'
            }), 400

        # 템플릿 조회
        templates_response, status_code = get_service_templates()
        # get_service_templates()가 (Response, status_code) 튜플을 반환한다고 가정합니다.
        templates_data = json.loads(templates_response.get_data(as_text=True))  # pyright: ignore

        if not templates_data['success']:
            return jsonify({
                'success': False,
                'error': '템플릿 목록을 가져올 수 없습니다.',
                'message': '템플릿 시스템에 문제가 있습니다.'
            }), 500

        template = None
        for t in templates_data['data']:
            if t['id'] == template_id:
                template = t
                break

        if not template:
            return jsonify({
                'success': False,
                'error': '템플릿을 찾을 수 없습니다.',
                'message': f'템플릿 ID {template_id}가 존재하지 않습니다.'
            }), 404

        # 템플릿 설정과 사용자 설정 병합
        template_config = template['template'].copy()
        template_config['name'] = data.get('name', template_config['name'])
        template_config['plugin_id'] = data['plugin_id']

        # 사용자 설정으로 덮어쓰기
        if 'environment' in data:
            template_config['environment'].update(data['environment'])
        if 'resource_limits' in data:
            template_config['resource_limits'].update(data['resource_limits'])

        # ServiceConfig 생성
        config = ServiceConfig(
            name=template_config['name'],
            plugin_id=template_config['plugin_id'],
            service_type=ServiceType(template_config['service_type']),
            port=template_config['port'],
            environment=template_config.get('environment', {}),
            health_check=template_config.get('health_check'),
            resource_limits=template_config.get('resource_limits')
        )

        # 서비스 생성
        service_id = run_async(microservice_manager.create_service(data['plugin_id'],  config))

        return jsonify({
            'success': True,
            'data': {
                'service_id': service_id,
                'template_id': template_id,
                'template_name': template['name']
            },
            'message': f'템플릿을 사용하여 서비스가 성공적으로 생성되었습니다.'
        }), 201

    except Exception as e:
        logger.error(f"템플릿 서비스 생성 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '템플릿 서비스 생성 중 오류가 발생했습니다.'
        }), 500

# 에러 핸들러


@plugin_microservice_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '요청한 리소스를 찾을 수 없습니다.',
        'message': '올바른 API 엔드포인트를 확인해주세요.'
    }), 404


@plugin_microservice_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '내부 서버 오류가 발생했습니다.',
        'message': '잠시 후 다시 시도해주세요.'
    }), 500
