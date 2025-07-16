from concurrent.futures import ThreadPoolExecutor, as_completed  # pyright: ignore
import redis
import hashlib
from collections import defaultdict, deque
import numpy as np
from dataclasses import dataclass
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
import threading
import asyncio
import time
import json
import logging
from functools import wraps
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app, g
from typing import Optional
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
통합 AI API (개선된 버전)
모든 AI 기능 통합, 실시간 처리, 캐싱, 에러 핸들링, 성능 모니터링, 확장성
"""


logger = logging.getLogger(__name__)

integrated_ai_bp = Blueprint('integrated_ai', __name__, url_prefix='/api/ai')


@dataclass
class AIRequest:
    """AI 요청"""
    id: str
    user_id: int
    request_type: str
    data: Dict[str, Any]
    timestamp: datetime
    status: str  # pending, processing, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


@dataclass
class AICache:
    """AI 캐시"""
    key: str
    data: Any
    timestamp: datetime
    ttl: int
    access_count: int


class AICacheManager:
    """AI 캐시 관리"""

    def __init__(self,  redis_url: Optional[str] = None):
        self.cache: Dict[str, AICache] = {}
        self.redis_client = None

        if redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()
                logger.info("Redis AI 캐시 연결 성공")
            except Exception as e:
                logger.warning(f"Redis AI 캐시 연결 실패: {e}")

    def get(self,  key: str) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        # Redis에서 먼저 확인
        if self.redis_client:
            try:
                cached_data = self.redis_client.get(f"ai_cache:{key}")
                if cached_data:
                    if isinstance(cached_data, bytes):
                        cached_data = cached_data.decode('utf-8')
                    if isinstance(cached_data, str):
                        return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis AI 캐시 조회 실패: {e}")

        # 메모리 캐시에서 확인
        if key in self.cache:
            cache_item = self.cache[key]

            # TTL 확인
            if datetime.utcnow() - cache_item.timestamp > timedelta(seconds=cache_item.ttl):
                del self.cache[key]
                return None

            # 접근 횟수 증가
            cache_item.access_count += 1
            return cache_item.data

        return None

    def set(self,  key: str,  data: Any, ttl=300) -> bool:
        """캐시에 데이터 저장"""
        try:
            # 메모리 캐시에 저장
            self.cache[key] = AICache(
                key=key,
                data=data,
                timestamp=datetime.utcnow(),
                ttl=ttl,
                access_count=1
            )

            # Redis에도 저장
            if self.redis_client:
                try:
                    serialized_data = json.dumps(data, default=str)
                    self.redis_client.setex(f"ai_cache:{key}", ttl, serialized_data)
                except Exception as e:
                    logger.warning(f"Redis AI 캐시 저장 실패: {e}")

            return True

        except Exception as e:
            logger.error(f"AI 캐시 저장 실패: {e}")
            return False

    def clear(self):
        """캐시 정리"""
        self.cache.clear()
        if self.redis_client:
            try:
                keys = self.redis_client.keys("ai_cache:*")
                # keys가 bytes 리스트일 수 있으므로 문자열로 변환
                if keys:
                    if isinstance(keys[0], bytes):
                        keys = [k.decode('utf-8') for k in keys]
                    self.redis_client.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis AI 캐시 정리 실패: {e}")


class AIRequestManager:
    """AI 요청 관리"""

    def __init__(self):
        self.requests: Dict[str, AIRequest] = {}
        self.request_queue = deque()
        self.processing_threads = []
        self.max_concurrent_requests = 10
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_requests)

    def submit_request(self,  user_id: int,  request_type: str,  data: Dict[str,  Any]) -> str:
        """AI 요청 제출"""
        request_id = hashlib.md5(f"{user_id}_{time.time()}_{request_type}".encode()).hexdigest()

        request = AIRequest(
            id=request_id,
            user_id=user_id,
            request_type=request_type,
            data=data,
            timestamp=datetime.utcnow(),
            status='pending'
        )

        self.requests[request_id] = request
        self.request_queue.append(request_id)

        # 비동기 처리 시작
        self._process_request_async(request_id)

        return request_id

    def _process_request_async(self, request_id: str):
        """비동기 요청 처리"""
        def process():
            try:
                request = self.requests[request_id]
                request.status = 'processing'
                start_time = time.time()

                # 요청 타입별 처리
                result = self._process_by_type(request.request_type,  request.data)

                request.result = result
                request.status = 'completed'
                request.processing_time = time.time() - start_time

            except Exception as e:
                if request_id in self.requests:
                    request = self.requests[request_id]
                    request.status = 'failed'
                    request.error = str(e)
                logger.error(f"AI 요청 처리 실패: {e}")

        # 스레드 풀에서 실행
        self.executor.submit(process)

    def _process_by_type(self,  request_type: str,  data: Dict[str,  Any]) -> Dict[str, Any]:
        """요청 타입별 처리"""
        processors = {
            'prediction': self._process_prediction,
            'analysis': self._process_analysis,
            'recommendation': self._process_recommendation,
            'optimization': self._process_optimization,
            'monitoring': self._process_monitoring,
            'sentiment': self._process_sentiment,
            'anomaly': self._process_anomaly,
            'forecast': self._process_forecast
        }

        processor = processors.get(request_type)
        if not processor:
            raise ValueError(f"지원하지 않는 요청 타입: {request_type}")

        return processor(data)

    def _process_prediction(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 처리"""
        # 실제로는 AI 모델을 사용한 예측
        prediction_type = data.get('type', 'sales')

        predictions = {
            'sales': {
                'next_week': np.random.randint(10000, 50000),
                'next_month': np.random.randint(50000, 200000),
                'confidence': np.random.uniform(0.7, 0.95)
            },
            'inventory': {
                'shortage_risk': np.random.uniform(0.1, 0.3),
                'optimal_stock': np.random.randint(100, 1000),
                'reorder_point': np.random.randint(50, 500)
            },
            'customer': {
                'churn_risk': np.random.uniform(0.05, 0.25),
                'lifetime_value': np.random.randint(100000, 1000000),
                'next_purchase': np.random.randint(1, 30)
            }
        }

        return {
            'type': prediction_type,
            'predictions': predictions.get(prediction_type, {}),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """분석 처리"""
        analysis_type = data.get('type', 'trend')

        analyses = {
            'trend': {
                'trend_direction': np.random.choice(['up', 'down', 'stable']),
                'trend_strength': np.random.uniform(0.1, 0.9),
                'key_factors': ['요인1', '요인2', '요인3']
            },
            'performance': {
                'score': np.random.uniform(0.6, 0.95),
                'benchmark': np.random.uniform(0.5, 0.9),
                'improvements': ['개선사항1', '개선사항2']
            },
            'correlation': {
                'correlation_matrix': np.random.rand(3, 3).tolist(),
                'key_relationships': ['관계1', '관계2']
            }
        }

        return {
            'type': analysis_type,
            'analysis': analyses.get(analysis_type, {}),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_recommendation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """추천 처리"""
        recommendation_type = data.get('type', 'product')

        recommendations = {
            'product': [
                {'id': 1, 'name': '제품A', 'score': 0.95, 'reason': '인기 제품'},
                {'id': 2, 'name': '제품B', 'score': 0.87, 'reason': '고객 선호도 높음'},
                {'id': 3, 'name': '제품C', 'score': 0.82, 'reason': '수익성 우수'}
            ],
            'action': [
                {'action': '재고 확충', 'priority': 'high', 'impact': 0.8},
                {'action': '가격 조정', 'priority': 'medium', 'impact': 0.6},
                {'action': '마케팅 강화', 'priority': 'low', 'impact': 0.4}
            ],
            'optimization': [
                {'area': '공정 최적화', 'savings': 150000, 'effort': 'medium'},
                {'area': '자동화 도입', 'savings': 300000, 'effort': 'high'},
                {'area': '공급망 개선', 'savings': 200000, 'effort': 'medium'}
            ]
        }

        return {
            'type': recommendation_type,
            'recommendations': recommendations.get(recommendation_type, []),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_optimization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 처리"""
        optimization_type = data.get('type', 'resource')

        optimizations = {
            'resource': {
                'cpu_optimization': {'current': 75, 'optimal': 60, 'savings': 20},
                'memory_optimization': {'current': 80, 'optimal': 65, 'savings': 15},
                'storage_optimization': {'current': 70, 'optimal': 55, 'savings': 25}
            },
            'process': {
                'automation_opportunities': ['프로세스1', '프로세스2'],
                'efficiency_gains': [0.15, 0.25, 0.1],
                'implementation_time': [2, 4, 1]  # 주 단위
            },
            'cost': {
                'current_cost': 1000000,
                'optimized_cost': 750000,
                'savings_percentage': 25,
                'payback_period': 6  # 개월
            }
        }

        return {
            'type': optimization_type,
            'optimization': optimizations.get(optimization_type, {}),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_monitoring(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """모니터링 처리"""
        monitoring_type = data.get('type', 'system')

        monitoring_data = {
            'system': {
                'cpu_usage': np.random.uniform(20, 80),
                'memory_usage': np.random.uniform(30, 85),
                'disk_usage': np.random.uniform(40, 90),
                'network_usage': np.random.uniform(10, 60),
                'alerts': ['경고1', '경고2'] if np.random.random() > 0.7 else []
            },
            'business': {
                'sales_today': np.random.randint(50000, 200000),
                'orders_today': np.random.randint(10, 100),
                'customers_online': np.random.randint(5, 50),
                'conversion_rate': np.random.uniform(0.02, 0.08),
                'issues': ['이슈1'] if np.random.random() > 0.8 else []
            },
            'security': {
                'failed_logins': np.random.randint(0, 10),
                'suspicious_activities': np.random.randint(0, 5),
                'security_score': np.random.uniform(0.7, 0.95),
                'threats_blocked': np.random.randint(0, 20)
            }
        }

        return {
            'type': monitoring_type,
            'monitoring': monitoring_data.get(monitoring_type, {}),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_sentiment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """감정 분석 처리"""
        text = data.get('text', '')

        # 간단한 감정 분석 (실제로는 NLP 모델 사용)
        positive_words = ['좋다', '훌륭하다', '만족', '추천', '최고']
        negative_words = ['나쁘다', '실망', '불만', '최악', '별로']

        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)

        if positive_count > negative_count:
            sentiment = 'positive'
            score = 0.7 + (positive_count - negative_count) * 0.1
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = 0.3 - (negative_count - positive_count) * 0.1
        else:
            sentiment = 'neutral'
            score = 0.5

        return {
            'sentiment': sentiment,
            'score': min(max(score, 0.0), 1.0),
            'confidence': np.random.uniform(0.7, 0.95),
            'keywords': ['키워드1', '키워드2'],
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_anomaly(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """이상 탐지 처리"""
        anomaly_type = data.get('type', 'data')

        anomalies = {
            'data': [
                {'field': '매출', 'value': 150000, 'expected': 100000, 'severity': 'high'},
                {'field': '주문수', 'value': 150, 'expected': 100, 'severity': 'medium'}
            ],
            'system': [
                {'metric': 'CPU 사용률', 'value': 95, 'threshold': 80, 'severity': 'critical'},
                {'metric': '메모리 사용률', 'value': 88, 'threshold': 85, 'severity': 'high'}
            ],
            'security': [
                {'event': '비정상 로그인', 'location': '192.168.1.100', 'severity': 'high'},
                {'event': '권한 상승 시도', 'user': 'user123', 'severity': 'critical'}
            ]
        }

        return {
            'type': anomaly_type,
            'anomalies': anomalies.get(anomaly_type, []),
            'total_count': len(anomalies.get(anomaly_type, [])),
            'timestamp': datetime.utcnow().isoformat()
        }

    def _process_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """예측 처리"""
        forecast_type = data.get('type', 'sales')
        periods = data.get('periods', 12)

        # 시계열 예측 데이터 생성
        base_value = np.random.randint(1000, 10000)
        trend = np.random.uniform(0.95, 1.05)
        seasonality = np.sin(np.linspace(0, 2*np.pi, periods))

        forecast_data = []
        for i in range(periods):
            value = base_value * (trend ** i) * (1 + 0.1 * seasonality[i])
            forecast_data.append({
                'period': i + 1,
                'value': int(value),
                'confidence_lower': int(value * 0.9),
                'confidence_upper': int(value * 1.1)
            })

        return {
            'type': forecast_type,
            'forecast': forecast_data,
            'accuracy': np.random.uniform(0.8, 0.95),
            'timestamp': datetime.utcnow().isoformat()
        }

    def get_request_status(self,  request_id: str) -> Optional[Dict[str, Any]]:
        """요청 상태 조회"""
        if request_id not in self.requests:
            return None

        request = self.requests[request_id]
        return {
            'id': request.id,
            'status': request.status,
            'result': request.result,
            'error': request.error,
            'processing_time': request.processing_time,
            'timestamp': request.timestamp.isoformat()
        }

    def get_user_requests(self,  user_id: int,  limit: int = 50) -> List[Dict[str, Any]]:
        """사용자 요청 조회"""
        user_requests = [r for r in self.requests.values() if r.user_id == user_id]
        user_requests.sort(key=lambda x: x.timestamp, reverse=True)

        return [
            {
                'id': req.id,
                'type': req.request_type,
                'status': req.status,
                'timestamp': req.timestamp.isoformat(),
                'processing_time': req.processing_time
            }
            for req in user_requests[:limit]
        ]


class AIPerformanceMonitor:
    """AI 성능 모니터링"""

    def __init__(self):
        self.metrics = defaultdict(list)
        self.performance_history = deque(maxlen=1000)

    def record_request(self,  request_type: str,  processing_time: float,  success: bool):
        """요청 성능 기록"""
        metric = {
            'type': request_type,
            'processing_time': processing_time,
            'success': success,
            'timestamp': datetime.utcnow()
        }

        self.metrics[request_type].append(metric)
        self.performance_history.append(metric)

        # 최근 100개만 유지
        if len(self.metrics[request_type]) > 100:
            self.metrics[request_type] = self.metrics[request_type][-100:]

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        stats = {}

        for request_type, metrics in self.metrics.items():
            if metrics:
                processing_times = [m['processing_time'] for m in metrics]
                success_count = sum(1 for m in metrics if m['success'])

                stats[request_type] = {
                    'total_requests': len(metrics),
                    'success_rate': success_count / len(metrics),
                    'avg_processing_time': sum(processing_times) / len(processing_times),
                    'min_processing_time': min(processing_times),
                    'max_processing_time': max(processing_times)
                }

        return stats


# 전역 매니저 인스턴스
cache_manager = AICacheManager()
request_manager = AIRequestManager()
performance_monitor = AIPerformanceMonitor()


@integrated_ai_bp.route('/request', methods=['POST'])
@login_required
def submit_ai_request():
    """AI 요청 제출"""
    try:
        user_id = current_user.id
        data = request.get_json()

        if not data or 'type' not in data:
            return jsonify({'error': '요청 타입이 필요합니다.'}), 400

        # 캐시 확인
        cache_key = f"{user_id}_{data['type']}_{hash(str(data))}"
        cached_result = cache_manager.get(cache_key)

        if cached_result:
            return jsonify({
                'success': True,
                'cached': True,
                'result': cached_result
            })

        # 새 요청 제출
        request_id = request_manager.submit_request(user_id,  data['type'],  data)

        return jsonify({
            'success': True,
            'request_id': request_id,
            'message': 'AI 요청이 제출되었습니다.'
        })

    except Exception as e:
        logger.error(f"AI 요청 제출 실패: {e}")
        return jsonify({'error': 'AI 요청 제출에 실패했습니다.'}), 500


@integrated_ai_bp.route('/request/<request_id>/status', methods=['GET'])
@login_required
def get_request_status(request_id: str):
    """요청 상태 조회"""
    try:
        status = request_manager.get_request_status(request_id)

        if not status:
            return jsonify({'error': '요청을 찾을 수 없습니다.'}), 404

        return jsonify({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"요청 상태 조회 실패: {e}")
        return jsonify({'error': '요청 상태 조회에 실패했습니다.'}), 500


@integrated_ai_bp.route('/requests', methods=['GET'])
@login_required
def get_user_requests():
    """사용자 요청 조회"""
    try:
        user_id = current_user.id
        limit = request.args.get('limit', 50, type=int)

        requests = request_manager.get_user_requests(user_id,  limit)

        return jsonify({
            'success': True,
            'requests': requests
        })

    except Exception as e:
        logger.error(f"사용자 요청 조회 실패: {e}")
        return jsonify({'error': '사용자 요청 조회에 실패했습니다.'}), 500


@integrated_ai_bp.route('/batch', methods=['POST'])
@login_required
def batch_ai_processing():
    """배치 AI 처리"""
    try:
        user_id = current_user.id
        data = request.get_json()

        if not data or 'requests' not in data:
            return jsonify({'error': '배치 요청이 필요합니다.'}), 400

        batch_requests = data['requests']
        if len(batch_requests) > 10:  # 최대 10개 요청
            return jsonify({'error': '최대 10개 요청만 처리 가능합니다.'}), 400

        # 배치 처리
        request_ids = []
        for req_data in batch_requests:
            request_id = request_manager.submit_request(user_id,  req_data['type'],  req_data)
            request_ids.append(request_id)

        return jsonify({
            'success': True,
            'request_ids': request_ids,
            'message': f'{len(request_ids)}개 요청이 제출되었습니다.'
        })

    except Exception as e:
        logger.error(f"배치 AI 처리 실패: {e}")
        return jsonify({'error': '배치 AI 처리에 실패했습니다.'}), 500


@integrated_ai_bp.route('/cache/clear', methods=['POST'])
@login_required
def clear_ai_cache():
    """AI 캐시 정리"""
    try:
        cache_manager.clear()

        return jsonify({
            'success': True,
            'message': 'AI 캐시가 정리되었습니다.'
        })

    except Exception as e:
        logger.error(f"AI 캐시 정리 실패: {e}")
        return jsonify({'error': 'AI 캐시 정리에 실패했습니다.'}), 500


@integrated_ai_bp.route('/performance', methods=['GET'])
@login_required
def get_ai_performance():
    """AI 성능 통계 조회"""
    try:
        stats = performance_monitor.get_performance_stats()

        return jsonify({
            'success': True,
            'performance': stats
        })

    except Exception as e:
        logger.error(f"AI 성능 통계 조회 실패: {e}")
        return jsonify({'error': 'AI 성능 통계 조회에 실패했습니다.'}), 500


@integrated_ai_bp.route('/health', methods=['GET'])
def ai_health_check():
    """AI 시스템 상태 확인"""
    try:
        health_status = {
            'status': 'healthy',
            'cache_manager': 'active',
            'request_manager': 'active',
            'performance_monitor': 'active',
            'active_requests': len(request_manager.requests),
            'cache_size': len(cache_manager.cache),
            'timestamp': datetime.utcnow().isoformat()
        }

        return jsonify({
            'success': True,
            'health': health_status
        })

    except Exception as e:
        logger.error(f"AI 상태 확인 실패: {e}")
        return jsonify({
            'success': False,
            'health': {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        }), 500
