from extensions import redis_client
from models_main import Order, User, Notification, SystemLog, db
import joblib
import pickle
from dataclasses import dataclass, asdict
import aiohttp
import asyncio
from collections import defaultdict, deque
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading
import time
import json
import logging
from flask_login import login_required, current_user
from flask import Blueprint, request, jsonify, current_app
from typing import Optional
args = None  # pyright: ignore
form = None  # pyright: ignore
"""
실시간 AI 모니터링 및 자동화 시스템
AI 모델 성능 실시간 추적, 자동 재훈련, 성능 알림 시스템
"""


# 데이터베이스 모델 import

logger = logging.getLogger(__name__)

ai_monitoring_bp = Blueprint('ai_monitoring', __name__)


@dataclass
class ModelPerformance:
    """모델 성능 데이터 클래스"""
    model_name: str
    accuracy: float
    prediction_count: int
    error_count: int
    avg_response_time: float
    last_prediction: datetime
    last_training: datetime
    drift_score: float
    status: str  # 'healthy', 'warning', 'critical', 'training'


@dataclass
class PredictionLog:
    """예측 로그 데이터 클래스"""
    model_name: str
    prediction_id: str
    input_data: Optional[Dict[str, Any]]
    prediction_result: Optional[Dict[str, Any]]
    actual_result: Optional[Dict[str, Any]]
    confidence: float
    response_time: float
    timestamp: datetime
    user_id: Optional[int]


