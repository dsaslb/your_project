#!/usr/bin/env python3
"""
🚀 Your Program 성능 및 부하 테스트 스크립트

이 스크립트는 프로덕션 배포 전 시스템의 성능과 안정성을 검증하기 위한
포괄적인 테스트를 수행합니다.

사용법:
    python scripts/performance_load_test.py
    python scripts/performance_load_test.py --load-test --duration 300
    python scripts/performance_load_test.py --stress-test --concurrent 100
"""

import asyncio
import aiohttp
import time
import json
import logging
import statistics
import psutil
import argparse
import concurrent.futures
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('performance_test.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    timestamp: datetime
    test_name: str
    endpoint: str
    method: str
    response_time: float
    status_code: int
    success: bool
    error_message: Optional[str] = None
    payload_size: int = 0
    response_size: int = 0

@dataclass
class PerformanceMetrics:
    """성능 메트릭 데이터"""
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    median_response_time: float
    p95_response_time: float
    p99_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float
    throughput_mbps: float

@dataclass
class SystemMetrics:
    """시스템 메트릭 데이터"""
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    disk_io_read: float
    disk_io_write: float
    network_sent: float
    network_recv: float
    load_average: Tuple[float, float, float]

class SystemMonitor:
    """시스템 리소스 모니터링 클래스"""
    
    def __init__(self):
        self.metrics: List[SystemMetrics] = []
        self.monitoring = False
        self._monitor_task = None
        
    async def start_monitoring(self, interval: float = 1.0):
        """시스템 모니터링 시작"""
        self.monitoring = True
        self._monitor_task = asyncio.create_task(self._monitor_loop(interval))
        
    async def stop_monitoring(self):
        """시스템 모니터링 중지"""
        self.monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
                
    async def _monitor_loop(self, interval: float):
        """모니터링 루프"""
        last_disk_io = psutil.disk_io_counters()
        last_network = psutil.net_io_counters()
        last_time = time.time()
        
        while self.monitoring:
            try:
                current_time = time.time()
                time_delta = current_time - last_time
                
                # CPU 및 메모리
                cpu_percent = psutil.cpu_percent()
                memory_percent = psutil.virtual_memory().percent
                
                # 디스크 I/O
                current_disk_io = psutil.disk_io_counters()
                disk_read_rate = (current_disk_io.read_bytes - last_disk_io.read_bytes) / time_delta
                disk_write_rate = (current_disk_io.write_bytes - last_disk_io.write_bytes) / time_delta
                
                # 네트워크 I/O
                current_network = psutil.net_io_counters()
                network_sent_rate = (current_network.bytes_sent - last_network.bytes_sent) / time_delta
                network_recv_rate = (current_network.bytes_recv - last_network.bytes_recv) / time_delta
                
                # 로드 평균
                load_avg = psutil.getloadavg()
                
                metric = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_percent=cpu_percent,
                    memory_percent=memory_percent,
                    disk_io_read=disk_read_rate,
                    disk_io_write=disk_write_rate,
                    network_sent=network_sent_rate,
                    network_recv=network_recv_rate,
                    load_average=load_avg
                )
                
                self.metrics.append(metric)
                
                # 다음 측정을 위한 값 업데이트
                last_disk_io = current_disk_io
                last_network = current_network
                last_time = current_time
                
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"시스템 메트릭 수집 오류: {e}")
                await asyncio.sleep(interval)

