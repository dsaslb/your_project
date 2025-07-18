from core.backend.plugin_automation_workflow import (  # pyright: ignore
    PluginAutomationWorkflow, WorkflowConfig, WorkflowStatus, WorkflowStep
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
플러그인 자동화 및 워크플로우 관리 API
고도화된 자동 배포, 테스트, 모니터링 워크플로우 REST API 제공
"""


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Blueprint 생성
plugin_automation_bp = Blueprint('plugin_automation', __name__, url_prefix='/api/plugin-automation')

# 전역 워크플로우 매니저 인스턴스
workflow_manager = PluginAutomationWorkflow()

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


@plugin_automation_bp.route('/workflows', methods=['GET'])
@cross_origin()
def list_workflows():
    """워크플로우 목록 조회"""
    try:
        workflows = run_async(workflow_manager.list_workflows())

        return jsonify({
            'success': True,
            'data': workflows,
            'message': f'{len(workflows)}개의 워크플로우를 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"워크플로우 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 목록 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/workflows/<workflow_id>', methods=['GET'])
@cross_origin()
def get_workflow(workflow_id):
    """특정 워크플로우 조회"""
    try:
        workflow = run_async(workflow_manager.get_workflow(workflow_id))

        if not workflow:
            return jsonify({
                'success': False,
                'error': '워크플로우를 찾을 수 없습니다.',
                'message': f'워크플로우 ID {workflow_id}가 존재하지 않습니다.'
            }), 404

        return jsonify({
            'success': True,
            'data': {
                'id': workflow_id,
                'name': workflow.name,
                'description': workflow.description,
                'steps': [step.value if step is not None else None for step in workflow.steps],
                'timeout_minutes': workflow.timeout_minutes,
                'auto_rollback': workflow.auto_rollback,
                'parallel_execution': workflow.parallel_execution,
                'notification_channels': workflow.notification_channels,
                'environment_variables': workflow.environment_variables
            },
            'message': '워크플로우 정보를 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"워크플로우 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/workflows', methods=['POST'])
@cross_origin()
def create_workflow():
    """새 워크플로우 생성"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '요청 데이터가 없습니다.',
                'message': '워크플로우 생성에 필요한 데이터를 제공해주세요.'
            }), 400

        # 필수 필드 검증
        required_fields = ['id', 'name', 'description', 'steps']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 없습니다: {field}',
                    'message': f'워크플로우 생성에 필요한 {field} 필드를 제공해주세요.'
                }), 400

        # 단계 검증
        valid_steps = [step.value for step in WorkflowStep]
        for step in data['steps']:
            if step not in valid_steps:
                return jsonify({
                    'success': False,
                    'error': f'유효하지 않은 단계입니다: {step}',
                    'message': f'유효한 단계: {", ".join(valid_steps)}'
                }), 400

        # 워크플로우 설정 생성
        config = WorkflowConfig(
            name=data['name'],
            description=data['description'],
            steps=[WorkflowStep(step) for step in data['steps']],
            timeout_minutes=data.get('timeout_minutes', 30),
            auto_rollback=data.get('auto_rollback', True),
            parallel_execution=data.get('parallel_execution', False),
            notification_channels=data.get('notification_channels', ['email', 'webhook']),
            environment_variables=data.get('environment_variables', {})
        )

        # 워크플로우 생성
        success = run_async(workflow_manager.create_workflow(data['id'], config))

        if success:
            return jsonify({
                'success': True,
                'data': {'workflow_id': data['id']},
                'message': '워크플로우가 성공적으로 생성되었습니다.'
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': '워크플로우 생성에 실패했습니다.',
                'message': '워크플로우 생성 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"워크플로우 생성 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 생성 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/workflows/<workflow_id>', methods=['PUT'])
@cross_origin()
def update_workflow(workflow_id):
    """워크플로우 수정"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '요청 데이터가 없습니다.',
                'message': '워크플로우 수정에 필요한 데이터를 제공해주세요.'
            }), 400

        # 기존 워크플로우 확인
        existing_workflow = run_async(workflow_manager.get_workflow(workflow_id))
        if not existing_workflow:
            return jsonify({
                'success': False,
                'error': '워크플로우를 찾을 수 없습니다.',
                'message': f'워크플로우 ID {workflow_id}가 존재하지 않습니다.'
            }), 404

        # 단계 검증
        if 'steps' in data:
            valid_steps = [step.value for step in WorkflowStep]
            for step in data['steps']:
                if step not in valid_steps:
                    return jsonify({
                        'success': False,
                        'error': f'유효하지 않은 단계입니다: {step}',
                        'message': f'유효한 단계: {", ".join(valid_steps)}'
                    }), 400

        # 업데이트된 설정 생성
        updated_config = WorkflowConfig(
            name=data.get('name', existing_workflow.name),
            description=data.get('description', existing_workflow.description),
            steps=[WorkflowStep(step) for step in data.get('steps', [s.value for s in existing_workflow.steps])],
            timeout_minutes=data.get('timeout_minutes', existing_workflow.timeout_minutes),
            auto_rollback=data.get('auto_rollback', existing_workflow.auto_rollback),
            parallel_execution=data.get('parallel_execution', existing_workflow.parallel_execution),
            notification_channels=data.get('notification_channels', existing_workflow.notification_channels),
            environment_variables=data.get('environment_variables', existing_workflow.environment_variables)
        )

        # 워크플로우 업데이트
        success = run_async(workflow_manager.create_workflow(workflow_id, updated_config))

        if success:
            return jsonify({
                'success': True,
                'data': {'workflow_id': workflow_id},
                'message': '워크플로우가 성공적으로 수정되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '워크플로우 수정에 실패했습니다.',
                'message': '워크플로우 수정 중 오류가 발생했습니다.'
            }), 500

    except Exception as e:
        logger.error(f"워크플로우 수정 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 수정 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/workflows/<workflow_id>', methods=['DELETE'])
@cross_origin()
def delete_workflow(workflow_id):
    """워크플로우 삭제"""
    try:
        # 기본 워크플로우는 삭제 불가
        if workflow_id in ['full_deployment', 'quick_deploy', 'security_focus', 'testing_only']:
            return jsonify({
                'success': False,
                'error': '기본 워크플로우는 삭제할 수 없습니다.',
                'message': '시스템 기본 워크플로우는 삭제가 제한됩니다.'
            }), 403

        # 워크플로우 존재 확인
        workflow = run_async(workflow_manager.get_workflow(workflow_id))
        if not workflow:
            return jsonify({
                'success': False,
                'error': '워크플로우를 찾을 수 없습니다.',
                'message': f'워크플로우 ID {workflow_id}가 존재하지 않습니다.'
            }), 404

        # 워크플로우 삭제 (워크플로우 매니저에서 제거)
        if hasattr(workflow_manager, 'workflows') and workflow_id in workflow_manager.workflows:
            del workflow_manager.workflows[workflow_id]
            run_async(workflow_manager._save_workflows())

        return jsonify({
            'success': True,
            'data': {'workflow_id': workflow_id},
            'message': '워크플로우가 성공적으로 삭제되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"워크플로우 삭제 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 삭제 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/execute', methods=['POST'])
@cross_origin()
def execute_workflow():
    """워크플로우 실행"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '요청 데이터가 없습니다.',
                'message': '워크플로우 실행에 필요한 데이터를 제공해주세요.'
            }), 400

        # 필수 필드 검증
        required_fields = ['workflow_id', 'plugin_id']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'필수 필드가 없습니다: {field}',
                    'message': f'워크플로우 실행에 필요한 {field} 필드를 제공해주세요.'
                }), 400

        workflow_id = str(data['workflow_id']) if data and data.get('workflow_id') else None
        plugin_id = str(data['plugin_id']) if data and data.get('plugin_id') else None
        parameters = data.get('parameters', {}) if data else {}

        if not workflow_id or not plugin_id:
            return jsonify({
                'success': False,
                'error': 'workflow_id와 plugin_id는 필수입니다',
                'message': '워크플로우 실행에 필요한 필수 필드를 제공해주세요.'
            }), 400

        # 워크플로우 존재 확인
        workflow = run_async(workflow_manager.get_workflow(workflow_id))
        if not workflow:
            return jsonify({
                'success': False,
                'error': '워크플로우를 찾을 수 없습니다.',
                'message': f'워크플로우 ID {workflow_id}가 존재하지 않습니다.'
            }), 404

        # 워크플로우 실행
        execution_id = run_async(workflow_manager.execute_workflow(workflow_id, plugin_id, parameters))

        return jsonify({
            'success': True,
            'data': {
                'execution_id': execution_id,
                'workflow_id': workflow_id,
                'plugin_id': plugin_id,
                'status': 'pending'
            },
            'message': '워크플로우 실행이 시작되었습니다.'
        }), 202

    except Exception as e:
        logger.error(f"워크플로우 실행 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '워크플로우 실행 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/executions', methods=['GET'])
@cross_origin()
def list_executions():
    """워크플로우 실행 목록 조회"""
    try:
        # 쿼리 파라미터
        plugin_id = request.args.get('plugin_id') if request.args else None
        status = request.args.get('status') if request.args else None
        limit = int(request.args.get('limit', 50)) if request.args else 50

        # 상태 필터링
        status_filter = None
        if status:
            try:
                status_filter = WorkflowStatus(status)
            except ValueError:
                return jsonify({
                    'success': False,
                    'error': '유효하지 않은 상태값입니다.',
                    'message': f'유효한 상태: {", ".join([s.value for s in WorkflowStatus])}'
                }), 400

        executions = run_async(workflow_manager.list_executions(plugin_id, status_filter, limit))

        return jsonify({
            'success': True,
            'data': executions,
            'message': f'{len(executions)}개의 실행 기록을 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"실행 목록 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '실행 목록 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/executions/<execution_id>', methods=['GET'])
@cross_origin()
def get_execution(execution_id):
    """특정 워크플로우 실행 조회"""
    try:
        execution = run_async(workflow_manager.get_execution(execution_id))

        if not execution:
            return jsonify({
                'success': False,
                'error': '실행 기록을 찾을 수 없습니다.',
                'message': f'실행 ID {execution_id}가 존재하지 않습니다.'
            }), 404

        return jsonify({
            'success': True,
            'data': execution.to_dict(),
            'message': '실행 정보를 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"실행 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '실행 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/executions/<execution_id>/logs', methods=['GET'])
@cross_origin()
def get_execution_logs(execution_id):
    """워크플로우 실행 로그 조회"""
    try:
        logs = run_async(workflow_manager.get_execution_logs(execution_id))

        if logs is None:
            return jsonify({
                'success': False,
                'error': '실행 기록을 찾을 수 없습니다.',
                'message': f'실행 ID {execution_id}가 존재하지 않습니다.'
            }), 404

        return jsonify({
            'success': True,
            'data': logs,
            'message': f'{len(logs)}개의 로그 항목을 찾았습니다.'
        }), 200

    except Exception as e:
        logger.error(f"실행 로그 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '실행 로그 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/executions/<execution_id>/cancel', methods=['POST'])
@cross_origin()
def cancel_execution(execution_id):
    """워크플로우 실행 취소"""
    try:
        success = run_async(workflow_manager.cancel_execution(execution_id))

        if success:
            return jsonify({
                'success': True,
                'data': {'execution_id': execution_id},
                'message': '워크플로우 실행이 취소되었습니다.'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': '실행 취소에 실패했습니다.',
                'message': '이미 완료되었거나 취소할 수 없는 상태입니다.'
            }), 400

    except Exception as e:
        logger.error(f"실행 취소 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '실행 취소 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/statistics', methods=['GET'])
@cross_origin()
def get_statistics():
    """워크플로우 통계 정보 조회"""
    try:
        stats = run_async(workflow_manager.get_workflow_statistics())

        return jsonify({
            'success': True,
            'data': stats,
            'message': '워크플로우 통계 정보를 성공적으로 조회했습니다.'
        }), 200

    except Exception as e:
        logger.error(f"통계 조회 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '통계 조회 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/cleanup', methods=['POST'])
@cross_origin()
def cleanup_executions():
    """오래된 실행 기록 정리"""
    try:
        data = request.get_json() or {}
        days = int(data.get('days', 30)) if data else 30

        cleaned_count = run_async(workflow_manager.cleanup_old_executions(days))

        return jsonify({
            'success': True,
            'data': {
                'cleaned_count': cleaned_count,
                'days': days
            },
            'message': f'{cleaned_count}개의 오래된 실행 기록이 정리되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"실행 기록 정리 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '실행 기록 정리 중 오류가 발생했습니다.'
        }), 500


@plugin_automation_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """헬스 체크"""
    try:
        # 워크플로우 매니저 상태 확인
        workflows_count = len(workflow_manager.workflows)
        executions_count = len(workflow_manager.executions)

        return jsonify({
            'success': True,
            'data': {
                'status': 'healthy',
                'workflows_count': workflows_count,
                'executions_count': executions_count,
                'timestamp': datetime.now().isoformat()
            },
            'message': '플러그인 자동화 시스템이 정상적으로 작동 중입니다.'
        }), 200

    except Exception as e:
        logger.error(f"헬스 체크 실패: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'message': '시스템 상태 확인 중 오류가 발생했습니다.'
        }), 500

# 에러 핸들러


@plugin_automation_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': '요청한 리소스를 찾을 수 없습니다.',
        'message': '올바른 API 엔드포인트를 확인해주세요.'
    }), 404


@plugin_automation_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': '내부 서버 오류가 발생했습니다.',
        'message': '잠시 후 다시 시도해주세요.'
    }), 500
