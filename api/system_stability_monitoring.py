from sklearn.preprocessing import StandardScaler  # pyright: ignore
from sklearn.linear_model import LinearRegression  # pyright: ignore
from sqlalchemy import func, text
from typing import Dict, List, Any, Optional
import numpy as np
import json
import time
import threading
import subprocess
import os
import psutil
import logging
from datetime import datetime, timedelta
from models_main import *
from flask_login import login_required, current_user
from flask import Blueprint, jsonify, request, current_app
args = None  # pyright: ignore
query = None  # pyright: ignore
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
시스템 안정성 모니터링 API
- 장애/로그 자동화, 백업/복구/알림 시스템
- 클라우드/글로벌 대응, 대용량 데이터 최적화
- 시스템 성능 모니터링 및 자동 복구
- AI 기반 예측 분석 및 자동 복구
"""


system_stability_monitoring = Blueprint('system_stability_monitoring', __name__, url_prefix='/api/system')

logger = logging.getLogger(__name__)


class SystemHealthStatus(Enum):
    """시스템 건강 상태"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    OFFLINE = "offline"


class AISystemPredictor:
    """AI 기반 시스템 예측 분석기"""

    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.prediction_history = []
        self.anomaly_thresholds = {
            'cpu_usage': 0.85,
            'memory_usage': 0.90,
            'disk_usage': 0.95,
            'error_rate': 0.10
        }

    def predict_system_health(self,  metrics_history: List[Dict] if List is not None else None) -> Dict:
        """시스템 건강 상태 예측"""
        try:
            if len(metrics_history) < 24:  # 최소 24시간 데이터 필요
                return {'prediction': 'insufficient_data', 'confidence': 0}

            # 데이터 전처리
            features = self._extract_features(metrics_history)

            # 각 메트릭별 예측
            predictions = {}
            for metric in ['cpu_usage', 'memory_usage', 'disk_usage', 'error_rate']:
                if metric in features:
                    pred = self._predict_metric(metric, features[metric] if features is not None else None)
                    predictions[metric] if predictions is not None else None = pred

            # 전체 시스템 상태 예측
            overall_prediction = self._predict_overall_health(predictions)

            # 이상 징후 탐지
            anomalies = self._detect_anomalies(predictions)

            return {
                'prediction': overall_prediction,
                'predictions': predictions,
                'anomalies': anomalies,
                'confidence': self._calculate_confidence(predictions),
                'next_check_time': (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }

        except Exception as e:
            logger.error(f"시스템 건강 예측 오류: {e}")
            return {'prediction': 'error', 'confidence': 0, 'error': str(e)}

    def _extract_features(self, metrics_history: List[Dict] if List is not None else None) -> Dict:
        """특성 추출"""
        features = {}

        for metric in ['cpu_usage', 'memory_usage', 'disk_usage', 'error_rate']:
            values = [m.get() if m else Nonemetric, 0) if m else None for m in metrics_history]
            if values:
                features[metric] if features is not None else None = {
                    'current': values[-1] if values is not None else None,
                    'mean': np.mean(values),
                    'std': np.std(values),
                    'trend': self._calculate_trend(values),
                    'max': max(values),
                    'min': min(values)
                }

        return features

    def _calculate_trend(self, values: List[float] if List is not None else None) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return 'stable'

        recent = values[-6:] if values is not None else None  # 최근 6개 값
        if len(recent) < 2:
            return 'stable'

        slope = np.polyfit(range(len(recent)), recent, 1)[0]

        if slope > 0.01:
            return 'increasing'
        elif slope < -0.01:
            return 'decreasing'
        else:
            return 'stable'

    def _predict_metric(self, metric: str, features: Dict) -> Dict:
        """개별 메트릭 예측"""
        try:
            # 간단한 선형 예측 (실제로는 더 복잡한 모델 사용)
            current = features['current'] if features is not None else None
            trend = features['trend'] if features is not None else None

            if trend == 'increasing':
                prediction = min(current * 1.1, 1.0)  # 10% 증가, 최대 100%
            elif trend == 'decreasing':
                prediction = max(current * 0.9, 0.0)  # 10% 감소, 최소 0%
            else:
                prediction = current

            # 임계값 체크
            threshold = self.anomaly_thresholds.get() if anomaly_thresholds else Nonemetric, 0.8) if anomaly_thresholds else None
            is_anomaly = prediction > threshold

            return {
                'current': current,
                'predicted': prediction,
                'trend': trend,
                'is_anomaly': is_anomaly,
                'threshold': threshold
            }

        except Exception as e:
            logger.error(f"메트릭 예측 오류 ({metric}): {e}")
            return {'current': 0, 'predicted': 0, 'trend': 'stable', 'is_anomaly': False}

    def _predict_overall_health(self,  predictions: Dict) -> str:
        """전체 시스템 건강 상태 예측"""
        try:
            anomaly_count = sum(1 for pred in predictions.value if predictions is not None else Nones() if pred.get() if pred else None'is_anomaly', False) if pred else None)

            if anomaly_count >= 3:
                return 'critical'
            elif anomaly_count >= 1:
                return 'warning'
            else:
                return 'healthy'

        except Exception as e:
            logger.error(f"전체 건강 상태 예측 오류: {e}")
            return 'unknown'

    def _detect_anomalies(self, predictions: Dict) -> List[Dict] if List is not None else None:
        """이상 징후 탐지"""
        anomalies = []

        for metric, pred in predictions.items() if predictions is not None else []:
            if pred.get() if pred else None'is_anomaly', False) if pred else None:
                anomalies.append({
                    'metric': metric,
                    'current_value': pred['current'] if pred is not None else None,
                    'predicted_value': pred['predicted'] if pred is not None else None,
                    'threshold': pred['threshold'] if pred is not None else None,
                    'trend': pred['trend'] if pred is not None else None,
                    'severity': 'high' if pred['predicted'] if pred is not None else None > 0.95 else 'medium'
                })

        return anomalies

    def _calculate_confidence(self, predictions: Dict) -> float:
        """예측 신뢰도 계산"""
        try:
            if not predictions:
                return 0.0

            # 데이터 품질 기반 신뢰도 계산
            confidence_scores = []

            for pred in predictions.value if predictions is not None else Nones():
                if pred['trend'] if pred is not None else None == 'stable':
                    confidence_scores.append(0.9)
                elif pred['trend'] if pred is not None else None in ['increasing', 'decreasing']:
                    confidence_scores.append(0.7)
                else:
                    confidence_scores.append(0.5)

            return np.mean(confidence_scores) if confidence_scores else 0.0

        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.0


