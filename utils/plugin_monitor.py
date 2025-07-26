import time
import threading
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass
import statistics
import random

# requests가 없을 경우를 대비한 안전한 import
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None

# psutil이 없을 경우를 대비한 안전한 import
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None

logger = logging.getLogger(__name__)

@dataclass
class PluginMetrics:
    """플러그인 메트릭 데이터 클래스"""
    plugin_id: int
    response_time_ms: float = 0.0
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0
    execution_time_seconds: float = 0.0
    api_calls_count: int = 0
    api_errors_count: int = 0
    db_queries_count: int = 0
    file_operations_count: int = 0
    network_requests_count: int = 0
    measured_at: datetime = None
    
    def __post_init__(self):
        if self.measured_at is None:
            self.measured_at = datetime.utcnow()

class PluginMonitor:
    """플러그인 모니터링 시스템"""
    
    def __init__(self):
        self.monitoring_threads = {}
        self.health_check_threads = {}
        self.alert_handlers = {}
        self.metrics_history = {}
        self.is_running = False
        
    def start_monitoring(self, plugin_id: int, config: Dict[str, Any]):
        """플러그인 모니터링 시작"""
        if plugin_id in self.monitoring_threads:
            logger.warning(f"플러그인 {plugin_id} 모니터링이 이미 실행 중입니다.")
            return
            
        thread = threading.Thread(
            target=self._monitoring_loop,
            args=(plugin_id, config),
            daemon=True
        )
        thread.start()
        self.monitoring_threads[plugin_id] = thread
        logger.info(f"플러그인 {plugin_id} 모니터링이 시작되었습니다.")
        
    def stop_monitoring(self, plugin_id: int):
        """플러그인 모니터링 중지"""
        if plugin_id in self.monitoring_threads:
            # 스레드 중지 신호
            self.monitoring_threads[plugin_id] = None
            del self.monitoring_threads[plugin_id]
            logger.info(f"플러그인 {plugin_id} 모니터링이 중지되었습니다.")
            
    def _monitoring_loop(self, plugin_id: int, config: Dict[str, Any]):
        """모니터링 루프"""
        interval = config.get('monitoring_interval_seconds', 300)
        
        while self.monitoring_threads.get(plugin_id):
            try:
                # 메트릭 수집
                metrics = self._collect_metrics(plugin_id)
                
                # 메트릭 저장
                self._save_metrics(plugin_id, metrics)
                
                # 임계값 체크 및 알림
                self._check_thresholds(plugin_id, metrics, config)
                
                # 메트릭 히스토리 업데이트
                self._update_metrics_history(plugin_id, metrics)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"플러그인 {plugin_id} 모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
                
    def _collect_metrics(self, plugin_id: int) -> PluginMetrics:
        """플러그인 메트릭 수집"""
        metrics = PluginMetrics(plugin_id=plugin_id)
        
        try:
            # 더미 메트릭 생성 (실제 API 호출 대신)
            metrics.response_time_ms = random.uniform(50, 500)
            metrics.api_calls_count = random.randint(10, 100)
            metrics.api_errors_count = random.randint(0, 5)
            metrics.db_queries_count = random.randint(5, 50)
            metrics.file_operations_count = random.randint(0, 20)
            metrics.network_requests_count = random.randint(0, 30)
            
            # 리소스 사용량 측정 (psutil 사용)
            if PSUTIL_AVAILABLE:
                try:
                    process = psutil.Process()
                    metrics.cpu_usage_percent = process.cpu_percent()
                    metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                except Exception as e:
                    logger.warning(f"리소스 사용량 측정 실패: {e}")
                    # 더미 리소스 데이터
                    metrics.cpu_usage_percent = random.uniform(5, 80)
                    metrics.memory_usage_mb = random.uniform(20, 300)
            else:
                # 더미 리소스 데이터
                metrics.cpu_usage_percent = random.uniform(5, 80)
                metrics.memory_usage_mb = random.uniform(20, 300)
                
        except Exception as e:
            logger.warning(f"플러그인 {plugin_id} 메트릭 수집 실패: {e}")
            # 기본값 설정
            metrics.response_time_ms = 100.0
            metrics.cpu_usage_percent = 10.0
            metrics.memory_usage_mb = 50.0
            
        return metrics
        
    def _save_metrics(self, plugin_id: int, metrics: PluginMetrics):
        """메트릭을 데이터베이스에 저장"""
        try:
            # 실제 구현에서는 DB에 저장
            logger.debug(f"플러그인 {plugin_id} 메트릭 저장: {metrics}")
        except Exception as e:
            logger.error(f"메트릭 저장 실패: {e}")
            
    def _check_thresholds(self, plugin_id: int, metrics: PluginMetrics, config: Dict[str, Any]):
        """임계값 체크 및 알림"""
        alerts = []
        
        # 응답 시간 체크
        max_response_time = config.get('max_response_time_ms', 5000)
        if metrics.response_time_ms > max_response_time:
            alerts.append({
                'type': 'performance',
                'level': 'warning',
                'title': '응답 시간 초과',
                'message': f'응답 시간이 {metrics.response_time_ms:.2f}ms로 임계값 {max_response_time}ms를 초과했습니다.',
                'threshold_value': max_response_time,
                'current_value': metrics.response_time_ms
            })
            
        # CPU 사용량 체크
        max_cpu_usage = config.get('max_cpu_usage_percent', 80)
        if metrics.cpu_usage_percent > max_cpu_usage:
            alerts.append({
                'type': 'resource',
                'level': 'warning',
                'title': 'CPU 사용량 초과',
                'message': f'CPU 사용량이 {metrics.cpu_usage_percent:.1f}%로 임계값 {max_cpu_usage}%를 초과했습니다.',
                'threshold_value': max_cpu_usage,
                'current_value': metrics.cpu_usage_percent
            })
            
        # 메모리 사용량 체크
        max_memory_usage = config.get('max_memory_usage_mb', 512)
        if metrics.memory_usage_mb > max_memory_usage:
            alerts.append({
                'type': 'resource',
                'level': 'error',
                'title': '메모리 사용량 초과',
                'message': f'메모리 사용량이 {metrics.memory_usage_mb:.1f}MB로 임계값 {max_memory_usage}MB를 초과했습니다.',
                'threshold_value': max_memory_usage,
                'current_value': metrics.memory_usage_mb
            })
            
        # 오류율 체크
        if metrics.api_calls_count > 0:
            error_rate = (metrics.api_errors_count / metrics.api_calls_count) * 100
            max_error_rate = config.get('max_error_rate_percent', 5.0)
            if error_rate > max_error_rate:
                alerts.append({
                    'type': 'error',
                    'level': 'critical',
                    'title': '오류율 초과',
                    'message': f'오류율이 {error_rate:.1f}%로 임계값 {max_error_rate}%를 초과했습니다.',
                    'threshold_value': max_error_rate,
                    'current_value': error_rate
                })
                
        # 알림 발송
        for alert in alerts:
            self._send_alert(plugin_id, alert)
            
    def _send_alert(self, plugin_id: int, alert: Dict[str, Any]):
        """알림 발송"""
        try:
            # 실제 구현에서는 알림 시스템에 전송
            logger.warning(f"플러그인 {plugin_id} 알림: {alert['title']} - {alert['message']}")
            
            # 대시보드 알림
            self._send_dashboard_alert(plugin_id, alert)
            
        except Exception as e:
            logger.error(f"알림 발송 실패: {e}")
            
    def _send_dashboard_alert(self, plugin_id: int, alert: Dict[str, Any]):
        """대시보드 알림 전송"""
        # 실제 구현에서는 WebSocket이나 SSE를 통해 실시간 알림
        pass
        
    def _update_metrics_history(self, plugin_id: int, metrics: PluginMetrics):
        """메트릭 히스토리 업데이트"""
        if plugin_id not in self.metrics_history:
            self.metrics_history[plugin_id] = []
            
        self.metrics_history[plugin_id].append(metrics)
        
        # 최근 100개만 유지
        if len(self.metrics_history[plugin_id]) > 100:
            self.metrics_history[plugin_id] = self.metrics_history[plugin_id][-100:]

