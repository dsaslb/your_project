"""
⚡ 성능 최적화 시스템

실시간 성능 분석을 기반으로 자동 최적화를 수행하는 시스템입니다.
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
import psutil
import redis
import sqlite3
from pathlib import Path
import aiohttp
import gc
import threading
import queue

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OptimizationRule:
    """최적화 규칙"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    action: Callable[[Dict[str, Any]], None]
    priority: int = 1
    cooldown: int = 300  # 5분 쿨다운
    last_executed: Optional[datetime] = None

@dataclass
class OptimizationResult:
    """최적화 결과"""
    rule_name: str
    timestamp: datetime
    success: bool
    message: str
    performance_impact: Dict[str, float]
    execution_time: float

class PerformanceOptimizer:
    """성능 최적화 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        # 최적화 규칙 저장소
        self.optimization_rules: List[OptimizationRule] = []
        
        # 최적화 결과 저장소
        self.db_path = Path(config.get('db_path', 'optimization_results.db'))
        self.init_database()
        
        # 최적화 상태
        self.is_optimizing = False
        self.optimization_queue = queue.Queue()
        self.optimization_thread = None
        
        # 성능 기준선
        self.baseline_metrics = {}
        
        # 최적화 규칙 등록
        self.register_default_rules()
        
    def init_database(self):
        """SQLite 데이터베이스 초기화"""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 최적화 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS optimization_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rule_name TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                message TEXT NOT NULL,
                performance_impact TEXT,
                execution_time REAL
            )
        ''')
        
        # 성능 기준선 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS performance_baseline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                cpu_percent REAL,
                memory_percent REAL,
                response_time REAL,
                throughput REAL,
                error_rate REAL
            )
        ''')
        
        # 인덱스 생성
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opt_results_timestamp ON optimization_results(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_opt_results_rule ON optimization_results(rule_name)')
        
        conn.commit()
        conn.close()
        
    def register_default_rules(self):
        """기본 최적화 규칙 등록"""
        
        # 1. 메모리 최적화 규칙
        def memory_optimization_condition(metrics: Dict[str, Any]) -> bool:
            return (metrics.get('memory_percent', 0) > 85 and 
                   metrics.get('memory_percent', 0) < 95)
        
        def memory_optimization_action(metrics: Dict[str, Any]):
            logger.info("메모리 최적화 실행 중...")
            # 가비지 컬렉션 강제 실행
            collected = gc.collect()
            logger.info(f"가비지 컬렉션 완료: {collected}개 객체 정리")
            
            # Redis 캐시 정리
            try:
                # 오래된 캐시 키 삭제
                keys = self.redis_client.keys('cache:*')
                if len(keys) > 1000:  # 캐시가 너무 많으면 정리
                    # 가장 오래된 20% 삭제
                    keys_to_delete = keys[:len(keys) // 5]
                    if keys_to_delete:
                        self.redis_client.delete(*keys_to_delete)
                        logger.info(f"Redis 캐시 정리: {len(keys_to_delete)}개 키 삭제")
            except Exception as e:
                logger.error(f"Redis 캐시 정리 중 오류: {e}")
        
        self.add_optimization_rule(
            OptimizationRule(
                name="memory_optimization",
                condition=memory_optimization_condition,
                action=memory_optimization_action,
                priority=1,
                cooldown=600  # 10분
            )
        )
        
        # 2. CPU 최적화 규칙
        def cpu_optimization_condition(metrics: Dict[str, Any]) -> bool:
            return metrics.get('cpu_percent', 0) > 90
        
        def cpu_optimization_action(metrics: Dict[str, Any]):
            logger.info("CPU 최적화 실행 중...")
            # 백그라운드 작업 일시 중지
            try:
                # Redis에서 백그라운드 작업 상태 확인
                background_jobs = self.redis_client.keys('background:*')
                for job_key in background_jobs[:5]:  # 최대 5개 작업 일시 중지
                    self.redis_client.set(f"{job_key}:paused", "true", ex=300)
                    logger.info(f"백그라운드 작업 일시 중지: {job_key}")
            except Exception as e:
                logger.error(f"백그라운드 작업 중지 중 오류: {e}")
        
        self.add_optimization_rule(
            OptimizationRule(
                name="cpu_optimization",
                condition=cpu_optimization_condition,
                action=cpu_optimization_action,
                priority=2,
                cooldown=300  # 5분
            )
        )
        
        # 3. 응답 시간 최적화 규칙
        def response_time_optimization_condition(metrics: Dict[str, Any]) -> bool:
            return metrics.get('response_time', 0) > 3.0
        
        def response_time_optimization_action(metrics: Dict[str, Any]):
            logger.info("응답 시간 최적화 실행 중...")
            # 캐시 워밍업
            try:
                # 자주 사용되는 데이터를 캐시에 미리 로드
                popular_keys = self.redis_client.keys('popular:*')
                if len(popular_keys) < 100:  # 캐시가 부족하면 워밍업
                    # 예시: 사용자 세션 데이터 캐시
                    self.redis_client.setex('cache:warmup:users', 3600, 'warmed')
                    logger.info("캐시 워밍업 완료")
            except Exception as e:
                logger.error(f"캐시 워밍업 중 오류: {e}")
        
        self.add_optimization_rule(
            OptimizationRule(
                name="response_time_optimization",
                condition=response_time_optimization_condition,
                action=response_time_optimization_action,
                priority=3,
                cooldown=180  # 3분
            )
        )
        
        # 4. 오류율 최적화 규칙
        def error_rate_optimization_condition(metrics: Dict[str, Any]) -> bool:
            return metrics.get('error_rate', 0) > 10.0
        
        def error_rate_optimization_action(metrics: Dict[str, Any]):
            logger.info("오류율 최적화 실행 중...")
            # 서킷 브레이커 활성화
            try:
                # 오류율이 높은 서비스에 서킷 브레이커 적용
                self.redis_client.setex('circuit_breaker:active', 300, 'true')
                logger.info("서킷 브레이커 활성화")
            except Exception as e:
                logger.error(f"서킷 브레이커 활성화 중 오류: {e}")
        
        self.add_optimization_rule(
            OptimizationRule(
                name="error_rate_optimization",
                condition=error_rate_optimization_condition,
                action=error_rate_optimization_action,
                priority=4,
                cooldown=120  # 2분
            )
        )
        
        # 5. 디스크 공간 최적화 규칙
        def disk_optimization_condition(metrics: Dict[str, Any]) -> bool:
            return metrics.get('disk_usage_percent', 0) > 90
        
        def disk_optimization_action(metrics: Dict[str, Any]):
            logger.info("디스크 공간 최적화 실행 중...")
            # 로그 파일 정리
            try:
                # 오래된 로그 파일 삭제
                log_dir = Path("logs")
                if log_dir.exists():
                    current_time = time.time()
                    for log_file in log_dir.glob("*.log"):
                        # 7일 이상 된 로그 파일 삭제
                        if current_time - log_file.stat().st_mtime > 7 * 24 * 3600:
                            log_file.unlink()
                            logger.info(f"오래된 로그 파일 삭제: {log_file}")
            except Exception as e:
                logger.error(f"로그 파일 정리 중 오류: {e}")
        
        self.add_optimization_rule(
            OptimizationRule(
                name="disk_optimization",
                condition=disk_optimization_condition,
                action=disk_optimization_action,
                priority=5,
                cooldown=3600  # 1시간
            )
        )
        
    def add_optimization_rule(self, rule: OptimizationRule):
        """최적화 규칙 추가"""
        self.optimization_rules.append(rule)
        # 우선순위별 정렬
        self.optimization_rules.sort(key=lambda x: x.priority)
        logger.info(f"최적화 규칙 추가: {rule.name}")
        
    async def start_optimization(self):
        """최적화 시작"""
        if self.is_optimizing:
            logger.warning("최적화가 이미 실행 중입니다.")
            return
            
        self.is_optimizing = True
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        logger.info("성능 최적화를 시작합니다.")
        
    async def stop_optimization(self):
        """최적화 중지"""
        self.is_optimizing = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("성능 최적화를 중지합니다.")
        
    def _optimization_loop(self):
        """최적화 루프"""
        while self.is_optimizing:
            try:
                # 최적화 큐에서 메트릭 가져오기
                try:
                    metrics = self.optimization_queue.get(timeout=30)
                    self._evaluate_and_optimize(metrics)
                except queue.Empty:
                    continue
                    
            except Exception as e:
                logger.error(f"최적화 루프 중 오류: {e}")
                time.sleep(5)
                
    def _evaluate_and_optimize(self, metrics: Dict[str, Any]):
        """메트릭 평가 및 최적화 실행"""
        current_time = datetime.now()
        
        for rule in self.optimization_rules:
            # 쿨다운 확인
            if (rule.last_executed and 
                (current_time - rule.last_executed).total_seconds() < rule.cooldown):
                continue
                
            # 조건 확인
            if rule.condition(metrics):
                logger.info(f"최적화 규칙 실행: {rule.name}")
                
                # 최적화 실행
                start_time = time.time()
                try:
                    rule.action(metrics)
                    execution_time = time.time() - start_time
                    
                    # 성능 영향 측정
                    performance_impact = self._measure_performance_impact(metrics)
                    
                    # 결과 저장
                    result = OptimizationResult(
                        rule_name=rule.name,
                        timestamp=current_time,
                        success=True,
                        message=f"최적화 성공: {rule.name}",
                        performance_impact=performance_impact,
                        execution_time=execution_time
                    )
                    
                    self._save_optimization_result(result)
                    rule.last_executed = current_time
                    
                    logger.info(f"최적화 완료: {rule.name} (실행시간: {execution_time:.2f}초)")
                    
                except Exception as e:
                    execution_time = time.time() - start_time
                    logger.error(f"최적화 실패: {rule.name} - {e}")
                    
                    result = OptimizationResult(
                        rule_name=rule.name,
                        timestamp=current_time,
                        success=False,
                        message=f"최적화 실패: {e}",
                        performance_impact={},
                        execution_time=execution_time
                    )
                    
                    self._save_optimization_result(result)
                    
    def _measure_performance_impact(self, before_metrics: Dict[str, Any]) -> Dict[str, float]:
        """최적화 전후 성능 영향 측정"""
        try:
            # 최적화 후 메트릭 수집 (1분 후)
            time.sleep(60)
            
            after_metrics = self._collect_current_metrics()
            
            impact = {}
            for key in ['cpu_percent', 'memory_percent', 'response_time', 'error_rate']:
                if key in before_metrics and key in after_metrics:
                    before_val = before_metrics[key]
                    after_val = after_metrics[key]
                    if before_val > 0:
                        impact[key] = ((after_val - before_val) / before_val) * 100
                    else:
                        impact[key] = 0.0
                        
            return impact
            
        except Exception as e:
            logger.error(f"성능 영향 측정 중 오류: {e}")
            return {}
            
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # 디스크 사용률
            disk = psutil.disk_usage('/')
            disk_usage_percent = (disk.used / disk.total) * 100
            
            # Redis에서 애플리케이션 메트릭 가져오기
            response_time = float(self.redis_client.get('app:response_time') or 0)
            error_rate = float(self.redis_client.get('app:error_rate') or 0)
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_usage_percent': disk_usage_percent,
                'response_time': response_time,
                'error_rate': error_rate
            }
            
        except Exception as e:
            logger.error(f"현재 메트릭 수집 중 오류: {e}")
            return {}
            
    def _save_optimization_result(self, result: OptimizationResult):
        """최적화 결과 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO optimization_results 
                (timestamp, rule_name, success, message, performance_impact, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                result.timestamp.isoformat(),
                result.rule_name,
                result.success,
                result.message,
                json.dumps(result.performance_impact),
                result.execution_time
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"최적화 결과 저장 중 오류: {e}")
            
    async def optimize_performance(self, metrics: Dict[str, Any]):
        """성능 최적화 실행"""
        # 최적화 큐에 메트릭 추가
        self.optimization_queue.put(metrics)
        
    async def set_performance_baseline(self, metrics: Dict[str, Any]):
        """성능 기준선 설정"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO performance_baseline 
                (timestamp, cpu_percent, memory_percent, response_time, throughput, error_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                metrics.get('cpu_percent', 0),
                metrics.get('memory_percent', 0),
                metrics.get('response_time', 0),
                metrics.get('throughput', 0),
                metrics.get('error_rate', 0)
            ))
            
            conn.commit()
            conn.close()
            
            self.baseline_metrics = metrics
            logger.info("성능 기준선이 설정되었습니다.")
            
        except Exception as e:
            logger.error(f"성능 기준선 설정 중 오류: {e}")
            
    async def get_optimization_summary(self, hours: int = 24) -> Dict[str, Any]:
        """최적화 요약 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 시간 범위 계산
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            cursor.execute('''
                SELECT 
                    rule_name,
                    COUNT(*) as execution_count,
                    AVG(CASE WHEN success THEN 1 ELSE 0 END) as success_rate,
                    AVG(execution_time) as avg_execution_time,
                    AVG(CAST(performance_impact AS REAL)) as avg_impact
                FROM optimization_results
                WHERE timestamp BETWEEN ? AND ?
                GROUP BY rule_name
            ''', (start_time.isoformat(), end_time.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            summary = {
                'period_hours': hours,
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'rules': []
            }
            
            for row in rows:
                summary['rules'].append({
                    'rule_name': row[0],
                    'execution_count': row[1],
                    'success_rate': round(row[2] * 100, 2),
                    'avg_execution_time': round(row[3], 3) if row[3] else 0,
                    'avg_impact': round(row[4], 2) if row[4] else 0
                })
                
            return summary
            
        except Exception as e:
            logger.error(f"최적화 요약 조회 중 오류: {e}")
            return {}
            
    async def get_recent_optimizations(self, limit: int = 20) -> List[Dict[str, Any]]:
        """최근 최적화 결과 조회"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, rule_name, success, message, performance_impact, execution_time
                FROM optimization_results
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            conn.close()
            
            optimizations = []
            for row in rows:
                optimizations.append({
                    'timestamp': row[0],
                    'rule_name': row[1],
                    'success': bool(row[2]),
                    'message': row[3],
                    'performance_impact': json.loads(row[4]) if row[4] else {},
                    'execution_time': row[5]
                })
                
            return optimizations
            
        except Exception as e:
            logger.error(f"최근 최적화 결과 조회 중 오류: {e}")
            return []
            
    def get_optimization_rules(self) -> List[Dict[str, Any]]:
        """등록된 최적화 규칙 조회"""
        rules = []
        for rule in self.optimization_rules:
            rules.append({
                'name': rule.name,
                'priority': rule.priority,
                'cooldown': rule.cooldown,
                'last_executed': rule.last_executed.isoformat() if rule.last_executed else None
            })
        return rules

# 성능 최적화 인스턴스
performance_optimizer = None

async def start_performance_optimization(config: Dict[str, Any]):
    """성능 최적화 시작"""
    global performance_optimizer
    
    if performance_optimizer is None:
        performance_optimizer = PerformanceOptimizer(config)
        
    await performance_optimizer.start_optimization()

async def stop_performance_optimization():
    """성능 최적화 중지"""
    global performance_optimizer
    
    if performance_optimizer:
        await performance_optimizer.stop_optimization()

def get_performance_optimizer() -> Optional[PerformanceOptimizer]:
    """성능 최적화 인스턴스 반환"""
    return performance_optimizer 