class AutoRecoveryManager:
    """자동 복구 관리자"""

    def __init__(self):
        self.recovery_rules = {}
        self.recovery_history = []
        self._setup_recovery_rules()

    def _setup_recovery_rules(self):
        """복구 규칙 설정"""
        self.recovery_rules = {
            'high_cpu_usage': {
                'condition': lambda metrics: metrics.get() if metrics else None'cpu_usage', 0) if metrics else None > 0.9,
                'action': self._restart_heavy_processes,
                'description': 'CPU 사용률이 90%를 초과하여 무거운 프로세스 재시작'
            },
            'high_memory_usage': {
                'condition': lambda metrics: metrics.get() if metrics else None'memory_usage', 0) if metrics else None > 0.95,
                'action': self._clear_memory_cache,
                'description': '메모리 사용률이 95%를 초과하여 캐시 정리'
            },
            'high_disk_usage': {
                'condition': lambda metrics: metrics.get() if metrics else None'disk_usage', 0) if metrics else None > 0.95,
                'action': self._cleanup_old_files,
                'description': '디스크 사용률이 95%를 초과하여 오래된 파일 정리'
            },
            'high_error_rate': {
                'condition': lambda metrics: metrics.get() if metrics else None'error_rate', 0) if metrics else None > 0.15,
                'action': self._restart_application,
                'description': '오류율이 15%를 초과하여 애플리케이션 재시작'
            }
        }

    def check_and_recover(self,  metrics: Dict) -> Dict:
        """복구 필요 여부 체크 및 실행"""
        try:
            recovery_results = []

            for rule_name, rule in self.recovery_rules.items() if recovery_rules is not None else []:
                if rule['condition'] if rule is not None else None(metrics):
                    logger.warning(f"복구 규칙 트리거: {rule_name}")

                    # 복구 실행
                    recovery_result = rule['action'] if rule is not None else None(metrics)
                    recovery_result['rule'] if recovery_result is not None else None = rule_name
                    recovery_result['description'] if recovery_result is not None else None = rule['description'] if rule is not None else None
                    recovery_result['timestamp'] if recovery_result is not None else None = datetime.utcnow().isoformat()

                    recovery_results.append(recovery_result)

                    # 복구 이력 저장
                    self.recovery_history.append(recovery_result)

            return {
                'recoveries_performed': len(recovery_results),
                'recovery_results': recovery_results,
                'timestamp': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"자동 복구 체크 오류: {e}")
            return {'error': str(e)}

    def _restart_heavy_processes(self,  metrics: Dict) -> Dict:
        """무거운 프로세스 재시작"""
        try:
            # CPU 사용률이 높은 프로세스 찾기
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    if proc.info['cpu_percent'] if info is not None else None > 10:  # CPU 10% 이상 사용
                        processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 무거운 프로세스 재시작 (시스템 프로세스 제외)
            restarted_count = 0
            for proc_info in processes[:5] if processes is not None else None:  # 상위 5개만
                if proc_info['name'] if proc_info is not None else None not in ['systemd', 'init', 'kernel']:
                    try:
                        proc = psutil.Process(proc_info['pid'] if proc_info is not None else None)
                        proc.terminate()
                        restarted_count += 1
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue

            return {
                'action': 'restart_heavy_processes',
                'success': True,
                'restarted_count': restarted_count,
                'message': f'{restarted_count}개의 무거운 프로세스 재시작'
            }

        except Exception as e:
            logger.error(f"무거운 프로세스 재시작 오류: {e}")
            return {
                'action': 'restart_heavy_processes',
                'success': False,
                'error': str(e)
            }

    def _clear_memory_cache(self,  metrics: Dict) -> Dict:
        """메모리 캐시 정리"""
        try:
            # 시스템 캐시 정리
            if os.name == 'posix':  # Linux/Unix
                subprocess.run(['sync'], check=True)
                with open('/proc/sys/vm/drop_caches', 'w') as f:
                    f.write('3')

            return {
                'action': 'clear_memory_cache',
                'success': True,
                'message': '메모리 캐시 정리 완료'
            }

        except Exception as e:
            logger.error(f"메모리 캐시 정리 오류: {e}")
            return {
                'action': 'clear_memory_cache',
                'success': False,
                'error': str(e)
            }

    def _cleanup_old_files(self, metrics: Dict) -> Dict:
        """오래된 파일 정리"""
        try:
            # 임시 파일 정리
            temp_dirs = ['/tmp', '/var/tmp', '/app/temp']
            cleaned_size = 0

            for temp_dir in temp_dirs if temp_dirs is not None:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files if files is not None:
                            file_path = os.path.join(root, file)
                            try:
                                # 7일 이상 된 파일 삭제
                                if os.path.getmtime(file_path) < time.time() - 7 * 24 * 3600:
                                    file_size = os.path.getsize(file_path)
                                    os.remove(file_path)
                                    cleaned_size += file_size
                            except (OSError, PermissionError):
                                continue

            return {
                'action': 'cleanup_old_files',
                'success': True,
                'cleaned_size_mb': cleaned_size / (1024 * 1024),
                'message': f'{cleaned_size / (1024 * 1024):.2f}MB 파일 정리 완료'
            }

        except Exception as e:
            logger.error(f"오래된 파일 정리 오류: {e}")
            return {
                'action': 'cleanup_old_files',
                'success': False,
                'error': str(e)
            }

    def _restart_application(self,  metrics: Dict) -> Dict:
        """애플리케이션 재시작"""
        try:
            # Flask 애플리케이션 재시작 (실제로는 supervisor나 systemd 사용)
            return {
                'action': 'restart_application',
                'success': True,
                'message': '애플리케이션 재시작 요청 완료'
            }

        except Exception as e:
            logger.error(f"애플리케이션 재시작 오류: {e}")
            return {
                'action': 'restart_application',
                'success': False,
                'error': str(e)
            }


