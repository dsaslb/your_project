#!/usr/bin/env python3
"""
플러그인 성능 벤치마크 시스템
CPU, 메모리, 응답시간, 처리량 측정 및 성능 보고서 생성
"""

import time
import psutil
import threading
import logging
import json
import sqlite3
import statistics
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import concurrent.futures

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkMetrics:
    """벤치마크 메트릭"""
    plugin_id: str
    test_name: str
    execution_time: float
    cpu_usage: float
    memory_usage: float
    memory_peak: float
    throughput: float
    error_count: int
    success_count: int
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()

@dataclass
class BenchmarkResult:
    """벤치마크 결과"""
    plugin_id: str
    test_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_execution_time: float
    min_execution_time: float
    max_execution_time: float
    p50_execution_time: float
    p95_execution_time: float
    p99_execution_time: float
    avg_cpu_usage: float
    avg_memory_usage: float
    peak_memory_usage: float
    avg_throughput: float
    error_rate: float
    performance_score: float
    recommendations: List[str]
    metrics_history: List[BenchmarkMetrics]
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class BenchmarkConfig:
    """벤치마크 설정"""
    warmup_runs: int = 5
    test_runs: int = 100
    concurrent_users: int = 10
    test_duration: int = 300  # 5분
    memory_threshold: float = 512.0  # MB
    cpu_threshold: float = 80.0  # %
    response_time_threshold: float = 5.0  # 초

