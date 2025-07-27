#!/usr/bin/env python3
"""
성능 모니터링 시스템
"""

import time
import psutil
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
from dataclasses import dataclass, asdict
import sqlite3
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('monitoring/performance.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_io: Dict[str, float]
    api_response_time: Optional[float]
    api_status: Optional[str]
    active_connections: int
    error_count: int

@dataclass
class Alert:
    timestamp: datetime
    level: str  # 'info', 'warning', 'error', 'critical'
    message: str
    metric: str
    value: float
    threshold: float

class PerformanceMonitor:
    def __init__(self, config: Dict = None):
        self.config = config or {
            'monitoring_interval': 30,  # 초
            'api_endpoints': [
                'http://localhost:5000/api/health',
                'http://localhost:5000/api/employee/dashboard',
                'http://localhost:3000'
            ],
            'thresholds': {
                'cpu_percent': 80.0,
                'memory_percent': 85.0,
                'disk_usage_percent': 90.0,
                'api_response_time': 2.0,  # 초
                'error_rate': 5.0  # %
            },
            'alert_channels': ['log', 'file'],
            'retention_days': 30
        }
        
        self.metrics_history: List[PerformanceMetrics] = []
        self.alerts_history: List[Alert] = []
        self.is_monitoring = False
        self.monitor_thread = None
        
        # 데이터베이스 초기화
        self.init_database()
        
    def init_database(self):
        """모니터링 데이터베이스 초기화"""
        os.makedirs('monitoring', exist_ok=True)
        
        conn = sqlite3.connect('monitoring/performance.db')
        cursor = conn.cursor()
        
        # 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage_percent REAL,
                network_io TEXT,
                api_response_time REAL,
                api_status TEXT,
                active_connections INTEGER,
                error_count INTEGER
            )
        ''')
        
        # 알림 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                metric TEXT NOT NULL,
                value REAL,
                threshold REAL
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_monitoring:
            logger.warning("모니터링이 이미 실행 중입니다.")
            return
            
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("성능 모니터링이 시작되었습니다.")
        
    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        logger.info("성능 모니터링이 중지되었습니다.")
        
    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.is_monitoring:
            try:
                metrics = self.collect_metrics()
                self.metrics_history.append(metrics)
                
                # 알림 확인
                alerts = self.check_alerts(metrics)
                for alert in alerts:
                    self.alerts_history.append(alert)
                    self.send_alert(alert)
                
                # 데이터베이스에 저장
                self.save_metrics(metrics)
                for alert in alerts:
                    self.save_alert(alert)
                
                # 오래된 데이터 정리
                self.cleanup_old_data()
                
                time.sleep(self.config['monitoring_interval'])
                
            except Exception as e:
                logger.error(f"모니터링 중 오류 발생: {e}")
                time.sleep(5)
                
    def collect_metrics(self) -> PerformanceMetrics:
        """시스템 메트릭 수집"""
        timestamp = datetime.now()
        
        # CPU 사용률
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 메모리 사용률
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # 디스크 사용률
        disk = psutil.disk_usage('/')
        disk_usage_percent = disk.percent
        
        # 네트워크 I/O
        network_io = psutil.net_io_counters()
        network_data = {
            'bytes_sent': network_io.bytes_sent,
            'bytes_recv': network_io.bytes_recv,
            'packets_sent': network_io.packets_sent,
            'packets_recv': network_io.packets_recv
        }
        
        # API 응답 시간 및 상태
        api_response_time = None
        api_status = None
        try:
            start_time = time.time()
            response = requests.get(self.config['api_endpoints'][0], timeout=5)
            api_response_time = time.time() - start_time
            api_status = response.status_code
        except Exception as e:
            api_status = 'error'
            logger.warning(f"API 헬스체크 실패: {e}")
        
        # 활성 연결 수 (대략적 추정)
        active_connections = len(psutil.net_connections())
        
        # 오류 수 (최근 1분간)
        error_count = self.get_recent_error_count()
        
        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            disk_usage_percent=disk_usage_percent,
            network_io=network_data,
            api_response_time=api_response_time,
            api_status=api_status,
            active_connections=active_connections,
            error_count=error_count
        )
        
    def get_recent_error_count(self) -> int:
        """최근 오류 수 계산"""
        # 실제 구현에서는 로그 파일이나 데이터베이스에서 오류 수를 계산
        # 여기서는 간단한 예시로 0을 반환
        return 0
        
    def check_alerts(self, metrics: PerformanceMetrics) -> List[Alert]:
        """알림 조건 확인"""
        alerts = []
        thresholds = self.config['thresholds']
        
        # CPU 사용률 알림
        if metrics.cpu_percent > thresholds['cpu_percent']:
            alerts.append(Alert(
                timestamp=metrics.timestamp,
                level='warning' if metrics.cpu_percent < 95 else 'critical',
                message=f"CPU 사용률이 높습니다: {metrics.cpu_percent:.1f}%",
                metric='cpu_percent',
                value=metrics.cpu_percent,
                threshold=thresholds['cpu_percent']
            ))
        
        # 메모리 사용률 알림
        if metrics.memory_percent > thresholds['memory_percent']:
            alerts.append(Alert(
                timestamp=metrics.timestamp,
                level='warning' if metrics.memory_percent < 95 else 'critical',
                message=f"메모리 사용률이 높습니다: {metrics.memory_percent:.1f}%",
                metric='memory_percent',
                value=metrics.memory_percent,
                threshold=thresholds['memory_percent']
            ))
        
        # 디스크 사용률 알림
        if metrics.disk_usage_percent > thresholds['disk_usage_percent']:
            alerts.append(Alert(
                timestamp=metrics.timestamp,
                level='warning',
                message=f"디스크 사용률이 높습니다: {metrics.disk_usage_percent:.1f}%",
                metric='disk_usage_percent',
                value=metrics.disk_usage_percent,
                threshold=thresholds['disk_usage_percent']
            ))
        
        # API 응답 시간 알림
        if metrics.api_response_time and metrics.api_response_time > thresholds['api_response_time']:
            alerts.append(Alert(
                timestamp=metrics.timestamp,
                level='warning',
                message=f"API 응답 시간이 느립니다: {metrics.api_response_time:.2f}초",
                metric='api_response_time',
                value=metrics.api_response_time,
                threshold=thresholds['api_response_time']
            ))
        
        # API 상태 알림
        if metrics.api_status and metrics.api_status != 200:
            alerts.append(Alert(
                timestamp=metrics.timestamp,
                level='error',
                message=f"API 상태 오류: {metrics.api_status}",
                metric='api_status',
                value=metrics.api_status,
                threshold=200
            ))
        
        return alerts
        
    def send_alert(self, alert: Alert):
        """알림 전송"""
        alert_message = f"[{alert.level.upper()}] {alert.message}"
        
        if 'log' in self.config['alert_channels']:
            if alert.level == 'critical':
                logger.critical(alert_message)
            elif alert.level == 'error':
                logger.error(alert_message)
            elif alert.level == 'warning':
                logger.warning(alert_message)
            else:
                logger.info(alert_message)
        
        if 'file' in self.config['alert_channels']:
            with open('monitoring/alerts.log', 'a', encoding='utf-8') as f:
                f.write(f"{alert.timestamp.isoformat()} - {alert_message}\n")
        
        # WebSocket을 통한 실시간 알림 (선택사항)
        self.send_realtime_alert(alert)
        
    def send_realtime_alert(self, alert: Alert):
        """실시간 알림 전송"""
        try:
            # WebSocket을 통해 프론트엔드로 알림 전송
            alert_data = {
                'type': 'performance_alert',
                'level': alert.level,
                'message': alert.message,
                'metric': alert.metric,
                'value': alert.value,
                'threshold': alert.threshold,
                'timestamp': alert.timestamp.isoformat()
            }
            
            # 실제 구현에서는 WebSocket 매니저를 통해 전송
            logger.info(f"실시간 알림 전송: {alert_data}")
            
        except Exception as e:
            logger.error(f"실시간 알림 전송 실패: {e}")
        
    def save_metrics(self, metrics: PerformanceMetrics):
        """메트릭을 데이터베이스에 저장"""
        conn = sqlite3.connect('monitoring/performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metrics (
                timestamp, cpu_percent, memory_percent, disk_usage_percent,
                network_io, api_response_time, api_status, active_connections, error_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            metrics.timestamp.isoformat(),
            metrics.cpu_percent,
            metrics.memory_percent,
            metrics.disk_usage_percent,
            json.dumps(metrics.network_io),
            metrics.api_response_time,
            metrics.api_status,
            metrics.active_connections,
            metrics.error_count
        ))
        
        conn.commit()
        conn.close()
        
    def save_alert(self, alert: Alert):
        """알림을 데이터베이스에 저장"""
        conn = sqlite3.connect('monitoring/performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO alerts (
                timestamp, level, message, metric, value, threshold
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            alert.timestamp.isoformat(),
            alert.level,
            alert.message,
            alert.metric,
            alert.value,
            alert.threshold
        ))
        
        conn.commit()
        conn.close()
        
    def cleanup_old_data(self):
        """오래된 데이터 정리"""
        cutoff_date = datetime.now() - timedelta(days=self.config['retention_days'])
        
        conn = sqlite3.connect('monitoring/performance.db')
        cursor = conn.cursor()
        
        # 오래된 메트릭 삭제
        cursor.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_date.isoformat(),))
        
        # 오래된 알림 삭제
        cursor.execute('DELETE FROM alerts WHERE timestamp < ?', (cutoff_date.isoformat(),))
        
        conn.commit()
        conn.close()
        
    def get_metrics_summary(self, hours: int = 24) -> Dict:
        """메트릭 요약 정보 반환"""
        cutoff_date = datetime.now() - timedelta(hours=hours)
        
        conn = sqlite3.connect('monitoring/performance.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                AVG(cpu_percent) as avg_cpu,
                MAX(cpu_percent) as max_cpu,
                AVG(memory_percent) as avg_memory,
                MAX(memory_percent) as max_memory,
                AVG(api_response_time) as avg_response_time,
                MAX(api_response_time) as max_response_time,
                COUNT(*) as total_metrics
            FROM metrics 
            WHERE timestamp > ?
        ''', (cutoff_date.isoformat(),))
        
        result = cursor.fetchone()
        
        # 알림 통계
        cursor.execute('''
            SELECT level, COUNT(*) as count
            FROM alerts 
            WHERE timestamp > ?
            GROUP BY level
        ''', (cutoff_date.isoformat(),))
        
        alerts_by_level = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            'period_hours': hours,
            'avg_cpu_percent': result[0] or 0,
            'max_cpu_percent': result[1] or 0,
            'avg_memory_percent': result[2] or 0,
            'max_memory_percent': result[3] or 0,
            'avg_api_response_time': result[4] or 0,
            'max_api_response_time': result[5] or 0,
            'total_metrics': result[6] or 0,
            'alerts_by_level': alerts_by_level
        }

