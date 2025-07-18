import sys
import signal
import subprocess
import os
import sqlite3
from collections import defaultdict, deque
import redis
import psutil
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
import threading
import time
import logging
import json
from flask import request
config = None  # pyright: ignore
form = None  # pyright: ignore
"""
시스템 모니터링 고도화 모듈
실시간 메트릭, 자동 장애 감지 및 복구 기능 제공
"""


logger = logging.getLogger(__name__)


class SystemMonitorAdvanced:
    """고도화된 시스템 모니터링 클래스"""

    def __init__(self, app=None):
        self.app = app
        self.redis_client = None
        self.metrics_history = defaultdict(lambda: deque(maxlen=1000))
        self.alert_thresholds = {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time': 2.0,
            'error_rate': 5.0
        }
        self.auto_recovery_enabled = True
        self.monitoring_active = False
        self.recovery_actions = {}
        self.health_checks = {}

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Flask 앱 초기화"""
        self.app = app

        # Redis 연결
        try:
            self.redis_client = redis.Redis(
                host=app.config.get('REDIS_HOST', 'localhost'),
                port=app.config.get('REDIS_PORT', 6379),
                db=app.config.get('REDIS_DB', 0),
                decode_responses=True
            )
        except Exception as e:
            logger.warning(f"Redis 연결 실패: {e}")
            self.redis_client = None

        # 기본 복구 액션 등록
        self._register_default_recovery_actions()

        # 기본 헬스 체크 등록
        self._register_default_health_checks()

        # 모니터링 시작
        self.start_monitoring()

    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return

        self.monitoring_active = True

        # 시스템 메트릭 수집 스레드
        metrics_thread = threading.Thread(target=self._collect_system_metrics, daemon=True)
        metrics_thread.start()

        # 장애 감지 스레드
        detection_thread = threading.Thread(target=self._detect_anomalies, daemon=True)
        detection_thread.start()

        # 자동 복구 스레드
        if self.auto_recovery_enabled:
            recovery_thread = threading.Thread(target=self._auto_recovery_loop, daemon=True)
            recovery_thread.start()

        logger.info("고도화된 시스템 모니터링 시작됨")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        logger.info("시스템 모니터링 중지됨")

    def set_alert_threshold(self, metric: str, threshold: float):
        """알림 임계값 설정"""
        self.alert_thresholds[metric] = threshold
        logger.info(f"알림 임계값 업데이트: {metric} = {threshold}")

    def register_recovery_action(self, condition: str, action: Callable[..., Any]):
        """복구 액션 등록"""
        self.recovery_actions[condition] = action
        logger.info(f"복구 액션 등록: {condition}")

    def register_health_check(self, name: str, check_func: Callable[..., Any]):
        """헬스 체크 등록"""
        self.health_checks[name] = check_func
        logger.info(f"헬스 체크 등록: {name}")

    def get_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 조회"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)

            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent

            # 네트워크 사용량
            network = psutil.net_io_counters()

            # 프로세스 수
            process_count = len(psutil.pids())

            # 시스템 부하
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]

            metrics = {
                'timestamp': datetime.now().isoformat(),
                'cpu': {
                    'usage_percent': cpu_percent,
                    'load_average': load_avg
                },
                'memory': {
                    'usage_percent': memory_percent,
                    'total': memory.total,
                    'available': memory.available,
                    'used': memory.used
                },
                'disk': {
                    'usage_percent': disk_percent,
                    'total': disk.total,
                    'free': disk.free,
                    'used': disk.used
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'processes': {
                    'count': process_count
                }
            }

            # 메트릭 히스토리에 저장
            self._store_metrics(metrics)

            return metrics

        except Exception as e:
            logger.error(f"시스템 메트릭 수집 오류: {e}")
            return {'error': str(e)}

    def get_application_metrics(self) -> Dict[str, Any]:
        """애플리케이션 메트릭 조회"""
        try:
            if not self.app:
                return {'error': 'Flask 앱이 초기화되지 않음'}

            # 요청 통계 (Redis에서)
            request_stats = self._get_request_stats()

            # 에러 통계
            error_stats = self._get_error_stats()

            # 데이터베이스 연결 상태
            db_status = self._check_database_connection()

            # Redis 연결 상태
            redis_status = self._check_redis_connection()

            return {
                'timestamp': datetime.now().isoformat(),
                'requests': request_stats,
                'errors': error_stats,
                'database': db_status,
                'redis': redis_status,
                'uptime': self._get_uptime()
            }

        except Exception as e:
            logger.error(f"애플리케이션 메트릭 수집 오류: {e}")
            return {'error': str(e)}

    def run_health_checks(self) -> Dict[str, Any]:
        """헬스 체크 실행"""
        results: Dict[str, Any] = {}

        for name, check_func in self.health_checks.items():
            try:
                result = check_func()
                results[name] = {
                    'status': 'healthy' if result else 'unhealthy',
                    'timestamp': datetime.now().isoformat(),
                    'details': result
                }
            except Exception as e:
                results[name] = {
                    'status': 'error',
                    'timestamp': datetime.now().isoformat(),
                    'error': str(e)
                }

        return results

    def get_anomaly_detection(self) -> Dict[str, Any]:
        """이상 감지 결과"""
        try:
            anomalies: List[Dict[str, Any]] = []

            # CPU 사용률 이상 감지
            cpu_metrics = list(self.metrics_history['cpu_usage'])
            if len(cpu_metrics) > 10:
                avg_cpu = sum(cpu_metrics[-10:]) / 10
                if avg_cpu > self.alert_thresholds['cpu_usage']:
                    anomalies.append({
                        'type': 'high_cpu_usage',
                        'severity': 'warning' if avg_cpu < 95 else 'critical',
                        'value': avg_cpu,
                        'threshold': self.alert_thresholds['cpu_usage'],
                        'timestamp': datetime.now().isoformat()
                    })

            # 메모리 사용률 이상 감지
            memory_metrics = list(self.metrics_history['memory_usage'])
            if len(memory_metrics) > 10:
                avg_memory = sum(memory_metrics[-10:]) / 10
                if avg_memory > self.alert_thresholds['memory_usage']:
                    anomalies.append({
                        'type': 'high_memory_usage',
                        'severity': 'warning' if avg_memory < 95 else 'critical',
                        'value': avg_memory,
                        'threshold': self.alert_thresholds['memory_usage'],
                        'timestamp': datetime.now().isoformat()
                    })

            # 디스크 사용률 이상 감지
            disk_metrics = list(self.metrics_history['disk_usage'])
            if len(disk_metrics) > 5:
                avg_disk = sum(disk_metrics[-5:]) / 5
                if avg_disk > self.alert_thresholds['disk_usage']:
                    anomalies.append({
                        'type': 'high_disk_usage',
                        'severity': 'warning' if avg_disk < 95 else 'critical',
                        'value': avg_disk,
                        'threshold': self.alert_thresholds['disk_usage'],
                        'timestamp': datetime.now().isoformat()
                    })

            return {
                'anomalies': anomalies,
                'total_anomalies': len(anomalies),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"이상 감지 오류: {e}")
            return {'error': str(e)}

    def _collect_system_metrics(self):
        """시스템 메트릭 수집 루프"""
        while self.monitoring_active:
            try:
                metrics = self.get_system_metrics()

                # 개별 메트릭 저장
                if 'cpu' in metrics:
                    self.metrics_history['cpu_usage'].append(metrics['cpu']['usage_percent'])
                if 'memory' in metrics:
                    self.metrics_history['memory_usage'].append(metrics['memory']['usage_percent'])
                if 'disk' in metrics:
                    self.metrics_history['disk_usage'].append(metrics['disk']['usage_percent'])

                # Redis에 저장
                if self.redis_client:
                    try:
                        self.redis_client.setex(
                            'system_metrics',
                            300,  # 5분 TTL
                            json.dumps(metrics)
                        )
                    except Exception as e:
                        logger.warning(f"Redis 메트릭 저장 실패: {e}")

                time.sleep(30)  # 30초마다 수집

            except Exception as e:
                logger.error(f"메트릭 수집 오류: {e}")
                time.sleep(60)

    def _detect_anomalies(self):
        """이상 감지 루프"""
        while self.monitoring_active:
            try:
                anomalies = self.get_anomaly_detection()

                if anomalies.get('total_anomalies', 0) > 0:
                    logger.warning(f"이상 감지됨: {anomalies['anomalies']}")

                    # 자동 복구 트리거
                    if self.auto_recovery_enabled:
                        self._trigger_recovery_actions(anomalies['anomalies'])

                time.sleep(60)  # 1분마다 감지

            except Exception as e:
                logger.error(f"이상 감지 오류: {e}")
                time.sleep(120)

    def _auto_recovery_loop(self):
        """자동 복구 루프"""
        while self.monitoring_active:
            try:
                # 복구 액션 실행
                self._execute_recovery_actions()

                time.sleep(300)  # 5분마다 복구 체크

            except Exception as e:
                logger.error(f"자동 복구 오류: {e}")
                time.sleep(600)

    def _trigger_recovery_actions(self, anomalies: List[Dict[str, Any]]):
        """복구 액션 트리거"""
        for anomaly in anomalies:
            anomaly_type = anomaly['type']

            if anomaly_type in self.recovery_actions:
                try:
                    logger.info(f"복구 액션 실행: {anomaly_type}")
                    self.recovery_actions[anomaly_type](anomaly)
                except Exception as e:
                    logger.error(f"복구 액션 실행 실패: {e}")

    def _execute_recovery_actions(self):
        """복구 액션 실행"""
        try:
            # 메모리 정리
            if len(self.metrics_history['memory_usage']) > 0:
                recent_memory = self.metrics_history['memory_usage'][-5:]
                if all(usage > 90 for usage in recent_memory):
                    self._cleanup_memory()

            # 디스크 정리
            if len(self.metrics_history['disk_usage']) > 0:
                recent_disk = self.metrics_history['disk_usage'][-3:]
                if all(usage > 95 for usage in recent_disk):
                    self._cleanup_disk()

            # 프로세스 재시작 (필요시)
            if len(self.metrics_history['cpu_usage']) > 0:
                recent_cpu = self.metrics_history['cpu_usage'][-10:]
                if all(usage > 95 for usage in recent_cpu):
                    self._restart_critical_processes()

        except Exception as e:
            logger.error(f"복구 액션 실행 오류: {e}")

    def _cleanup_memory(self):
        """메모리 정리"""
        try:
            import gc
            collected = gc.collect()
            logger.info(f"메모리 정리 완료: {collected} 객체 정리")

            # 캐시 정리
            if self.redis_client:
                try:
                    self.redis_client.flushdb()
                    logger.info("Redis 캐시 정리 완료")
                except Exception as e:
                    logger.warning(f"Redis 캐시 정리 실패: {e}")

        except Exception as e:
            logger.error(f"메모리 정리 오류: {e}")

    def _cleanup_disk(self):
        """디스크 정리"""
        try:
            # 로그 파일 정리
            log_dir = 'logs'
            if os.path.exists(log_dir):
                for file in os.listdir(log_dir):
                    if file.endswith('.log'):
                        file_path = os.path.join(log_dir, file)
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > 7 * 24 * 3600:  # 7일 이상
                            os.remove(file_path)
                            logger.info(f"오래된 로그 파일 삭제: {file}")

            # 임시 파일 정리
            temp_dir = '/tmp'
            if os.path.exists(temp_dir):
                for file in os.listdir(temp_dir):
                    if file.startswith('your_program_'):
                        file_path = os.path.join(temp_dir, file)
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > 24 * 3600:  # 24시간 이상
                            try:
                                os.remove(file_path)
                                logger.info(f"임시 파일 삭제: {file}")
                            except:
                                pass

        except Exception as e:
            logger.error(f"디스크 정리 오류: {e}")

    def _restart_critical_processes(self):
        """중요 프로세스 재시작"""
        try:
            # 현재 프로세스 ID
            current_pid = os.getpid()

            # 웹 서버 재시작 (Flask 개발 서버인 경우)
            if 'flask' in sys.argv[0].lower() or 'python' in sys.argv[0].lower():
                logger.warning("중요 프로세스 재시작 시도")
                # 실제로는 supervisor나 systemd를 통해 재시작해야 함

        except Exception as e:
            logger.error(f"프로세스 재시작 오류: {e}")

    def _store_metrics(self, metrics: Dict[str, Any]):
        """메트릭 저장"""
        try:
            # 메모리에 저장
            for key, value in metrics.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, (int, float)):
                            self.metrics_history[f"{key}_{sub_key}"].append(sub_value)
                elif isinstance(value, (int, float)):
                    self.metrics_history[key].append(value)

        except Exception as e:
            logger.error(f"메트릭 저장 오류: {e}")

    def _get_request_stats(self) -> Dict[str, Any]:
        """요청 통계 조회"""
        try:
            if self.redis_client:
                stats = self.redis_client.hgetall('request_stats')
                return {
                    'total_requests': int(stats.get('total', 0)),
                    'successful_requests': int(stats.get('success', 0)),
                    'failed_requests': int(stats.get('failed', 0)),
                    'avg_response_time': float(stats.get('avg_response_time', 0))
                }
            return {'error': 'Redis 연결 없음'}
        except Exception as e:
            return {'error': str(e)}

    def _get_error_stats(self) -> Dict[str, Any]:
        """에러 통계 조회"""
        try:
            if self.redis_client:
                stats = self.redis_client.hgetall('error_stats')
                return {
                    'total_errors': int(stats.get('total', 0)),
                    'error_rate': float(stats.get('rate', 0)),
                    'last_error': stats.get('last_error', ''),
                    'error_types': json.loads(stats.get('types', '{}'))
                }
            return {'error': 'Redis 연결 없음'}
        except Exception as e:
            return {'error': str(e)}

    def _check_database_connection(self) -> Dict[str, Any]:
        """데이터베이스 연결 상태 확인"""
        try:
            # SQLite 연결 테스트
            conn = sqlite3.connect('instance/your_program.db')
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            conn.close()

            return {
                'status': 'connected' if result else 'disconnected',
                'response_time': 0.001  # 실제로는 측정 필요
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _check_redis_connection(self) -> Dict[str, Any]:
        """Redis 연결 상태 확인"""
        try:
            if self.redis_client:
                start_time = time.time()
                self.redis_client.ping()
                response_time = time.time() - start_time

                return {
                    'status': 'connected',
                    'response_time': response_time
                }
            else:
                return {
                    'status': 'disconnected',
                    'error': 'Redis 클라이언트 없음'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }

    def _get_uptime(self) -> Dict[str, Any]:
        """시스템 업타임 조회"""
        try:
            uptime_seconds = time.time() - psutil.boot_time()
            uptime_days = uptime_seconds // (24 * 3600)
            uptime_hours = (uptime_seconds % (24 * 3600)) // 3600
            uptime_minutes = (uptime_seconds % 3600) // 60

            return {
                'seconds': int(uptime_seconds),
                'formatted': f"{int(uptime_days)}일 {int(uptime_hours)}시간 {int(uptime_minutes)}분"
            }
        except Exception as e:
            return {'error': str(e)}

    def _register_default_recovery_actions(self):
        """기본 복구 액션 등록"""
        self.register_recovery_action('high_cpu_usage', self._handle_high_cpu)
        self.register_recovery_action('high_memory_usage', self._handle_high_memory)
        self.register_recovery_action('high_disk_usage', self._handle_high_disk)

    def _register_default_health_checks(self):
        """기본 헬스 체크 등록"""
        self.register_health_check('database', self._check_database_connection)
        self.register_health_check('redis', self._check_redis_connection)
        self.register_health_check('disk_space', self._check_disk_space)
        self.register_health_check('memory_usage', self._check_memory_usage)

    def _handle_high_cpu(self, anomaly: Dict[str, Any]):
        """높은 CPU 사용률 처리"""
        logger.warning(f"높은 CPU 사용률 감지: {anomaly['value']}%")
        # CPU 집약적 프로세스 종료 또는 스케줄링 조정

    def _handle_high_memory(self, anomaly: Dict[str, Any]):
        """높은 메모리 사용률 처리"""
        logger.warning(f"높은 메모리 사용률 감지: {anomaly['value']}%")
        self._cleanup_memory()

    def _handle_high_disk(self, anomaly: Dict[str, Any]):
        """높은 디스크 사용률 처리"""
        logger.warning(f"높은 디스크 사용률 감지: {anomaly['value']}%")
        self._cleanup_disk()

    def _check_disk_space(self) -> bool:
        """디스크 공간 확인"""
        try:
            disk = psutil.disk_usage('/')
            return disk.percent < 90
        except:
            return False

    def _check_memory_usage(self) -> bool:
        """메모리 사용률 확인"""
        try:
            memory = psutil.virtual_memory()
            return memory.percent < 90
        except:
            return False


# 전역 인스턴스
system_monitor = SystemMonitorAdvanced()


def init_system_monitoring(app):
    """시스템 모니터링 초기화"""
    system_monitor.init_app(app)
    return system_monitor


def get_system_status() -> Dict[str, Any]:
    """시스템 상태 조회"""
    return {
        'system_metrics': system_monitor.get_system_metrics(),
        'application_metrics': system_monitor.get_application_metrics(),
        'health_checks': system_monitor.run_health_checks(),
        'anomalies': system_monitor.get_anomaly_detection()
    }


def set_monitoring_threshold(metric: str, threshold: float):
    """모니터링 임계값 설정"""
    system_monitor.set_alert_threshold(metric, threshold)


def register_custom_health_check(name: str, check_func: Callable[..., Any]):
    """커스텀 헬스 체크 등록"""
    system_monitor.register_health_check(name, check_func)


def register_custom_recovery_action(condition: str, action: Callable[..., Any]):
    """커스텀 복구 액션 등록"""
    system_monitor.register_recovery_action(condition, action)
