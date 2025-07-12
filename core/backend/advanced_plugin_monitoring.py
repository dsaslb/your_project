"""
플러그인별 상세 모니터링 고도화
실시간 그래프, 상세 로그, 트렌드, 사용량 등 심화 대시보드 기능
"""

import logging
import time
import json
import sqlite3
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import threading
from collections import defaultdict, deque
import statistics

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 타입"""
    CPU = "cpu"
    MEMORY = "memory"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CONNECTIONS = "connections"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"

@dataclass
class DetailedMetrics:
    """상세 메트릭"""
    plugin_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    memory_rss: float
    memory_vms: float
    response_time_p50: float
    response_time_p95: float
    response_time_p99: float
    error_rate: float
    throughput: float
    active_connections: int
    total_connections: int
    disk_read_bytes: int
    disk_write_bytes: int
    network_rx_bytes: int
    network_tx_bytes: int
    custom_metrics: Dict[str, Any]

@dataclass
class PerformanceTrend:
    """성능 트렌드"""
    plugin_id: str
    metric_type: MetricType
    current_value: float
    previous_value: float
    change_percent: float
    trend_direction: str  # 'up', 'down', 'stable'
    trend_strength: str   # 'strong', 'moderate', 'weak'

@dataclass
class UsagePattern:
    """사용량 패턴"""
    plugin_id: str
    peak_hours: List[int]
    low_usage_hours: List[int]
    daily_usage_pattern: Dict[str, float]
    weekly_usage_pattern: Dict[str, float]
    monthly_usage_pattern: Dict[str, float]

class AdvancedPluginMonitor:
    """고급 플러그인 모니터링"""
    
    def __init__(self, db_path: str = "plugin_monitoring.db"):
        self.db_path = db_path
        self.metrics_buffer: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.trends: Dict[str, Dict[MetricType, PerformanceTrend]] = defaultdict(dict)
        self.usage_patterns: Dict[str, UsagePattern] = {}
        self.anomaly_detectors: Dict[str, AnomalyDetector] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable[[Any], None]] = []
        
        # 데이터베이스 초기화
        self._init_database()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 상세 메트릭 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS detailed_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        timestamp DATETIME NOT NULL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        memory_rss REAL,
                        memory_vms REAL,
                        response_time_p50 REAL,
                        response_time_p95 REAL,
                        response_time_p99 REAL,
                        error_rate REAL,
                        throughput REAL,
                        active_connections INTEGER,
                        total_connections INTEGER,
                        disk_read_bytes INTEGER,
                        disk_write_bytes INTEGER,
                        network_rx_bytes INTEGER,
                        network_tx_bytes INTEGER,
                        custom_metrics TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 성능 트렌드 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_trends (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        metric_type TEXT NOT NULL,
                        current_value REAL,
                        previous_value REAL,
                        change_percent REAL,
                        trend_direction TEXT,
                        trend_strength TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 사용량 패턴 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usage_patterns (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        pattern_type TEXT NOT NULL,
                        pattern_data TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_plugin_time ON detailed_metrics(plugin_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_plugin_type ON performance_trends(plugin_id, metric_type)')
                
                conn.commit()
                logger.info("플러그인 모니터링 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("고급 플러그인 모니터링 시작")
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("고급 플러그인 모니터링 중지")
        
    def register_plugin(self, plugin_id: str, plugin_name: str):
        """플러그인 등록"""
        # 기본 모니터에 등록
        from .plugin_monitoring import plugin_monitor
        plugin_monitor.register_plugin(plugin_id, plugin_name)
        
        # 이상 탐지기 초기화
        self.anomaly_detectors[plugin_id] = AnomalyDetector(plugin_id)
        
        logger.info(f"고급 모니터링에 플러그인 등록: {plugin_name} ({plugin_id})")
        
    def update_detailed_metrics(self, plugin_id: str, metrics: Dict[str, Any]):
        """상세 메트릭 업데이트"""
        try:
            # 상세 메트릭 객체 생성
            detailed_metric = DetailedMetrics(
                plugin_id=plugin_id,
                timestamp=datetime.utcnow(),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                memory_rss=metrics.get('memory_rss', 0.0),
                memory_vms=metrics.get('memory_vms', 0.0),
                response_time_p50=metrics.get('response_time_p50', 0.0),
                response_time_p95=metrics.get('response_time_p95', 0.0),
                response_time_p99=metrics.get('response_time_p99', 0.0),
                error_rate=metrics.get('error_rate', 0.0),
                throughput=metrics.get('throughput', 0.0),
                active_connections=metrics.get('active_connections', 0),
                total_connections=metrics.get('total_connections', 0),
                disk_read_bytes=metrics.get('disk_read_bytes', 0),
                disk_write_bytes=metrics.get('disk_write_bytes', 0),
                network_rx_bytes=metrics.get('network_rx_bytes', 0),
                network_tx_bytes=metrics.get('network_tx_bytes', 0),
                custom_metrics=metrics.get('custom_metrics', {})
            )
            
            # 메모리 버퍼에 저장
            self.metrics_buffer[plugin_id].append(detailed_metric)
            
            # 데이터베이스에 저장
            self._save_metrics_to_db(detailed_metric)
            
            # 트렌드 분석
            self._analyze_trends(plugin_id, detailed_metric)
            
            # 이상 탐지
            self._detect_anomalies(plugin_id, detailed_metric)
            
            # 사용량 패턴 분석
            self._analyze_usage_patterns(plugin_id, detailed_metric)
            
        except Exception as e:
            logger.error(f"상세 메트릭 업데이트 오류: {e}")
            
    def _save_metrics_to_db(self, metric: DetailedMetrics):
        """메트릭을 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO detailed_metrics (
                        plugin_id, timestamp, cpu_usage, memory_usage, memory_rss, memory_vms,
                        response_time_p50, response_time_p95, response_time_p99, error_rate,
                        throughput, active_connections, total_connections, disk_read_bytes,
                        disk_write_bytes, network_rx_bytes, network_tx_bytes, custom_metrics
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric.plugin_id, metric.timestamp.isoformat(), metric.cpu_usage,
                    metric.memory_usage, metric.memory_rss, metric.memory_vms,
                    metric.response_time_p50, metric.response_time_p95, metric.response_time_p99,
                    metric.error_rate, metric.throughput, metric.active_connections,
                    metric.total_connections, metric.disk_read_bytes, metric.disk_write_bytes,
                    metric.network_rx_bytes, metric.network_tx_bytes,
                    json.dumps(metric.custom_metrics)
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"메트릭 저장 오류: {e}")
            
    def _analyze_trends(self, plugin_id: str, metric: DetailedMetrics):
        """트렌드 분석"""
        try:
            # 이전 메트릭 가져오기
            previous_metrics = self._get_previous_metrics(plugin_id, 1)
            if not previous_metrics:
                return
                
            previous = previous_metrics[0]
            
            # 각 메트릭 타입별 트렌드 분석
            metric_types = [
                (MetricType.CPU, metric.cpu_usage, previous.cpu_usage),
                (MetricType.MEMORY, metric.memory_usage, previous.memory_usage),
                (MetricType.RESPONSE_TIME, metric.response_time_p95, previous.response_time_p95),
                (MetricType.ERROR_RATE, metric.error_rate, previous.error_rate),
                (MetricType.THROUGHPUT, metric.throughput, previous.throughput)
            ]
            
            for metric_type, current, prev in metric_types:
                if prev == 0:
                    continue
                    
                change_percent = ((current - prev) / prev) * 100
                trend_direction = 'up' if change_percent > 0 else 'down' if change_percent < 0 else 'stable'
                trend_strength = 'strong' if abs(change_percent) > 20 else 'moderate' if abs(change_percent) > 10 else 'weak'
                
                trend = PerformanceTrend(
                    plugin_id=plugin_id,
                    metric_type=metric_type,
                    current_value=current,
                    previous_value=prev,
                    change_percent=change_percent,
                    trend_direction=trend_direction,
                    trend_strength=trend_strength
                )
                
                self.trends[plugin_id][metric_type] = trend
                self._save_trend_to_db(trend)
                
        except Exception as e:
            logger.error(f"트렌드 분석 오류: {e}")
            
    def _detect_anomalies(self, plugin_id: str, metric: DetailedMetrics):
        """이상 탐지"""
        if plugin_id in self.anomaly_detectors:
            anomalies = self.anomaly_detectors[plugin_id].detect(metric)
            for anomaly in anomalies:
                self._trigger_alert_callbacks(anomaly)
                
    def _analyze_usage_patterns(self, plugin_id: str, metric: DetailedMetrics):
        """사용량 패턴 분석"""
        try:
            now = metric.timestamp
            day_of_week = now.strftime('%A')
            if plugin_id not in self.usage_patterns:
                self.usage_patterns[plugin_id] = UsagePattern(
                    plugin_id=plugin_id,
                    peak_hours=[],
                    low_usage_hours=[],
                    daily_usage_pattern={},
                    weekly_usage_pattern={},
                    monthly_usage_pattern={}
                )
            pattern = self.usage_patterns[plugin_id]
            # 일일 패턴 업데이트
            if day_of_week not in pattern.daily_usage_pattern:
                pattern.daily_usage_pattern[day_of_week] = 0.0  # float로 초기화
            # 최근 24시간 데이터로 피크 시간 분석
            recent_metrics = self._get_previous_metrics(plugin_id, 24)
            if len(recent_metrics) >= 24:
                hourly_usage = defaultdict(list)
                for m in recent_metrics:
                    hourly_usage[m.timestamp.hour].append(m.cpu_usage)
                avg_hourly_usage = {hour: statistics.mean(usage) for hour, usage in hourly_usage.items()}
                sorted_hours = sorted(avg_hourly_usage.items(), key=lambda x: x[1], reverse=True)
                pattern.peak_hours = [hour for hour, _ in sorted_hours[:3]]
                pattern.low_usage_hours = [hour for hour, _ in sorted_hours[-3:]]
        except Exception as e:
            logger.error(f"사용량 패턴 분석 오류: {e}")
            
    def _get_previous_metrics(self, plugin_id: str, count: int) -> List[DetailedMetrics]:
        """이전 메트릭 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM detailed_metrics 
                    WHERE plugin_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                ''', (plugin_id, count))
                
                rows = cursor.fetchall()
                metrics = []
                
                for row in rows:
                    metric = DetailedMetrics(
                        plugin_id=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        cpu_usage=row[3],
                        memory_usage=row[4],
                        memory_rss=row[5],
                        memory_vms=row[6],
                        response_time_p50=row[7],
                        response_time_p95=row[8],
                        response_time_p99=row[9],
                        error_rate=row[10],
                        throughput=row[11],
                        active_connections=row[12],
                        total_connections=row[13],
                        disk_read_bytes=row[14],
                        disk_write_bytes=row[15],
                        network_rx_bytes=row[16],
                        network_tx_bytes=row[17],
                        custom_metrics=json.loads(row[18]) if row[18] else {}
                    )
                    metrics.append(metric)
                    
                return metrics
                
        except Exception as e:
            logger.error(f"이전 메트릭 조회 오류: {e}")
            return []
            
    def _save_trend_to_db(self, trend: PerformanceTrend):
        """트렌드를 데이터베이스에 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_trends (
                        plugin_id, metric_type, current_value, previous_value,
                        change_percent, trend_direction, trend_strength
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trend.plugin_id, trend.metric_type.value, trend.current_value,
                    trend.previous_value, trend.change_percent, trend.trend_direction,
                    trend.trend_strength
                ))
                conn.commit()
                
        except Exception as e:
            logger.error(f"트렌드 저장 오류: {e}")
            
    def _trigger_alert_callbacks(self, alert):
        """알림 콜백 함수들 호출"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {e}")
                
    def add_alert_callback(self, callback: Callable[[Any], None]):
        """알림 콜백 함수 등록"""
        self.alert_callbacks.append(callback)
        
    def get_detailed_metrics(self, plugin_id: str, hours: int = 24) -> List[DetailedMetrics]:
        """상세 메트릭 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = datetime.utcnow() - timedelta(hours=hours)
                cursor.execute('''
                    SELECT * FROM detailed_metrics 
                    WHERE plugin_id = ? AND timestamp >= ?
                    ORDER BY timestamp ASC
                ''', (plugin_id, cutoff_time.isoformat()))
                
                rows = cursor.fetchall()
                metrics = []
                
                for row in rows:
                    metric = DetailedMetrics(
                        plugin_id=row[1],
                        timestamp=datetime.fromisoformat(row[2]),
                        cpu_usage=row[3],
                        memory_usage=row[4],
                        memory_rss=row[5],
                        memory_vms=row[6],
                        response_time_p50=row[7],
                        response_time_p95=row[8],
                        response_time_p99=row[9],
                        error_rate=row[10],
                        throughput=row[11],
                        active_connections=row[12],
                        total_connections=row[13],
                        disk_read_bytes=row[14],
                        disk_write_bytes=row[15],
                        network_rx_bytes=row[16],
                        network_tx_bytes=row[17],
                        custom_metrics=json.loads(row[18]) if row[18] else {}
                    )
                    metrics.append(metric)
                    
                return metrics
                
        except Exception as e:
            logger.error(f"상세 메트릭 조회 오류: {e}")
            return []
            
    def get_performance_trends(self, plugin_id: str) -> Dict[MetricType, PerformanceTrend]:
        """성능 트렌드 조회"""
        return self.trends.get(plugin_id, {})
        
    def get_usage_patterns(self, plugin_id: str) -> Optional[UsagePattern]:
        """사용량 패턴 조회"""
        return self.usage_patterns.get(plugin_id)
        
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 주기적 분석 작업
                self._periodic_analysis()
                time.sleep(60)  # 1분마다 실행
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)
                
    def _periodic_analysis(self):
        """주기적 분석 작업"""
        try:
            # 장기 트렌드 분석
            for plugin_id in self.metrics_buffer.keys():
                self._analyze_long_term_trends(plugin_id)
                
            # 예측 분석
            for plugin_id in self.metrics_buffer.keys():
                self._predict_future_usage(plugin_id)
                
        except Exception as e:
            logger.error(f"주기적 분석 오류: {e}")
            
    def _analyze_long_term_trends(self, plugin_id: str):
        """장기 트렌드 분석"""
        # 7일, 30일 트렌드 분석
        pass
        
    def _predict_future_usage(self, plugin_id: str):
        """미래 사용량 예측"""
        # 머신러닝 기반 사용량 예측
        pass

