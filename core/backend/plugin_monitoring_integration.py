"""
플러그인 모니터링과 실시간 알림 통합 시스템
플러그인 성능 모니터링과 실시간 알림을 연동하여 자동 알림 발송
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from collections import defaultdict, deque

from .enhanced_realtime_alerts import EnhancedRealtimeAlertSystem, AlertType, AlertSeverity
from .plugin_monitoring import PluginMonitor

logger = logging.getLogger(__name__)

@dataclass
class PluginPerformanceData:
    """플러그인 성능 데이터"""
    plugin_id: str
    plugin_name: str
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    request_count: int
    uptime: float
    last_activity: datetime
    status: str
    timestamp: datetime

class PluginMonitoringIntegration:
    """플러그인 모니터링과 실시간 알림 통합 시스템"""
    
    def __init__(self):
        self.alert_system = EnhancedRealtimeAlertSystem()
        self.plugin_monitor = PluginMonitor()
        self.integration_active = False
        self.integration_thread: Optional[threading.Thread] = None
        
        # 플러그인 성능 데이터 캐시
        self.plugin_performance_cache: Dict[str, PluginPerformanceData] = {}
        
        # 성능 트렌드 데이터 (최근 100개 데이터 포인트)
        self.performance_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        
        # 알림 발송 이력 (중복 알림 방지)
        self.alert_history: Dict[str, datetime] = {}
        
        # 통합 설정
        self.integration_config = {
            'monitoring_interval': 30,  # 30초마다 모니터링
            'alert_cooldown': 300,      # 5분간 중복 알림 방지
            'trend_analysis_enabled': True,
            'auto_resolution_enabled': True,
            'performance_baseline_enabled': True
        }
        
        # 성능 기준선 (동적으로 계산)
        self.performance_baselines: Dict[str, Dict[str, float]] = {}
        
        # 통합 콜백 등록
        self._setup_integration_callbacks()
        
    def _setup_integration_callbacks(self):
        """통합 콜백 설정"""
        # 플러그인 모니터에서 메트릭 업데이트 시 알림 시스템에 전달
        self.plugin_monitor.add_alert_callback(self._on_plugin_alert)
        
        # 알림 시스템에서 알림 발생 시 추가 처리
        self.alert_system.add_alert_callback(self._on_alert_generated)
        
    def start_integration(self):
        """통합 시스템 시작"""
        if self.integration_active:
            return
            
        self.integration_active = True
        
        # 개별 시스템 시작
        self.alert_system.start_monitoring()
        self.plugin_monitor.start_monitoring()
        
        # 통합 모니터링 스레드 시작
        self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
        self.integration_thread.start()
        
        logger.info("플러그인 모니터링과 실시간 알림 통합 시스템 시작")
        
    def stop_integration(self):
        """통합 시스템 중지"""
        self.integration_active = False
        
        # 개별 시스템 중지
        self.alert_system.stop_monitoring()
        self.plugin_monitor.stop_monitoring()
        
        if self.integration_thread:
            self.integration_thread.join(timeout=5)
            
        logger.info("플러그인 모니터링과 실시간 알림 통합 시스템 중지")
        
    def register_plugin(self, plugin_id: str, plugin_name: str):
        """플러그인 등록"""
        # 플러그인 모니터에 등록
        self.plugin_monitor.register_plugin(plugin_id, plugin_name)
        
        # 알림 시스템에 플러그인 정보 전달
        self.alert_system.plugin_metrics[plugin_id] = {
            'plugin_name': plugin_name,
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time': 0.0,
            'error_rate': 0.0,
            'request_count': 0,
            'uptime': 0.0,
            'last_activity': datetime.utcnow().isoformat(),
            'status': 'active',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # 성능 기준선 초기화
        self.performance_baselines[plugin_id] = {
            'cpu_usage': 0.0,
            'memory_usage': 0.0,
            'response_time': 0.0,
            'error_rate': 0.0
        }
        
        logger.info(f"플러그인 등록: {plugin_name} ({plugin_id})")
        
    def update_plugin_metrics(self, plugin_id: str, metrics: Dict[str, Any]):
        """플러그인 메트릭 업데이트"""
        try:
            # 플러그인 모니터에 메트릭 전달
            self.plugin_monitor.update_metrics(plugin_id, metrics)
            
            # 알림 시스템에 메트릭 전달
            self.alert_system.update_plugin_metrics(plugin_id, metrics)
            
            # 성능 데이터 캐시 업데이트
            performance_data = PluginPerformanceData(
                plugin_id=plugin_id,
                plugin_name=metrics.get('plugin_name', plugin_id),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                response_time=metrics.get('response_time', 0.0),
                error_rate=metrics.get('error_rate', 0.0),
                request_count=metrics.get('request_count', 0),
                uptime=metrics.get('uptime', 0.0),
                last_activity=datetime.fromisoformat(metrics.get('last_activity', datetime.utcnow().isoformat())),
                status=metrics.get('status', 'active'),
                timestamp=datetime.utcnow()
            )
            
            self.plugin_performance_cache[plugin_id] = performance_data
            
            # 성능 트렌드 데이터 추가
            self.performance_trends[plugin_id].append(performance_data)
            
            # 성능 기준선 업데이트
            self._update_performance_baseline(plugin_id, performance_data)
            
            # 트렌드 분석 및 예측 알림
            if self.integration_config['trend_analysis_enabled']:
                self._analyze_performance_trends(plugin_id)
                
        except Exception as e:
            logger.error(f"플러그인 메트릭 업데이트 실패: {e}")
            
    def _update_performance_baseline(self, plugin_id: str, performance_data: PluginPerformanceData):
        """성능 기준선 업데이트"""
        if not self.integration_config['performance_baseline_enabled']:
            return
            
        baseline = self.performance_baselines[plugin_id]
        
        # 이동 평균으로 기준선 계산 (최근 20개 데이터 포인트)
        recent_data = list(self.performance_trends[plugin_id])[-20:]
        
        if len(recent_data) >= 5:  # 최소 5개 데이터 포인트 필요
            baseline['cpu_usage'] = sum(d.cpu_usage for d in recent_data) / len(recent_data)
            baseline['memory_usage'] = sum(d.memory_usage for d in recent_data) / len(recent_data)
            baseline['response_time'] = sum(d.response_time for d in recent_data) / len(recent_data)
            baseline['error_rate'] = sum(d.error_rate for d in recent_data) / len(recent_data)
            
    def _analyze_performance_trends(self, plugin_id: str):
        """성능 트렌드 분석 및 예측 알림"""
        try:
            trend_data = list(self.performance_trends[plugin_id])
            
            if len(trend_data) < 10:  # 최소 10개 데이터 포인트 필요
                return
                
            # 최근 10개 데이터 포인트 분석
            recent_data = trend_data[-10:]
            
            # CPU 사용률 트렌드 분석
            cpu_trend = self._calculate_trend([d.cpu_usage for d in recent_data])
            if cpu_trend > 0.5:  # CPU 사용률이 지속적으로 증가하는 경우
                self._create_trend_alert(plugin_id, 'cpu_usage', 'increasing', cpu_trend)
                
            # 메모리 사용률 트렌드 분석
            memory_trend = self._calculate_trend([d.memory_usage for d in recent_data])
            if memory_trend > 0.5:  # 메모리 사용률이 지속적으로 증가하는 경우
                self._create_trend_alert(plugin_id, 'memory_usage', 'increasing', memory_trend)
                
            # 에러율 트렌드 분석
            error_trend = self._calculate_trend([d.error_rate for d in recent_data])
            if error_trend > 0.3:  # 에러율이 지속적으로 증가하는 경우
                self._create_trend_alert(plugin_id, 'error_rate', 'increasing', error_trend)
                
            # 응답시간 트렌드 분석
            response_trend = self._calculate_trend([d.response_time for d in recent_data])
            if response_trend > 0.3:  # 응답시간이 지속적으로 증가하는 경우
                self._create_trend_alert(plugin_id, 'response_time', 'increasing', response_trend)
                
        except Exception as e:
            logger.error(f"성능 트렌드 분석 실패: {e}")
            
    def _calculate_trend(self, values: List[float]) -> float:
        """트렌드 계산 (선형 회귀 기울기)"""
        if len(values) < 2:
            return 0.0
            
        n = len(values)
        x_sum = sum(range(n))
        y_sum = sum(values)
        xy_sum = sum(i * val for i, val in enumerate(values))
        x_sq_sum = sum(i * i for i in range(n))
        
        # 선형 회귀 기울기 계산
        slope = (n * xy_sum - x_sum * y_sum) / (n * x_sq_sum - x_sum * x_sum)
        
        return slope
        
    def _create_trend_alert(self, plugin_id: str, metric: str, trend: str, slope: float):
        """트렌드 기반 알림 생성"""
        alert_key = f"trend_{plugin_id}_{metric}_{trend}"
        
        # 중복 알림 방지
        if alert_key in self.alert_history:
            last_alert = self.alert_history[alert_key]
            if (datetime.utcnow() - last_alert).total_seconds() < self.integration_config['alert_cooldown']:
                return
                
        plugin_name = self.plugin_performance_cache.get(plugin_id, PluginPerformanceData(
            plugin_id=plugin_id, plugin_name=plugin_id, cpu_usage=0, memory_usage=0,
            response_time=0, error_rate=0, request_count=0, uptime=0,
            last_activity=datetime.utcnow(), status='active', timestamp=datetime.utcnow()
        )).plugin_name
        
        metric_names = {
            'cpu_usage': 'CPU 사용률',
            'memory_usage': '메모리 사용률',
            'error_rate': '에러율',
            'response_time': '응답시간'
        }
        
        alert = self.alert_system._create_alert(
            AlertType.CUSTOM_ALERT,
            AlertSeverity.WARNING,
            f"플러그인 성능 트렌드 경고",
            f"플러그인 {plugin_name}의 {metric_names.get(metric, metric)}이(가) 지속적으로 증가하고 있습니다. (기울기: {slope:.3f})",
            plugin_id=plugin_id,
            metadata={
                'trend_analysis': True,
                'metric': metric,
                'trend': trend,
                'slope': slope
            }
        )
        
        if alert:
            self.alert_system._send_alert(alert)
            self.alert_history[alert_key] = datetime.utcnow()
            
    def _on_plugin_alert(self, alert):
        """플러그인 모니터에서 알림 발생 시 처리"""
        try:
            # 알림 시스템에 전달
            self.alert_system._send_alert(alert)
            
            # 추가 분석 및 처리
            if alert.plugin_id:
                self._handle_plugin_alert(alert)
                
        except Exception as e:
            logger.error(f"플러그인 알림 처리 실패: {e}")
            
    def _on_alert_generated(self, alert):
        """알림 시스템에서 알림 생성 시 처리"""
        try:
            # 알림 통계 업데이트
            self._update_alert_statistics(alert)
            
            # 자동 해결 로직
            if self.integration_config['auto_resolution_enabled']:
                self._check_auto_resolution(alert)
                
        except Exception as e:
            logger.error(f"알림 생성 후처리 실패: {e}")
            
    def _handle_plugin_alert(self, alert):
        """플러그인 알림 특별 처리"""
        try:
            if alert.plugin_id and alert.plugin_id in self.plugin_performance_cache:
                performance_data = self.plugin_performance_cache[alert.plugin_id]
                
                # 성능 기준선과 비교
                baseline = self.performance_baselines.get(alert.plugin_id, {})
                
                if baseline:
                    # 기준선 대비 성능 분석
                    self._analyze_baseline_deviation(alert.plugin_id, performance_data, baseline)
                    
        except Exception as e:
            logger.error(f"플러그인 알림 특별 처리 실패: {e}")
            
    def _analyze_baseline_deviation(self, plugin_id: str, current: PluginPerformanceData, baseline: Dict[str, float]):
        """기준선 대비 성능 편차 분석"""
        try:
            deviations = {}
            
            # CPU 사용률 편차
            if baseline.get('cpu_usage', 0) > 0:
                cpu_deviation = (current.cpu_usage - baseline['cpu_usage']) / baseline['cpu_usage']
                if abs(cpu_deviation) > 0.5:  # 50% 이상 편차
                    deviations['cpu_usage'] = cpu_deviation
                    
            # 메모리 사용률 편차
            if baseline.get('memory_usage', 0) > 0:
                memory_deviation = (current.memory_usage - baseline['memory_usage']) / baseline['memory_usage']
                if abs(memory_deviation) > 0.5:  # 50% 이상 편차
                    deviations['memory_usage'] = memory_deviation
                    
            # 에러율 편차
            if baseline.get('error_rate', 0) > 0:
                error_deviation = (current.error_rate - baseline['error_rate']) / baseline['error_rate']
                if abs(error_deviation) > 1.0:  # 100% 이상 편차
                    deviations['error_rate'] = error_deviation
                    
            # 편차가 큰 경우 추가 알림 생성
            if deviations:
                self._create_baseline_deviation_alert(plugin_id, deviations)
                
        except Exception as e:
            logger.error(f"기준선 편차 분석 실패: {e}")
            
    def _create_baseline_deviation_alert(self, plugin_id: str, deviations: Dict[str, float]):
        """기준선 편차 알림 생성"""
        try:
            plugin_name = self.plugin_performance_cache.get(plugin_id, PluginPerformanceData(
                plugin_id=plugin_id, plugin_name=plugin_id, cpu_usage=0, memory_usage=0,
                response_time=0, error_rate=0, request_count=0, uptime=0,
                last_activity=datetime.utcnow(), status='active', timestamp=datetime.utcnow()
            )).plugin_name
            
            deviation_messages = []
            for metric, deviation in deviations.items():
                metric_names = {
                    'cpu_usage': 'CPU 사용률',
                    'memory_usage': '메모리 사용률',
                    'error_rate': '에러율',
                    'response_time': '응답시간'
                }
                direction = "증가" if deviation > 0 else "감소"
                percentage = abs(deviation) * 100
                deviation_messages.append(f"{metric_names.get(metric, metric)} {direction}: {percentage:.1f}%")
                
            alert = self.alert_system._create_alert(
                AlertType.CUSTOM_ALERT,
                AlertSeverity.WARNING,
                f"플러그인 성능 기준선 편차",
                f"플러그인 {plugin_name}의 성능이 기준선에서 크게 벗어났습니다: {', '.join(deviation_messages)}",
                plugin_id=plugin_id,
                metadata={
                    'baseline_deviation': True,
                    'deviations': deviations
                }
            )
            
            if alert:
                self.alert_system._send_alert(alert)
                
        except Exception as e:
            logger.error(f"기준선 편차 알림 생성 실패: {e}")
            
    def _update_alert_statistics(self, alert):
        """알림 통계 업데이트"""
        # 실제 구현에서는 데이터베이스에 통계 저장
        pass
        
    def _check_auto_resolution(self, alert):
        """자동 해결 로직 확인"""
        try:
            if alert.plugin_id and alert.type in [AlertType.PLUGIN_CPU_HIGH, AlertType.PLUGIN_MEMORY_HIGH]:
                # 일정 시간 후 자동으로 해결 상태로 변경
                threading.Timer(300, self._auto_resolve_alert, args=[alert.id]).start()
                
        except Exception as e:
            logger.error(f"자동 해결 확인 실패: {e}")
            
    def _auto_resolve_alert(self, alert_id: str):
        """알림 자동 해결"""
        try:
            self.alert_system.resolve_alert(alert_id)
            logger.info(f"알림 자동 해결: {alert_id}")
            
        except Exception as e:
            logger.error(f"알림 자동 해결 실패: {e}")
            
    def _integration_loop(self):
        """통합 모니터링 루프"""
        while self.integration_active:
            try:
                # 플러그인 상태 체크
                self._check_plugin_health()
                
                # 오래된 데이터 정리
                self._cleanup_old_data()
                
                # 통합 상태 로깅
                self._log_integration_status()
                
                time.sleep(self.integration_config['monitoring_interval'])
                
            except Exception as e:
                logger.error(f"통합 모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
                
    def _check_plugin_health(self):
        """플러그인 상태 체크"""
        try:
            current_time = datetime.utcnow()
            
            for plugin_id, performance_data in self.plugin_performance_cache.items():
                # 비활성 플러그인 체크
                if (current_time - performance_data.last_activity).total_seconds() > 300:  # 5분
                    if performance_data.status == 'active':
                        # 비활성 상태로 변경
                        self._update_plugin_status(plugin_id, 'inactive')
                        
        except Exception as e:
            logger.error(f"플러그인 상태 체크 실패: {e}")
            
    def _update_plugin_status(self, plugin_id: str, status: str):
        """플러그인 상태 업데이트"""
        try:
            if plugin_id in self.plugin_performance_cache:
                self.plugin_performance_cache[plugin_id].status = status
                
            if plugin_id in self.alert_system.plugin_metrics:
                self.alert_system.plugin_metrics[plugin_id]['status'] = status
                
        except Exception as e:
            logger.error(f"플러그인 상태 업데이트 실패: {e}")
            
    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        try:
            current_time = datetime.utcnow()
            cutoff_time = current_time - timedelta(days=7)  # 7일 전
            
            # 오래된 알림 이력 정리
            alert_history_to_remove = []
            for alert_key, timestamp in self.alert_history.items():
                if (current_time - timestamp).total_seconds() > self.integration_config['alert_cooldown'] * 10:
                    alert_history_to_remove.append(alert_key)
                    
            for alert_key in alert_history_to_remove:
                del self.alert_history[alert_key]
                
        except Exception as e:
            logger.error(f"오래된 데이터 정리 실패: {e}")
            
    def _log_integration_status(self):
        """통합 상태 로깅"""
        try:
            active_plugins = len([p for p in self.plugin_performance_cache.values() if p.status == 'active'])
            total_alerts = len(self.alert_system.alerts)
            active_alerts = len([a for a in self.alert_system.alerts.values() if not a.resolved])
            
            logger.info(f"통합 시스템 상태 - 활성 플러그인: {active_plugins}, 총 알림: {total_alerts}, 활성 알림: {active_alerts}")
            
        except Exception as e:
            logger.error(f"통합 상태 로깅 실패: {e}")
            
    def get_integration_status(self) -> Dict[str, Any]:
        """통합 시스템 상태 조회"""
        try:
            return {
                'integration_active': self.integration_active,
                'active_plugins': len([p for p in self.plugin_performance_cache.values() if p.status == 'active']),
                'total_plugins': len(self.plugin_performance_cache),
                'total_alerts': len(self.alert_system.alerts),
                'active_alerts': len([a for a in self.alert_system.alerts.values() if not a.resolved]),
                'performance_baselines': len(self.performance_baselines),
                'trend_data_points': sum(len(trend) for trend in self.performance_trends.values()),
                'last_update': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"통합 상태 조회 실패: {e}")
            return {}

# 전역 인스턴스
plugin_monitoring_integration = PluginMonitoringIntegration() 