class PluginHealthChecker:
    """플러그인 헬스체크 시스템"""
    
    def __init__(self):
        self.health_check_threads = {}
        self.is_running = False
        
    def start_health_check(self, plugin_id: int, config: Dict[str, Any]):
        """헬스체크 시작"""
        if plugin_id in self.health_check_threads:
            logger.warning(f"플러그인 {plugin_id} 헬스체크가 이미 실행 중입니다.")
            return
            
        thread = threading.Thread(
            target=self._health_check_loop,
            args=(plugin_id, config),
            daemon=True
        )
        thread.start()
        self.health_check_threads[plugin_id] = thread
        logger.info(f"플러그인 {plugin_id} 헬스체크가 시작되었습니다.")
        
    def stop_health_check(self, plugin_id: int):
        """헬스체크 중지"""
        if plugin_id in self.health_check_threads:
            self.health_check_threads[plugin_id] = None
            del self.health_check_threads[plugin_id]
            logger.info(f"플러그인 {plugin_id} 헬스체크가 중지되었습니다.")
            
    def _health_check_loop(self, plugin_id: int, config: Dict[str, Any]):
        """헬스체크 루프"""
        interval = config.get('health_check_interval_seconds', 60)
        timeout = config.get('health_check_timeout_seconds', 30)
        
        while self.health_check_threads.get(plugin_id):
            try:
                health_status = self._perform_health_check(plugin_id, timeout)
                self._save_health_check(plugin_id, health_status)
                
                time.sleep(interval)
                
            except Exception as e:
                logger.error(f"플러그인 {plugin_id} 헬스체크 오류: {e}")
                time.sleep(30)  # 오류 시 30초 대기
                
    def _perform_health_check(self, plugin_id: int, timeout: int) -> Dict[str, Any]:
        """헬스체크 수행"""
        start_time = time.time()
        health_status = {
            'plugin_id': plugin_id,
            'health_status': 'unknown',
            'response_time_ms': 0,
            'is_responding': False,
            'checks': {},
            'details': {},
            'error_message': None,
            'checked_at': datetime.utcnow()
        }
        
        try:
            # 더미 헬스체크 (실제 API 호출 대신)
            health_status['response_time_ms'] = random.uniform(10, 200)
            health_status['is_responding'] = random.choice([True, True, True, False])  # 75% 성공률
            health_status['checks']['api_endpoint'] = health_status['is_responding']
            health_status['checks']['database_connection'] = True
            health_status['checks']['file_system'] = True
            health_status['checks']['memory_usage'] = True
            health_status['checks']['cpu_usage'] = True
            health_status['checks']['plugin_functionality'] = health_status['is_responding']
            
            if health_status['is_responding']:
                health_status['health_status'] = 'healthy'
                health_status['details'] = {
                    'version': '1.0.0',
                    'uptime': random.randint(1, 100),
                    'last_error': None
                }
            else:
                health_status['health_status'] = 'unhealthy'
                health_status['error_message'] = "더미 오류: 플러그인 응답 없음"
                
        except Exception as e:
            health_status['health_status'] = 'unhealthy'
            health_status['error_message'] = str(e)
            health_status['checks']['api_endpoint'] = False
            
        return health_status
        
    def _save_health_check(self, plugin_id: int, health_status: Dict[str, Any]):
        """헬스체크 결과 저장"""
        try:
            # 실제 구현에서는 DB에 저장
            logger.debug(f"플러그인 {plugin_id} 헬스체크 결과: {health_status['health_status']}")
        except Exception as e:
            logger.error(f"헬스체크 결과 저장 실패: {e}")