def main():
    """메인 실행 함수"""
    print("🚀 성능 모니터링 시스템 시작...")
    
    # 모니터링 설정
    config = {
        'monitoring_interval': 30,  # 30초마다 체크
        'api_endpoints': [
            'http://localhost:5000/api/health',
            'http://localhost:5000/api/employee/dashboard'
        ],
        'thresholds': {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'api_response_time': 2.0,
            'error_rate': 5.0
        },
        'alert_channels': ['log', 'file'],
        'retention_days': 30
    }
    
    # 모니터링 시작
    monitor = PerformanceMonitor(config)
    monitor.start_monitoring()
    
    try:
        while True:
            time.sleep(60)  # 1분마다 요약 출력
            
            # 요약 정보 출력
            summary = monitor.get_metrics_summary(hours=1)
            print(f"\n📊 성능 요약 (최근 1시간):")
            print(f"  CPU 평균: {summary['avg_cpu_percent']:.1f}% (최대: {summary['max_cpu_percent']:.1f}%)")
            print(f"  메모리 평균: {summary['avg_memory_percent']:.1f}% (최대: {summary['max_memory_percent']:.1f}%)")
            print(f"  API 응답시간 평균: {summary['avg_api_response_time']:.2f}초 (최대: {summary['max_api_response_time']:.2f}초)")
            print(f"  알림: {summary['alerts_by_level']}")
            
    except KeyboardInterrupt:
        print("\n🛑 모니터링 중지...")
        monitor.stop_monitoring()
        print("✅ 모니터링이 중지되었습니다.")

if __name__ == "__main__":
    main() 