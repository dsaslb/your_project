#!/usr/bin/env python3
"""
플러그인 리소스 사용량 테스트
CPU, 메모리, 디스크 I/O, 네트워크 사용량 모니터링
"""

import os
import sys
import time
import json
import psutil
import threading
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import requests

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ResourceMonitor:
    """리소스 모니터링 클래스"""

    def __init__(self):
        self.monitoring = False
        self.metrics = []
        self.start_time = None
        self.end_time = None

    def start_monitoring(self):
        """모니터링 시작"""
        self.monitoring = True
        self.start_time = datetime.now()
        self.metrics = []

        # 백그라운드에서 메트릭 수집
        self.monitor_thread = threading.Thread(target=self._collect_metrics)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("리소스 모니터링 시작됨")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring = False
        self.end_time = datetime.now()

        if hasattr(self, "monitor_thread"):
            self.monitor_thread.join(timeout=5)

        print("리소스 모니터링 중지됨")

    def _collect_metrics(self):
        """메트릭 수집"""
        while self.monitoring:
            try:
                metric = {
                    "timestamp": datetime.now().isoformat(),
                    "cpu_percent": psutil.cpu_percent(interval=1),
                    "memory_percent": psutil.virtual_memory().percent,
                    "memory_used_mb": psutil.virtual_memory().used / (1024 * 1024),
                    "disk_io": psutil.disk_io_counters(),
                    "network_io": psutil.net_io_counters(),
                    "open_files": len(psutil.Process().open_files()),
                    "threads": psutil.Process().num_threads(),
                    "connections": len(psutil.Process().connections()),
                }

                self.metrics.append(metric)
                time.sleep(1)  # 1초마다 수집

            except Exception as e:
                print(f"메트릭 수집 오류: {e}")
                time.sleep(1)

    def get_summary(self) -> Dict[str, Any]:
        """모니터링 결과 요약"""
        if not self.metrics:
            return {}

        # CPU 사용률 통계
        cpu_values = [m["cpu_percent"] for m in self.metrics]
        memory_values = [m["memory_percent"] for m in self.metrics]
        memory_mb_values = [m["memory_used_mb"] for m in self.metrics]

        # 디스크 I/O 통계
        disk_reads = []
        disk_writes = []
        for metric in self.metrics:
            if metric["disk_io"]:
                disk_reads.append(metric["disk_io"].read_bytes)
                disk_writes.append(metric["disk_io"].write_bytes)

        # 네트워크 I/O 통계
        net_bytes_sent = []
        net_bytes_recv = []
        for metric in self.metrics:
            if metric["network_io"]:
                net_bytes_sent.append(metric["network_io"].bytes_sent)
                net_bytes_recv.append(metric["network_io"].bytes_recv)

        summary = {
            "duration": (
                (self.end_time - self.start_time).total_seconds()
                if self.end_time and self.start_time
                else 0
            ),
            "total_samples": len(self.metrics),
            "cpu": {
                "average": sum(cpu_values) / len(cpu_values) if cpu_values else 0,
                "max": max(cpu_values) if cpu_values else 0,
                "min": min(cpu_values) if cpu_values else 0,
            },
            "memory": {
                "average_percent": (
                    sum(memory_values) / len(memory_values) if memory_values else 0
                ),
                "max_percent": max(memory_values) if memory_values else 0,
                "average_mb": (
                    sum(memory_mb_values) / len(memory_mb_values)
                    if memory_mb_values
                    else 0
                ),
                "max_mb": max(memory_mb_values) if memory_mb_values else 0,
            },
            "disk_io": {
                "total_read_mb": sum(disk_reads) / (1024 * 1024) if disk_reads else 0,
                "total_write_mb": (
                    sum(disk_writes) / (1024 * 1024) if disk_writes else 0
                ),
                "read_rate_mbps": (
                    (max(disk_reads) - min(disk_reads)) / (1024 * 1024)
                    if len(disk_reads) > 1
                    else 0
                ),
                "write_rate_mbps": (
                    (max(disk_writes) - min(disk_writes)) / (1024 * 1024)
                    if len(disk_writes) > 1
                    else 0
                ),
            },
            "network_io": {
                "total_sent_mb": (
                    sum(net_bytes_sent) / (1024 * 1024) if net_bytes_sent else 0
                ),
                "total_recv_mb": (
                    sum(net_bytes_recv) / (1024 * 1024) if net_bytes_recv else 0
                ),
                "send_rate_mbps": (
                    (max(net_bytes_sent) - min(net_bytes_sent)) / (1024 * 1024)
                    if len(net_bytes_sent) > 1
                    else 0
                ),
                "recv_rate_mbps": (
                    (max(net_bytes_recv) - min(net_bytes_recv)) / (1024 * 1024)
                    if len(net_bytes_recv) > 1
                    else 0
                ),
            },
        }

        return summary