class PluginAlertManager:
    """플러그인 알림 관리자"""
    
    def __init__(self):
        self.alert_handlers = {}
        self.alert_history = []
        
    def register_alert_handler(self, alert_type: str, handler: Callable):
        """알림 핸들러 등록"""
        self.alert_handlers[alert_type] = handler
        
    def send_alert(self, plugin_id: int, alert: Dict[str, Any]):
        """알림 발송"""
        try:
            # 알림 히스토리에 추가
            alert_record = {
                'plugin_id': plugin_id,
                'alert': alert,
                'sent_at': datetime.utcnow()
            }
            self.alert_history.append(alert_record)
            
            # 최근 1000개만 유지
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]
                
            # 알림 핸들러 호출
            alert_type = alert.get('type', 'general')
            if alert_type in self.alert_handlers:
                self.alert_handlers[alert_type](plugin_id, alert)
            else:
                self._default_alert_handler(plugin_id, alert)
                
        except Exception as e:
            logger.error(f"알림 발송 실패: {e}")
            
    def _default_alert_handler(self, plugin_id: int, alert: Dict[str, Any]):
        """기본 알림 핸들러"""
        logger.warning(f"플러그인 {plugin_id} 알림: [{alert['level'].upper()}] {alert['title']} - {alert['message']}")
        
    def get_alert_history(self, plugin_id: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """알림 히스토리 조회"""
        history = self.alert_history
        
        if plugin_id:
            history = [h for h in history if h['plugin_id'] == plugin_id]
            
        return history[-limit:]
        
    def acknowledge_alert(self, alert_id: int, user_id: int):
        """알림 확인 처리"""
        try:
            # 실제 구현에서는 DB에서 알림 상태 업데이트
            logger.info(f"알림 {alert_id}가 사용자 {user_id}에 의해 확인되었습니다.")
        except Exception as e:
            logger.error(f"알림 확인 처리 실패: {e}")

class PluginSystemMonitor:
    """플러그인 시스템 모니터"""
    
    def __init__(self):
        self.monitor = PluginMonitor()
        self.health_checker = PluginHealthChecker()
        self.alert_manager = PluginAlertManager()
        self.system_status = {
            'system_status': 'healthy',
            'total_plugins': 0,
            'active_plugins': 0,
            'error_plugins': 0,
            'avg_response_time_ms': 0.0,
            'avg_cpu_usage_percent': 0.0,
            'avg_memory_usage_mb': 0.0,
            'total_api_calls': 0,
            'error_rate_percent': 0.0,
            'last_updated': datetime.utcnow()
        }
        
    def start_system_monitoring(self):
        """시스템 모니터링 시작"""
        self.is_running = True
        thread = threading.Thread(target=self._system_monitoring_loop, daemon=True)
        thread.start()
        logger.info("플러그인 시스템 모니터링이 시작되었습니다.")
        
    def stop_system_monitoring(self):
        """시스템 모니터링 중지"""
        self.is_running = False
        logger.info("플러그인 시스템 모니터링이 중지되었습니다.")
        
    def _system_monitoring_loop(self):
        """시스템 모니터링 루프"""
        while self.is_running:
            try:
                self._update_system_status()
                time.sleep(60)  # 1분마다 업데이트
            except Exception as e:
                logger.error(f"시스템 모니터링 오류: {e}")
                time.sleep(30)
                
    def _update_system_status(self):
        """시스템 상태 업데이트"""
        try:
            # 전체 플러그인 통계 계산
            all_metrics = []
            for plugin_metrics in self.monitor.metrics_history.values():
                if plugin_metrics:
                    all_metrics.extend(plugin_metrics)
                    
            if all_metrics:
                self.system_status.update({
                    'total_plugins': len(self.monitor.metrics_history),
                    'active_plugins': len([m for m in all_metrics if m.api_calls_count > 0]),
                    'avg_response_time_ms': statistics.mean([m.response_time_ms for m in all_metrics]),
                    'avg_cpu_usage_percent': statistics.mean([m.cpu_usage_percent for m in all_metrics]),
                    'avg_memory_usage_mb': statistics.mean([m.memory_usage_mb for m in all_metrics]),
                    'total_api_calls': sum([m.api_calls_count for m in all_metrics]),
                    'error_rate_percent': self._calculate_error_rate(all_metrics),
                    'last_updated': datetime.utcnow()
                })
                
        except Exception as e:
            logger.error(f"시스템 상태 업데이트 실패: {e}")
            
    def _calculate_error_rate(self, metrics: List[PluginMetrics]) -> float:
        """오류율 계산"""
        total_calls = sum([m.api_calls_count for m in metrics])
        total_errors = sum([m.api_errors_count for m in metrics])
        
        if total_calls > 0:
            return (total_errors / total_calls) * 100
        return 0.0
        
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return self.system_status.copy()
        
    def get_plugin_metrics(self, plugin_id: int, hours: int = 24) -> List[PluginMetrics]:
        """플러그인 메트릭 조회"""
        if plugin_id not in self.monitor.metrics_history:
            return []
            
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            m for m in self.monitor.metrics_history[plugin_id]
            if m.measured_at > cutoff_time
        ] 