class AIMonitoringService:
    """AI 모니터링 서비스"""

    def __init__(self):
        self.model_performance = {}
        self.prediction_logs = deque(maxlen=10000)  # 최근 10,000개 예측 로그
        self.performance_history = defaultdict(lambda: deque(maxlen=1000))  # 각 모델별 성능 이력
        self.alert_thresholds = {
            'accuracy_threshold': 0.7,
            'response_time_threshold': 2.0,  # 초
            'error_rate_threshold': 0.1,
            'drift_threshold': 0.2
        }
        self.monitoring_active = True
        self.auto_retrain_enabled = True

        # 모니터링 스레드 시작
        self._start_monitoring_thread()

    def _start_monitoring_thread(self):
        """모니터링 스레드 시작"""
        def monitoring_loop():
            while self.monitoring_active:
                try:
                    self._check_model_performance()
                    self._detect_model_drift()
                    self._send_performance_alerts()
                    time.sleep(60)  # 1분마다 체크
                except Exception as e:
                    logger.error(f"모니터링 스레드 오류: {e}")
                    time.sleep(60)

        # AI 모니터링 스레드 비활성화됨 (서버는 계속 실행)
        # thread = threading.Thread(target=monitoring_loop, daemon=True)
        # thread.start()
        logger.info("AI 모니터링 스레드 비활성화됨")

    def log_prediction(self, model_name: str, prediction_data: Optional[Dict[str, Any]],
                       result: Optional[Dict[str, Any]], user_id: Optional[int] = None) -> str:
        """예측 로그 기록"""
        try:
            prediction_id = f"{model_name}_{int(time.time() * 1000)}"

            # 응답 시간 계산
            response_time = result.get('response_time', 0.0) if result else 0.0

            # 신뢰도 추출
            confidence = result.get('confidence', 0.0) if result else 0.0
            if isinstance(confidence, dict):
                confidence = confidence.get('overall', 0.0) if confidence else 0.0

            # 예측 로그 생성
            prediction_log = PredictionLog(
                model_name=model_name,
                prediction_id=prediction_id,
                input_data=prediction_data,
                prediction_result=result,
                actual_result=None,  # 나중에 실제 결과와 비교
                confidence=confidence,
                response_time=response_time,
                timestamp=datetime.now(),
                user_id=user_id
            )

            # 로그 저장
            self.prediction_logs.append(prediction_log)

            # 성능 메트릭 업데이트
            self._update_performance_metrics(model_name,  prediction_log)

            # Redis에 로그 캐시
            self._cache_prediction_log(prediction_log)

            logger.debug(f"예측 로그 기록: {prediction_id}")
            return prediction_id

        except Exception as e:
            logger.error(f"예측 로그 기록 실패: {e}")
            return ""

    def update_actual_result(self,  prediction_id: str,  actual_result: Optional[Dict[str,  Any]]):
        """실제 결과 업데이트"""
        try:
            # 예측 로그에서 해당 ID 찾기
            for log in self.prediction_logs:
                if log.prediction_id == prediction_id:
                    log.actual_result = actual_result

                    # 정확도 계산 및 업데이트
                    self._calculate_accuracy(log)
                    break

            # Redis 캐시 업데이트
            self._update_cached_log(prediction_id,  actual_result)

        except Exception as e:
            logger.error(f"실제 결과 업데이트 실패: {e}")

    def _update_performance_metrics(self,  model_name: str,  prediction_log: PredictionLog):
        """성능 메트릭 업데이트"""
        try:
            if model_name not in self.model_performance:
                self.model_performance[model_name] = ModelPerformance(
                    model_name=model_name,
                    accuracy=0.0,
                    prediction_count=0,
                    error_count=0,
                    avg_response_time=0.0,
                    last_prediction=datetime.now(),
                    last_training=datetime.now(),
                    drift_score=0.0,
                    status='healthy'
                )

            performance = self.model_performance[model_name]

            # 예측 횟수 증가
            performance.prediction_count += 1

            # 마지막 예측 시간 업데이트
            performance.last_prediction = prediction_log.timestamp

            # 응답 시간 평균 업데이트
            if performance.prediction_count == 1:
                performance.avg_response_time = prediction_log.response_time
            else:
                performance.avg_response_time = (
                    (performance.avg_response_time * (performance.prediction_count - 1) +
                     prediction_log.response_time) / performance.prediction_count
                )

            # 에러 카운트 업데이트
            if prediction_log.confidence < 0.5:  # 낮은 신뢰도는 에러로 간주
                performance.error_count += 1

            # 성능 이력에 추가
            self.performance_history[model_name].append({
                'timestamp': prediction_log.timestamp,
                'accuracy': performance.accuracy,
                'response_time': prediction_log.response_time,
                'confidence': prediction_log.confidence,
                'error_rate': performance.error_count / performance.prediction_count
            })

        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")

    def _calculate_accuracy(self,  prediction_log: PredictionLog):
        """정확도 계산"""
        try:
            if not prediction_log.actual_result:
                return

            # 예측 결과와 실제 결과 비교
            predicted = prediction_log.prediction_result
            actual = prediction_log.actual_result

            # 모델별 정확도 계산 로직
            if 'sales_forecast' in prediction_log.model_name:
                accuracy = self._calculate_sales_accuracy(predicted,  actual)
            elif 'inventory' in prediction_log.model_name:
                accuracy = self._calculate_inventory_accuracy(predicted, actual)
            elif 'customer' in prediction_log.model_name:
                accuracy = self._calculate_customer_accuracy(predicted, actual)
            else:
                accuracy = 0.5  # 기본값

            # 성능 업데이트
            performance = self.model_performance[prediction_log.model_name]
            performance.accuracy = accuracy

        except Exception as e:
            logger.error(f"정확도 계산 실패: {e}")

    def _calculate_sales_accuracy(self, predicted: Optional[Dict[str, Any]], actual: Optional[Dict[str, Any]]) -> float:
        """매출 예측 정확도 계산"""
        try:
            pred_sales = predicted.get('predicted_sales', 0) if predicted else 0
            actual_sales = actual.get('actual_sales', 0) if actual else 0
            if actual_sales == 0:
                return 0.5
            relative_error = abs(pred_sales - actual_sales) / actual_sales
            accuracy = max(0, 1 - relative_error)
            return accuracy
        except Exception as e:
            logger.error(f"매출 정확도 계산 실패: {e}")
            return 0.5

    def _calculate_inventory_accuracy(self, predicted: Optional[Dict[str, Any]], actual: Optional[Dict[str, Any]]) -> float:
        """재고 예측 정확도 계산"""
        try:
            pred_stock = predicted.get('predicted_stock', 0) if predicted else 0
            actual_stock = actual.get('actual_stock', 0) if actual else 0
            if actual_stock == 0:
                return 0.5
            relative_error = abs(pred_stock - actual_stock) / actual_stock
            accuracy = max(0, 1 - relative_error)
            return accuracy
        except Exception as e:
            logger.error(f"재고 정확도 계산 실패: {e}")
            return 0.5

    def _calculate_customer_accuracy(self, predicted: Optional[Dict[str, Any]], actual: Optional[Dict[str, Any]]) -> float:
        """고객 예측 정확도 계산"""
        try:
            pred_churn = predicted.get('churn_probability', 0.5) if predicted else 0.5
            actual_churn = actual.get('actual_churn', False) if actual else False
            if actual_churn and pred_churn > 0.5:
                return 1.0
            elif not actual_churn and pred_churn <= 0.5:
                return 1.0
            else:
                return 0.0
        except Exception as e:
            logger.error(f"고객 정확도 계산 실패: {e}")
            return 0.5

    def _check_model_performance(self):
        """모델 성능 체크"""
        try:
            if self.model_performance is not None:
                for model_name, performance in self.model_performance.items():
                    if performance.accuracy < self.alert_thresholds.get('accuracy_threshold', 0.7):
                        self._send_performance_alert(model_name, 'accuracy', performance.accuracy)
                    if performance.avg_response_time > self.alert_thresholds.get('response_time_threshold', 2.0):
                        self._send_performance_alert(model_name, 'response_time', performance.avg_response_time)
                    error_rate = performance.error_count / max(1, performance.prediction_count)
                    if error_rate > self.alert_thresholds.get('error_rate_threshold', 0.1):
                        self._send_performance_alert(model_name, 'error_rate', error_rate)
                    self._update_model_status(model_name, performance)
        except Exception as e:
            logger.error(f"모델 성능 체크 실패: {e}")

    def _detect_model_drift(self):
        """모델 드리프트 감지"""
        try:
            if self.model_performance is not None:
                for model_name, performance in self.model_performance.items():
                    recent_performance = list(self.performance_history[model_name])[-100:] if self.performance_history and model_name in self.performance_history else []
                    if len(recent_performance) < 10:
                        continue
                    recent_accuracies = [p['accuracy'] for p in recent_performance[-20:] if isinstance(p, dict) and 'accuracy' in p]
                    older_accuracies = [p['accuracy'] for p in recent_performance[-40:-20] if isinstance(p, dict) and 'accuracy' in p]
                    if len(recent_accuracies) >= 10 and len(older_accuracies) >= 10:
                        recent_avg = np.mean(recent_accuracies)
                        older_avg = np.mean(older_accuracies)
                        drift_score = abs(recent_avg - older_avg)
                        performance.drift_score = drift_score
                        if drift_score > self.alert_thresholds.get('drift_threshold', 0.1):
                            self._send_drift_alert(model_name, drift_score)
                            if self.auto_retrain_enabled:
                                self._trigger_auto_retrain(model_name)
        except Exception as e:
            logger.error(f"모델 드리프트 감지 실패: {e}")

    def _update_model_status(self,  model_name: str,  performance: ModelPerformance):
        """모델 상태 업데이트"""
        try:
            # 상태 결정 로직
            if performance.accuracy < 0.5 or performance.drift_score > 0.3:
                performance.status = 'critical'
            elif performance.accuracy < 0.7 or performance.drift_score > 0.2:
                performance.status = 'warning'
            elif performance.accuracy < 0.8:
                performance.status = 'training'
            else:
                performance.status = 'healthy'

        except Exception as e:
            logger.error(f"모델 상태 업데이트 실패: {e}")

    def _send_performance_alert(self, model_name: str, metric: str, value: float):
        """성능 알림 전송"""
        try:
            alert_message = f"AI 모델 '{model_name}' {metric} 경고: {value:.3f}"
            notification = Notification(
                user_id=1,
                title=f"AI 모델 성능 경고 - {model_name}",
                message=alert_message,
                type='ai_performance_warning',
                priority='high',
                data=json.dumps({
                    'model_name': model_name,
                    'metric': metric,
                    'value': value,
                    'threshold': self.alert_thresholds.get(f'{metric}_threshold', 0)
                })
            )
            db.session.add(notification)
            db.session.commit()
            system_log = SystemLog(
                level='warning',
                message=alert_message,
                category='ai_monitoring',
                data=json.dumps({
                    'model_name': model_name,
                    'metric': metric,
                    'value': value
                })
            )
            db.session.add(system_log)
            db.session.commit()
            logger.warning(f"AI 성능 알림: {alert_message}")
        except Exception as e:
            logger.error(f"성능 알림 전송 실패: {e}")

    def _send_drift_alert(self, model_name: str, drift_score: float):
        """드리프트 알림 전송"""
        try:
            alert_message = f"AI 모델 '{model_name}' 드리프트 감지: {drift_score:.3f}"
            notification = Notification(
                user_id=1,
                title=f"AI 모델 드리프트 감지 - {model_name}",
                message=alert_message,
                type='ai_drift_warning',
                priority='critical',
                data=json.dumps({
                    'model_name': model_name,
                    'drift_score': drift_score,
                    'threshold': self.alert_thresholds.get('drift_threshold', 0.1)
                })
            )
            db.session.add(notification)
            db.session.commit()
            logger.warning(f"AI 드리프트 알림: {alert_message}")
        except Exception as e:
            logger.error(f"드리프트 알림 전송 실패: {e}")

    def _trigger_auto_retrain(self,  model_name: str):
        """자동 재훈련 트리거"""
        try:
            # 재훈련 작업 큐에 추가
            retrain_task = {
                'model_name': model_name,
                'triggered_at': datetime.now().isoformat(),
                'reason': 'model_drift',
                'priority': 'high'
            }

            # Redis에 재훈련 작업 저장
            redis_client.lpush('ai_retrain_queue', json.dumps(retrain_task))

            # 알림 전송
            notification = Notification(
                user_id=1,
                title=f"AI 모델 자동 재훈련 시작 - {model_name}",
                message=f"모델 드리프트로 인한 자동 재훈련이 시작되었습니다.",
                type='ai_retrain_started',
                priority='medium',
                data=json.dumps(retrain_task)
            )

            db.session.add(notification)
            db.session.commit()

            logger.info(f"AI 모델 자동 재훈련 트리거: {model_name}")

        except Exception as e:
            logger.error(f"자동 재훈련 트리거 실패: {e}")

    def _cache_prediction_log(self,  prediction_log: PredictionLog):
        """예측 로그 캐시"""
        try:
            # Redis에 로그 저장 (24시간 만료)
            key = f"ai_prediction_log:{prediction_log.prediction_id}"
            redis_client.setex(key, 86400, json.dumps(asdict(prediction_log), default=str))

        except Exception as e:
            logger.error(f"예측 로그 캐시 실패: {e}")

    def _update_cached_log(self,  prediction_id: str,  actual_result: Optional[Dict[str,  Any]]):
        """캐시된 로그 업데이트"""
        try:
            key = f"ai_prediction_log:{prediction_id}"
            cached_data = redis_client.get(key) if redis_client else None

            if cached_data:
                log_data = json.loads(cached_data)
                log_data['actual_result'] = actual_result
                redis_client.setex(key, 86400, json.dumps(log_data))

        except Exception as e:
            logger.error(f"캐시 로그 업데이트 실패: {e}")

    def get_model_performance(self,  model_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """모델 성능 조회"""
        try:
            if model_name:
                if model_name in self.model_performance:
                    performance = self.model_performance[model_name]
                    return {
                        'success': True,
                        'performance': asdict(performance),
                        'history': list(self.performance_history[model_name])
                    }
                else:
                    return {'error': f'모델 {model_name}을 찾을 수 없습니다.'}
            else:
                # 모든 모델 성능 반환
                performances = {}
                for name, perf in self.model_performance.items():
                    performances[name] = {
                        **asdict(perf),
                        'history_count': len(self.performance_history[name])
                    }

                return {
                    'success': True,
                    'performances': performances,
                    'total_models': len(performances)
                }

        except Exception as e:
            logger.error(f"모델 성능 조회 실패: {e}")
            return {'error': f'성능 조회 실패: {str(e)}'}

    def get_performance_summary(self) -> Optional[Dict[str, Any]]:
        """성능 요약 조회"""
        try:
            total_predictions = sum(p.prediction_count for p in self.model_performance.values())
            avg_accuracy = np.mean([p.accuracy for p in self.model_performance.values()]) if self.model_performance else 0
            avg_response_time = np.mean([p.avg_response_time for p in self.model_performance.values()]) if self.model_performance else 0

            status_counts = defaultdict(int)
            for perf in self.model_performance.values():
                status_counts[perf.status] += 1

            return {
                'success': True,
                'summary': {
                    'total_models': len(self.model_performance),
                    'total_predictions': total_predictions,
                    'avg_accuracy': avg_accuracy,
                    'avg_response_time': avg_response_time,
                    'status_distribution': dict(status_counts),
                    'monitoring_active': self.monitoring_active,
                    'auto_retrain_enabled': self.auto_retrain_enabled
                },
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"성능 요약 조회 실패: {e}")
            return {'error': f'요약 조회 실패: {str(e)}'}

    def update_alert_thresholds(self,  thresholds: Optional[Dict[str,  float]]):
        """알림 임계값 업데이트"""
        try:
            self.alert_thresholds.update(thresholds)

            # 설정 저장
            redis_client.set('ai_alert_thresholds', json.dumps(self.alert_thresholds))

            logger.info(f"알림 임계값 업데이트: {thresholds}")

            return {'success': True, 'message': '임계값이 업데이트되었습니다.'}

        except Exception as e:
            logger.error(f"임계값 업데이트 실패: {e}")
            return {'error': f'임계값 업데이트 실패: {str(e)}'}


# 전역 서비스 인스턴스
ai_monitoring_service = AIMonitoringService()

# API 엔드포인트들


@ai_monitoring_bp.route('/api/ai/monitoring/performance', methods=['GET'])
@login_required
def get_model_performance():
    """모델 성능 조회"""
    try:
        model_name = request.args.get('model_name') if args else None
        result = ai_monitoring_service.get_model_performance(model_name)
        return jsonify(result)
    except Exception as e:
        logger.error(f"모델 성능 조회 API 오류: {e}")
        return jsonify({'error': '성능 조회에 실패했습니다.'}), 500


@ai_monitoring_bp.route('/api/ai/monitoring/summary', methods=['GET'])
@login_required
def get_performance_summary():
    """성능 요약 조회"""
    try:
        result = ai_monitoring_service.get_performance_summary()
        return jsonify(result)
    except Exception as e:
        logger.error(f"성능 요약 조회 API 오류: {e}")
        return jsonify({'error': '요약 조회에 실패했습니다.'}), 500


@ai_monitoring_bp.route('/api/ai/monitoring/thresholds', methods=['PUT'])
@login_required
def update_thresholds():
    """알림 임계값 업데이트"""
    try:
        data = request.get_json()
        result = ai_monitoring_service.update_alert_thresholds(data)
        return jsonify(result)
    except Exception as e:
        logger.error(f"임계값 업데이트 API 오류: {e}")
        return jsonify({'error': '임계값 업데이트에 실패했습니다.'}), 500


@ai_monitoring_bp.route('/api/ai/monitoring/log-prediction', methods=['POST'])
@login_required
def log_prediction():
    """예측 로그 기록"""
    try:
        data = request.get_json()
        model_name = data.get('model_name') if data else None
        prediction_data = data.get('prediction_data', {}) if data else {}
        result = data.get('result', {}) if data else {}
        user_id = current_user.id if current_user else None

        prediction_id = ai_monitoring_service.log_prediction(
            model_name, prediction_data, result, user_id
        )

        return jsonify({
            'success': True,
            'prediction_id': prediction_id
        })

    except Exception as e:
        logger.error(f"예측 로그 기록 API 오류: {e}")
        return jsonify({'error': '로그 기록에 실패했습니다.'}), 500


@ai_monitoring_bp.route('/api/ai/monitoring/update-result', methods=['POST'])
@login_required
def update_actual_result():
    """실제 결과 업데이트"""
    try:
        data = request.get_json()
        prediction_id = data.get('prediction_id') if data else None
        actual_result = data.get('actual_result', {}) if data else {}

        ai_monitoring_service.update_actual_result(prediction_id,  actual_result)

        return jsonify({
            'success': True,
            'message': '실제 결과가 업데이트되었습니다.'
        })

    except Exception as e:
        logger.error(f"실제 결과 업데이트 API 오류: {e}")
        return jsonify({'error': '결과 업데이트에 실패했습니다.'}), 500


@ai_monitoring_bp.route('/api/ai/monitoring/status', methods=['GET'])
@login_required
def get_monitoring_status():
    """모니터링 상태 조회"""
    try:
        return jsonify({
            'success': True,
            'monitoring_active': ai_monitoring_service.monitoring_active,
            'auto_retrain_enabled': ai_monitoring_service.auto_retrain_enabled,
            'alert_thresholds': ai_monitoring_service.alert_thresholds,
            'total_models': len(ai_monitoring_service.model_performance),
            'total_logs': len(ai_monitoring_service.prediction_logs),
            'timestamp': datetime.now().isoformat()
        })

    except Exception as e:
        logger.error(f"모니터링 상태 조회 API 오류: {e}")
        return jsonify({'error': '상태 조회에 실패했습니다.'}), 500
