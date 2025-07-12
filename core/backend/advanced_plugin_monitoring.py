"""
플러그인별 상세 모니터링 고도화 시스템
실시간 그래프/차트, 상세 로그/이벤트 추적, 드릴다운 보기
"""

import logging
import time
import threading
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import psutil
import asyncio
from pathlib import Path

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """메트릭 타입"""
    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    REQUEST_COUNT = "request_count"
    THROUGHPUT = "throughput"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"
    CUSTOM = "custom"

class LogLevel(Enum):
    """로그 레벨"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class DetailedMetric:
    """상세 메트릭 데이터"""
    plugin_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.fromisoformat(self.timestamp) if isinstance(self.timestamp, str) else datetime.now()

@dataclass
class PluginLog:
    """플러그인 로그"""
    plugin_id: str
    level: LogLevel
    message: str
    timestamp: datetime
    context: Dict[str, Any] = None
    traceback: str = None
    
    def __post_init__(self):
        if self.context is None:
            self.context = {}
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.fromisoformat(self.timestamp) if isinstance(self.timestamp, str) else datetime.now()

@dataclass
class PluginEvent:
    """플러그인 이벤트"""
    plugin_id: str
    event_type: str
    description: str
    timestamp: datetime
    severity: str
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.fromisoformat(self.timestamp) if isinstance(self.timestamp, str) else datetime.now()

@dataclass
class PerformanceSnapshot:
    """성능 스냅샷"""
    plugin_id: str
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    response_time: float
    error_rate: float
    request_count: int
    throughput: float
    disk_io: Dict[str, float]
    network_io: Dict[str, float]
    custom_metrics: Dict[str, float] = None
    
    def __post_init__(self):
        if self.custom_metrics is None:
            self.custom_metrics = {}
        if not isinstance(self.timestamp, datetime):
            self.timestamp = datetime.fromisoformat(self.timestamp) if isinstance(self.timestamp, str) else datetime.now()

class AdvancedPluginMonitor:
    """고도화된 플러그인 모니터링 시스템"""
    
    def __init__(self, db_path: str = "advanced_monitoring.db"):
        self.db_path = db_path
        self.monitoring_active = False
        self.monitor_thread = None
        
        # 메트릭 저장소 (메모리 캐시)
        self.metrics_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.logs_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=5000))
        self.events_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=2000))
        self.snapshots_cache: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        
        # 실시간 통계
        self.real_time_stats: Dict[str, Dict[str, Any]] = {}
        
        # 알림 콜백
        self.alert_callbacks: List[Any] = []
        
        # 데이터베이스 초기화
        self._init_database()
        
        # 모니터링 설정
        self.monitoring_config = {
            'metrics_interval': 5,  # 5초
            'snapshot_interval': 30,  # 30초
            'retention_days': 30,  # 30일
            'max_metrics_per_plugin': 10000,
            'max_logs_per_plugin': 5000,
            'max_events_per_plugin': 2000
        }
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 메트릭 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    value REAL NOT NULL,
                    timestamp DATETIME NOT NULL,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 로그 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    context TEXT,
                    traceback TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 이벤트 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS plugin_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    severity TEXT NOT NULL,
                    data TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 성능 스냅샷 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_snapshots (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plugin_id TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    cpu_usage REAL NOT NULL,
                    memory_usage REAL NOT NULL,
                    response_time REAL NOT NULL,
                    error_rate REAL NOT NULL,
                    request_count INTEGER NOT NULL,
                    throughput REAL NOT NULL,
                    disk_io TEXT NOT NULL,
                    network_io TEXT NOT NULL,
                    custom_metrics TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_plugin_time ON plugin_metrics(plugin_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_logs_plugin_time ON plugin_logs(plugin_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_events_plugin_time ON plugin_events(plugin_id, timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_snapshots_plugin_time ON performance_snapshots(plugin_id, timestamp)')
            
            conn.commit()
            conn.close()
            logger.info("고도화된 모니터링 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            return
            
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("고도화된 플러그인 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("고도화된 플러그인 모니터링 중지")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 데이터 정리
                self._cleanup_old_data()
                
                # 실시간 통계 업데이트
                self._update_real_time_stats()
                
                # 데이터베이스 동기화
                self._sync_to_database()
                
                time.sleep(self.monitoring_config['metrics_interval'])
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)
    
    def record_metric(self, plugin_id: str, metric_type: MetricType, value: float, metadata: Dict[str, Any] = None):
        """메트릭 기록"""
        try:
            metric = DetailedMetric(
                plugin_id=plugin_id,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.utcnow(),
                metadata=metadata or {}
            )
            
            # 메모리 캐시에 저장
            cache_key = f"{plugin_id}_{metric_type.value}"
            self.metrics_cache[cache_key].append(metric)
            
            # 실시간 통계 업데이트
            self._update_plugin_stats(plugin_id, metric_type, value)
            
        except Exception as e:
            logger.error(f"메트릭 기록 오류: {e}")
    
    def record_log(self, plugin_id: str, level: LogLevel, message: str, context: Dict[str, Any] = None, traceback: str = None):
        """로그 기록"""
        try:
            log = PluginLog(
                plugin_id=plugin_id,
                level=level,
                message=message,
                timestamp=datetime.utcnow(),
                context=context or {},
                traceback=traceback
            )
            
            # 메모리 캐시에 저장
            self.logs_cache[plugin_id].append(log)
            
            # 중요 로그는 이벤트로도 기록
            if level in [LogLevel.ERROR, LogLevel.CRITICAL]:
                self.record_event(
                    plugin_id=plugin_id,
                    event_type="log_error",
                    description=f"로그 오류: {message}",
                    severity=level.value,
                    data={"context": context, "traceback": traceback}
                )
            
        except Exception as e:
            logger.error(f"로그 기록 오류: {e}")
    
    def record_event(self, plugin_id: str, event_type: str, description: str, severity: str, data: Dict[str, Any] = None):
        """이벤트 기록"""
        try:
            event = PluginEvent(
                plugin_id=plugin_id,
                event_type=event_type,
                description=description,
                timestamp=datetime.utcnow(),
                severity=severity,
                data=data or {}
            )
            
            # 메모리 캐시에 저장
            self.events_cache[plugin_id].append(event)
            
            # 알림 콜백 실행
            self._trigger_alert_callbacks(event)
            
        except Exception as e:
            logger.error(f"이벤트 기록 오류: {e}")
    
    def create_snapshot(self, plugin_id: str, metrics: Dict[str, Any]):
        """성능 스냅샷 생성"""
        try:
            snapshot = PerformanceSnapshot(
                plugin_id=plugin_id,
                timestamp=datetime.utcnow(),
                cpu_usage=metrics.get('cpu_usage', 0.0),
                memory_usage=metrics.get('memory_usage', 0.0),
                response_time=metrics.get('response_time', 0.0),
                error_rate=metrics.get('error_rate', 0.0),
                request_count=metrics.get('request_count', 0),
                throughput=metrics.get('throughput', 0.0),
                disk_io=metrics.get('disk_io', {}),
                network_io=metrics.get('network_io', {}),
                custom_metrics=metrics.get('custom_metrics', {})
            )
            
            # 메모리 캐시에 저장
            self.snapshots_cache[plugin_id].append(snapshot)
            
        except Exception as e:
            logger.error(f"스냅샷 생성 오류: {e}")
    
    def _update_plugin_stats(self, plugin_id: str, metric_type: MetricType, value: float):
        """플러그인 통계 업데이트"""
        if plugin_id not in self.real_time_stats:
            self.real_time_stats[plugin_id] = {
                'metrics': {},
                'last_update': datetime.utcnow(),
                'total_requests': 0,
                'total_errors': 0,
                'avg_response_time': 0.0
            }
        
        stats = self.real_time_stats[plugin_id]
        metric_key = metric_type.value
        
        if metric_key not in stats['metrics']:
            stats['metrics'][metric_key] = {
                'current': value,
                'min': value,
                'max': value,
                'avg': value,
                'count': 1
            }
        else:
            metric_stats = stats['metrics'][metric_key]
            metric_stats['current'] = value
            metric_stats['min'] = min(metric_stats['min'], value)
            metric_stats['max'] = max(metric_stats['max'], value)
            metric_stats['count'] += 1
            metric_stats['avg'] = (metric_stats['avg'] * (metric_stats['count'] - 1) + value) / metric_stats['count']
        
        stats['last_update'] = datetime.utcnow()
    
    def _update_real_time_stats(self):
        """실시간 통계 업데이트"""
        current_time = datetime.utcnow()
        
        for plugin_id, stats in self.real_time_stats.items():
            # 5분 이상 업데이트가 없으면 비활성으로 표시
            if (current_time - stats['last_update']).total_seconds() > 300:
                stats['status'] = 'inactive'
            else:
                stats['status'] = 'active'
    
    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        cutoff_time = datetime.utcnow() - timedelta(days=self.monitoring_config['retention_days'])
        
        # 메트릭 정리
        for cache_key, metrics in self.metrics_cache.items():
            while metrics and metrics[0].timestamp < cutoff_time:
                metrics.popleft()
        
        # 로그 정리
        for plugin_id, logs in self.logs_cache.items():
            while logs and logs[0].timestamp < cutoff_time:
                logs.popleft()
        
        # 이벤트 정리
        for plugin_id, events in self.events_cache.items():
            while events and events[0].timestamp < cutoff_time:
                events.popleft()
        
        # 스냅샷 정리
        for plugin_id, snapshots in self.snapshots_cache.items():
            while snapshots and snapshots[0].timestamp < cutoff_time:
                snapshots.popleft()
    
    def _sync_to_database(self):
        """데이터베이스 동기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 메트릭 동기화
            for cache_key, metrics in self.metrics_cache.items():
                if metrics:
                    plugin_id, metric_type = cache_key.split('_', 1)
                    metric = metrics[-1]  # 최신 메트릭
                    
                    cursor.execute('''
                        INSERT INTO plugin_metrics (plugin_id, metric_type, value, timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        plugin_id,
                        metric_type,
                        metric.value,
                        metric.timestamp.isoformat(),
                        json.dumps(metric.metadata)
                    ))
            
            # 로그 동기화 (최근 100개만)
            for plugin_id, logs in self.logs_cache.items():
                recent_logs = list(logs)[-100:]
                for log in recent_logs:
                    cursor.execute('''
                        INSERT INTO plugin_logs (plugin_id, level, message, timestamp, context, traceback)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        log.plugin_id,
                        log.level.value,
                        log.message,
                        log.timestamp.isoformat(),
                        json.dumps(log.context),
                        log.traceback
                    ))
            
            # 이벤트 동기화 (최근 50개만)
            for plugin_id, events in self.events_cache.items():
                recent_events = list(events)[-50:]
                for event in recent_events:
                    cursor.execute('''
                        INSERT INTO plugin_events (plugin_id, event_type, description, timestamp, severity, data)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        event.plugin_id,
                        event.event_type,
                        event.description,
                        event.timestamp.isoformat(),
                        event.severity,
                        json.dumps(event.data)
                    ))
            
            # 스냅샷 동기화 (최근 10개만)
            for plugin_id, snapshots in self.snapshots_cache.items():
                recent_snapshots = list(snapshots)[-10:]
                for snapshot in recent_snapshots:
                    cursor.execute('''
                        INSERT INTO performance_snapshots 
                        (plugin_id, timestamp, cpu_usage, memory_usage, response_time, error_rate, 
                         request_count, throughput, disk_io, network_io, custom_metrics)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        snapshot.plugin_id,
                        snapshot.timestamp.isoformat(),
                        snapshot.cpu_usage,
                        snapshot.memory_usage,
                        snapshot.response_time,
                        snapshot.error_rate,
                        snapshot.request_count,
                        snapshot.throughput,
                        json.dumps(snapshot.disk_io),
                        json.dumps(snapshot.network_io),
                        json.dumps(snapshot.custom_metrics)
                    ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"데이터베이스 동기화 오류: {e}")
    
    def _trigger_alert_callbacks(self, event: PluginEvent):
        """알림 콜백 실행"""
        for callback in self.alert_callbacks:
            try:
                callback(event)
            except Exception as e:
                logger.error(f"알림 콜백 실행 오류: {e}")
    
    def add_alert_callback(self, callback):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)
    
    # 데이터 조회 메서드들
    def get_plugin_metrics(self, plugin_id: str, metric_type: MetricType = None, 
                          hours: int = 24) -> List[DetailedMetric]:
        """플러그인 메트릭 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        metrics = []
        
        if metric_type:
            cache_key = f"{plugin_id}_{metric_type.value}"
            if cache_key in self.metrics_cache:
                metrics = [m for m in self.metrics_cache[cache_key] if m.timestamp >= cutoff_time]
        else:
            # 모든 메트릭 타입
            for cache_key, metric_list in self.metrics_cache.items():
                if cache_key.startswith(f"{plugin_id}_"):
                    metrics.extend([m for m in metric_list if m.timestamp >= cutoff_time])
        
        return sorted(metrics, key=lambda x: x.timestamp)
    
    def get_plugin_logs(self, plugin_id: str, level: LogLevel = None, 
                       hours: int = 24) -> List[PluginLog]:
        """플러그인 로그 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if plugin_id in self.logs_cache:
            logs = [log for log in self.logs_cache[plugin_id] if log.timestamp >= cutoff_time]
            if level:
                logs = [log for log in logs if log.level == level]
            return sorted(logs, key=lambda x: x.timestamp)
        
        return []
    
    def get_plugin_events(self, plugin_id: str, event_type: str = None, 
                         hours: int = 24) -> List[PluginEvent]:
        """플러그인 이벤트 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if plugin_id in self.events_cache:
            events = [event for event in self.events_cache[plugin_id] if event.timestamp >= cutoff_time]
            if event_type:
                events = [event for event in events if event.event_type == event_type]
            return sorted(events, key=lambda x: x.timestamp)
        
        return []
    
    def get_performance_snapshots(self, plugin_id: str, hours: int = 24) -> List[PerformanceSnapshot]:
        """성능 스냅샷 조회"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        if plugin_id in self.snapshots_cache:
            snapshots = [s for s in self.snapshots_cache[plugin_id] if s.timestamp >= cutoff_time]
            return sorted(snapshots, key=lambda x: x.timestamp)
        
        return []
    
    def get_real_time_stats(self, plugin_id: str = None) -> Dict[str, Any]:
        """실시간 통계 조회"""
        if plugin_id:
            return self.real_time_stats.get(plugin_id, {})
        return self.real_time_stats
    
    def get_plugin_summary(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인 요약 정보"""
        stats = self.real_time_stats.get(plugin_id, {})
        metrics = self.get_plugin_metrics(plugin_id, hours=1)
        logs = self.get_plugin_logs(plugin_id, hours=1)
        events = self.get_plugin_events(plugin_id, hours=1)
        
        # 에러 로그 수 계산
        error_logs = [log for log in logs if log.level in [LogLevel.ERROR, LogLevel.CRITICAL]]
        
        return {
            'plugin_id': plugin_id,
            'status': stats.get('status', 'unknown'),
            'last_update': stats.get('last_update'),
            'metrics_count': len(metrics),
            'logs_count': len(logs),
            'error_logs_count': len(error_logs),
            'events_count': len(events),
            'current_metrics': stats.get('metrics', {}),
            'recent_errors': [log.message for log in error_logs[-5:]]  # 최근 5개 에러
        }
    
    def get_all_plugins_summary(self) -> List[Dict[str, Any]]:
        """모든 플러그인 요약 정보"""
        summaries = []
        for plugin_id in self.real_time_stats.keys():
            summaries.append(self.get_plugin_summary(plugin_id))
        return summaries

# 전역 인스턴스
advanced_plugin_monitor = AdvancedPluginMonitor() 