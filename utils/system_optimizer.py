import psutil
import sqlite3
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import threading
import time

class SystemOptimizer:
    def __init__(self, db_path: str = "app.db"):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self.optimization_history = []
        
    def analyze_database_performance(self) -> Dict[str, Any]:
        """데이터베이스 성능 분석"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 테이블 크기 분석
            cursor.execute("""
                SELECT name, sql FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            """)
            tables = cursor.fetchall()
            
            table_stats = {}
            total_size = 0
            
            for table_name, _ in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                # 대략적인 테이블 크기 계산
                estimated_size = row_count * len(columns) * 100  # 바이트 단위 추정
                total_size += estimated_size
                
                table_stats[table_name] = {
                    'row_count': row_count,
                    'column_count': len(columns),
                    'estimated_size_bytes': estimated_size
                }
            
            # 인덱스 분석
            cursor.execute("PRAGMA index_list")
            indexes = cursor.fetchall()
            
            # 쿼리 성능 분석
            cursor.execute("PRAGMA compile_options")
            compile_options = cursor.fetchall()
            
            conn.close()
            
            return {
                'table_stats': table_stats,
                'total_database_size_bytes': total_size,
                'index_count': len(indexes),
                'compile_options': [opt[0] for opt in compile_options],
                'optimization_recommendations': self._generate_db_recommendations(table_stats, indexes)
            }
            
        except Exception as e:
            self.logger.error(f"데이터베이스 성능 분석 중 오류: {e}")
            return {'error': str(e)}
    
    def _generate_db_recommendations(self, table_stats: Dict, indexes: List) -> List[str]:
        """데이터베이스 최적화 권장사항 생성"""
        recommendations = []
        
        for table_name, stats in table_stats.items():
            if stats['row_count'] > 1000:
                recommendations.append(f"테이블 '{table_name}'에 인덱스 추가 고려 (행 수: {stats['row_count']})")
            
            if stats['column_count'] > 10:
                recommendations.append(f"테이블 '{table_name}'의 컬럼 수가 많음 ({stats['column_count']}개), 정규화 고려")
        
        if len(indexes) < len(table_stats):
            recommendations.append("더 많은 인덱스 추가로 쿼리 성능 향상 가능")
        
        return recommendations
    
    def optimize_database(self) -> Dict[str, Any]:
        """데이터베이스 최적화 실행"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # VACUUM 실행으로 데이터베이스 최적화
            cursor.execute("VACUUM")
            
            # ANALYZE 실행으로 통계 정보 업데이트
            cursor.execute("ANALYZE")
            
            # WAL 모드 활성화 (성능 향상)
            cursor.execute("PRAGMA journal_mode=WAL")
            
            # 캐시 크기 증가
            cursor.execute("PRAGMA cache_size=10000")
            
            # 동기화 모드 최적화
            cursor.execute("PRAGMA synchronous=NORMAL")
            
            conn.commit()
            conn.close()
            
            optimization_result = {
                'status': 'success',
                'message': '데이터베이스 최적화 완료',
                'timestamp': datetime.now().isoformat(),
                'optimizations_applied': [
                    'VACUUM 실행',
                    'ANALYZE 실행',
                    'WAL 모드 활성화',
                    '캐시 크기 증가',
                    '동기화 모드 최적화'
                ]
            }
            
            self.optimization_history.append(optimization_result)
            return optimization_result
            
        except Exception as e:
            self.logger.error(f"데이터베이스 최적화 중 오류: {e}")
            return {'error': str(e)}
    
    def monitor_system_resources(self) -> Dict[str, Any]:
        """시스템 리소스 모니터링"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            
            # 네트워크 사용률
            network = psutil.net_io_counters()
            
            # 프로세스 정보
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # 상위 프로세스 정렬
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            top_processes = processes[:10]
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'count': cpu_count,
                    'status': 'normal' if cpu_percent < 80 else 'warning' if cpu_percent < 95 else 'critical'
                },
                'memory': {
                    'total': memory.total,
                    'available': memory.available,
                    'percent': memory.percent,
                    'status': 'normal' if memory.percent < 80 else 'warning' if memory.percent < 95 else 'critical'
                },
                'disk': {
                    'total': disk.total,
                    'used': disk.used,
                    'free': disk.free,
                    'percent': (disk.used / disk.total) * 100,
                    'status': 'normal' if (disk.used / disk.total) * 100 < 80 else 'warning'
                },
                'network': {
                    'bytes_sent': network.bytes_sent,
                    'bytes_recv': network.bytes_recv,
                    'packets_sent': network.packets_sent,
                    'packets_recv': network.packets_recv
                },
                'top_processes': top_processes,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"시스템 리소스 모니터링 중 오류: {e}")
            return {'error': str(e)}
    
    def generate_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        try:
            db_performance = self.analyze_database_performance()
            system_resources = self.monitor_system_resources()
            
            # 성능 점수 계산
            performance_score = self._calculate_performance_score(system_resources, db_performance)
            
            # 권장사항 생성
            recommendations = self._generate_system_recommendations(system_resources, db_performance)
            
            return {
                'performance_score': performance_score,
                'database_performance': db_performance,
                'system_resources': system_resources,
                'recommendations': recommendations,
                'optimization_history': self.optimization_history[-5:],  # 최근 5개
                'report_generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"성능 리포트 생성 중 오류: {e}")
            return {'error': str(e)}
    
    def _calculate_performance_score(self, system_resources: Dict, db_performance: Dict) -> int:
        """성능 점수 계산 (0-100)"""
        score = 100
        
        # CPU 점수
        cpu_percent = system_resources.get('cpu', {}).get('percent', 0)
        if cpu_percent > 80:
            score -= 20
        elif cpu_percent > 60:
            score -= 10
        
        # 메모리 점수
        memory_percent = system_resources.get('memory', {}).get('percent', 0)
        if memory_percent > 80:
            score -= 20
        elif memory_percent > 60:
            score -= 10
        
        # 디스크 점수
        disk_percent = system_resources.get('disk', {}).get('percent', 0)
        if disk_percent > 80:
            score -= 15
        elif disk_percent > 60:
            score -= 5
        
        return max(0, score)
    
    def _generate_system_recommendations(self, system_resources: Dict, db_performance: Dict) -> List[str]:
        """시스템 최적화 권장사항 생성"""
        recommendations = []
        
        # CPU 권장사항
        cpu_percent = system_resources.get('cpu', {}).get('percent', 0)
        if cpu_percent > 80:
            recommendations.append("CPU 사용률이 높습니다. 프로세스 최적화 또는 하드웨어 업그레이드 고려")
        
        # 메모리 권장사항
        memory_percent = system_resources.get('memory', {}).get('percent', 0)
        if memory_percent > 80:
            recommendations.append("메모리 사용률이 높습니다. 메모리 정리 또는 증설 고려")
        
        # 디스크 권장사항
        disk_percent = system_resources.get('disk', {}).get('percent', 0)
        if disk_percent > 80:
            recommendations.append("디스크 사용률이 높습니다. 불필요한 파일 정리 고려")
        
        # 데이터베이스 권장사항
        if 'optimization_recommendations' in db_performance:
            recommendations.extend(db_performance['optimization_recommendations'])
        
        return recommendations
    
    def start_continuous_monitoring(self, interval_seconds: int = 60):
        """연속 모니터링 시작"""
        def monitor_loop():
            while True:
                try:
                    report = self.generate_performance_report()
                    
                    # 성능 점수가 낮으면 경고 로그
                    if report.get('performance_score', 100) < 70:
                        self.logger.warning(f"시스템 성능 점수 낮음: {report['performance_score']}")
                    
                    # 임계값 초과 시 알림
                    system_resources = report.get('system_resources', {})
                    cpu_percent = system_resources.get('cpu', {}).get('percent', 0)
                    memory_percent = system_resources.get('memory', {}).get('percent', 0)
                    
                    if cpu_percent > 90 or memory_percent > 90:
                        self.logger.critical(f"시스템 리소스 임계값 초과 - CPU: {cpu_percent}%, Memory: {memory_percent}%")
                    
                    time.sleep(interval_seconds)
                    
                except Exception as e:
                    self.logger.error(f"연속 모니터링 중 오류: {e}")
                    time.sleep(interval_seconds)
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        return monitor_thread

# 전역 최적화기 인스턴스
system_optimizer = SystemOptimizer() 