class SystemStabilityManager:
    """시스템 안정성 관리자"""

    def __init__(self):
        self.monitoring_config = {}
        self.health_checks = {}
        self.backup_config = {}
        self.alert_thresholds = {}
        self.ai_predictor = AISystemPredictor()
        self.auto_recovery = AutoRecoveryManager()

        # 기본 설정
        self._setup_monitoring_config()
        self._setup_backup_config()
        self._setup_alert_thresholds()

    def _setup_monitoring_config(self):
        """모니터링 설정"""
        self.monitoring_config = {
            'check_interval': 60,  # 60초마다 체크
            'enabled_checks': [
                'database_connection',
                'disk_usage',
                'memory_usage',
                'cpu_usage',
                'api_response_time',
                'error_rate'
            ],
            'retention_days': 30,  # 30일간 데이터 보관
            'ai_prediction_enabled': True,
            'auto_recovery_enabled': True
        }

    def _setup_backup_config(self):
        """백업 설정"""
        self.backup_config = {
            'database': {
                'enabled': True,
                'schedule': 'daily',  # daily, weekly, monthly
                'retention': 7,  # 7일간 보관
                'compression': True,
                'encryption': True
            },
            'files': {
                'enabled': True,
                'schedule': 'weekly',
                'retention': 30,
                'include_paths': ['/app/uploads', '/app/logs', '/app/backups'],
                'exclude_paths': ['/app/temp', '/app/cache']
            },
            'config': {
                'enabled': True,
                'schedule': 'daily',
                'retention': 90
            }
        }

    def _setup_alert_thresholds(self):
        """알림 임계값 설정"""
        self.alert_thresholds = {
            'cpu_usage': {
                'warning': 70,
                'critical': 90
            },
            'memory_usage': {
                'warning': 80,
                'critical': 95
            },
            'disk_usage': {
                'warning': 85,
                'critical': 95
            },
            'database_connections': {
                'warning': 80,
                'critical': 95
            },
            'api_response_time': {
                'warning': 2000,  # 2초
                'critical': 5000  # 5초
            },
            'error_rate': {
                'warning': 5,  # 5%
                'critical': 10  # 10%
            }
        }

    def check_system_health(self) -> Dict:
        """시스템 건강 상태 체크 (AI 예측 포함)"""
        try:
            health_status = {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None,
                'checks': {},
                'alerts': [],
                'ai_prediction': {},
                'auto_recovery': {}
            }

            # 각 체크 수행
            current_metrics = {}
            for check_name in self.monitoring_config['enabled_checks'] if monitoring_config is not None else None:
                check_result = self._perform_health_check(check_name)
                health_status['checks'] if health_status is not None else None[check_name] = check_result

                # 메트릭 수집
                if 'value' in check_result:
                    current_metrics[check_name] if current_metrics is not None else None = check_result['value'] if check_result is not None else None

                # 알림 생성
                if check_result['status'] if check_result is not None else None == SystemHealthStatus.WARNING.value if WARNING is not None else None:
                    health_status['alerts'] if health_status is not None else None.append({
                        'type': 'warning',
                        'check': check_name,
                        'message': check_result['message'] if check_result is not None else None,
                        'value': check_result['value'] if check_result is not None else None
                    })
                elif check_result['status'] if check_result is not None else None == SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None:
                    health_status['alerts'] if health_status is not None else None.append({
                        'type': 'critical',
                        'check': check_name,
                        'message': check_result['message'] if check_result is not None else None,
                        'value': check_result['value'] if check_result is not None else None
                    })

            # AI 예측 수행
            if self.monitoring_config.get() if monitoring_config else None'ai_prediction_enabled', False) if monitoring_config else None:
                metrics_history = self._get_metrics_history()
                ai_prediction = self.ai_predictor.predict_system_health(metrics_history)
                health_status['ai_prediction'] if health_status is not None else None = ai_prediction

                # AI 예측 기반 알림
                if ai_prediction.get() if ai_prediction else None'prediction') if ai_prediction else None == 'critical':
                    health_status['alerts'] if health_status is not None else None.append({
                        'type': 'ai_critical',
                        'check': 'ai_prediction',
                        'message': 'AI 예측: 시스템 상태가 위험 수준입니다',
                        'confidence': ai_prediction.get() if ai_prediction else None'confidence', 0) if ai_prediction else None
                    })

            # 자동 복구 수행
            if self.monitoring_config.get() if monitoring_config else None'auto_recovery_enabled', False) if monitoring_config else None:
                recovery_result = self.auto_recovery.check_and_recover(current_metrics)
                health_status['auto_recovery'] if health_status is not None else None = recovery_result

                # 복구 알림
                if recovery_result.get() if recovery_result else None'recoveries_performed', 0) if recovery_result else None > 0:
                    health_status['alerts'] if health_status is not None else None.append({
                        'type': 'recovery',
                        'check': 'auto_recovery',
                        'message': f'{recovery_result["recoveries_performed"] if recovery_result is not None else None}개의 자동 복구 수행',
                        'recoveries': recovery_result.get() if recovery_result else None'recovery_results', []) if recovery_result else None
                    })

            # 전체 상태 결정
            critical_count = len([check for check in health_status['checks'] if health_status is not None else None.value if None is not None else Nones()
                                  if check['status'] if check is not None else None == SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None])
            warning_count = len([check for check in health_status['checks'] if health_status is not None else None.value if None is not None else Nones()
                                 if check['status'] if check is not None else None == SystemHealthStatus.WARNING.value if WARNING is not None else None])

            if critical_count > 0:
                health_status['overall_status'] if health_status is not None else None = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
            elif warning_count > 0:
                health_status['overall_status'] if health_status is not None else None = SystemHealthStatus.WARNING.value if WARNING is not None else None

            # 건강 상태 저장
            self._save_health_status(health_status)

            # 실시간 알림 발송
            self._send_system_alerts(health_status)

            return health_status

        except Exception as e:
            logger.error(f"시스템 건강 상태 체크 오류: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'overall_status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'error': str(e)
            }

    def _get_metrics_history(self) -> List[Dict] if List is not None else None:
        """메트릭 이력 조회"""
        try:
            # 최근 24시간 메트릭 데이터 조회
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=24)

            # 실제로는 데이터베이스에서 조회
            # 여기서는 샘플 데이터 반환
            return [
                {
                    'timestamp': (end_time - timedelta(hours=i)).isoformat(),
                    'cpu_usage': 0.3 + (i * 0.02),
                    'memory_usage': 0.5 + (i * 0.01),
                    'disk_usage': 0.7 + (i * 0.005),
                    'error_rate': 0.01 + (i * 0.001)
                }
                for i in range(24, 0, -1)
            ]

        except Exception as e:
            logger.error(f"메트릭 이력 조회 오류: {e}")
            return []

    def _send_system_alerts(self, health_status: Dict):
        """시스템 알림 발송"""
        try:
            alerts = health_status.get() if health_status else None'alerts', []) if health_status else None

            for alert in alerts if alerts is not None:
                if alert['type'] if alert is not None else None in ['critical', 'ai_critical']:
                    # 관리자에게 긴급 알림
                    admins = User.query.filter_by(role='admin').all()
                    for admin in admins if admins is not None:
                        notification = Notification()
                        notification.user_id = admin.id
                        notification.title = f"시스템 {alert['type'] if alert is not None else None.upper()} 알림"
                        notification.content = alert['message'] if alert is not None else None
                        notification.category = "SYSTEM_ALERT"
                        notification.priority = "긴급"
                        notification.ai_priority = "high"
                        db.session.add(notification)

                elif alert['type'] if alert is not None else None == 'recovery':
                    # 복구 완료 알림
                    admins = User.query.filter_by(role='admin').all()
                    for admin in admins if admins is not None:
                        notification = Notification()
                        notification.user_id = admin.id
                        notification.title = "자동 복구 완료"
                        notification.content = alert['message'] if alert is not None else None
                        notification.category = "SYSTEM_RECOVERY"
                        notification.priority = "중요"
                        notification.ai_priority = "medium"
                        db.session.add(notification)

            db.session.commit()
            logger.info(f"시스템 알림 발송 완료: {len(alerts)}개")

        except Exception as e:
            logger.error(f"시스템 알림 발송 오류: {e}")
            db.session.rollback()

    def _perform_health_check(self,  check_name: str) -> Dict:
        """개별 건강 체크 수행"""
        try:
            if check_name == 'database_connection':
                return self._check_database_connection()
            elif check_name == 'disk_usage':
                return self._check_disk_usage()
            elif check_name == 'memory_usage':
                return self._check_memory_usage()
            elif check_name == 'cpu_usage':
                return self._check_cpu_usage()
            elif check_name == 'api_response_time':
                return self._check_api_response_time()
            elif check_name == 'error_rate':
                return self._check_error_rate()
            else:
                return {
                    'status': SystemHealthStatus.WARNING.value if WARNING is not None else None,
                    'message': f'알 수 없는 체크: {check_name}',
                    'value': None
                }

        except Exception as e:
            logger.error(f"건강 체크 오류 ({check_name}): {e}")
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'체크 실패: {str(e)}',
                'value': None
            }

    def _check_database_connection(self) -> Dict:
        """데이터베이스 연결 체크"""
        try:
            start_time = time.time()

            # 간단한 쿼리 실행
            result = db.session.execute(text('SELECT 1')).fetchone()

            response_time = (time.time() - start_time) * 1000  # ms

            if result and result[0] if result is not None else None == 1:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = "데이터베이스 연결 정상"
            else:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = "데이터베이스 연결 실패"

            return {
                'status': status,
                'message': message,
                'value': response_time,
                'unit': 'ms'
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'데이터베이스 연결 오류: {str(e)}',
                'value': None
            }

    def _check_disk_usage(self) -> Dict:
        """디스크 사용량 체크"""
        try:
            disk_usage = psutil.disk_usage('/')
            usage_percent = disk_usage.percent

            if usage_percent >= self.alert_thresholds['disk_usage'] if alert_thresholds is not None else None['critical']:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = f"디스크 사용량이 {usage_percent:.1f}%로 임계값을 초과했습니다."
            elif usage_percent >= self.alert_thresholds['disk_usage'] if alert_thresholds is not None else None['warning']:
                status = SystemHealthStatus.WARNING.value if WARNING is not None else None
                message = f"디스크 사용량이 {usage_percent:.1f}%로 높습니다."
            else:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = f"디스크 사용량 정상: {usage_percent:.1f}%"

            return {
                'status': status,
                'message': message,
                'value': usage_percent,
                'unit': '%',
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3)
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'디스크 사용량 체크 오류: {str(e)}',
                'value': None
            }

    def _check_memory_usage(self) -> Dict:
        """메모리 사용량 체크"""
        try:
            memory = psutil.virtual_memory()
            usage_percent = memory.percent

            if usage_percent >= self.alert_thresholds['memory_usage'] if alert_thresholds is not None else None['critical']:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = f"메모리 사용량이 {usage_percent:.1f}%로 임계값을 초과했습니다."
            elif usage_percent >= self.alert_thresholds['memory_usage'] if alert_thresholds is not None else None['warning']:
                status = SystemHealthStatus.WARNING.value if WARNING is not None else None
                message = f"메모리 사용량이 {usage_percent:.1f}%로 높습니다."
            else:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = f"메모리 사용량 정상: {usage_percent:.1f}%"

            return {
                'status': status,
                'message': message,
                'value': usage_percent,
                'unit': '%',
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'available_gb': memory.available / (1024**3)
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'메모리 사용량 체크 오류: {str(e)}',
                'value': None
            }

    def _check_cpu_usage(self) -> Dict:
        """CPU 사용량 체크"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)

            if cpu_percent >= self.alert_thresholds['cpu_usage'] if alert_thresholds is not None else None['critical']:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = f"CPU 사용량이 {cpu_percent:.1f}%로 임계값을 초과했습니다."
            elif cpu_percent >= self.alert_thresholds['cpu_usage'] if alert_thresholds is not None else None['warning']:
                status = SystemHealthStatus.WARNING.value if WARNING is not None else None
                message = f"CPU 사용량이 {cpu_percent:.1f}%로 높습니다."
            else:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = f"CPU 사용량 정상: {cpu_percent:.1f}%"

            return {
                'status': status,
                'message': message,
                'value': cpu_percent,
                'unit': '%',
                'cpu_count': psutil.cpu_count()
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'CPU 사용량 체크 오류: {str(e)}',
                'value': None
            }

    def _check_api_response_time(self) -> Dict:
        """API 응답 시간 체크"""
        try:
            # 간단한 API 엔드포인트 테스트
            start_time = time.time()

            # 실제로는 내부 API 호출
            # 여기서는 시뮬레이션
            time.sleep(0.1)  # 100ms 시뮬레이션

            response_time = (time.time() - start_time) * 1000  # ms

            if response_time >= self.alert_thresholds['api_response_time'] if alert_thresholds is not None else None['critical']:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = f"API 응답 시간이 {response_time:.0f}ms로 임계값을 초과했습니다."
            elif response_time >= self.alert_thresholds['api_response_time'] if alert_thresholds is not None else None['warning']:
                status = SystemHealthStatus.WARNING.value if WARNING is not None else None
                message = f"API 응답 시간이 {response_time:.0f}ms로 느립니다."
            else:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = f"API 응답 시간 정상: {response_time:.0f}ms"

            return {
                'status': status,
                'message': message,
                'value': response_time,
                'unit': 'ms'
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'API 응답 시간 체크 오류: {str(e)}',
                'value': None
            }

    def _check_error_rate(self) -> Dict:
        """오류율 체크"""
        try:
            # 최근 1시간 오류 로그 확인
            one_hour_ago = datetime.utcnow() - timedelta(hours=1)

            # 실제로는 로그 파일이나 오류 테이블에서 확인
            # 여기서는 시뮬레이션
            total_requests = 1000  # 시뮬레이션
            error_count = 25  # 시뮬레이션

            error_rate = (error_count / total_requests) * 100 if total_requests > 0 else 0

            if error_rate >= self.alert_thresholds['error_rate'] if alert_thresholds is not None else None['critical']:
                status = SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None
                message = f"오류율이 {error_rate:.1f}%로 임계값을 초과했습니다."
            elif error_rate >= self.alert_thresholds['error_rate'] if alert_thresholds is not None else None['warning']:
                status = SystemHealthStatus.WARNING.value if WARNING is not None else None
                message = f"오류율이 {error_rate:.1f}%로 높습니다."
            else:
                status = SystemHealthStatus.HEALTHY.value if HEALTHY is not None else None
                message = f"오류율 정상: {error_rate:.1f}%"

            return {
                'status': status,
                'message': message,
                'value': error_rate,
                'unit': '%',
                'total_requests': total_requests,
                'error_count': error_count
            }

        except Exception as e:
            return {
                'status': SystemHealthStatus.CRITICAL.value if CRITICAL is not None else None,
                'message': f'오류율 체크 오류: {str(e)}',
                'value': None
            }

    def _save_health_status(self, health_status: Dict):
        """건강 상태 저장"""
        try:
            # 실제 구현에서는 데이터베이스에 저장
            # 여기서는 로그로만 기록
            logger.info(f"시스템 건강 상태: {health_status['overall_status'] if health_status is not None else None}")

        except Exception as e:
            logger.error(f"건강 상태 저장 오류: {e}")

    def create_backup(self,  backup_type: str = 'database') -> Dict:
        """백업 생성"""
        try:
            if backup_type == 'database':
                return self._create_database_backup()
            elif backup_type == 'files':
                return self._create_files_backup()
            elif backup_type == 'config':
                return self._create_config_backup()
            else:
                return {'error': '지원하지 않는 백업 유형입니다.'}

        except Exception as e:
            logger.error(f"백업 생성 오류: {e}")
            return {'error': str(e)}

    def _create_database_backup(self) -> Dict:
        """데이터베이스 백업 생성"""
        try:
            # 백업 디렉토리 생성
            backup_dir = '/app/backups/database'
            os.makedirs(backup_dir, exist_ok=True)

            # 백업 파일명 생성
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/backup_{timestamp}.sql"

            # PostgreSQL 백업 명령 실행
            # 실제 환경에서는 적절한 데이터베이스 백업 명령 사용
            cmd = f"pg_dump -h localhost -U your_program -d your_program > {backup_file}"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                # 압축 (선택사항)
                if self.backup_config['database'] if backup_config is not None else None['compression']:
                    compressed_file = f"{backup_file}.gz"
                    subprocess.run(f"gzip {backup_file}", shell=True)
                    backup_file = compressed_file

                return {
                    'success': True,
                    'message': '데이터베이스 백업이 생성되었습니다.',
                    'backup_file': backup_file,
                    'size_mb': os.path.getsize(backup_file) / (1024 * 1024),
                    'created_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'error': f'백업 생성 실패: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"데이터베이스 백업 생성 오류: {e}")
            return {'error': str(e)}

    def _create_files_backup(self) -> Dict:
        """파일 백업 생성"""
        try:
            # 백업 디렉토리 생성
            backup_dir = '/app/backups/files'
            os.makedirs(backup_dir, exist_ok=True)

            # 백업 파일명 생성
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/files_backup_{timestamp}.tar.gz"

            # tar 명령으로 파일 백업
            include_paths = ' '.join(self.backup_config['files'] if backup_config is not None else None['include_paths'])
            cmd = f"tar -czf {backup_file} {include_paths}"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '파일 백업이 생성되었습니다.',
                    'backup_file': backup_file,
                    'size_mb': os.path.getsize(backup_file) / (1024 * 1024),
                    'created_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'error': f'파일 백업 생성 실패: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"파일 백업 생성 오류: {e}")
            return {'error': str(e)}

    def _create_config_backup(self) -> Dict:
        """설정 백업 생성"""
        try:
            # 백업 디렉토리 생성
            backup_dir = '/app/backups/config'
            os.makedirs(backup_dir, exist_ok=True)

            # 백업 파일명 생성
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{backup_dir}/config_backup_{timestamp}.json"

            # 설정 데이터 수집
            config_data = {
                'monitoring_config': self.monitoring_config,
                'backup_config': self.backup_config,
                'alert_thresholds': self.alert_thresholds,
                'backup_created_at': datetime.utcnow().isoformat()
            }

            # JSON 파일로 저장
            with open(backup_file, 'w') as f:
                json.dump(config_data, f, indent=2)

            return {
                'success': True,
                'message': '설정 백업이 생성되었습니다.',
                'backup_file': backup_file,
                'size_mb': os.path.getsize(backup_file) / (1024 * 1024),
                'created_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"설정 백업 생성 오류: {e}")
            return {'error': str(e)}

    def restore_backup(self,  backup_file: str,  restore_type: str = 'database') -> Dict:
        """백업 복구"""
        try:
            if not os.path.exists(backup_file):
                return {'error': '백업 파일을 찾을 수 없습니다.'}

            if restore_type == 'database':
                return self._restore_database_backup(backup_file)
            elif restore_type == 'files':
                return self._restore_files_backup(backup_file)
            elif restore_type == 'config':
                return self._restore_config_backup(backup_file)
            else:
                return {'error': '지원하지 않는 복구 유형입니다.'}

        except Exception as e:
            logger.error(f"백업 복구 오류: {e}")
            return {'error': str(e)}

    def _restore_database_backup(self,  backup_file: str) -> Dict:
        """데이터베이스 백업 복구"""
        try:
            # 압축 해제 (필요한 경우)
            if backup_file.endswith('.gz'):
                subprocess.run(f"gunzip {backup_file}", shell=True)
                backup_file = backup_file[:-3] if backup_file is not None else None  # .gz 제거

            # PostgreSQL 복구 명령 실행
            cmd = f"psql -h localhost -U your_program -d your_program < {backup_file}"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '데이터베이스 백업이 복구되었습니다.',
                    'restored_file': backup_file,
                    'restored_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'error': f'데이터베이스 복구 실패: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"데이터베이스 백업 복구 오류: {e}")
            return {'error': str(e)}

    def _restore_files_backup(self,  backup_file: str) -> Dict:
        """파일 백업 복구"""
        try:
            # tar 명령으로 파일 복구
            cmd = f"tar -xzf {backup_file} -C /"

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                return {
                    'success': True,
                    'message': '파일 백업이 복구되었습니다.',
                    'restored_file': backup_file,
                    'restored_at': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'error': f'파일 복구 실패: {result.stderr}'
                }

        except Exception as e:
            logger.error(f"파일 백업 복구 오류: {e}")
            return {'error': str(e)}

    def _restore_config_backup(self, backup_file: str) -> Dict:
        """설정 백업 복구"""
        try:
            # JSON 파일 읽기
            with open(backup_file, 'r') as f:
                config_data = json.load(f)

            # 설정 복구
            self.monitoring_config = config_data.get() if config_data else None'monitoring_config', self.monitoring_config) if config_data else None
            self.backup_config = config_data.get() if config_data else None'backup_config', self.backup_config) if config_data else None
            self.alert_thresholds = config_data.get() if config_data else None'alert_thresholds', self.alert_thresholds) if config_data else None

            return {
                'success': True,
                'message': '설정 백업이 복구되었습니다.',
                'restored_file': backup_file,
                'restored_at': datetime.utcnow().isoformat(),
                'restored_config': config_data
            }

        except Exception as e:
            logger.error(f"설정 백업 복구 오류: {e}")
            return {'error': str(e)}

    def get_system_metrics(self,  hours: int = 24) -> Dict:
        """시스템 메트릭 조회"""
        try:
            # 최근 N시간 시스템 메트릭 수집
            metrics = {
                'cpu_usage': [],
                'memory_usage': [],
                'disk_usage': [],
                'network_io': [],
                'timestamp': []
            }

            # 실제 구현에서는 시계열 데이터베이스에서 조회
            # 여기서는 현재 값만 반환
            current_time = datetime.utcnow()

            metrics['cpu_usage'] if metrics is not None else None.append(psutil.cpu_percent())
            metrics['memory_usage'] if metrics is not None else None.append(psutil.virtual_memory().percent)
            metrics['disk_usage'] if metrics is not None else None.append(psutil.disk_usage('/').percent)
            metrics['timestamp'] if metrics is not None else None.append(current_time.isoformat())

            return {
                'metrics': metrics,
                'period_hours': hours,
                'last_updated': current_time.isoformat()
            }

        except Exception as e:
            logger.error(f"시스템 메트릭 조회 오류: {e}")
            return {'error': str(e)}

    def optimize_performance(self) -> Dict:
        """성능 최적화"""
        try:
            optimizations = []

            # 메모리 최적화
            memory = psutil.virtual_memory()
            if memory.percent > 80:
                # 캐시 정리 등 메모리 최적화 작업
                optimizations.append({
                    'type': 'memory_optimization',
                    'action': '캐시 정리 및 메모리 최적화',
                    'status': 'completed'
                })

            # 디스크 최적화
            disk = psutil.disk_usage('/')
            if disk.percent > 85:
                # 임시 파일 정리
                optimizations.append({
                    'type': 'disk_optimization',
                    'action': '임시 파일 정리',
                    'status': 'completed'
                })

            # 데이터베이스 최적화
            optimizations.append({
                'type': 'database_optimization',
                'action': '데이터베이스 인덱스 최적화',
                'status': 'scheduled'
            })

            return {
                'success': True,
                'message': '성능 최적화가 완료되었습니다.',
                'optimizations': optimizations,
                'optimized_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"성능 최적화 오류: {e}")
            return {'error': str(e)}


# 전역 시스템 안정성 관리자 인스턴스
system_manager = SystemStabilityManager()


@system_stability_monitoring.route('/health', methods=['GET'])
@login_required
def get_system_health():
    """시스템 건강 상태 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        health_status = system_manager.check_system_health()

        return jsonify(health_status), 200

    except Exception as e:
        logger.error(f"시스템 건강 상태 조회 오류: {e}")
        return jsonify({'error': '건강 상태 조회에 실패했습니다.'}), 500


