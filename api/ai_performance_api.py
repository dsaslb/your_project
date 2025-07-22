"""
AI 기반 성능 예측/이상 탐지/자동화 API
- /api/ai/performance/predict
- /api/ai/performance/anomaly
- /api/ai/performance/auto-optimize
"""

from flask import Blueprint, request, jsonify
from ai.ai_performance_optimizer import get_ai_optimizer
from utils.performance_monitor import get_performance_monitor

bp = Blueprint('ai_performance_api', __name__, url_prefix='/api/ai/performance')

# 실시간 메트릭 데이터 수집 함수
# (실제 운영에서는 Redis, DB, 모니터링 시스템에서 가져옴)
def get_recent_metrics(hours: int = 1):
    monitor = get_performance_monitor()
    if monitor:
        return [m.__dict__ for m in list(monitor.metrics_history)[-hours*60:]]
    return []

@bp.route('/predict', methods=['GET'])
def predict_performance():
    """미래 부하/리소스 사용량 예측"""
    hours = int(request.args.get('hours', 1))
    steps = int(request.args.get('steps', 10))
    metrics = get_recent_metrics(hours)
    ai = get_ai_optimizer()
    cpu_pred = ai.predict_future(metrics, 'cpu_usage', steps)
    mem_pred = ai.predict_future(metrics, 'memory_usage', steps)
    return jsonify({
        'future_cpu': cpu_pred,
        'future_memory': mem_pred,
        'steps': steps
    })

@bp.route('/anomaly', methods=['GET'])
def detect_anomaly():
    """실시간 이상 탐지 결과 제공"""
    hours = int(request.args.get('hours', 1))
    metrics = get_recent_metrics(hours)
    ai = get_ai_optimizer()
    anomalies = ai.detect_anomalies(metrics)
    return jsonify({
        'anomaly_count': len(anomalies),
        'anomalies': anomalies
    })

@bp.route('/auto-optimize', methods=['POST'])
def auto_optimize():
    """AI 기반 자동 최적화 실행"""
    hours = int(request.json.get('hours', 1)) if request.is_json else 1
    metrics = get_recent_metrics(hours)
    ai = get_ai_optimizer()
    signal = ai.auto_optimize_signal(metrics)
    # 실제 자동화(스케일업, 캐시조정 등)는 signal 값에 따라 별도 트리거
    return jsonify(signal) 