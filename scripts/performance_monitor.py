# -*- coding: utf-8 -*-
"""
실시간 성능 모니터링 및 알림 시스템
시스템 성능을 지속적으로 모니터링하고 임계값 초과 시 알림을 발송
"""

import psutil
import time
import json
import logging
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/performance_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """실시간 성능 모니터링 클래스"""
    
    def __init__(self):
        self.monitoring = False
        self.monitor_thread = None
        self.alert_thresholds = {
            'cpu_percent': 80,  # CPU 사용률 80% 초과 시 알림
            'memory_percent': 85,  # 메모리 사용률 85% 초과 시 알림
            'disk_percent': 90,  # 디스크 사용률 90% 초과 시 알림
            'response_time': 5,  # 응답시간 5초 초과 시 알림
        }
        self.alert_history = []
        self.performance_history = []
        self.max_history_size = 1000
        
    def start_monitoring(self):
        """성능 모니터링 시작"""
        if self.monitoring:
            logger.info("성능 모니터링이 이미 실행 중입니다.")
            return
            
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("성능 모니터링이 시작되었습니다.")
        
    def stop_monitoring(self):
        """성능 모니터링 중지"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("성능 모니터링이 중지되었습니다.")
        
    def _monitor_loop(self):
        """모니터링 루프"""
        while self.monitoring:
            try:
                # 시스템 성능 데이터 수집
                performance_data = self._collect_performance_data()
                
                # 성능 데이터 저장
                self._save_performance_data(performance_data)
                
                # 임계값 체크 및 알림
                self._check_thresholds(performance_data)
                
                # 30초 대기
                time.sleep(30)
                
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(60)  # 오류 발생 시 1분 대기
                
    def _collect_performance_data(self) -> Dict[str, Any]:
        """시스템 성능 데이터 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # 네트워크 사용량
            network = psutil.net_io_counters()
            
            # 프로세스 수
            process_count = len(psutil.pids())
            
            # 백엔드 서버 응답시간 체크
            response_time = self._check_backend_response()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'memory_available_gb': round(memory_available_gb, 2),
                'disk_percent': disk_percent,
                'disk_free_gb': round(disk_free_gb, 2),
                'network_bytes_sent': network.bytes_sent,
                'network_bytes_recv': network.bytes_recv,
                'process_count': process_count,
                'response_time': response_time,
                'status': 'healthy' if response_time < 5 else 'warning'
            }
            
        except Exception as e:
            logger.error(f"성능 데이터 수집 오류: {e}")
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
            
    def _check_backend_response(self) -> float:
        """백엔드 서버 응답시간 체크"""
        try:
            import requests
            start_time = time.time()
            response = requests.get('http://localhost:5000/health', timeout=10)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return round(response_time, 3)
            else:
                return 999.0  # 오류 시 큰 값 반환
                
        except Exception as e:
            logger.error(f"백엔드 응답시간 체크 오류: {e}")
            return 999.0
            
    def _save_performance_data(self, data: Dict[str, Any]):
        """성능 데이터 저장"""
        try:
            # 메모리에 저장
            self.performance_history.append(data)
            
            # 최대 크기 제한
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
                
            # 데이터베이스에 저장
            self._save_to_database(data)
            
        except Exception as e:
            logger.error(f"성능 데이터 저장 오류: {e}")
            
    def _save_to_database(self, data: Dict[str, Any]):
        """데이터베이스에 성능 데이터 저장"""
        try:
            conn = sqlite3.connect('data/performance_metrics.db')
            cursor = conn.cursor()
            
            # 테이블 생성 (없는 경우)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    cpu_percent REAL,
                    memory_percent REAL,
                    memory_available_gb REAL,
                    disk_percent REAL,
                    disk_free_gb REAL,
                    network_bytes_sent INTEGER,
                    network_bytes_recv INTEGER,
                    process_count INTEGER,
                    response_time REAL,
                    status TEXT
                )
            ''')
            
            # 데이터 삽입
            cursor.execute('''
                INSERT INTO performance_metrics (
                    timestamp, cpu_percent, memory_percent, memory_available_gb,
                    disk_percent, disk_free_gb, network_bytes_sent, network_bytes_recv,
                    process_count, response_time, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('timestamp'),
                data.get('cpu_percent'),
                data.get('memory_percent'),
                data.get('memory_available_gb'),
                data.get('disk_percent'),
                data.get('disk_free_gb'),
                data.get('network_bytes_sent'),
                data.get('network_bytes_recv'),
                data.get('process_count'),
                data.get('response_time'),
                data.get('status')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"데이터베이스 저장 오류: {e}")
            
    def _check_thresholds(self, data: Dict[str, Any]):
        """임계값 체크 및 알림"""
        alerts = []
        
        # CPU 사용률 체크
        if data.get('cpu_percent', 0) > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'cpu_high',
                'message': f"CPU 사용률이 높습니다: {data.get('cpu_percent')}%",
                'value': data.get('cpu_percent'),
                'threshold': self.alert_thresholds['cpu_percent']
            })
            
        # 메모리 사용률 체크
        if data.get('memory_percent', 0) > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'memory_high',
                'message': f"메모리 사용률이 높습니다: {data.get('memory_percent')}%",
                'value': data.get('memory_percent'),
                'threshold': self.alert_thresholds['memory_percent']
            })
            
        # 디스크 사용률 체크
        if data.get('disk_percent', 0) > self.alert_thresholds['disk_percent']:
            alerts.append({
                'type': 'disk_high',
                'message': f"디스크 사용률이 높습니다: {data.get('disk_percent')}%",
                'value': data.get('disk_percent'),
                'threshold': self.alert_thresholds['disk_percent']
            })
            
        # 응답시간 체크
        if data.get('response_time', 0) > self.alert_thresholds['response_time']:
            alerts.append({
                'type': 'response_slow',
                'message': f"백엔드 응답시간이 느립니다: {data.get('response_time')}초",
                'value': data.get('response_time'),
                'threshold': self.alert_thresholds['response_time']
            })
            
        # 알림 발송
        for alert in alerts:
            self._send_alert(alert)
            
    def _send_alert(self, alert: Dict[str, Any]):
        """알림 발송"""
        try:
            alert_data = {
                'timestamp': datetime.now().isoformat(),
                'alert_type': alert['type'],
                'message': alert['message'],
                'value': alert['value'],
                'threshold': alert['threshold'],
                'severity': 'warning'
            }
            
            # 알림 히스토리에 저장
            self.alert_history.append(alert_data)
            
            # 최대 크기 제한
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-100:]
                
            # 로그에 기록
            logger.warning(f"성능 알림: {alert['message']}")
            
            # 파일에 저장
            self._save_alert_to_file(alert_data)
            
            # 웹훅이나 이메일로 알림 발송 (필요시 구현)
            # self._send_webhook_alert(alert_data)
            
        except Exception as e:
            logger.error(f"알림 발송 오류: {e}")
            
    def _save_alert_to_file(self, alert_data: Dict[str, Any]):
        """알림을 파일에 저장"""
        try:
            alert_file = 'logs/performance_alerts.json'
            
            # 기존 알림 로드
            alerts = []
            if os.path.exists(alert_file):
                with open(alert_file, 'r', encoding='utf-8') as f:
                    alerts = json.load(f)
                    
            # 새 알림 추가
            alerts.append(alert_data)
            
            # 최대 100개만 유지
            if len(alerts) > 100:
                alerts = alerts[-100:]
                
            # 파일에 저장
            with open(alert_file, 'w', encoding='utf-8') as f:
                json.dump(alerts, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"알림 파일 저장 오류: {e}")
            
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보 반환"""
        try:
            if not self.performance_history:
                return {'message': '성능 데이터가 없습니다.'}
                
            recent_data = self.performance_history[-10:]  # 최근 10개 데이터
            
            # 평균값 계산
            cpu_avg = sum(d.get('cpu_percent', 0) for d in recent_data) / len(recent_data)
            memory_avg = sum(d.get('memory_percent', 0) for d in recent_data) / len(recent_data)
            disk_avg = sum(d.get('disk_percent', 0) for d in recent_data) / len(recent_data)
            response_avg = sum(d.get('response_time', 0) for d in recent_data) / len(recent_data)
            
            # 최근 알림 수
            recent_alerts = len([a for a in self.alert_history 
                               if datetime.fromisoformat(a['timestamp']) > datetime.now() - timedelta(hours=1)])
            
            return {
                'current_status': 'monitoring' if self.monitoring else 'stopped',
                'cpu_average': round(cpu_avg, 2),
                'memory_average': round(memory_avg, 2),
                'disk_average': round(disk_avg, 2),
                'response_average': round(response_avg, 3),
                'recent_alerts': recent_alerts,
                'total_alerts': len(self.alert_history),
                'data_points': len(self.performance_history)
            }
            
        except Exception as e:
            logger.error(f"성능 요약 생성 오류: {e}")
            return {'error': str(e)}
            
    def get_alert_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """알림 히스토리 반환"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=hours)
            recent_alerts = [
                alert for alert in self.alert_history
                if datetime.fromisoformat(alert['timestamp']) > cutoff_time
            ]
            return recent_alerts
            
        except Exception as e:
            logger.error(f"알림 히스토리 조회 오류: {e}")
            return []


# 전역 인스턴스
performance_monitor = PerformanceMonitor()


def start_performance_monitoring():
    """성능 모니터링 시작"""
    performance_monitor.start_monitoring()


def stop_performance_monitoring():
    """성능 모니터링 중지"""
    performance_monitor.stop_monitoring()


def get_performance_status():
    """성능 모니터링 상태 반환"""
    return performance_monitor.get_performance_summary()


if __name__ == "__main__":
    # 테스트 실행
    print("성능 모니터링 시작...")
    start_performance_monitoring()
    
    try:
        # 5분간 모니터링
        time.sleep(300)
    except KeyboardInterrupt:
        print("\n모니터링 중지...")
    finally:
        stop_performance_monitoring()
        print("성능 모니터링 완료.")