class PluginResourceTest:
    """플러그인 리소스 테스트"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.monitor = ResourceMonitor()
        self.results = {}

    def test_plugin_loading(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 로딩 테스트"""
        print(f"플러그인 로딩 테스트: {plugin_name}")

        # 모니터링 시작
        self.monitor.start_monitoring()

        try:
            # 플러그인 로드 API 호출
            response = requests.post(
                f"{self.base_url}/api/plugins/{plugin_name}/load", timeout=30
            )

            # 잠시 대기
            time.sleep(5)

            # 모니터링 중지
            self.monitor.stop_monitoring()

            # 결과 수집
            summary = self.monitor.get_summary()

            result = {
                "plugin_name": plugin_name,
                "test_type": "loading",
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code,
                "metrics": summary,
            }

            self.results[f"{plugin_name}_loading"] = result
            return result

        except Exception as e:
            self.monitor.stop_monitoring()
            result = {
                "plugin_name": plugin_name,
                "test_type": "loading",
                "success": False,
                "error": str(e),
                "metrics": self.monitor.get_summary(),
            }
            self.results[f"{plugin_name}_loading"] = result
            return result

    def test_plugin_operation(
        self, plugin_name: str, operation: str = "test"
    ) -> Dict[str, Any]:
        """플러그인 작업 테스트"""
        print(f"플러그인 작업 테스트: {plugin_name} - {operation}")

        # 모니터링 시작
        self.monitor.start_monitoring()

        try:
            # 플러그인 작업 API 호출
            response = requests.post(
                f"{self.base_url}/api/plugins/{plugin_name}/{operation}", timeout=30
            )

            # 잠시 대기
            time.sleep(3)

            # 모니터링 중지
            self.monitor.stop_monitoring()

            # 결과 수집
            summary = self.monitor.get_summary()

            result = {
                "plugin_name": plugin_name,
                "test_type": "operation",
                "operation": operation,
                "success": response.status_code == 200,
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code,
                "metrics": summary,
            }

            self.results[f"{plugin_name}_{operation}"] = result
            return result

        except Exception as e:
            self.monitor.stop_monitoring()
            result = {
                "plugin_name": plugin_name,
                "test_type": "operation",
                "operation": operation,
                "success": False,
                "error": str(e),
                "metrics": self.monitor.get_summary(),
            }
            self.results[f"{plugin_name}_{operation}"] = result
            return result

    def test_concurrent_operations(
        self, plugin_name: str, num_operations: int = 10
    ) -> Dict[str, Any]:
        """동시 작업 테스트"""
        print(f"동시 작업 테스트: {plugin_name} - {num_operations}개 작업")

        # 모니터링 시작
        self.monitor.start_monitoring()

        results = []
        errors = []

        def run_operation():
            try:
                response = requests.post(
                    f"{self.base_url}/api/plugins/{plugin_name}/test", timeout=10
                )
                results.append(
                    {
                        "success": response.status_code == 200,
                        "response_time": response.elapsed.total_seconds(),
                        "status_code": response.status_code,
                    }
                )
            except Exception as e:
                errors.append(str(e))

        # 동시 작업 실행
        threads = []
        for _ in range(num_operations):
            thread = threading.Thread(target=run_operation)
            thread.start()
            threads.append(thread)

        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()

        # 모니터링 중지
        self.monitor.stop_monitoring()

        # 결과 분석
        successful_operations = len([r for r in results if r["success"]])
        avg_response_time = (
            sum(r["response_time"] for r in results) / len(results) if results else 0
        )
        max_response_time = max(r["response_time"] for r in results) if results else 0

        summary = self.monitor.get_summary()

        result = {
            "plugin_name": plugin_name,
            "test_type": "concurrent",
            "total_operations": num_operations,
            "successful_operations": successful_operations,
            "failed_operations": num_operations - successful_operations,
            "success_rate": (successful_operations / num_operations) * 100,
            "avg_response_time": avg_response_time,
            "max_response_time": max_response_time,
            "errors": errors,
            "metrics": summary,
        }

        self.results[f"{plugin_name}_concurrent"] = result
        return result

    def test_memory_leak(self, plugin_name: str, duration: int = 60) -> Dict[str, Any]:
        """메모리 누수 테스트"""
        print(f"메모리 누수 테스트: {plugin_name} - {duration}초")

        # 모니터링 시작
        self.monitor.start_monitoring()

        memory_samples = []
        start_time = time.time()

        try:
            while time.time() - start_time < duration:
                # 플러그인 작업 반복 실행
                response = requests.post(
                    f"{self.base_url}/api/plugins/{plugin_name}/test", timeout=5
                )

                # 메모리 사용량 기록
                memory_info = psutil.virtual_memory()
                memory_samples.append(
                    {
                        "timestamp": time.time() - start_time,
                        "memory_percent": memory_info.percent,
                        "memory_used_mb": memory_info.used / (1024 * 1024),
                    }
                )

                time.sleep(2)  # 2초마다 실행

            # 모니터링 중지
            self.monitor.stop_monitoring()

            # 메모리 누수 분석
            if len(memory_samples) > 1:
                initial_memory = memory_samples[0]["memory_used_mb"]
                final_memory = memory_samples[-1]["memory_used_mb"]
                memory_increase = final_memory - initial_memory
                memory_increase_percent = (
                    (memory_increase / initial_memory) * 100
                    if initial_memory > 0
                    else 0
                )
            else:
                memory_increase = 0
                memory_increase_percent = 0

            summary = self.monitor.get_summary()
            summary["memory_leak"] = {
                "initial_memory_mb": (
                    memory_samples[0]["memory_used_mb"] if memory_samples else 0
                ),
                "final_memory_mb": (
                    memory_samples[-1]["memory_used_mb"] if memory_samples else 0
                ),
                "memory_increase_mb": memory_increase,
                "memory_increase_percent": memory_increase_percent,
                "samples": memory_samples,
            }

            result = {
                "plugin_name": plugin_name,
                "test_type": "memory_leak",
                "duration_seconds": duration,
                "success": True,
                "memory_increase_mb": memory_increase,
                "memory_increase_percent": memory_increase_percent,
                "metrics": summary,
            }

            self.results[f"{plugin_name}_memory_leak"] = result
            return result

        except Exception as e:
            self.monitor.stop_monitoring()
            result = {
                "plugin_name": plugin_name,
                "test_type": "memory_leak",
                "duration_seconds": duration,
                "success": False,
                "error": str(e),
                "metrics": self.monitor.get_summary(),
            }
            self.results[f"{plugin_name}_memory_leak"] = result
            return result

    def generate_report(self) -> Dict[str, Any]:
        """테스트 리포트 생성"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "successful_tests": len(
                [r for r in self.results.values() if r.get("success", False)]
            ),
            "failed_tests": len(
                [r for r in self.results.values() if not r.get("success", True)]
            ),
            "results": self.results,
            "summary": self._generate_summary(),
        }

        return report

    def _generate_summary(self) -> Dict[str, Any]:
        """결과 요약 생성"""
        if not self.results:
            return {}

        # 성능 메트릭 집계
        all_metrics = [
            r.get("metrics", {}) for r in self.results.values() if r.get("metrics")
        ]

        if not all_metrics:
            return {}

        # CPU 사용률 통계
        cpu_averages = [m.get("cpu", {}).get("average", 0) for m in all_metrics]
        memory_averages = [
            m.get("memory", {}).get("average_percent", 0) for m in all_metrics
        ]

        # 응답 시간 통계
        response_times = []
        for result in self.results.values():
            if "response_time" in result:
                response_times.append(result["response_time"])

        summary = {
            "overall_cpu_average": (
                sum(cpu_averages) / len(cpu_averages) if cpu_averages else 0
            ),
            "overall_memory_average": (
                sum(memory_averages) / len(memory_averages) if memory_averages else 0
            ),
            "avg_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "max_response_time": max(response_times) if response_times else 0,
            "total_duration": sum(m.get("duration", 0) for m in all_metrics),
            "total_samples": sum(m.get("total_samples", 0) for m in all_metrics),
        }

        return summary

    def save_report(self, filename: str = None):
        """리포트 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plugin_resource_test_report_{timestamp}.json"

        report = self.generate_report()

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"리포트 저장됨: {filename}")
        return filename