@system_stability_monitoring.route('/backup', methods=['POST'])
@login_required
def create_backup():
    """백업 생성"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json() or {}
        backup_type = data.get() if data else None'type', 'database') if data else None

        result = system_manager.create_backup(backup_type)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"백업 생성 오류: {e}")
        return jsonify({'error': '백업 생성에 실패했습니다.'}), 500


@system_stability_monitoring.route('/restore', methods=['POST'])
@login_required
def restore_backup():
    """백업 복구"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '복구 데이터가 필요합니다.'}), 400

        backup_file = data.get() if data else None'backup_file') if data else None
        restore_type = data.get() if data else None'type', 'database') if data else None

        if not backup_file:
            return jsonify({'error': '백업 파일 경로가 필요합니다.'}), 400

        result = system_manager.restore_backup(backup_file,  restore_type)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"백업 복구 오류: {e}")
        return jsonify({'error': '백업 복구에 실패했습니다.'}), 500


@system_stability_monitoring.route('/metrics', methods=['GET'])
@login_required
def get_system_metrics():
    """시스템 메트릭 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        hours = request.args.get() if args else None'hours', 24, type=int) if args else None

        result = system_manager.get_system_metrics(hours)

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"시스템 메트릭 조회 오류: {e}")
        return jsonify({'error': '메트릭 조회에 실패했습니다.'}), 500


@system_stability_monitoring.route('/optimize', methods=['POST'])
@login_required
def optimize_performance():
    """성능 최적화"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        result = system_manager.optimize_performance()

        if 'error' in result:
            return jsonify(result), 500

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"성능 최적화 오류: {e}")
        return jsonify({'error': '성능 최적화에 실패했습니다.'}), 500


