#!/usr/bin/env python3
"""
플러그인 성능 모니터링 도구
플러그인의 성능을 실시간으로 모니터링하고 분석하는 도구
"""

import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from collections import defaultdict, deque
from dataclasses import dataclass, asdict


@dataclass
class PerformanceMetrics:
    """성능 지표 데이터 클래스"""

    timestamp: str
    cpu_percent: float
    memory_rss: float
    memory_vms: float
    memory_percent: float
    thread_count: int
    open_files: int
    network_connections: int
    disk_io_read: float
    disk_io_write: float


class PluginPerformanceMonitor:
    def __init__(self, base_path: str = "plugins"):
        self.base_path = Path(base_path)
        self.monitoring_active = False
        self.metrics_history = defaultdict(deque)
        self.alert_thresholds = {
            "cpu_percent": 80.0,
            "memory_percent": 85.0,
            "memory_rss_mb": 500.0,
            "thread_count": 100,
        }
        self.alert_callbacks = []
        self.monitoring_interval = 1.0  # 1초
        self.max_history_size = 3600  # 1시간 (3600초)

    def start_monitoring(self, plugin_id: str, interval: float = 1.0) -> bool:
        """성능 모니터링 시작"""
        try:
            self.monitoring_interval = interval
            self.monitoring_active = True

            # 모니터링 스레드 시작
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop, args=(plugin_id,), daemon=True
            )
            self.monitor_thread.start()

            print(f"🚀 {plugin_id} 플러그인 성능 모니터링이 시작되었습니다.")
            print(f"📊 모니터링 간격: {interval}초")
            return True

        except Exception as e:
            print(f"❌ 성능 모니터링 시작 실패: {e}")
            return False

    def stop_monitoring(self) -> Dict[str, Any]:
        """성능 모니터링 중지"""
        try:
            self.monitoring_active = False

            if hasattr(self, "monitor_thread"):
                self.monitor_thread.join(timeout=5)

            # 최종 통계 계산
            summary = self._calculate_performance_summary()

            print("✅ 성능 모니터링이 중지되었습니다.")
            return summary

        except Exception as e:
            print(f"❌ 성능 모니터링 중지 실패: {e}")
            return {"error": str(e)}

    def _monitor_loop(self, plugin_id: str):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                # 성능 지표 수집
                metrics = self._collect_metrics(plugin_id)

                # 히스토리에 저장
                self._store_metrics(plugin_id, metrics)

                # 알림 체크
                self._check_alerts(plugin_id, metrics)

                # 히스토리 크기 제한
                self._limit_history_size()

                time.sleep(self.monitoring_interval)

            except Exception as e:
                print(f"❌ 모니터링 루프 오류: {e}")
                time.sleep(self.monitoring_interval)

    def _collect_metrics(self, plugin_id: str) -> PerformanceMetrics:
        """성능 지표 수집"""
        try:
            # 현재 프로세스 정보
            process = psutil.Process()

            # CPU 사용량
            cpu_percent = process.cpu_percent(interval=0.1)

            # 메모리 사용량
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()

            # 스레드 수
            thread_count = process.num_threads()

            # 열린 파일 수
            open_files = len(process.open_files())

            # 네트워크 연결 수
            network_connections = len(process.connections())

            # 디스크 I/O
            disk_io = process.io_counters()

            return PerformanceMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=cpu_percent,
                memory_rss=memory_info.rss / 1024 / 1024,  # MB
                memory_vms=memory_info.vms / 1024 / 1024,  # MB
                memory_percent=memory_percent,
                thread_count=thread_count,
                open_files=open_files,
                network_connections=network_connections,
                disk_io_read=disk_io.read_bytes / 1024 / 1024,  # MB
                disk_io_write=disk_io.write_bytes / 1024 / 1024,  # MB
            )

        except Exception as e:
            print(f"❌ 성능 지표 수집 오류: {e}")
            # 기본값 반환
            return PerformanceMetrics(
                timestamp=datetime.utcnow().isoformat(),
                cpu_percent=0.0,
                memory_rss=0.0,
                memory_vms=0.0,
                memory_percent=0.0,
                thread_count=0,
                open_files=0,
                network_connections=0,
                disk_io_read=0.0,
                disk_io_write=0.0,
            )

    def _store_metrics(self, plugin_id: str, metrics: PerformanceMetrics):
        """성능 지표 저장"""
        metrics_dict = asdict(metrics)

        for key, value in metrics_dict.items():
            if key != "timestamp":
                self.metrics_history[f"{plugin_id}_{key}"].append(
                    {"timestamp": metrics.timestamp, "value": value}
                )

    def _check_alerts(self, plugin_id: str, metrics: PerformanceMetrics):
        """알림 체크"""
        alerts = []

        # CPU 사용량 알림
        if metrics.cpu_percent > self.alert_thresholds["cpu_percent"]:
            alerts.append(
                {
                    "type": "cpu_high",
                    "message": f"CPU 사용량이 높습니다: {metrics.cpu_percent:.1f}%",
                    "value": metrics.cpu_percent,
                    "threshold": self.alert_thresholds["cpu_percent"],
                }
            )

        # 메모리 사용량 알림
        if metrics.memory_percent > self.alert_thresholds["memory_percent"]:
            alerts.append(
                {
                    "type": "memory_high",
                    "message": f"메모리 사용량이 높습니다: {metrics.memory_percent:.1f}%",
                    "value": metrics.memory_percent,
                    "threshold": self.alert_thresholds["memory_percent"],
                }
            )

        if metrics.memory_rss > self.alert_thresholds["memory_rss_mb"]:
            alerts.append(
                {
                    "type": "memory_rss_high",
                    "message": f"메모리 RSS가 높습니다: {metrics.memory_rss:.1f}MB",
                    "value": metrics.memory_rss,
                    "threshold": self.alert_thresholds["memory_rss_mb"],
                }
            )

        # 스레드 수 알림
        if metrics.thread_count > self.alert_thresholds["thread_count"]:
            alerts.append(
                {
                    "type": "thread_high",
                    "message": f"스레드 수가 많습니다: {metrics.thread_count}",
                    "value": metrics.thread_count,
                    "threshold": self.alert_thresholds["thread_count"],
                }
            )

        # 알림 콜백 실행
        for alert in alerts:
            for callback in self.alert_callbacks:
                try:
                    callback(plugin_id, alert)
                except Exception as e:
                    print(f"❌ 알림 콜백 실행 오류: {e}")

    def _limit_history_size(self):
        """히스토리 크기 제한"""
        for key in self.metrics_history:
            while len(self.metrics_history[key]) > self.max_history_size:
                self.metrics_history[key].popleft()

    def add_alert_callback(self, callback: Callable[[str, Dict], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)

    def set_alert_thresholds(self, thresholds: Dict[str, float]):
        """알림 임계값 설정"""
        self.alert_thresholds.update(thresholds)

    def get_current_metrics(self, plugin_id: str) -> Optional[PerformanceMetrics]:
        """현재 성능 지표 조회"""
        try:
            # 가장 최근 지표 찾기
            latest_timestamp = None
            latest_metrics = None

            for key in self.metrics_history:
                if key.startswith(f"{plugin_id}_"):
                    if self.metrics_history[key]:
                        entry = self.metrics_history[key][-1]
                        if (
                            latest_timestamp is None
                            or entry["timestamp"] > latest_timestamp
                        ):
                            latest_timestamp = entry["timestamp"]
                            latest_metrics = self._reconstruct_metrics(
                                plugin_id, latest_timestamp
                            )

            return latest_metrics

        except Exception as e:
            print(f"❌ 현재 지표 조회 오류: {e}")
            return None

    def _reconstruct_metrics(
        self, plugin_id: str, timestamp: str
    ) -> PerformanceMetrics:
        """타임스탬프로부터 성능 지표 재구성"""
        metrics_data = {}

        for key in self.metrics_history:
            if key.startswith(f"{plugin_id}_"):
                metric_name = key.replace(f"{plugin_id}_", "")

                # 해당 타임스탬프의 값 찾기
                for entry in self.metrics_history[key]:
                    if entry["timestamp"] == timestamp:
                        metrics_data[metric_name] = entry["value"]
                        break

        return PerformanceMetrics(
            timestamp=timestamp,
            cpu_percent=metrics_data.get("cpu_percent", 0.0),
            memory_rss=metrics_data.get("memory_rss", 0.0),
            memory_vms=metrics_data.get("memory_vms", 0.0),
            memory_percent=metrics_data.get("memory_percent", 0.0),
            thread_count=metrics_data.get("thread_count", 0),
            open_files=metrics_data.get("open_files", 0),
            network_connections=metrics_data.get("network_connections", 0),
            disk_io_read=metrics_data.get("disk_io_read", 0.0),
            disk_io_write=metrics_data.get("disk_io_write", 0.0),
        )

    def get_metrics_history(
        self, plugin_id: str, metric_name: str, hours: int = 1
    ) -> List[Dict[str, Any]]:
        """성능 지표 히스토리 조회"""
        try:
            key = f"{plugin_id}_{metric_name}"
            if key not in self.metrics_history:
                return []

            # 시간 범위 계산
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)

            history = []
            for entry in self.metrics_history[key]:
                entry_time = datetime.fromisoformat(
                    entry["timestamp"].replace("Z", "+00:00")
                )
                if entry_time >= cutoff_time:
                    history.append(entry)

            return history

        except Exception as e:
            print(f"❌ 히스토리 조회 오류: {e}")
            return []

    def _calculate_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 계산"""
        try:
            summary = {
                "monitoring_duration": 0,
                "total_samples": 0,
                "average_metrics": {},
                "peak_metrics": {},
                "alert_count": 0,
            }

            if not self.metrics_history:
                return summary

            # 모든 플러그인 ID 수집
            plugin_ids = set()
            for key in self.metrics_history:
                if "_" in key:
                    plugin_id = key.split("_")[0]
                    plugin_ids.add(plugin_id)

            for plugin_id in plugin_ids:
                plugin_summary = self._calculate_plugin_summary(plugin_id)
                summary[plugin_id] = plugin_summary

                # 전체 통계 업데이트
                summary["total_samples"] += plugin_summary.get("total_samples", 0)

            return summary

        except Exception as e:
            print(f"❌ 성능 요약 계산 오류: {e}")
            return {"error": str(e)}

    def _calculate_plugin_summary(self, plugin_id: str) -> Dict[str, Any]:
        """플러그인별 성능 요약 계산"""
        try:
            summary = {
                "total_samples": 0,
                "average_metrics": {},
                "peak_metrics": {},
                "min_metrics": {},
            }

            metric_names = [
                "cpu_percent",
                "memory_rss",
                "memory_percent",
                "thread_count",
            ]

            for metric_name in metric_names:
                key = f"{plugin_id}_{metric_name}"
                if key in self.metrics_history and self.metrics_history[key]:
                    values = [entry["value"] for entry in self.metrics_history[key]]

                    if values:
                        summary["total_samples"] = len(values)
                        summary["average_metrics"][metric_name] = sum(values) / len(
                            values
                        )
                        summary["peak_metrics"][metric_name] = max(values)
                        summary["min_metrics"][metric_name] = min(values)

            return summary

        except Exception as e:
            print(f"❌ 플러그인 요약 계산 오류: {e}")
            return {"error": str(e)}

    def generate_performance_report(
        self, plugin_id: str, output_format: str = "json"
    ) -> str:
        """성능 리포트 생성"""
        try:
            # 현재 지표
            current_metrics = self.get_current_metrics(plugin_id)

            # 히스토리 데이터 (최근 1시간)
            cpu_history = self.get_metrics_history(plugin_id, "cpu_percent", 1)
            memory_history = self.get_metrics_history(plugin_id, "memory_rss", 1)

            # 성능 요약
            summary = self._calculate_plugin_summary(plugin_id)

            report = {
                "plugin_id": plugin_id,
                "generated_at": datetime.utcnow().isoformat(),
                "current_metrics": asdict(current_metrics) if current_metrics else None,
                "performance_summary": summary,
                "history_samples": {
                    "cpu_percent": len(cpu_history),
                    "memory_rss": len(memory_history),
                },
            }

            # 출력 형식에 따라 처리
            if output_format == "json":
                report_path = (
                    Path("logs")
                    / f"performance_report_{plugin_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
                )
                with open(report_path, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)

                return str(report_path)

            elif output_format == "html":
                return self._generate_html_report(report)

            else:
                return json.dumps(report, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"❌ 성능 리포트 생성 오류: {e}")
            return ""

    def _generate_html_report(self, report: Dict[str, Any]) -> str:
        """HTML 리포트 생성"""
        try:
            html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>성능 리포트 - {report['plugin_id']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .metric {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
        .current {{ background-color: #f0f8ff; }}
        .summary {{ background-color: #f0fff0; }}
        .history {{ background-color: #fff8f0; }}
    </style>
</head>
<body>
    <h1>성능 리포트 - {report['plugin_id']}</h1>
    <p>생성 시간: {report['generated_at']}</p>
    
    <div class="metric current">
        <h2>현재 지표</h2>
        <pre>{json.dumps(report['current_metrics'], indent=2, ensure_ascii=False)}</pre>
    </div>
    
    <div class="metric summary">
        <h2>성능 요약</h2>
        <pre>{json.dumps(report['performance_summary'], indent=2, ensure_ascii=False)}</pre>
    </div>
    
    <div class="metric history">
        <h2>히스토리 샘플</h2>
        <pre>{json.dumps(report['history_samples'], indent=2, ensure_ascii=False)}</pre>
    </div>
</body>
</html>
"""

            report_path = (
                Path("logs")
                / f"performance_report_{report['plugin_id']}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.html"
            )
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            return str(report_path)

        except Exception as e:
            print(f"❌ HTML 리포트 생성 오류: {e}")
            return ""

    def detect_memory_leak(
        self, plugin_id: str, threshold: float = 0.1
    ) -> Dict[str, Any]:
        """메모리 누수 감지"""
        try:
            memory_history = self.get_metrics_history(
                plugin_id, "memory_rss", 24
            )  # 24시간

            if len(memory_history) < 10:
                return {"detected": False, "reason": "충분한 데이터가 없습니다."}

            # 메모리 사용량 추세 분석
            timestamps = [
                datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
                for entry in memory_history
            ]
            values = [entry["value"] for entry in memory_history]

            # 선형 회귀로 추세 계산
            x = [(t - timestamps[0]).total_seconds() for t in timestamps]
            y = values

            if len(x) > 1:
                # 간단한 선형 회귀 계산
                n = len(x)
                sum_x = sum(x)
                sum_y = sum(y)
                sum_xy = sum(x[i] * y[i] for i in range(n))
                sum_x2 = sum(x[i] * x[i] for i in range(n))

                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)

                # 메모리 증가율 계산 (MB/시간)
                growth_rate = slope * 3600  # 시간당 증가량

                leak_detected = growth_rate > threshold

                return {
                    "detected": leak_detected,
                    "growth_rate_mb_per_hour": growth_rate,
                    "threshold": threshold,
                    "analysis_period_hours": 24,
                    "data_points": len(memory_history),
                    "trend": "increasing" if growth_rate > 0 else "decreasing",
                }
            else:
                return {"detected": False, "reason": "데이터 포인트가 부족합니다."}

        except Exception as e:
            print(f"❌ 메모리 누수 감지 오류: {e}")
            return {"detected": False, "error": str(e)}

    def find_performance_bottlenecks(self, plugin_id: str) -> List[Dict[str, Any]]:
        """성능 병목 지점 찾기"""
        try:
            bottlenecks = []

            # CPU 병목 체크
            cpu_history = self.get_metrics_history(plugin_id, "cpu_percent", 1)
            if cpu_history:
                cpu_values = [entry["value"] for entry in cpu_history]
                avg_cpu = sum(cpu_values) / len(cpu_values)
                max_cpu = max(cpu_values)

                if avg_cpu > 70:
                    bottlenecks.append(
                        {
                            "type": "cpu_high_average",
                            "severity": "high" if avg_cpu > 90 else "medium",
                            "message": f"CPU 평균 사용량이 높습니다: {avg_cpu:.1f}%",
                            "value": avg_cpu,
                            "threshold": 70,
                        }
                    )

                if max_cpu > 95:
                    bottlenecks.append(
                        {
                            "type": "cpu_peak",
                            "severity": "critical",
                            "message": f"CPU 사용량이 최고점에 도달했습니다: {max_cpu:.1f}%",
                            "value": max_cpu,
                            "threshold": 95,
                        }
                    )

            # 메모리 병목 체크
            memory_history = self.get_metrics_history(plugin_id, "memory_rss", 1)
            if memory_history:
                memory_values = [entry["value"] for entry in memory_history]
                avg_memory = sum(memory_values) / len(memory_values)
                max_memory = max(memory_values)

                if avg_memory > 500:  # 500MB
                    bottlenecks.append(
                        {
                            "type": "memory_high_average",
                            "severity": "high" if avg_memory > 1000 else "medium",
                            "message": f"메모리 평균 사용량이 높습니다: {avg_memory:.1f}MB",
                            "value": avg_memory,
                            "threshold": 500,
                        }
                    )

                if max_memory > 1000:  # 1GB
                    bottlenecks.append(
                        {
                            "type": "memory_peak",
                            "severity": "critical",
                            "message": f"메모리 사용량이 최고점에 도달했습니다: {max_memory:.1f}MB",
                            "value": max_memory,
                            "threshold": 1000,
                        }
                    )

            # 스레드 병목 체크
            thread_history = self.get_metrics_history(plugin_id, "thread_count", 1)
            if thread_history:
                thread_values = [entry["value"] for entry in thread_history]
                avg_threads = sum(thread_values) / len(thread_values)
                max_threads = max(thread_values)

                if avg_threads > 50:
                    bottlenecks.append(
                        {
                            "type": "thread_high_average",
                            "severity": "medium",
                            "message": f"평균 스레드 수가 많습니다: {avg_threads:.1f}",
                            "value": avg_threads,
                            "threshold": 50,
                        }
                    )

                if max_threads > 100:
                    bottlenecks.append(
                        {
                            "type": "thread_peak",
                            "severity": "high",
                            "message": f"스레드 수가 최고점에 도달했습니다: {max_threads}",
                            "value": max_threads,
                            "threshold": 100,
                        }
                    )

            return bottlenecks

        except Exception as e:
            print(f"❌ 성능 병목 지점 찾기 오류: {e}")
            return []


