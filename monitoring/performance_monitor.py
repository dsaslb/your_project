"""
📊 성능 모니터링 시스템

실시간으로 시스템 성능을 모니터링하고 최적화하는 시스템입니다.
"""

import asyncio
import logging
import time
import psutil
import json
import redis
import prometheus_client
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from prometheus_client import Counter, Histogram, Gauge, Summary
import aiohttp
import sqlite3
from pathlib import Path

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터 클래스"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    response_time: float
    throughput: float
    error_rate: float
    active_connections: int
    queue_size: int

@dataclass
class AlertThreshold:
    """알림 임계값 설정"""
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 95.0
    disk_warning: float = 85.0
    disk_critical: float = 95.0
    response_time_warning: float = 2.0
    response_time_critical: float = 5.0
    error_rate_warning: float = 5.0
    error_rate_critical: float = 10.0

class PerformanceMonitor:
    """성능 모니터링 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        # Prometheus 메트릭 초기화
        self.init_prometheus_metrics()
        
        # 알림 임계값 설정
        self.thresholds = AlertThreshold(**config.get('thresholds', {}))
        
        # 성능 데이터 저장소
        self.db_path = Path(config.get('db_path', 'performance_data.db'))
        self.init_database()
        
        # 모니터링 상태
        self.is_monitoring = False
        self.metrics_history: List[PerformanceMetrics] = []
        self.alerts: List[Dict[str, Any]] = []
        
        # 모니터링 간격 (초)
        self.monitoring_interval = config.get('monitoring_interval', 30)
        
    def init_prometheus_metrics(self):
        """Prometheus 메트릭 초기화"""
        # 시스템 메트릭
        self.cpu_gauge = Gauge('system_cpu_percent', 'CPU 사용률 (%)')
        self.memory_gauge = Gauge('system_memory_percent', '메모리 사용률 (%)')
        self.disk_gauge = Gauge('system_disk_percent', '디스크 사용률 (%)')
        
        # 네트워크 메트릭
        self.network_bytes_sent = Counter('network_bytes_sent', '전송된 바이트')
        self.network_bytes_recv = Counter('network_bytes_recv', '수신된 바이트')
        
        # 애플리케이션 메트릭
        self.response_time_histogram = Histogram(
            'http_request_duration_seconds',
            'HTTP 요청 응답 시간',
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
        )
        self.request_counter = Counter('http_requests_total', '총 HTTP 요청 수')
        self.error_counter = Counter('http_errors_total', '총 HTTP 오류 수')
        
        # 비즈니스 메트릭
        self.active_users_gauge = Gauge('active_users', '활성 사용자 수')
        self.queue_size_gauge = Gauge('queue_size', '큐 크기')
        self.throughput_gauge = Gauge('requests_per_second', '초당 요청 수')
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 성능 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage_percent REAL,
                network_io TEXT,
                response_time REAL,
                throughput REAL,
                error_rate REAL,
                active_connections INTEGER,
                queue_size INTEGER
            )
        ''')
        
        # 알림 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL,
                metric_value REAL,
                threshold_value REAL
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)')
        
        conn.commit()
        conn.close()
        
    async def start_monitoring(self):
        """성능 모니터링 시작"""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
            
        self.is_monitoring = True
        logger.info("성능 모니터링을 시작합니다.")
        
        try:
            while self.is_monitoring:
                # 성능 메트릭 수집
                metrics = await self.collect_metrics()
                
                # 메트릭 저장
                await self.save_metrics(metrics)
                
                # Prometheus 메트릭 업데이트
                self.update_prometheus_metrics(metrics)
                
                # 알림 확인
                await self.check_alerts(metrics)
                
                # 메트릭 히스토리 관리
                self.manage_metrics_history(metrics)
                
                # 모니터링 간격만큼 대기
                await asyncio.sleep(self.monitoring_interval)
                
        except Exception as e:
            logger.error(f"모니터링 중 오류 발생: {e}")
            self.is_monitoring = False
            
    async def stop_monitoring(self):
        """성능 모니터링 중지"""
        self.is_monitoring = False
        logger.info("성능 모니터링을 중지합니다.")
        
    async def collect_metrics(self) -> PerformanceMetrics:
        """시스템 성능 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # 네트워크 I/O
            network_io = psutil.net_io_counters()
            network_data = {
                'bytes_sent': network_io.bytes_sent,
                'bytes_recv': network_io.bytes_recv,
                'packets_sent': network_io.packets_sent,
                'packets_recv': network_io.packets_recv
            }
            
            # 애플리케이션 메트릭 (Redis에서 가져오기)
            app_metrics = await self.get_application_metrics()
            
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_io=network_data,
                response_time=app_metrics.get('response_time', 0.0),
                throughput=app_metrics.get('throughput', 0.0),
                error_rate=app_metrics.get('error_rate', 0.0),
                active_connections=app_metrics.get('active_connections', 0),
                queue_size=app_metrics.get('queue_size', 0)
            )
            
        except Exception as e:
            logger.error(f"메트릭 수집 중 오류: {e}")
            return PerformanceMetrics(
                timestamp=datetime.now(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_io={},
                response_time=0.0,
                throughput=0.0,
                error_rate=0.0,
                active_connections=0,
                queue_size=0
            )
            
    async def get_application_metrics(self) -> Dict[str, Any]:
        """애플리케이션 메트릭 수집"""
        try:
            # Redis에서 애플리케이션 메트릭 가져오기
            metrics = {}
            
            # 응답 시간
            response_time = self.redis_client.get('app:response_time')
            if response_time:
                metrics['response_time'] = float(response_time)
                
            # 처리량
            throughput = self.redis_client.get('app:throughput')
            if throughput:
                metrics['throughput'] = float(throughput)
                
            # 오류율
            error_rate = self.redis_client.get('app:error_rate')
            if error_rate:
                metrics['error_rate'] = float(error_rate)
                
            # 활성 연결 수
            active_connections = self.redis_client.get('app:active_connections')
            if active_connections:
                metrics['active_connections'] = int(active_connections)
                
            # 큐 크기
            queue_size = self.redis_client.get('app:queue_size')
            if queue_size:
                metrics['queue_size'] = int(queue_size)
                
            return metrics
            
        except Exception as e:
            logger.error(f"애플리케이션 메트릭 수집 중 오류: {e}")
            return {}
            
    async def save_metrics(self, metrics: PerformanceMetrics):
        """메트릭을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_metrics 
                (timestamp, cpu_percent, memory_percent, disk_usage_percent, 
                 network_io, response_time, throughput, error_rate, 
                 active_connections, queue_size)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.timestamp.isoformat(),
                metrics.cpu_percent,
                metrics.memory_percent,
                metrics.disk_usage_percent,
                json.dumps(metrics.network_io),
                metrics.response_time,
                metrics.throughput,
                metrics.error_rate,
                metrics.active_connections,
                metrics.queue_size
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"메트릭 저장 중 오류: {e}")
            
    def update_prometheus_metrics(self, metrics: PerformanceMetrics):
        """Prometheus 메트릭 업데이트"""
        try:
            # 시스템 메트릭
            self.cpu_gauge.set(metrics.cpu_percent)
            self.memory_gauge.set(metrics.memory_percent)
            self.disk_gauge.set(metrics.disk_usage_percent)
            
            # 네트워크 메트릭
            if metrics.network_io:
                self.network_bytes_sent.inc(metrics.network_io.get('bytes_sent', 0))
                self.network_bytes_recv.inc(metrics.network_io.get('bytes_recv', 0))
                
            # 애플리케이션 메트릭
            self.active_users_gauge.set(metrics.active_connections)
            self.queue_size_gauge.set(metrics.queue_size)
            self.throughput_gauge.set(metrics.throughput)
            
        except Exception as e:
            logger.error(f"Prometheus 메트릭 업데이트 중 오류: {e}")
            
    async def check_alerts(self, metrics: PerformanceMetrics):
        """알림 조건 확인"""
        alerts = []
        
        # CPU 사용률 알림
        if metrics.cpu_percent >= self.thresholds.cpu_critical:
            alerts.append({
                'type': 'cpu_usage',
                'severity': 'critical',
                'message': f'CPU 사용률이 임계값을 초과했습니다: {metrics.cpu_percent:.1f}%',
                'metric_value': metrics.cpu_percent,
                'threshold_value': self.thresholds.cpu_critical
            })
        elif metrics.cpu_percent >= self.thresholds.cpu_warning:
            alerts.append({
                'type': 'cpu_usage',
                'severity': 'warning',
                'message': f'CPU 사용률이 높습니다: {metrics.cpu_percent:.1f}%',
                'metric_value': metrics.cpu_percent,
                'threshold_value': self.thresholds.cpu_warning
            })
            
        # 메모리 사용률 알림
        if metrics.memory_percent >= self.thresholds.memory_critical:
            alerts.append({
                'type': 'memory_usage',
                'severity': 'critical',
                'message': f'메모리 사용률이 임계값을 초과했습니다: {metrics.memory_percent:.1f}%',
                'metric_value': metrics.memory_percent,
                'threshold_value': self.thresholds.memory_critical
            })
        elif metrics.memory_percent >= self.thresholds.memory_warning:
            alerts.append({
                'type': 'memory_usage',
                'severity': 'warning',
                'message': f'메모리 사용률이 높습니다: {metrics.memory_percent:.1f}%',
                'metric_value': metrics.memory_percent,
                'threshold_value': self.thresholds.memory_warning
            })
            
        # 디스크 사용률 알림
        if metrics.disk_usage_percent >= self.thresholds.disk_critical:
            alerts.append({
                'type': 'disk_usage',
                'severity': 'critical',
                'message': f'디스크 사용률이 임계값을 초과했습니다: {metrics.disk_usage_percent:.1f}%',
                'metric_value': metrics.disk_usage_percent,
                'threshold_value': self.thresholds.disk_critical
            })
        elif metrics.disk_usage_percent >= self.thresholds.disk_warning:
            alerts.append({
                'type': 'disk_usage',
                'severity': 'warning',
                'message': f'디스크 사용률이 높습니다: {metrics.disk_usage_percent:.1f}%',
                'metric_value': metrics.disk_usage_percent,
                'threshold_value': self.thresholds.disk_warning
            })
            
        # 응답 시간 알림
        if metrics.response_time >= self.thresholds.response_time_critical:
            alerts.append({
                'type': 'response_time',
                'severity': 'critical',
                'message': f'응답 시간이 임계값을 초과했습니다: {metrics.response_time:.2f}초',
                'metric_value': metrics.response_time,
                'threshold_value': self.thresholds.response_time_critical
            })
        elif metrics.response_time >= self.thresholds.response_time_warning:
            alerts.append({
                'type': 'response_time',
                'severity': 'warning',
                'message': f'응답 시간이 느립니다: {metrics.response_time:.2f}초',
                'metric_value': metrics.response_time,
                'threshold_value': self.thresholds.response_time_warning
            })
            
        # 오류율 알림
        if metrics.error_rate >= self.thresholds.error_rate_critical:
            alerts.append({
                'type': 'error_rate',
                'severity': 'critical',
                'message': f'오류율이 임계값을 초과했습니다: {metrics.error_rate:.1f}%',
                'metric_value': metrics.error_rate,
                'threshold_value': self.thresholds.error_rate_critical
            })
        elif metrics.error_rate >= self.thresholds.error_rate_warning:
            alerts.append({
                'type': 'error_rate',
                'severity': 'warning',
                'message': f'오류율이 높습니다: {metrics.error_rate:.1f}%',
                'metric_value': metrics.error_rate,
                'threshold_value': self.thresholds.error_rate_warning
            })
            
        # 알림 저장 및 전송
        for alert in alerts:
            await self.save_alert(alert)
            await self.send_alert(alert)
            
    async def save_alert(self, alert: Dict[str, Any]):
        """알림을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts 
                (timestamp, alert_type, severity, message, metric_value, threshold_value)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                alert['type'],
                alert['severity'],
                alert['message'],
                alert['metric_value'],
                alert['threshold_value']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"알림 저장 중 오류: {e}")
            
    async def send_alert(self, alert: Dict[str, Any]):
        """알림 전송"""
        try:
            # 로그 출력
            logger.warning(f"알림: {alert['message']}")
            
            # Redis에 알림 저장 (실시간 알림용)
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'type': alert['type'],
                'severity': alert['severity'],
                'message': alert['message'],
                'metric_value': alert['metric_value'],
                'threshold_value': alert['threshold_value']
            }
            
            self.redis_client.lpush('alerts:recent', json.dumps(alert_data))
            self.redis_client.ltrim('alerts:recent', 0, 99)  # 최근 100개만 유지
            
            # 웹훅 전송 (설정된 경우)
            webhook_url = self.config.get('webhook_url')
            if webhook_url:
                async with aiohttp.ClientSession() as session:
                    await session.post(webhook_url, json=alert_data)
                    
        except Exception as e:
            logger.error(f"알림 전송 중 오류: {e}")
            
    def manage_metrics_history(self, metrics: PerformanceMetrics):
        """메트릭 히스토리 관리"""
        self.metrics_history.append(metrics)
        
        # 최근 1000개 메트릭만 유지
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
            
    async def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """지정된 시간 동안의 메트릭 요약"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 시간 범위 계산
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    AVG(cpu_percent) as avg_cpu,
                    MAX(cpu_percent) as max_cpu,
                    AVG(memory_percent) as avg_memory,
                    MAX(memory_percent) as max_memory,
                    AVG(response_time) as avg_response_time,
                    MAX(response_time) as max_response_time,
                    AVG(throughput) as avg_throughput,
                    MAX(throughput) as max_throughput,
                    AVG(error_rate) as avg_error_rate,
                    MAX(error_rate) as max_error_rate
                FROM performance_metrics
                WHERE timestamp BETWEEN ? AND ?
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'period_hours': hours,
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'cpu': {
                        'average': round(row[0], 2) if row[0] else 0,
                        'maximum': round(row[1], 2) if row[1] else 0
                    },
                    'memory': {
                        'average': round(row[2], 2) if row[2] else 0,
                        'maximum': round(row[3], 2) if row[3] else 0
                    },
                    'response_time': {
                        'average': round(row[4], 3) if row[4] else 0,
                        'maximum': round(row[5], 3) if row[5] else 0
                    },
                    'throughput': {
                        'average': round(row[6], 2) if row[6] else 0,
                        'maximum': round(row[7], 2) if row[7] else 0
                    },
                    'error_rate': {
                        'average': round(row[8], 2) if row[8] else 0,
                        'maximum': round(row[9], 2) if row[9] else 0
                    }
                }
            else:
                return {}
                
        except Exception as e:
            logger.error(f"메트릭 요약 조회 중 오류: {e}")
            return {}
            
    async def get_recent_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """최근 알림 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, alert_type, severity, message, metric_value, threshold_value
                FROM alerts
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            alerts = []
            for row in rows:
                alerts.append({
                    'timestamp': row[0],
                    'type': row[1],
                    'severity': row[2],
                    'message': row[3],
                    'metric_value': row[4],
                    'threshold_value': row[5]
                })
                
            return alerts
            
        except Exception as e:
            logger.error(f"최근 알림 조회 중 오류: {e}")
            return []

# 성능 모니터링 인스턴스
performance_monitor = None

async def start_performance_monitoring(config: Dict[str, Any]):
    """성능 모니터링 시작"""
    global performance_monitor
    
    if performance_monitor is None:
        performance_monitor = PerformanceMonitor(config)
        
    await performance_monitor.start_monitoring()

async def stop_performance_monitoring():
    """성능 모니터링 중지"""
    global performance_monitor
    
    if performance_monitor:
        await performance_monitor.stop_monitoring()

def get_performance_monitor() -> Optional[PerformanceMonitor]:
    """성능 모니터링 인스턴스 반환"""
    return performance_monitor 