def main():
    """메인 테스트 실행"""
    print("플러그인 리소스 사용량 테스트 시작")

    # 테스트 인스턴스 생성
    tester = PluginResourceTest()

    # 테스트할 플러그인 목록
    plugins = ["your_program_management", "sample_analytics", "sample_notification"]

    # 각 플러그인에 대해 테스트 실행
    for plugin in plugins:
        print(f"\n=== {plugin} 플러그인 테스트 ===")

        # 1. 로딩 테스트
        tester.test_plugin_loading(plugin)

        # 2. 작업 테스트
        tester.test_plugin_operation(plugin, "test")

        # 3. 동시 작업 테스트
        tester.test_concurrent_operations(plugin, 5)

        # 4. 메모리 누수 테스트 (30초)
        tester.test_memory_leak(plugin, 30)

    # 리포트 생성 및 저장
    report = tester.generate_report()

    print("\n=== 테스트 결과 요약 ===")
    print(f"총 테스트 수: {report['total_tests']}")
    print(f"성공: {report['successful_tests']}")
    print(f"실패: {report['failed_tests']}")

    if report["summary"]:
        summary = report["summary"]
        print(f"평균 CPU 사용률: {summary['overall_cpu_average']:.2f}%")
        print(f"평균 메모리 사용률: {summary['overall_memory_average']:.2f}%")
        print(f"평균 응답 시간: {summary['avg_response_time']:.3f}초")
        print(f"최대 응답 시간: {summary['max_response_time']:.3f}초")

    # 리포트 저장
    tester.save_report()

    print("\n플러그인 리소스 사용량 테스트 완료")


if __name__ == "__main__":
    main()