def alert_callback(plugin_id: str, alert: Dict[str, Any]):
    """알림 콜백 함수"""
    print(f"🚨 {plugin_id} 플러그인 알림: {alert['message']}")


def main():
    """메인 함수"""
    monitor = PluginPerformanceMonitor()

    # 알림 콜백 등록
    monitor.add_alert_callback(alert_callback)

    print("📊 플러그인 성능 모니터링 도구")
    print("=" * 50)

    while True:
        print("\n사용 가능한 기능:")
        print("1. 성능 모니터링 시작")
        print("2. 성능 모니터링 중지")
        print("3. 현재 지표 조회")
        print("4. 히스토리 조회")
        print("5. 성능 리포트 생성")
        print("6. 메모리 누수 감지")
        print("7. 성능 병목 지점 찾기")
        print("8. 알림 임계값 설정")
        print("0. 종료")

        choice = input("\n선택 (0-8): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            plugin_id = input("플러그인 ID: ").strip()
            interval = input("모니터링 간격 (초, 기본값: 1): ").strip()
            interval = float(interval) if interval else 1.0
            monitor.start_monitoring(plugin_id, interval)
        elif choice == "2":
            summary = monitor.stop_monitoring()
            print(json.dumps(summary, indent=2, ensure_ascii=False))
        elif choice == "3":
            plugin_id = input("플러그인 ID: ").strip()
            metrics = monitor.get_current_metrics(plugin_id)
            if metrics:
                print(json.dumps(asdict(metrics), indent=2, ensure_ascii=False))
            else:
                print("현재 지표가 없습니다.")
        elif choice == "4":
            plugin_id = input("플러그인 ID: ").strip()
            metric_name = input("지표 이름 (예: cpu_percent): ").strip()
            hours = input("조회할 시간 (시간, 기본값: 1): ").strip()
            hours = int(hours) if hours.isdigit() else 1
            history = monitor.get_metrics_history(plugin_id, metric_name, hours)
            print(f"총 {len(history)}개 샘플")
            if history:
                print(
                    json.dumps(history[-5:], indent=2, ensure_ascii=False)
                )  # 최근 5개
        elif choice == "5":
            plugin_id = input("플러그인 ID: ").strip()
            format_choice = (
                input("출력 형식 (json/html/text, 기본값: json): ").strip() or "json"
            )
            report_path = monitor.generate_performance_report(plugin_id, format_choice)
            if report_path:
                print(f"📊 리포트 생성 완료: {report_path}")
        elif choice == "6":
            plugin_id = input("플러그인 ID: ").strip()
            threshold = input("임계값 (MB/시간, 기본값: 0.1): ").strip()
            threshold = float(threshold) if threshold else 0.1
            result = monitor.detect_memory_leak(plugin_id, threshold)
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif choice == "7":
            plugin_id = input("플러그인 ID: ").strip()
            bottlenecks = monitor.find_performance_bottlenecks(plugin_id)
            if bottlenecks:
                print(f"발견된 병목 지점: {len(bottlenecks)}개")
                for i, bottleneck in enumerate(bottlenecks, 1):
                    print(
                        f"{i}. [{bottleneck['severity'].upper()}] {bottleneck['message']}"
                    )
            else:
                print("병목 지점이 발견되지 않았습니다.")
        elif choice == "8":
            print("현재 임계값:")
            for key, value in monitor.alert_thresholds.items():
                print(f"  {key}: {value}")

            print("\n새 임계값 설정 (변경할 항목만 입력):")
            new_thresholds = {}

            cpu = input("CPU 임계값 (%): ").strip()
            if cpu:
                new_thresholds["cpu_percent"] = float(cpu)

            memory = input("메모리 임계값 (%): ").strip()
            if memory:
                new_thresholds["memory_percent"] = float(memory)

            memory_rss = input("메모리 RSS 임계값 (MB): ").strip()
            if memory_rss:
                new_thresholds["memory_rss_mb"] = float(memory_rss)

            thread = input("스레드 수 임계값: ").strip()
            if thread:
                new_thresholds["thread_count"] = int(thread)

            if new_thresholds:
                monitor.set_alert_thresholds(new_thresholds)
                print("✅ 임계값이 업데이트되었습니다.")
        else:
            print("❌ 잘못된 선택입니다.")


if __name__ == "__main__":
    main()