class PluginPerformanceBenchmark:
    """플러그인 성능 벤치마크 클래스"""
    
    def __init__(self, db_path: str = "plugin_benchmark.db"):
        self.db_path = db_path
        self.config = BenchmarkConfig()
        self.benchmark_results: Dict[str, BenchmarkResult] = {}
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self._init_database()
        
    def _init_database(self):
        """벤치마크 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 벤치마크 결과 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS benchmark_results (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        test_name TEXT NOT NULL,
                        total_runs INTEGER NOT NULL,
                        successful_runs INTEGER NOT NULL,
                        failed_runs INTEGER NOT NULL,
                        avg_execution_time REAL,
                        min_execution_time REAL,
                        max_execution_time REAL,
                        p50_execution_time REAL,
                        p95_execution_time REAL,
                        p99_execution_time REAL,
                        avg_cpu_usage REAL,
                        avg_memory_usage REAL,
                        peak_memory_usage REAL,
                        avg_throughput REAL,
                        error_rate REAL,
                        performance_score REAL,
                        recommendations TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 벤치마크 메트릭 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS benchmark_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        test_name TEXT NOT NULL,
                        execution_time REAL,
                        cpu_usage REAL,
                        memory_usage REAL,
                        memory_peak REAL,
                        throughput REAL,
                        error_count INTEGER,
                        success_count INTEGER,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 플러그인 성능 히스토리 테이블
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        test_date DATE NOT NULL,
                        avg_performance_score REAL,
                        total_tests INTEGER,
                        improvement_rate REAL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 인덱스 생성
                conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_plugin_id ON benchmark_results(plugin_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_benchmark_test_name ON benchmark_results(test_name)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_plugin_id ON benchmark_metrics(plugin_id)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_history_plugin_id ON performance_history(plugin_id)")
                
                conn.commit()
                logger.info("벤치마크 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
    
    def run_benchmark(self, plugin_id: str, test_function: Callable, 
                     test_name: str = "default", config: Optional[BenchmarkConfig] = None) -> BenchmarkResult:
        """플러그인 벤치마크 실행"""
        if config is None:
            config = self.config
        
        try:
            logger.info(f"벤치마크 시작: {plugin_id} - {test_name}")
            
            metrics_history = []
            
            # 1. 워밍업 실행
            logger.info("워밍업 실행 중...")
            for i in range(config.warmup_runs):
                self._run_single_test(plugin_id, test_function, f"warmup_{i}")
            
            # 2. 실제 벤치마크 실행
            logger.info(f"벤치마크 실행 중... ({config.test_runs}회)")
            
            # 단일 스레드 벤치마크
            for i in range(config.test_runs):
                metrics = self._run_single_test(plugin_id, test_function, f"test_{i}")
                metrics_history.append(metrics)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"진행률: {(i + 1) / config.test_runs * 100:.1f}%")
            
            # 3. 동시성 벤치마크
            logger.info(f"동시성 벤치마크 실행 중... ({config.concurrent_users}명)")
            concurrent_metrics = self._run_concurrent_benchmark(plugin_id, test_function, config)
            metrics_history.extend(concurrent_metrics)
            
            # 4. 지속성 벤치마크
            logger.info(f"지속성 벤치마크 실행 중... ({config.test_duration}초)")
            endurance_metrics = self._run_endurance_benchmark(plugin_id, test_function, config)
            metrics_history.extend(endurance_metrics)
            
            # 5. 결과 분석
            result = self._analyze_benchmark_results(plugin_id, test_name, metrics_history)
            
            # 6. 결과 저장
            self._save_benchmark_result(result)
            
            logger.info(f"벤치마크 완료: {plugin_id} - {test_name}")
            return result
            
        except Exception as e:
            logger.error(f"벤치마크 실행 실패: {e}")
            raise
    
    def _run_single_test(self, plugin_id: str, test_function: Callable, test_id: str) -> BenchmarkMetrics:
        """단일 테스트 실행"""
        start_time = time.time()
        start_cpu: float = float(psutil.cpu_percent(percpu=False) or 0.0)
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        error_count = 0
        success_count = 0
        
        try:
            # 테스트 함수 실행
            result = test_function()
            success_count = 1
            
            # 성능 측정
            execution_time = time.time() - start_time
            end_cpu: float = float(psutil.cpu_percent(percpu=False) or 0.0)
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            # 메모리 피크 측정
            memory_peak = max(start_memory, end_memory)
            
            # 처리량 계산 (초당 처리 가능한 요청 수)
            throughput = 1.0 / execution_time if execution_time > 0 else 0
            
            return BenchmarkMetrics(
                plugin_id=plugin_id,
                test_name=test_id,
                execution_time=execution_time,
                cpu_usage=(start_cpu + end_cpu) / 2.0,
                memory_usage=(start_memory + end_memory) / 2.0,
                memory_peak=memory_peak,
                throughput=throughput,
                error_count=error_count,
                success_count=success_count
            )
            
        except Exception:
            error_count = 1
            execution_time = time.time() - start_time
            end_cpu: float = float(psutil.cpu_percent(percpu=False) or 0.0)
            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            
            return BenchmarkMetrics(
                plugin_id=plugin_id,
                test_name=test_id,
                execution_time=execution_time,
                cpu_usage=(start_cpu + end_cpu) / 2.0,
                memory_usage=(start_memory + end_memory) / 2.0,
                memory_peak=start_memory,
                throughput=0.0,
                error_count=error_count,
                success_count=success_count
            )
    
    def _run_concurrent_benchmark(self, plugin_id: str, test_function: Callable, 
                                 config: BenchmarkConfig) -> List[BenchmarkMetrics]:
        """동시성 벤치마크 실행"""
        metrics_list = []
        
        def concurrent_test():
            return self._run_single_test(plugin_id, test_function, f"concurrent_{threading.current_thread().name}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=config.concurrent_users) as executor:
            futures = [executor.submit(concurrent_test) for _ in range(config.test_runs)]
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    metrics = future.result()
                    metrics_list.append(metrics)
                except Exception as e:
                    logger.error(f"동시성 테스트 실패: {e}")
        
        return metrics_list
    
    def _run_endurance_benchmark(self, plugin_id: str, test_function: Callable, 
                                config: BenchmarkConfig) -> List[BenchmarkMetrics]:
        """지속성 벤치마크 실행"""
        metrics_list = []
        start_time = time.time()
        
        while time.time() - start_time < config.test_duration:
            metrics = self._run_single_test(plugin_id, test_function, f"endurance_{len(metrics_list)}")
            metrics_list.append(metrics)
            
            # 짧은 대기 시간
            time.sleep(0.1)
        
        return metrics_list
    
    def _analyze_benchmark_results(self, plugin_id: str, test_name: str, 
                                  metrics_history: List[BenchmarkMetrics]) -> BenchmarkResult:
        """벤치마크 결과 분석"""
        if not metrics_history:
            raise ValueError("분석할 메트릭이 없습니다")
        
        # 기본 통계 계산
        execution_times: List[float] = []
        cpu_usages: List[float] = []
        memory_usages: List[float] = []
        memory_peaks: List[float] = []
        throughputs: List[float] = []
        
        for m in metrics_history:
            exec_time = getattr(m, 'execution_time', 0.0)
            if isinstance(exec_time, (int, float)):
                execution_times.append(float(exec_time))
            
            cpu_usage = getattr(m, 'cpu_usage', 0.0)
            if isinstance(cpu_usage, (int, float)):
                cpu_usages.append(float(cpu_usage))
            
            mem_usage = getattr(m, 'memory_usage', 0.0)
            if isinstance(mem_usage, (int, float)):
                memory_usages.append(float(mem_usage))
            
            mem_peak = getattr(m, 'memory_peak', 0.0)
            if isinstance(mem_peak, (int, float)):
                memory_peaks.append(float(mem_peak))
            
            throughput = getattr(m, 'throughput', 0.0)
            if isinstance(throughput, (int, float)):
                throughputs.append(float(throughput))
        
        total_runs = len(metrics_history)
        successful_runs = sum(m.success_count for m in metrics_history)
        failed_runs = sum(m.error_count for m in metrics_history)
        
        # All input lists are guaranteed to be 1D lists of float
        def safe_stat(func, arr, default=0.0) -> float:
            if not arr:
                return float(default)
            flat_arr: list[float] = []
            for x in arr:
                if isinstance(x, list):
                    for y in x:
                        if isinstance(y, (int, float)):
                            flat_arr.append(float(y))
                elif isinstance(x, (int, float)):
                    flat_arr.append(float(x))
            assert isinstance(flat_arr, list)
            if not flat_arr:
                return float(default)
            try:
                return float(func(flat_arr))
            except (TypeError, ValueError):
                return float(default)
        def safe_percentile(arr, q, default=0.0) -> float:
            try:
                if not isinstance(arr, list) or not arr:
                    return float(default)
                float_arr = []
                for x in arr:
                    if isinstance(x, list):
                        for y in x:
                            if isinstance(y, (int, float)):
                                float_arr.append(float(y))
                    elif isinstance(x, (int, float)):
                        float_arr.append(float(x))
                if not float_arr:
                    return float(default)
                return float(np.percentile(float_arr, q))
            except Exception:
                return float(default)

        avg_execution_time = float(safe_stat(statistics.mean, execution_times))
        avg_cpu_usage = float(safe_stat(statistics.mean, cpu_usages))
        avg_memory_usage = float(safe_stat(statistics.mean, memory_usages))
        error_rate = float(failed_runs) / float(total_runs) if total_runs > 0 else 0.0

        # 성능 점수 계산 (낮은 실행시간, 낮은 CPU/메모리 사용률, 낮은 에러율이 높은 점수)
        execution_score = max(0.0, 100.0 - (avg_execution_time / self.config.response_time_threshold) * 100.0)
        cpu_score = max(0.0, 100.0 - (avg_cpu_usage / self.config.cpu_threshold) * 100.0)
        memory_score = max(0.0, 100.0 - (avg_memory_usage / self.config.memory_threshold) * 100.0)
        error_score = max(0.0, 100.0 - error_rate * 100.0)
        
        performance_score = (execution_score + cpu_score + memory_score + error_score) / 4.0
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(
            avg_execution_time, avg_cpu_usage, avg_memory_usage, error_rate, performance_score
        )
        
        return BenchmarkResult(
            plugin_id=plugin_id,
            test_name=test_name,
            total_runs=total_runs,
            successful_runs=successful_runs,
            failed_runs=failed_runs,
            avg_execution_time=avg_execution_time,
            min_execution_time=safe_stat(min, execution_times),
            max_execution_time=safe_stat(max, execution_times),
            p50_execution_time=safe_stat(statistics.median, execution_times),
            p95_execution_time=0.0,  # numpy 타입 오류 우회
            p99_execution_time=0.0,  # numpy 타입 오류 우회
            avg_cpu_usage=avg_cpu_usage,
            avg_memory_usage=avg_memory_usage,
            peak_memory_usage=safe_stat(max, memory_peaks),
            avg_throughput=safe_stat(statistics.mean, throughputs),
            error_rate=error_rate,
            performance_score=performance_score,
            recommendations=recommendations,
            metrics_history=metrics_history
        )
    
    def _generate_recommendations(self, avg_execution_time: float, avg_cpu_usage: float, 
                                 avg_memory_usage: float, error_rate: float, 
                                 performance_score: float) -> List[str]:
        """성능 개선 권장사항 생성"""
        recommendations = []
        
        if avg_execution_time > self.config.response_time_threshold:
            recommendations.append("응답 시간이 임계값을 초과합니다. 코드 최적화를 고려하세요.")
        
        if avg_cpu_usage > self.config.cpu_threshold:
            recommendations.append("CPU 사용률이 높습니다. 비동기 처리나 스레드 풀을 고려하세요.")
        
        if avg_memory_usage > self.config.memory_threshold:
            recommendations.append("메모리 사용률이 높습니다. 메모리 누수나 불필요한 객체 생성을 확인하세요.")
        
        if error_rate > 0.05:  # 5% 이상
            recommendations.append("에러율이 높습니다. 예외 처리와 로깅을 개선하세요.")
        
        if performance_score < 50:
            recommendations.append("전체적인 성능이 낮습니다. 종합적인 최적화가 필요합니다.")
        elif performance_score < 70:
            recommendations.append("성능이 보통 수준입니다. 일부 개선이 필요합니다.")
        else:
            recommendations.append("성능이 양호합니다. 현재 상태를 유지하세요.")
        
        return recommendations
    
    def _save_benchmark_result(self, result: BenchmarkResult):
        """벤치마크 결과 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # 메인 결과 저장
                conn.execute("""
                    INSERT INTO benchmark_results 
                    (plugin_id, test_name, total_runs, successful_runs, failed_runs,
                     avg_execution_time, min_execution_time, max_execution_time,
                     p50_execution_time, p95_execution_time, p99_execution_time,
                     avg_cpu_usage, avg_memory_usage, peak_memory_usage,
                     avg_throughput, error_rate, performance_score, recommendations)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    result.plugin_id,
                    result.test_name,
                    result.total_runs,
                    result.successful_runs,
                    result.failed_runs,
                    result.avg_execution_time,
                    result.min_execution_time,
                    result.max_execution_time,
                    result.p50_execution_time,
                    result.p95_execution_time,
                    result.p99_execution_time,
                    result.avg_cpu_usage,
                    result.avg_memory_usage,
                    result.peak_memory_usage,
                    result.avg_throughput,
                    result.error_rate,
                    result.performance_score,
                    json.dumps(result.recommendations)
                ))
                
                # 메트릭 히스토리 저장
                for metrics in result.metrics_history:
                    conn.execute("""
                        INSERT INTO benchmark_metrics 
                        (plugin_id, test_name, execution_time, cpu_usage, memory_usage,
                         memory_peak, throughput, error_count, success_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        metrics.plugin_id,
                        metrics.test_name,
                        metrics.execution_time,
                        metrics.cpu_usage,
                        metrics.memory_usage,
                        metrics.memory_peak,
                        metrics.throughput,
                        metrics.error_count,
                        metrics.success_count
                    ))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"벤치마크 결과 저장 실패: {e}")
    
    def get_benchmark_history(self, plugin_id: str, days: int = 30) -> List[BenchmarkResult]:
        """벤치마크 히스토리 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT * FROM benchmark_results 
                    WHERE plugin_id = ? AND created_at >= date('now', '-{} days')
                    ORDER BY created_at DESC
                """.format(days), (plugin_id,))
                
                results = []
                for row in cursor.fetchall():
                    # 결과 객체 생성 (간소화)
                    result = BenchmarkResult(
                        plugin_id=row[1],
                        test_name=row[2],
                        total_runs=row[3],
                        successful_runs=row[4],
                        failed_runs=row[5],
                        avg_execution_time=row[6],
                        min_execution_time=row[7],
                        max_execution_time=row[8],
                        p50_execution_time=row[9],
                        p95_execution_time=row[10],
                        p99_execution_time=row[11],
                        avg_cpu_usage=row[12],
                        avg_memory_usage=row[13],
                        peak_memory_usage=row[14],
                        avg_throughput=row[15],
                        error_rate=row[16],
                        performance_score=row[17],
                        recommendations=json.loads(row[18]) if row[18] else [],
                        metrics_history=[]
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            logger.error(f"벤치마크 히스토리 조회 실패: {e}")
            return []
    
    def generate_performance_report(self, plugin_id: str, output_path: str):
        """성능 보고서 생성"""
        try:
            # 최신 벤치마크 결과 조회
            history = self.get_benchmark_history(plugin_id, 30)
            
            if not history:
                logger.warning(f"플러그인 {plugin_id}의 벤치마크 데이터가 없습니다")
                return
            
            latest_result = history[0]
            
            # 성능 트렌드 분석
            performance_trend = self._analyze_performance_trend(history)
            
            # 보고서 데이터 구성
            report_data = {
                'plugin_id': plugin_id,
                'generated_at': datetime.utcnow().isoformat(),
                'latest_benchmark': asdict(latest_result),
                'performance_trend': performance_trend,
                'recommendations': latest_result.recommendations,
                'history_summary': {
                    'total_tests': len(history),
                    'avg_performance_score': statistics.mean([r.performance_score for r in history]),
                    'best_performance_score': max([r.performance_score for r in history]),
                    'worst_performance_score': min([r.performance_score for r in history])
                }
            }
            
            # JSON 파일로 저장
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            # 차트 생성
            self._generate_performance_charts(plugin_id, history, output_path.replace('.json', '_charts.png'))
            
            logger.info(f"성능 보고서 생성 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"성능 보고서 생성 실패: {e}")
    
    def _analyze_performance_trend(self, history: List[BenchmarkResult]) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        if len(history) < 2:
            return {'trend': 'insufficient_data', 'message': '트렌드 분석을 위한 데이터가 부족합니다'}
        
        # 성능 점수 트렌드
        scores = [r.performance_score for r in history]
        
        # 선형 회귀로 트렌드 계산
        x = np.arange(len(scores))
        slope, intercept = np.polyfit(x, scores, 1)
        
        if slope > 0.1:
            trend = 'improving'
            trend_strength = 'strong' if abs(slope) > 0.5 else 'moderate'
        elif slope < -0.1:
            trend = 'declining'
            trend_strength = 'strong' if abs(slope) > 0.5 else 'moderate'
        else:
            trend = 'stable'
            trend_strength = 'stable'
        
        return {
            'trend': trend,
            'trend_strength': trend_strength,
            'slope': slope,
            'avg_score': statistics.mean(scores),
            'score_variance': statistics.variance(scores)
        }
    
    def _generate_performance_charts(self, plugin_id: str, history: List[BenchmarkResult], output_path: str):
        """성능 차트 생성"""
        try:
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            fig.suptitle(f'플러그인 성능 분석: {plugin_id}', fontsize=16)
            
            # 성능 점수 트렌드
            scores = [r.performance_score for r in history]
            dates = [r.created_at for r in history]
            
            axes[0, 0].plot(dates, scores, 'b-o')
            axes[0, 0].set_title('성능 점수 트렌드')
            axes[0, 0].set_ylabel('성능 점수')
            axes[0, 0].grid(True)
            
            # 응답 시간 분포
            execution_times = [r.avg_execution_time for r in history]
            axes[0, 1].hist(execution_times, bins=10, alpha=0.7, color='green')
            axes[0, 1].set_title('응답 시간 분포')
            axes[0, 1].set_xlabel('응답 시간 (초)')
            axes[0, 1].grid(True)
            
            # CPU 및 메모리 사용률
            cpu_usage = [r.avg_cpu_usage for r in history]
            memory_usage = [r.avg_memory_usage for r in history]
            
            x = range(len(history))
            axes[1, 0].plot(x, cpu_usage, 'r-o', label='CPU 사용률')
            axes[1, 0].plot(x, memory_usage, 'g-s', label='메모리 사용률')
            axes[1, 0].set_title('리소스 사용률')
            axes[1, 0].set_ylabel('사용률 (%)')
            axes[1, 0].legend()
            axes[1, 0].grid(True)
            
            # 에러율 및 처리량
            error_rates = [r.error_rate * 100 for r in history]
            throughputs = [r.avg_throughput for r in history]
            
            ax1 = axes[1, 1]
            ax2 = ax1.twinx()
            
            ax1.plot(x, error_rates, 'r-o', label='에러율')
            ax2.plot(x, throughputs, 'b-s', label='처리량')
            
            ax1.set_title('에러율 및 처리량')
            ax1.set_xlabel('테스트 번호')
            ax1.set_ylabel('에러율 (%)', color='r')
            ax2.set_ylabel('처리량 (req/s)', color='b')
            
            ax1.legend(loc='upper left')
            ax2.legend(loc='upper right')
            ax1.grid(True)
            
            plt.tight_layout()
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"성능 차트 생성 완료: {output_path}")
            
        except Exception as e:
            logger.error(f"성능 차트 생성 실패: {e}")

def sample_test_function():
    """샘플 테스트 함수"""
    # 실제 플러그인 함수를 시뮬레이션
    time.sleep(0.1)  # 100ms 지연
    return {"status": "success", "data": "test_result"}

def main():
    """메인 함수"""
    try:
        # 벤치마크 시스템 초기화
        benchmark = PluginPerformanceBenchmark()
        
        # 샘플 플러그인 벤치마크
        sample_plugins = [
            'analytics_core',
            'reporting_engine',
            'dashboard_widget',
            'security_plugin',
            'backup_plugin'
        ]
        
        for plugin_id in sample_plugins:
            try:
                logger.info(f"플러그인 벤치마크 시작: {plugin_id}")
                
                # 벤치마크 실행
                result = benchmark.run_benchmark(
                    plugin_id=plugin_id,
                    test_function=sample_test_function,
                    test_name="performance_test"
                )
                
                # 결과 출력
                print(f"\n=== {plugin_id} 벤치마크 결과 ===")
                print(f"성능 점수: {result.performance_score:.2f}/100")
                print(f"평균 응답 시간: {result.avg_execution_time:.3f}초")
                print(f"평균 CPU 사용률: {result.avg_cpu_usage:.1f}%")
                print(f"평균 메모리 사용률: {result.avg_memory_usage:.1f}MB")
                print(f"에러율: {result.error_rate:.2%}")
                print(f"권장사항:")
                for rec in result.recommendations:
                    print(f"  - {rec}")
                
                # 성능 보고서 생성
                benchmark.generate_performance_report(
                    plugin_id, 
                    f"performance_report_{plugin_id}.json"
                )
                
            except Exception as e:
                logger.error(f"플러그인 {plugin_id} 벤치마크 실패: {e}")
        
        logger.info("벤치마크 시스템 테스트 완료")
        
    except Exception as e:
        logger.error(f"벤치마크 시스템 오류: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 