class PerformanceTester:
    """성능 테스트 클래스"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results: List[TestResult] = []
        self.system_monitor = SystemMonitor()
        
    async def run_basic_performance_test(self) -> Dict[str, Any]:
        """기본 성능 테스트 실행"""
        logger.info("🏃 기본 성능 테스트 시작")
        
        # 시스템 모니터링 시작
        await self.system_monitor.start_monitoring()
        
        test_scenarios = [
            {"name": "health_check", "endpoint": "/health", "method": "GET"},
            {"name": "metrics", "endpoint": "/metrics", "method": "GET"},
            {"name": "security_status", "endpoint": "/security/status", "method": "GET", "base_url": "http://localhost:8007"},
        ]
        
        try:
            async with aiohttp.ClientSession() as session:
                for scenario in test_scenarios:
                    await self._run_scenario(session, scenario, iterations=10)
                    await asyncio.sleep(1)  # 시나리오 간 대기
                    
        except Exception as e:
            logger.error(f"기본 성능 테스트 오류: {e}")
        finally:
            await self.system_monitor.stop_monitoring()
        
        return self._calculate_metrics()
    
    async def run_load_test(self, duration: int = 60, concurrent_users: int = 10) -> Dict[str, Any]:
        """부하 테스트 실행"""
        logger.info(f"⚡ 부하 테스트 시작 - 동시 사용자: {concurrent_users}, 지속 시간: {duration}초")
        
        # 시스템 모니터링 시작
        await self.system_monitor.start_monitoring()
        
        start_time = time.time()
        end_time = start_time + duration
        
        # 테스트 시나리오 정의
        scenarios = [
            {"name": "api_health", "endpoint": "/health", "method": "GET", "weight": 0.3},
            {"name": "api_metrics", "endpoint": "/metrics", "method": "GET", "weight": 0.2},
            {"name": "security_status", "endpoint": "/security/status", "method": "GET", "base_url": "http://localhost:8007", "weight": 0.2},
            {"name": "performance_data", "endpoint": "/performance/metrics/realtime", "method": "GET", "weight": 0.3},
        ]
        
        try:
            # 동시 사용자 시뮬레이션
            tasks = []
            for i in range(concurrent_users):
                task = asyncio.create_task(
                    self._user_simulation(scenarios, end_time, user_id=i)
                )
                tasks.append(task)
            
            # 모든 사용자 시뮬레이션 완료 대기
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"부하 테스트 오류: {e}")
        finally:
            await self.system_monitor.stop_monitoring()
        
        return self._calculate_metrics()
    
    async def run_stress_test(self, max_concurrent: int = 100, ramp_up_time: int = 60) -> Dict[str, Any]:
        """스트레스 테스트 실행 (점진적 부하 증가)"""
        logger.info(f"💪 스트레스 테스트 시작 - 최대 동시 연결: {max_concurrent}, 램프업 시간: {ramp_up_time}초")
        
        # 시스템 모니터링 시작
        await self.system_monitor.start_monitoring()
        
        start_time = time.time()
        test_duration = ramp_up_time + 120  # 램프업 + 안정화 시간
        end_time = start_time + test_duration
        
        scenarios = [
            {"name": "health_check", "endpoint": "/health", "method": "GET", "weight": 0.5},
            {"name": "metrics", "endpoint": "/metrics", "method": "GET", "weight": 0.3},
            {"name": "security", "endpoint": "/security/status", "method": "GET", "base_url": "http://localhost:8007", "weight": 0.2},
        ]
        
        try:
            tasks = []
            
            # 점진적으로 사용자 추가
            for concurrent_level in range(1, max_concurrent + 1):
                if time.time() >= end_time:
                    break
                    
                # 새 사용자 추가
                task = asyncio.create_task(
                    self._user_simulation(scenarios, end_time, user_id=concurrent_level)
                )
                tasks.append(task)
                
                # 램프업 속도 조절
                await asyncio.sleep(ramp_up_time / max_concurrent)
                
                # 중간 결과 로깅
                if concurrent_level % 10 == 0:
                    logger.info(f"현재 동시 사용자: {concurrent_level}")
            
            # 모든 사용자 시뮬레이션 완료 대기
            logger.info("모든 사용자 시뮬레이션 완료 대기 중...")
            await asyncio.gather(*tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"스트레스 테스트 오류: {e}")
        finally:
            await self.system_monitor.stop_monitoring()
        
        return self._calculate_metrics()
    
    async def run_spike_test(self, normal_load: int = 10, spike_load: int = 100, spike_duration: int = 30) -> Dict[str, Any]:
        """스파이크 테스트 실행 (급격한 부하 증가)"""
        logger.info(f"⚡ 스파이크 테스트 시작 - 정상 부하: {normal_load}, 스파이크 부하: {spike_load}")
        
        # 시스템 모니터링 시작
        await self.system_monitor.start_monitoring()
        
        scenarios = [{"name": "health_check", "endpoint": "/health", "method": "GET", "weight": 1.0}]
        
        try:
            # 1단계: 정상 부하 (30초)
            logger.info("1단계: 정상 부하 생성 중...")
            end_time = time.time() + 30
            normal_tasks = [
                asyncio.create_task(self._user_simulation(scenarios, end_time, user_id=i))
                for i in range(normal_load)
            ]
            await asyncio.gather(*normal_tasks, return_exceptions=True)
            
            # 2단계: 스파이크 부하
            logger.info("2단계: 스파이크 부하 생성 중...")
            end_time = time.time() + spike_duration
            spike_tasks = [
                asyncio.create_task(self._user_simulation(scenarios, end_time, user_id=i))
                for i in range(spike_load)
            ]
            await asyncio.gather(*spike_tasks, return_exceptions=True)
            
            # 3단계: 정상 부하로 복귀 (30초)
            logger.info("3단계: 정상 부하로 복귀...")
            end_time = time.time() + 30
            recovery_tasks = [
                asyncio.create_task(self._user_simulation(scenarios, end_time, user_id=i))
                for i in range(normal_load)
            ]
            await asyncio.gather(*recovery_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"스파이크 테스트 오류: {e}")
        finally:
            await self.system_monitor.stop_monitoring()
        
        return self._calculate_metrics()
    
    async def _user_simulation(self, scenarios: List[Dict], end_time: float, user_id: int):
        """개별 사용자 시뮬레이션"""
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                try:
                    # 가중치에 따른 시나리오 선택
                    import random
                    scenario = random.choices(
                        scenarios,
                        weights=[s.get('weight', 1.0) for s in scenarios]
                    )[0]
                    
                    await self._execute_request(session, scenario, user_id)
                    
                    # 사용자 간격 시뮬레이션 (0.1~2초)
                    await asyncio.sleep(random.uniform(0.1, 2.0))
                    
                except Exception as e:
                    logger.debug(f"사용자 {user_id} 시뮬레이션 오류: {e}")
                    await asyncio.sleep(1)  # 오류 시 대기
    
    async def _execute_request(self, session: aiohttp.ClientSession, scenario: Dict, user_id: int = 0):
        """개별 요청 실행"""
        base_url = scenario.get('base_url', self.base_url)
        url = f"{base_url}{scenario['endpoint']}"
        method = scenario['method'].upper()
        
        start_time = time.time()
        error_message = None
        status_code = 0
        response_size = 0
        
        try:
            async with session.request(method, url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                status_code = response.status
                response_data = await response.read()
                response_size = len(response_data)
                
                success = 200 <= status_code < 400
                
        except asyncio.TimeoutError:
            success = False
            error_message = "Timeout"
            status_code = 0
        except Exception as e:
            success = False
            error_message = str(e)
            status_code = 0
        
        end_time = time.time()
        response_time = (end_time - start_time) * 1000  # ms
        
        result = TestResult(
            timestamp=datetime.now(),
            test_name=scenario['name'],
            endpoint=scenario['endpoint'],
            method=method,
            response_time=response_time,
            status_code=status_code,
            success=success,
            error_message=error_message,
            payload_size=0,
            response_size=response_size
        )
        
        self.results.append(result)
    
    async def _run_scenario(self, session: aiohttp.ClientSession, scenario: Dict, iterations: int = 1):
        """시나리오 실행"""
        logger.info(f"📋 시나리오 실행: {scenario['name']} ({iterations}회)")
        
        for i in range(iterations):
            await self._execute_request(session, scenario)
            if iterations > 1:
                await asyncio.sleep(0.1)  # 요청 간 간격
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 계산"""
        if not self.results:
            return {"error": "테스트 결과가 없습니다"}
        
        # 응답 시간 통계
        response_times = [r.response_time for r in self.results if r.success]
        successful_requests = len([r for r in self.results if r.success])
        failed_requests = len([r for r in self.results if not r.success])
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            p95_response_time = np.percentile(response_times, 95)
            p99_response_time = np.percentile(response_times, 99)
        else:
            avg_response_time = median_response_time = min_response_time = max_response_time = 0
            p95_response_time = p99_response_time = 0
        
        # 처리량 계산
        if self.results:
            test_duration = (self.results[-1].timestamp - self.results[0].timestamp).total_seconds()
            requests_per_second = len(self.results) / max(test_duration, 1)
            
            # 처리량 (MB/s)
            total_bytes = sum(r.response_size for r in self.results)
            throughput_mbps = (total_bytes / max(test_duration, 1)) / (1024 * 1024)
        else:
            requests_per_second = throughput_mbps = 0
        
        # 에러율
        total_requests = len(self.results)
        error_rate = (failed_requests / total_requests * 100) if total_requests > 0 else 0
        
        metrics = PerformanceMetrics(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            average_response_time=avg_response_time,
            median_response_time=median_response_time,
            p95_response_time=p95_response_time,
            p99_response_time=p99_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            throughput_mbps=throughput_mbps
        )
        
        # 시스템 메트릭 요약
        system_summary = self._summarize_system_metrics()
        
        return {
            "performance_metrics": asdict(metrics),
            "system_metrics": system_summary,
            "test_summary": {
                "test_duration": test_duration if self.results else 0,
                "endpoints_tested": len(set(r.endpoint for r in self.results)),
                "peak_requests_per_second": max([
                    len([r for r in self.results 
                         if r.timestamp.replace(second=0, microsecond=0) == minute])
                    for minute in set(r.timestamp.replace(second=0, microsecond=0) 
                                    for r in self.results)
                ] + [0])
            }
        }
    
    def _summarize_system_metrics(self) -> Dict[str, Any]:
        """시스템 메트릭 요약"""
        if not self.system_monitor.metrics:
            return {"error": "시스템 메트릭이 없습니다"}
        
        metrics = self.system_monitor.metrics
        
        return {
            "cpu": {
                "average": np.mean([m.cpu_percent for m in metrics]),
                "max": np.max([m.cpu_percent for m in metrics]),
                "min": np.min([m.cpu_percent for m in metrics])
            },
            "memory": {
                "average": np.mean([m.memory_percent for m in metrics]),
                "max": np.max([m.memory_percent for m in metrics]),
                "min": np.min([m.memory_percent for m in metrics])
            },
            "network": {
                "sent_mbps": np.mean([m.network_sent for m in metrics]) / (1024 * 1024),
                "recv_mbps": np.mean([m.network_recv for m in metrics]) / (1024 * 1024)
            },
            "load_average": {
                "1min": np.mean([m.load_average[0] for m in metrics]),
                "5min": np.mean([m.load_average[1] for m in metrics]),
                "15min": np.mean([m.load_average[2] for m in metrics])
            }
        }
    
    def generate_report(self, results: Dict[str, Any], output_file: str = None) -> str:
        """테스트 리포트 생성"""
        report_lines = [
            "="*80,
            "🚀 YOUR PROGRAM 성능 테스트 리포트",
            "="*80,
            f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"📊 총 요청 수: {results['performance_metrics']['total_requests']:,}",
            f"✅ 성공 요청: {results['performance_metrics']['successful_requests']:,}",
            f"❌ 실패 요청: {results['performance_metrics']['failed_requests']:,}",
            f"📈 에러율: {results['performance_metrics']['error_rate']:.2f}%",
            "",
            "📊 응답 시간 통계:",
            f"  평균: {results['performance_metrics']['average_response_time']:.2f}ms",
            f"  중간값: {results['performance_metrics']['median_response_time']:.2f}ms",
            f"  95%: {results['performance_metrics']['p95_response_time']:.2f}ms",
            f"  99%: {results['performance_metrics']['p99_response_time']:.2f}ms",
            f"  최소: {results['performance_metrics']['min_response_time']:.2f}ms",
            f"  최대: {results['performance_metrics']['max_response_time']:.2f}ms",
            "",
            "⚡ 처리량:",
            f"  초당 요청 수: {results['performance_metrics']['requests_per_second']:.2f} RPS",
            f"  처리량: {results['performance_metrics']['throughput_mbps']:.2f} MB/s",
            "",
            "💻 시스템 리소스:",
            f"  평균 CPU: {results['system_metrics']['cpu']['average']:.1f}%",
            f"  최대 CPU: {results['system_metrics']['cpu']['max']:.1f}%",
            f"  평균 메모리: {results['system_metrics']['memory']['average']:.1f}%",
            f"  최대 메모리: {results['system_metrics']['memory']['max']:.1f}%",
            f"  네트워크 송신: {results['system_metrics']['network']['sent_mbps']:.2f} MB/s",
            f"  네트워크 수신: {results['system_metrics']['network']['recv_mbps']:.2f} MB/s",
            "",
            "🎯 성능 평가:",
        ]
        
        # 성능 평가
        metrics = results['performance_metrics']
        system = results['system_metrics']
        
        # 응답 시간 평가
        if metrics['average_response_time'] < 100:
            report_lines.append("  ✅ 응답 시간: 우수 (100ms 미만)")
        elif metrics['average_response_time'] < 500:
            report_lines.append("  ⚠️ 응답 시간: 양호 (500ms 미만)")
        else:
            report_lines.append("  ❌ 응답 시간: 개선 필요 (500ms 이상)")
        
        # 에러율 평가
        if metrics['error_rate'] < 1:
            report_lines.append("  ✅ 에러율: 우수 (1% 미만)")
        elif metrics['error_rate'] < 5:
            report_lines.append("  ⚠️ 에러율: 주의 (5% 미만)")
        else:
            report_lines.append("  ❌ 에러율: 위험 (5% 이상)")
        
        # CPU 사용률 평가
        if system['cpu']['max'] < 80:
            report_lines.append("  ✅ CPU 사용률: 안정적 (80% 미만)")
        elif system['cpu']['max'] < 95:
            report_lines.append("  ⚠️ CPU 사용률: 주의 (95% 미만)")
        else:
            report_lines.append("  ❌ CPU 사용률: 위험 (95% 이상)")
        
        # 메모리 사용률 평가
        if system['memory']['max'] < 85:
            report_lines.append("  ✅ 메모리 사용률: 안정적 (85% 미만)")
        elif system['memory']['max'] < 95:
            report_lines.append("  ⚠️ 메모리 사용률: 주의 (95% 미만)")
        else:
            report_lines.append("  ❌ 메모리 사용률: 위험 (95% 이상)")
        
        # 처리량 평가
        if metrics['requests_per_second'] > 100:
            report_lines.append("  ✅ 처리량: 우수 (100 RPS 이상)")
        elif metrics['requests_per_second'] > 50:
            report_lines.append("  ⚠️ 처리량: 양호 (50 RPS 이상)")
        else:
            report_lines.append("  ❌ 처리량: 개선 필요 (50 RPS 미만)")
        
        report_lines.extend([
            "",
            "="*80
        ])
        
        report = "\n".join(report_lines)
        
        if output_file:
            Path(output_file).write_text(report, encoding='utf-8')
            logger.info(f"💾 리포트가 {output_file}에 저장되었습니다")
        
        return report
    
    def generate_charts(self, results: Dict[str, Any], output_dir: str = "performance_charts"):
        """성능 차트 생성"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        try:
            # 응답 시간 히스토그램
            if self.results:
                response_times = [r.response_time for r in self.results if r.success]
                
                plt.figure(figsize=(12, 8))
                
                # 1. 응답 시간 히스토그램
                plt.subplot(2, 2, 1)
                plt.hist(response_times, bins=50, alpha=0.7, color='blue')
                plt.title('응답 시간 분포')
                plt.xlabel('응답 시간 (ms)')
                plt.ylabel('빈도')
                
                # 2. 시간별 응답 시간
                plt.subplot(2, 2, 2)
                timestamps = [r.timestamp for r in self.results if r.success]
                plt.plot(timestamps, response_times, alpha=0.6)
                plt.title('시간별 응답 시간')
                plt.xlabel('시간')
                plt.ylabel('응답 시간 (ms)')
                plt.xticks(rotation=45)
                
                # 3. 시스템 CPU 사용률
                if self.system_monitor.metrics:
                    plt.subplot(2, 2, 3)
                    cpu_times = [m.timestamp for m in self.system_monitor.metrics]
                    cpu_values = [m.cpu_percent for m in self.system_monitor.metrics]
                    plt.plot(cpu_times, cpu_values, color='red')
                    plt.title('CPU 사용률')
                    plt.xlabel('시간')
                    plt.ylabel('CPU (%)')
                    plt.xticks(rotation=45)
                
                # 4. 시스템 메모리 사용률
                if self.system_monitor.metrics:
                    plt.subplot(2, 2, 4)
                    memory_values = [m.memory_percent for m in self.system_monitor.metrics]
                    plt.plot(cpu_times, memory_values, color='green')
                    plt.title('메모리 사용률')
                    plt.xlabel('시간')
                    plt.ylabel('메모리 (%)')
                    plt.xticks(rotation=45)
                
                plt.tight_layout()
                chart_file = output_path / f"performance_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                plt.savefig(chart_file, dpi=300, bbox_inches='tight')
                plt.close()
                
                logger.info(f"📊 차트가 {chart_file}에 저장되었습니다")
                
        except Exception as e:
            logger.error(f"차트 생성 오류: {e}")

async def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Your Program 성능 및 부하 테스트")
    parser.add_argument("--base-url", default="http://localhost:8000", help="기본 URL")
    parser.add_argument("--load-test", action="store_true", help="부하 테스트 실행")
    parser.add_argument("--stress-test", action="store_true", help="스트레스 테스트 실행")
    parser.add_argument("--spike-test", action="store_true", help="스파이크 테스트 실행")
    parser.add_argument("--duration", type=int, default=60, help="테스트 지속 시간 (초)")
    parser.add_argument("--concurrent", type=int, default=10, help="동시 사용자 수")
    parser.add_argument("--output", help="결과 JSON 파일 경로")
    parser.add_argument("--report", help="리포트 파일 경로")
    parser.add_argument("--charts", action="store_true", help="성능 차트 생성")
    
    args = parser.parse_args()
    
    try:
        tester = PerformanceTester(args.base_url)
        
        # 테스트 유형에 따른 실행
        if args.stress_test:
            logger.info("💪 스트레스 테스트 모드")
            results = await tester.run_stress_test(
                max_concurrent=args.concurrent,
                ramp_up_time=args.duration
            )
        elif args.spike_test:
            logger.info("⚡ 스파이크 테스트 모드")
            results = await tester.run_spike_test(
                normal_load=10,
                spike_load=args.concurrent,
                spike_duration=30
            )
        elif args.load_test:
            logger.info("🔥 부하 테스트 모드")
            results = await tester.run_load_test(
                duration=args.duration,
                concurrent_users=args.concurrent
            )
        else:
            logger.info("🏃 기본 성능 테스트 모드")
            results = await tester.run_basic_performance_test()
        
        # 결과 저장
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"💾 결과가 {args.output}에 저장되었습니다")
        
        # 리포트 생성
        report = tester.generate_report(results, args.report)
        print(report)
        
        # 차트 생성
        if args.charts:
            tester.generate_charts(results)
        
        # 테스트 결과에 따른 종료 코드
        metrics = results.get('performance_metrics', {})
        if (metrics.get('error_rate', 0) < 5 and 
            metrics.get('average_response_time', 0) < 500):
            logger.info("✅ 성능 테스트 통과")
            return 0
        else:
            logger.warning("⚠️ 성능 테스트 기준 미달")
            return 1
            
    except KeyboardInterrupt:
        logger.info("⏹️ 테스트가 사용자에 의해 중단되었습니다")
        return 130
    except Exception as e:
        logger.error(f"❌ 테스트 실행 오류: {e}")
        return 1

if __name__ == "__main__":
    import sys
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        sys.exit(130) 