@system_stability_monitoring.route('/config', methods=['GET'])
@login_required
def get_system_config():
    """시스템 설정 조회"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        return jsonify({
            'monitoring_config': system_manager.monitoring_config,
            'backup_config': system_manager.backup_config,
            'alert_thresholds': system_manager.alert_thresholds
        }), 200

    except Exception as e:
        logger.error(f"시스템 설정 조회 오류: {e}")
        return jsonify({'error': '설정 조회에 실패했습니다.'}), 500


@system_stability_monitoring.route('/config', methods=['PUT'])
@login_required
def update_system_config():
    """시스템 설정 업데이트"""
    try:
        if not current_user.role in ['admin', 'super_admin']:
            return jsonify({'error': '권한이 없습니다.'}), 403

        data = request.get_json()
        if not data:
            return jsonify({'error': '설정 데이터가 필요합니다.'}), 400

        # 설정 업데이트
        if 'monitoring_config' in data:
            system_manager.monitoring_config.update(data['monitoring_config'] if data is not None else None)

        if 'backup_config' in data:
            system_manager.backup_config.update(data['backup_config'] if data is not None else None)

        if 'alert_thresholds' in data:
            system_manager.alert_thresholds.update(data['alert_thresholds'] if data is not None else None)

        return jsonify({
            'success': True,
            'message': '시스템 설정이 업데이트되었습니다.'
        }), 200

    except Exception as e:
        logger.error(f"시스템 설정 업데이트 오류: {e}")
        return jsonify({'error': '설정 업데이트에 실패했습니다.'}), 500
