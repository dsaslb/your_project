import time
import threading
import psutil
import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import queue
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터 클래스"""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    network_sent: int
    network_recv: int
    active_connections: int
    active_users: int
    request_count: int
    error_count: int
    response_time_avg: float

@dataclass
class UserActivity:
    """사용자 활동 데이터 클래스"""
    user_id: str
    session_id: str
    action: str
    page: str
    timestamp: float
    duration: float
    ip_address: str
    user_agent: str
    success: bool
    error_message: Optional[str] = None

@dataclass
class PerformanceAlert:
    """성능 알림 데이터 클래스"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: float
    metrics: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[float] = None

class RealTimeMonitor:
    """실시간 모니터링 시스템"""
    
    def __init__(self, db_path: str = "data/monitoring.db"):
        self.db_path = db_path
        self.metrics_queue = queue.Queue()
        self.activity_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        self.running = False
        self.monitor_thread = None
        self.processor_thread = None
        
        # 임계값 설정
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'response_time_avg': 2.0,
            'error_rate': 5.0
        }
        
        # 통계 데이터
        self.stats = {
            'request_count': 0,
            'error_count': 0,
            'response_times': deque(maxlen=1000),
            'active_users': set(),
            'active_sessions': set()
        }
        
        # 알림 핸들러
        self.alert_handlers: List[Callable] = []
        
        # 데이터베이스 초기화
        self._init_database()
        
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 시스템 메트릭 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS system_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp REAL NOT NULL,
                        cpu_percent REAL NOT NULL,
                        memory_percent REAL NOT NULL,
                        disk_usage_percent REAL NOT NULL,
                        network_sent INTEGER NOT NULL,
                        network_recv INTEGER NOT NULL,
                        active_connections INTEGER NOT NULL,
                        active_users INTEGER NOT NULL,
                        request_count INTEGER NOT NULL,
                        error_count INTEGER NOT NULL,
                        response_time_avg REAL NOT NULL
                    )
                ''')
                
                # 사용자 활동 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_activities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id TEXT NOT NULL,
                        session_id TEXT NOT NULL,
                        action TEXT NOT NULL,
                        page TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        duration REAL NOT NULL,
                        ip_address TEXT NOT NULL,
                        user_agent TEXT NOT NULL,
                        success BOOLEAN NOT NULL,
                        error_message TEXT
                    )
                ''')
                
                # 성능 알림 테이블
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        timestamp REAL NOT NULL,
                        metrics TEXT NOT NULL,
                        resolved BOOLEAN NOT NULL DEFAULT FALSE,
                        resolved_at REAL
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON system_metrics(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_timestamp ON user_activities(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_activities_user_id ON user_activities(user_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON performance_alerts(timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_alerts_resolved ON performance_alerts(resolved)')
                
                conn.commit()
                logger.info("모니터링 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        if self.running:
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.processor_thread = threading.Thread(target=self._processor_loop, daemon=True)
        
        self.monitor_thread.start()
        self.processor_thread.start()
        
        logger.info("실시간 모니터링 시작")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        if self.processor_thread:
            self.processor_thread.join()
        
        logger.info("실시간 모니터링 중지")
    
    def _monitor_loop(self):
        """모니터링 루프"""
        last_network_stats = psutil.net_io_counters()
        last_check_time = time.time()
        
        while self.running:
            try:
                current_time = time.time()
                
                # 시스템 메트릭 수집
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                network_stats = psutil.net_io_counters()
                
                # 네트워크 사용량 계산
                network_sent = network_stats.bytes_sent - last_network_stats.bytes_sent
                network_recv = network_stats.bytes_recv - last_network_stats.bytes_recv
                
                # 연결 수 계산 (대략적)
                connections = len(psutil.net_connections())
                
                # 통계 데이터에서 값 가져오기
                request_count = self.stats['request_count']
                error_count = self.stats['error_count']
                active_users = len(self.stats['active_users'])
                
                # 평균 응답 시간 계산
                response_time_avg = 0.0
                if self.stats['response_times']:
                    response_time_avg = sum(self.stats['response_times']) / len(self.stats['response_times'])
                
                # 메트릭 객체 생성
                metrics = SystemMetrics(
                    timestamp=current_time,
                    cpu_percent=cpu_percent,
                    memory_percent=memory.percent,
                    disk_usage_percent=disk.percent,
                    network_sent=network_sent,
                    network_recv=network_recv,
                    active_connections=connections,
                    active_users=active_users,
                    request_count=request_count,
                    error_count=error_count,
                    response_time_avg=response_time_avg
                )
                
                # 큐에 메트릭 추가
                self.metrics_queue.put(metrics)
                
                # 임계값 체크 및 알림 생성
                self._check_thresholds(metrics)
                
                # 통계 초기화 (1분마다)
                if current_time - last_check_time >= 60:
                    self.stats['request_count'] = 0
                    self.stats['error_count'] = 0
                    self.stats['response_times'].clear()
                    last_check_time = current_time
                
                last_network_stats = network_stats
                time.sleep(5)  # 5초마다 체크
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(5)
    
    def _processor_loop(self):
        """데이터 처리 루프"""
        while self.running:
            try:
                # 메트릭 처리
                try:
                    metrics = self.metrics_queue.get_nowait()
                    self._save_metrics(metrics)
                except queue.Empty:
                    pass
                
                # 사용자 활동 처리
                try:
                    activity = self.activity_queue.get_nowait()
                    self._save_activity(activity)
                except queue.Empty:
                    pass
                
                # 알림 처리
                try:
                    alert = self.alert_queue.get_nowait()
                    self._save_alert(alert)
                    self._notify_alert(alert)
                except queue.Empty:
                    pass
                
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"데이터 처리 루프 오류: {e}")
                time.sleep(1)
    
    def _check_thresholds(self, metrics: SystemMetrics):
        """임계값 체크 및 알림 생성"""
        alerts = []
        
        # CPU 사용률 체크
        if metrics.cpu_percent > self.thresholds['cpu_percent']:
            alerts.append(PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                alert_type='high_cpu_usage',
                severity='warning' if metrics.cpu_percent < 95 else 'critical',
                message=f"CPU 사용률이 높습니다: {metrics.cpu_percent:.1f}%",
                timestamp=metrics.timestamp,
                metrics={'cpu_percent': metrics.cpu_percent}
            ))
        
        # 메모리 사용률 체크
        if metrics.memory_percent > self.thresholds['memory_percent']:
            alerts.append(PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                alert_type='high_memory_usage',
                severity='warning' if metrics.memory_percent < 95 else 'critical',
                message=f"메모리 사용률이 높습니다: {metrics.memory_percent:.1f}%",
                timestamp=metrics.timestamp,
                metrics={'memory_percent': metrics.memory_percent}
            ))
        
        # 디스크 사용률 체크
        if metrics.disk_usage_percent > self.thresholds['disk_usage_percent']:
            alerts.append(PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                alert_type='high_disk_usage',
                severity='warning' if metrics.disk_usage_percent < 95 else 'critical',
                message=f"디스크 사용률이 높습니다: {metrics.disk_usage_percent:.1f}%",
                timestamp=metrics.timestamp,
                metrics={'disk_usage_percent': metrics.disk_usage_percent}
            ))
        
        # 응답 시간 체크
        if metrics.response_time_avg > self.thresholds['response_time_avg']:
            alerts.append(PerformanceAlert(
                alert_id=str(uuid.uuid4()),
                alert_type='slow_response_time',
                severity='warning',
                message=f"평균 응답 시간이 느립니다: {metrics.response_time_avg:.2f}초",
                timestamp=metrics.timestamp,
                metrics={'response_time_avg': metrics.response_time_avg}
            ))
        
        # 에러율 체크
        if metrics.request_count > 0:
            error_rate = (metrics.error_count / metrics.request_count) * 100
            if error_rate > self.thresholds['error_rate']:
                alerts.append(PerformanceAlert(
                    alert_id=str(uuid.uuid4()),
                    alert_type='high_error_rate',
                    severity='critical',
                    message=f"에러율이 높습니다: {error_rate:.1f}%",
                    timestamp=metrics.timestamp,
                    metrics={'error_rate': error_rate, 'error_count': metrics.error_count, 'request_count': metrics.request_count}
                ))
        
        # 알림 큐에 추가
        for alert in alerts:
            self.alert_queue.put(alert)
    
    def _save_metrics(self, metrics: SystemMetrics):
        """메트릭 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO system_metrics 
                    (timestamp, cpu_percent, memory_percent, disk_usage_percent, 
                     network_sent, network_recv, active_connections, active_users,
                     request_count, error_count, response_time_avg)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metrics.timestamp, metrics.cpu_percent, metrics.memory_percent,
                    metrics.disk_usage_percent, metrics.network_sent, metrics.network_recv,
                    metrics.active_connections, metrics.active_users, metrics.request_count,
                    metrics.error_count, metrics.response_time_avg
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"메트릭 저장 실패: {e}")
    
    def _save_activity(self, activity: UserActivity):
        """사용자 활동 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO user_activities 
                    (user_id, session_id, action, page, timestamp, duration,
                     ip_address, user_agent, success, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    activity.user_id, activity.session_id, activity.action, activity.page,
                    activity.timestamp, activity.duration, activity.ip_address,
                    activity.user_agent, activity.success, activity.error_message
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"사용자 활동 저장 실패: {e}")
    
    def _save_alert(self, alert: PerformanceAlert):
        """알림 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO performance_alerts 
                    (alert_id, alert_type, severity, message, timestamp, metrics, resolved, resolved_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id, alert.alert_type, alert.severity, alert.message,
                    alert.timestamp, json.dumps(alert.metrics), alert.resolved, alert.resolved_at
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"알림 저장 실패: {e}")
    
    def _notify_alert(self, alert: PerformanceAlert):
        """알림 핸들러 호출"""
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                logger.error(f"알림 핸들러 오류: {e}")
    
    def record_request(self, user_id: str, session_id: str, response_time: float, success: bool = True):
        """요청 기록"""
        self.stats['request_count'] += 1
        if not success:
            self.stats['error_count'] += 1
        
        self.stats['response_times'].append(response_time)
        self.stats['active_users'].add(user_id)
        self.stats['active_sessions'].add(session_id)
    
    def record_user_activity(self, activity: UserActivity):
        """사용자 활동 기록"""
        self.activity_queue.put(activity)
    
    def add_alert_handler(self, handler: Callable[[PerformanceAlert], None]):
        """알림 핸들러 추가"""
        self.alert_handlers.append(handler)
    
    def get_recent_metrics(self, minutes: int = 60) -> List[SystemMetrics]:
        """최근 메트릭 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = time.time() - (minutes * 60)
                
                cursor.execute('''
                    SELECT timestamp, cpu_percent, memory_percent, disk_usage_percent,
                           network_sent, network_recv, active_connections, active_users,
                           request_count, error_count, response_time_avg
                    FROM system_metrics
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time,))
                
                metrics = []
                for row in cursor.fetchall():
                    metrics.append(SystemMetrics(
                        timestamp=row[0], cpu_percent=row[1], memory_percent=row[2],
                        disk_usage_percent=row[3], network_sent=row[4], network_recv=row[5],
                        active_connections=row[6], active_users=row[7], request_count=row[8],
                        error_count=row[9], response_time_avg=row[10]
                    ))
                
                return metrics
        except Exception as e:
            logger.error(f"메트릭 조회 실패: {e}")
            return []
    
    def get_recent_alerts(self, hours: int = 24) -> List[PerformanceAlert]:
        """최근 알림 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = time.time() - (hours * 3600)
                
                cursor.execute('''
                    SELECT alert_id, alert_type, severity, message, timestamp, metrics, resolved, resolved_at
                    FROM performance_alerts
                    WHERE timestamp >= ?
                    ORDER BY timestamp DESC
                ''', (cutoff_time,))
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append(PerformanceAlert(
                        alert_id=row[0], alert_type=row[1], severity=row[2],
                        message=row[3], timestamp=row[4], metrics=json.loads(row[5]),
                        resolved=bool(row[6]), resolved_at=row[7]
                    ))
                
                return alerts
        except Exception as e:
            logger.error(f"알림 조회 실패: {e}")
            return []
    
    def get_user_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """사용자 활동 요약"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cutoff_time = time.time() - (hours * 3600)
                
                # 총 활동 수
                cursor.execute('''
                    SELECT COUNT(*) FROM user_activities WHERE timestamp >= ?
                ''', (cutoff_time,))
                total_activities = cursor.fetchone()[0]
                
                # 성공/실패 비율
                cursor.execute('''
                    SELECT success, COUNT(*) FROM user_activities 
                    WHERE timestamp >= ? GROUP BY success
                ''', (cutoff_time,))
                success_stats = dict(cursor.fetchall())
                
                # 가장 활발한 사용자
                cursor.execute('''
                    SELECT user_id, COUNT(*) as activity_count 
                    FROM user_activities 
                    WHERE timestamp >= ? 
                    GROUP BY user_id 
                    ORDER BY activity_count DESC 
                    LIMIT 10
                ''', (cutoff_time,))
                top_users = cursor.fetchall()
                
                # 가장 많이 방문한 페이지
                cursor.execute('''
                    SELECT page, COUNT(*) as visit_count 
                    FROM user_activities 
                    WHERE timestamp >= ? 
                    GROUP BY page 
                    ORDER BY visit_count DESC 
                    LIMIT 10
                ''', (cutoff_time,))
                top_pages = cursor.fetchall()
                
                return {
                    'total_activities': total_activities,
                    'success_rate': (success_stats.get(True, 0) / total_activities * 100) if total_activities > 0 else 0,
                    'error_rate': (success_stats.get(False, 0) / total_activities * 100) if total_activities > 0 else 0,
                    'top_users': top_users,
                    'top_pages': top_pages
                }
        except Exception as e:
            logger.error(f"사용자 활동 요약 조회 실패: {e}")
            return {}
    
    def resolve_alert(self, alert_id: str):
        """알림 해결"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE performance_alerts 
                    SET resolved = TRUE, resolved_at = ? 
                    WHERE alert_id = ?
                ''', (time.time(), alert_id))
                conn.commit()
        except Exception as e:
            logger.error(f"알림 해결 실패: {e}")
    
    def update_thresholds(self, new_thresholds: Dict[str, float]):
        """임계값 업데이트"""
        self.thresholds.update(new_thresholds)
        logger.info(f"임계값 업데이트: {new_thresholds}")
    
    def get_current_metrics(self) -> SystemMetrics:
        """현재 시스템 메트릭 조회"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # 네트워크 통계
            network = psutil.net_io_counters()
            network_sent = network.bytes_sent
            network_recv = network.bytes_recv
            
            # 활성 연결 수 (대략적)
            active_connections = len(psutil.net_connections())
            
            # 활성 사용자 수
            active_users = len(self.stats['active_users'])
            
            # 요청 수 및 응답 시간
            request_count = self.stats['request_count']
            response_time_avg = sum(self.stats['response_times']) / len(self.stats['response_times']) if self.stats['response_times'] else 0
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_usage_percent=disk_usage_percent,
                network_sent=network_sent,
                network_recv=network_recv,
                active_connections=active_connections,
                active_users=active_users,
                request_count=request_count,
                error_count=self.stats['error_count'],
                response_time_avg=response_time_avg
            )
        except Exception as e:
            logger.error(f"현재 메트릭 조회 실패: {e}")
            # 기본값 반환
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_usage_percent=0.0,
                network_sent=0,
                network_recv=0,
                active_connections=0,
                active_users=0,
                request_count=0,
                error_count=0,
                response_time_avg=0.0
            )
    
    def get_database_status(self) -> Dict[str, Any]:
        """데이터베이스 상태 조회"""
        try:
            # SQLite 연결 테스트
            start_time = time.time()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                response_time = (time.time() - start_time) * 1000  # ms
            
            return {
                'connected': True,
                'response_time': round(response_time, 2),
                'active_connections': 1,  # SQLite는 단일 연결
                'database_size': self._get_database_size()
            }
        except Exception as e:
            logger.error(f"데이터베이스 상태 조회 실패: {e}")
            return {
                'connected': False,
                'response_time': 0,
                'active_connections': 0,
                'database_size': 0
            }
    
    def get_network_status(self) -> Dict[str, Any]:
        """네트워크 상태 조회"""
        try:
            # 네트워크 인터페이스 정보
            net_io = psutil.net_io_counters()
            
            # 대역폭 사용률 계산 (이전 값과 비교)
            if hasattr(self, '_prev_net_io'):
                time_diff = time.time() - getattr(self, '_prev_time', time.time())
                bytes_sent_diff = net_io.bytes_sent - self._prev_net_io.bytes_sent
                bytes_recv_diff = net_io.bytes_recv - self._prev_net_io.bytes_recv
                
                bandwidth_usage = min(100, (bytes_sent_diff + bytes_recv_diff) / (1024 * 1024 * time_diff) * 100)
            else:
                bandwidth_usage = 0
            
            # 패킷 손실률 (대략적 추정)
            packet_loss = 0.1  # 실제로는 ping 테스트 필요
            
            # 지연 시간 (대략적)
            latency = 50  # ms, 실제로는 ping 테스트 필요
            
            # 이전 값 저장
            self._prev_net_io = net_io
            self._prev_time = time.time()
            
            return {
                'bandwidth_usage': round(bandwidth_usage, 2),
                'packet_loss': packet_loss,
                'latency': latency,
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
        except Exception as e:
            logger.error(f"네트워크 상태 조회 실패: {e}")
            return {
                'bandwidth_usage': 0,
                'packet_loss': 0,
                'latency': 0,
                'bytes_sent': 0,
                'bytes_recv': 0
            }
    
    def get_metrics_by_hour(self, hours: int = 24) -> List[Dict[str, Any]]:
        """시간별 메트릭 데이터 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 시간별 평균 메트릭 조회
                query = """
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', datetime(timestamp, 'unixepoch')) as hour,
                    AVG(cpu_percent) as avg_cpu,
                    AVG(memory_percent) as avg_memory,
                    AVG(disk_usage_percent) as avg_disk,
                    AVG(active_users) as avg_users,
                    AVG(response_time_avg) as avg_response_time
                FROM system_metrics 
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY hour DESC
                LIMIT ?
                """
                
                start_time = time.time() - (hours * 3600)
                cursor.execute(query, (start_time, hours))
                
                results = []
                for row in cursor.fetchall():
                    results.append({
                        'hour': row[0],
                        'avg_cpu': round(row[1], 2),
                        'avg_memory': round(row[2], 2),
                        'avg_disk': round(row[3], 2),
                        'avg_users': round(row[4], 2),
                        'avg_response_time': round(row[5], 2)
                    })
                
                return results
        except Exception as e:
            logger.error(f"시간별 메트릭 조회 실패: {e}")
            return []
    
    def get_real_time_metrics(self) -> Dict[str, Any]:
        """실시간 메트릭 데이터"""
        current_metrics = self.get_current_metrics()
        return {
            'timestamp': current_metrics.timestamp,
            'cpu_percent': current_metrics.cpu_percent,
            'memory_percent': current_metrics.memory_percent,
            'disk_usage_percent': current_metrics.disk_usage_percent,
            'active_users': current_metrics.active_users,
            'response_time': current_metrics.response_time_avg
        }
    
    def get_real_time_alerts(self) -> List[Dict[str, Any]]:
        """실시간 알림 데이터"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = """
                SELECT alert_id, alert_type, severity, message, timestamp, resolved
                FROM performance_alerts 
                WHERE timestamp >= ? AND resolved = 0
                ORDER BY timestamp DESC
                LIMIT 10
                """
                
                start_time = time.time() - 3600  # 최근 1시간
                cursor.execute(query, (start_time,))
                
                alerts = []
                for row in cursor.fetchall():
                    alerts.append({
                        'id': row[0],
                        'type': row[1],
                        'severity': row[2],
                        'message': row[3],
                        'timestamp': row[4],
                        'resolved': bool(row[5])
                    })
                
                return alerts
        except Exception as e:
            logger.error(f"실시간 알림 조회 실패: {e}")
            return []
    
    def get_settings(self) -> Dict[str, Any]:
        """모니터링 설정 조회"""
        return {
            'real_time_enabled': self.running,
            'interval': 30,  # 기본값
            'retention_days': 30,
            'cpu_warning_threshold': self.thresholds.get('cpu_percent', 80),
            'cpu_critical_threshold': self.thresholds.get('cpu_percent', 90),
            'memory_warning_threshold': self.thresholds.get('memory_percent', 80),
            'memory_critical_threshold': self.thresholds.get('memory_percent', 90)
        }
    
    def update_settings(self, settings: Dict[str, Any]):
        """모니터링 설정 업데이트"""
        if 'cpu_warning_threshold' in settings:
            self.thresholds['cpu_percent'] = settings['cpu_warning_threshold']
        if 'memory_warning_threshold' in settings:
            self.thresholds['memory_percent'] = settings['memory_warning_threshold']
        
        logger.info(f"모니터링 설정 업데이트: {settings}")
    
    def _get_database_size(self) -> int:
        """데이터베이스 파일 크기 조회"""
        try:
            import os
            return os.path.getsize(self.db_path)
        except:
            return 0

# 전역 모니터링 인스턴스
monitor = RealTimeMonitor() 