class AnomalyDetector:
    """이상 탐지기"""
    
    def __init__(self, plugin_id: str):
        self.plugin_id = plugin_id
        self.baseline_metrics = {}
        self.anomaly_thresholds = {
            'cpu_usage': 0.3,  # 30% 이상 변화
            'memory_usage': 0.25,  # 25% 이상 변화
            'response_time': 0.5,  # 50% 이상 변화
            'error_rate': 0.1  # 10% 이상 변화
        }
        
    def detect(self, metric: DetailedMetrics) -> List[Dict]:
        """이상 탐지"""
        anomalies = []
        
        # 기준값이 없으면 현재 값을 기준값으로 설정
        if not self.baseline_metrics:
            self.baseline_metrics = {
                'cpu_usage': metric.cpu_usage,
                'memory_usage': metric.memory_usage,
                'response_time': metric.response_time_p95,
                'error_rate': metric.error_rate
            }
            return anomalies
            
        # 각 메트릭별 이상 탐지
        current_metrics = {
            'cpu_usage': metric.cpu_usage,
            'memory_usage': metric.memory_usage,
            'response_time': metric.response_time_p95,
            'error_rate': metric.error_rate
        }
        
        for metric_name, current_value in current_metrics.items():
            baseline = self.baseline_metrics.get(metric_name, current_value)
            threshold = self.anomaly_thresholds.get(metric_name, 0.2)
            
            if baseline > 0:
                change_ratio = abs(current_value - baseline) / baseline
                
                if change_ratio > threshold:
                    anomaly = {
                        'plugin_id': self.plugin_id,
                        'metric_name': metric_name,
                        'current_value': current_value,
                        'baseline_value': baseline,
                        'change_ratio': change_ratio,
                        'severity': 'high' if change_ratio > threshold * 2 else 'medium',
                        'timestamp': metric.timestamp.isoformat()
                    }
                    anomalies.append(anomaly)
                    
        # 기준값 업데이트 (점진적 업데이트)
        for metric_name, current_value in current_metrics.items():
            baseline = self.baseline_metrics.get(metric_name, current_value)
            self.baseline_metrics[metric_name] = baseline * 0.9 + current_value * 0.1
            
        return anomalies

# 전역 고급 모니터 인스턴스
advanced_monitor = AdvancedPluginMonitor() 