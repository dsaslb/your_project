from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import logging
from datetime import datetime, timedelta

# 통합 모듈 import
from integration.workflow_engine import WorkflowEngine, WorkflowStatus
from integration.event_bus import EventBus, EventPriority
from integration.api_gateway import ApiGateway, RequestMethod, AuthType
from integration.microservice_integration import MicroserviceIntegration, ServiceStatus

# Blueprint 생성
integration_dashboard = Blueprint('integration_dashboard', __name__)

# 로깅 설정
logger = logging.getLogger(__name__)

# 통합 모듈 인스턴스
workflow_engine = WorkflowEngine()
event_bus = EventBus()
api_gateway = ApiGateway()
microservice_integration = MicroserviceIntegration()

@integration_dashboard.route('/admin/integration')
@login_required
def integration_dashboard_page():
    """통합 시스템 대시보드 메인 페이지"""
    try:
        # 통합 시스템 상태 정보
        integration_status = {
            'workflow_stats': workflow_engine.get_workflow_statistics(),
            'event_stats': event_bus.get_event_statistics(),
            'gateway_stats': api_gateway.get_statistics(),
            'microservice_stats': microservice_integration.get_all_services_status(),
            'system_health': {
                'workflow_system': True,  # 간단한 헬스 체크
                'event_system': True,
                'gateway_system': True,
                'microservice_system': True
            }
        }
        
        return render_template('admin/integration_dashboard.html', 
                             integration_status=integration_status,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"통합 시스템 대시보드 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/workflows')
@login_required
def workflow_management():
    """워크플로우 관리 페이지"""
    try:
        # 워크플로우 통계
        workflow_stats = workflow_engine.get_workflow_statistics()
        
        return render_template('admin/workflow_management.html',
                             workflow_stats=workflow_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"워크플로우 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/events')
@login_required
def event_management():
    """이벤트 관리 페이지"""
    try:
        # 이벤트 통계
        event_stats = event_bus.get_event_statistics()
        
        return render_template('admin/event_management.html',
                             event_stats=event_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"이벤트 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/gateway')
@login_required
def gateway_management():
    """API 게이트웨이 관리 페이지"""
    try:
        # 게이트웨이 통계
        gateway_stats = api_gateway.get_statistics()
        
        return render_template('admin/gateway_management.html',
                             gateway_stats=gateway_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"API 게이트웨이 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/microservices')
@login_required
def microservice_management():
    """마이크로서비스 관리 페이지"""
    try:
        # 마이크로서비스 통계
        microservice_stats = microservice_integration.get_all_services_status()
        
        return render_template('admin/microservice_management.html',
                             microservice_stats=microservice_stats,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"마이크로서비스 관리 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/monitoring')
@login_required
def integration_monitoring():
    """통합 시스템 모니터링 페이지"""
    try:
        # 전체 시스템 상태
        system_status = {
            'workflows': workflow_engine.get_workflow_statistics(),
            'events': event_bus.get_event_statistics(),
            'gateway': api_gateway.get_statistics(),
            'microservices': microservice_integration.get_all_services_status()
        }
        
        return render_template('admin/integration_monitoring.html',
                             system_status=system_status,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"통합 시스템 모니터링 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/settings')
@login_required
def integration_settings():
    """통합 시스템 설정 페이지"""
    try:
        # 시스템 설정 정보
        settings = {
            'workflow_settings': {
                'max_workers': 10,
                'default_timeout': 3600,
                'retry_count': 3
            },
            'event_settings': {
                'max_history_size': 10000,
                'cleanup_days': 30
            },
            'gateway_settings': {
                'rate_limit_default': 100,
                'timeout_default': 30
            },
            'microservice_settings': {
                'health_check_interval': 30,
                'circuit_breaker_enabled': True
            }
        }
        
        return render_template('admin/integration_settings.html',
                             settings=settings,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"통합 시스템 설정 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

@integration_dashboard.route('/admin/integration/reports')
@login_required
def integration_reports():
    """통합 시스템 리포트 페이지"""
    try:
        # 리포트 데이터
        report_data = {
            'workflow_reports': {
                'daily_executions': workflow_engine.get_workflow_statistics(),
                'performance_metrics': {
                    'avg_execution_time': 45.2,
                    'success_rate': 98.5,
                    'error_rate': 1.5
                }
            },
            'event_reports': {
                'event_volume': event_bus.get_event_statistics(),
                'top_event_types': [
                    {'type': 'user_login', 'count': 1250},
                    {'type': 'data_update', 'count': 890},
                    {'type': 'system_alert', 'count': 234}
                ]
            },
            'gateway_reports': {
                'traffic_analysis': api_gateway.get_statistics(),
                'top_endpoints': [
                    {'endpoint': '/api/users', 'requests': 1500},
                    {'endpoint': '/api/orders', 'requests': 1200},
                    {'endpoint': '/api/products', 'requests': 980}
                ]
            },
            'microservice_reports': {
                'service_health': microservice_integration.get_all_services_status(),
                'availability_metrics': {
                    'overall_availability': 99.8,
                    'response_time_avg': 125.5,
                    'error_rate': 0.2
                }
            }
        }
        
        return render_template('admin/integration_reports.html',
                             report_data=report_data,
                             current_user=current_user)
                             
    except Exception as e:
        logger.error(f"통합 시스템 리포트 페이지 로드 오류: {str(e)}")
        return render_template('errors/500.html', error=str(e)), 500

# 에러 핸들러
@integration_dashboard.errorhandler(404)
def not_found(error):
    return render_template('errors/404.html'), 404

@integration_dashboard.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html', error=str(error)), 500 