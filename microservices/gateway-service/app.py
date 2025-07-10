"""
API Gateway Service
모든 마이크로서비스의 진입점 역할을 하는 API 게이트웨이
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging
import os
from datetime import datetime

# OpenTelemetry 분산 추적 설정
try:
    from opentelemetry import trace  # type: ignore
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter  # type: ignore
    from opentelemetry.sdk.trace import TracerProvider  # type: ignore
    from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
    from opentelemetry.instrumentation.flask import FlaskInstrumentor  # type: ignore
    from opentelemetry.instrumentation.requests import RequestsInstrumentor  # type: ignore
    
    # Jaeger 설정
    jaeger_exporter = JaegerExporter(
        agent_host_name=os.getenv('JAEGER_HOST', 'jaeger-service.monitoring.svc.cluster.local'),
        agent_port=int(os.getenv('JAEGER_PORT', 14268)),
    )
    
    # Tracer Provider 설정
    trace.set_tracer_provider(TracerProvider())
    tracer_provider = trace.get_tracer_provider()  # type: ignore
    tracer_provider.add_span_processor(  # type: ignore
        BatchSpanProcessor(jaeger_exporter)
    )
    
    # Flask 및 Requests 계측
    FlaskInstrumentor().instrument()  # type: ignore
    RequestsInstrumentor().instrument()  # type: ignore
    
    TRACING_ENABLED = True
except ImportError:
    TRACING_ENABLED = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 서비스 엔드포인트 설정
SERVICES = {
    'user': os.getenv('USER_SERVICE_URL', 'http://localhost:5001'),
    'staff': os.getenv('STAFF_SERVICE_URL', 'http://localhost:5002'),
    'inventory': os.getenv('INVENTORY_SERVICE_URL', 'http://localhost:5003'),
    'order': os.getenv('ORDER_SERVICE_URL', 'http://localhost:5004'),
    'analytics': os.getenv('ANALYTICS_SERVICE_URL', 'http://localhost:5005'),
    'iot': os.getenv('IOT_SERVICE_URL', 'http://localhost:5006'),
    'notification': os.getenv('NOTIFICATION_SERVICE_URL', 'http://localhost:5007'),
    'ai': os.getenv('AI_SERVICE_URL', 'http://localhost:5008')
}

# 라우팅 규칙
ROUTES = {
    '/api/auth': 'user',
    '/api/users': 'user',
    '/api/staff': 'staff',
    '/api/attendance': 'staff',
    '/api/schedule': 'staff',
    '/api/inventory': 'inventory',
    '/api/orders': 'order',
    '/api/analytics': 'analytics',
    '/api/reports': 'analytics',
    '/api/iot': 'iot',
    '/api/notifications': 'notification',
    '/api/ai': 'ai',
    '/api/predictions': 'ai'
}

@app.before_request
def log_request():
    """요청 로깅"""
    logger.info(f"{datetime.now()} - {request.method} {request.path} from {request.remote_addr}")

@app.after_request
def log_response(response):
    """응답 로깅"""
    logger.info(f"{datetime.now()} - Response: {response.status_code}")
    return response

def get_target_service(path):
    """요청 경로에 따른 대상 서비스 결정"""
    for route, service in ROUTES.items():
        if path.startswith(route):
            return service
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({
        'status': 'healthy',
        'service': 'api-gateway',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/services/status', methods=['GET'])
def services_status():
    """모든 서비스 상태 확인"""
    status = {}
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'url': service_url,
                'response_time': response.elapsed.total_seconds()
            }
        except Exception as e:
            status[service_name] = {
                'status': 'error',
                'url': service_url,
                'error': str(e)
            }
    
    return jsonify({
        'gateway': 'healthy',
        'services': status,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH'])
def proxy_request(path):
    """요청을 적절한 서비스로 프록시"""
    full_path = f"/{path}"
    target_service = get_target_service(full_path)
    
    if not target_service:
        return jsonify({'error': 'Service not found'}), 404
    
    service_url = SERVICES[target_service]
    target_url = f"{service_url}{full_path}"
    
    try:
        # 요청 데이터 준비
        headers = {key: value for key, value in request.headers if key.lower() != 'host'}
        
        # 요청 전송
        if request.method == 'GET':
            response = requests.get(target_url, headers=headers, params=dict(request.args), timeout=30)
        elif request.method == 'POST':
            response = requests.post(target_url, headers=headers, json=request.get_json(), timeout=30)
        elif request.method == 'PUT':
            response = requests.put(target_url, headers=headers, json=request.get_json(), timeout=30)
        elif request.method == 'DELETE':
            response = requests.delete(target_url, headers=headers, timeout=30)
        elif request.method == 'PATCH':
            response = requests.patch(target_url, headers=headers, json=request.get_json(), timeout=30)
        
        # 응답 반환
        return response.content, response.status_code, dict(response.headers)
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout connecting to {target_service}")
        return jsonify({'error': f'Service {target_service} timeout'}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error to {target_service}")
        return jsonify({'error': f'Service {target_service} unavailable'}), 503
    except Exception as e:
        logger.error(f"Error proxying to {target_service}: {e}")
        return jsonify({'error': 'Internal gateway error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.getenv('GATEWAY_PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True) 