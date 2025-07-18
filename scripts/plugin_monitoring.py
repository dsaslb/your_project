#!/usr/bin/env python3
"""
플러그인 모니터링 시스템
실시간 성능 추적, 리소스 사용량 모니터링, 오류 감지
"""

import time
import psutil
import threading
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Deque
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import sqlite3
import signal
import sys
import asyncio

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PluginMetrics:
    """플러그인 메트릭 데이터 클래스"""

    plugin_id: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.timestamp, datetime):
            ts = self.timestamp
            if isinstance(ts, str):
                try:
                    self.timestamp = datetime.fromisoformat(ts)
                except Exception:
                    try:
                        self.timestamp = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        self.timestamp = datetime.now()
            else:
                self.timestamp = datetime.now()


@dataclass
class PerformanceAlert:
    """성능 알림 데이터 클래스"""

    plugin_id: str
    alert_type: str  # 'slow_execution', 'high_memory', 'high_cpu', 'error_rate'
    severity: str  # 'low', 'medium', 'high', 'critical'
    message: str
    threshold: float
    current_value: float
    timestamp: datetime = field(default_factory=datetime.now)


class PluginMonitor:
    """플러그인 모니터링 클래스"""

    def __init__(self, db_path: str = "plugin_monitoring.db"):
        self.db_path = db_path
        self.metrics_history: Dict[str, Deque[PluginMetrics]] = defaultdict(
            lambda: deque(maxlen=1000)
        )
        self.alerts: List[PerformanceAlert] = []
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.alert_callbacks: List[Callable[[PerformanceAlert], None]] = []

        # 임계값 설정
        self.thresholds = {
            "execution_time": 30.0,  # 30초
            "memory_usage": 512.0,  # 512MB
            "cpu_usage": 80.0,  # 80%
            "error_rate": 0.1,  # 10%
        }

        self._init_database()
        self._setup_signal_handlers()

    def _init_database(self):
        """모니터링 데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS plugin_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        execution_time REAL,
                        memory_usage REAL,
                        cpu_usage REAL,
                        success BOOLEAN,
                        error_message TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        metadata TEXT
                    )
                """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS performance_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        plugin_id TEXT NOT NULL,
                        alert_type TEXT NOT NULL,
                        severity TEXT NOT NULL,
                        message TEXT NOT NULL,
                        threshold REAL,
                        current_value REAL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        resolved BOOLEAN DEFAULT FALSE
                    )
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_plugin_metrics_plugin_id 
                    ON plugin_metrics(plugin_id)
                """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_plugin_metrics_timestamp 
                    ON plugin_metrics(timestamp)
                """
                )

                conn.commit()
                logger.info("모니터링 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")

    def _setup_signal_handlers(self):
        """시그널 핸들러 설정"""

        def signal_handler(signum, frame):
            logger.info("모니터링 시스템 종료 신호 수신")
            self.stop_monitoring()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def start_monitoring(self):
        """모니터링 시작"""
        if self.monitoring_active:
            logger.warning("모니터링이 이미 실행 중입니다")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()
        logger.info("플러그인 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("플러그인 모니터링 중지")

    def _monitoring_loop(self):
        """모니터링 루프"""
        while self.monitoring_active:
            try:
                self._check_performance_alerts()
                self._cleanup_old_data()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"모니터링 루프 오류: {e}")
                time.sleep(10)

    def record_metrics(self, metrics: PluginMetrics):
        """플러그인 메트릭 기록"""
        try:
            # PluginMetrics 타입 보장 및 timestamp 보장
            assert isinstance(metrics, PluginMetrics)
            assert isinstance(metrics.timestamp, datetime)
            self.metrics_history[metrics.plugin_id].append(
                metrics
            )  # pyright: ignore[reportArgumentType]

            # 데이터베이스에 저장
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO plugin_metrics 
                    (plugin_id, execution_time, memory_usage, cpu_usage, success, error_message, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        metrics.plugin_id,
                        metrics.execution_time,
                        metrics.memory_usage,
                        metrics.cpu_usage,
                        metrics.success,
                        metrics.error_message,
                        json.dumps(metrics.metadata),
                        metrics.timestamp.isoformat(),
                    ),
                )
                conn.commit()

            # 성능 임계값 체크
            self._check_thresholds(metrics)

        except Exception as e:
            logger.error(f"메트릭 기록 실패: {e}")

    def _check_thresholds(self, metrics: PluginMetrics):
        """성능 임계값 체크"""
        alerts = []

        # 실행 시간 체크
        if metrics.execution_time > self.thresholds["execution_time"]:
            alerts.append(
                PerformanceAlert(
                    plugin_id=metrics.plugin_id,
                    alert_type="slow_execution",
                    severity=(
                        "high"
                        if metrics.execution_time
                        > self.thresholds["execution_time"] * 2
                        else "medium"
                    ),
                    message=f"플러그인 실행 시간이 임계값을 초과했습니다: {metrics.execution_time:.2f}초",
                    threshold=self.thresholds["execution_time"],
                    current_value=metrics.execution_time,
                )
            )

        # 메모리 사용량 체크
        if metrics.memory_usage > self.thresholds["memory_usage"]:
            alerts.append(
                PerformanceAlert(
                    plugin_id=metrics.plugin_id,
                    alert_type="high_memory",
                    severity=(
                        "high"
                        if metrics.memory_usage > self.thresholds["memory_usage"] * 1.5
                        else "medium"
                    ),
                    message=f"플러그인 메모리 사용량이 임계값을 초과했습니다: {metrics.memory_usage:.2f}MB",
                    threshold=self.thresholds["memory_usage"],
                    current_value=metrics.memory_usage,
                )
            )

        # CPU 사용량 체크
        if metrics.cpu_usage > self.thresholds["cpu_usage"]:
            alerts.append(
                PerformanceAlert(
                    plugin_id=metrics.plugin_id,
                    alert_type="high_cpu",
                    severity=(
                        "high"
                        if metrics.cpu_usage > self.thresholds["cpu_usage"] * 1.2
                        else "medium"
                    ),
                    message=f"플러그인 CPU 사용량이 임계값을 초과했습니다: {metrics.cpu_usage:.2f}%",
                    threshold=self.thresholds["cpu_usage"],
                    current_value=metrics.cpu_usage,
                )
            )

        # 오류 체크
        if not metrics.success:
            alerts.append(
                PerformanceAlert(
                    plugin_id=metrics.plugin_id,
                    alert_type="execution_error",
                    severity="critical",
                    message=f"플러그인 실행 오류: {metrics.error_message}",
                    threshold=0,
                    current_value=1,
                )
            )

        # 알림 저장 및 콜백 실행
        for alert in alerts:
            self._save_alert(alert)
            self._trigger_alert_callbacks(alert)

    def _save_alert(self, alert: PerformanceAlert):
        """알림 저장"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO performance_alerts 
                    (plugin_id, alert_type, severity, message, threshold, current_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    (
                        alert.plugin_id,
                        alert.alert_type,
                        alert.severity,
                        alert.message,
                        alert.threshold,
                        alert.current_value,
                    ),
                )
                conn.commit()

            self.alerts.append(alert)
            logger.warning(f"성능 알림: {alert.message}")

        except Exception as e:
            logger.error(f"알림 저장 실패: {e}")

    def _trigger_alert_callbacks(self, alert: PerformanceAlert):
        """알림 콜백 실행"""
        for callback in self.alert_callbacks:
            try:
                # 비동기 함수인지 확인
                if asyncio.iscoroutinefunction(callback):
                    try:
                        # loop = asyncio.get_running_loop()  # 미사용 변수 제거
                        asyncio.create_task(callback(alert))
                    except RuntimeError:
                        logger.debug("이벤트 루프가 없어 비동기 콜백을 건너뜁니다")
                else:
                    callback(alert)
            except Exception as e:
                logger.error(f"알림 콜백 실행 실패: {e}")

    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """알림 콜백 추가"""
        self.alert_callbacks.append(callback)

    def _check_performance_alerts(self):
        """성능 알림 체크 (주기적)"""
        try:
            # 최근 1시간 동안의 메트릭 분석
            one_hour_ago = datetime.now() - timedelta(hours=1)

            for plugin_id, metrics in self.metrics_history.items():
                recent_metrics = [m for m in metrics if m.timestamp > one_hour_ago]

                if not recent_metrics:
                    continue

                # 오류율 계산
                error_count = sum(1 for m in recent_metrics if not m.success)
                error_rate = error_count / len(recent_metrics)

                if error_rate > self.thresholds["error_rate"]:
                    alert = PerformanceAlert(
                        plugin_id=plugin_id,
                        alert_type="high_error_rate",
                        severity="critical" if error_rate > 0.3 else "high",
                        message=f"플러그인 오류율이 높습니다: {error_rate:.2%}",
                        threshold=self.thresholds["error_rate"],
                        current_value=error_rate,
                    )
                    self._save_alert(alert)
                    self._trigger_alert_callbacks(alert)

                # 평균 실행 시간 체크
                avg_execution_time = sum(
                    m.execution_time for m in recent_metrics
                ) / len(recent_metrics)
                if avg_execution_time > self.thresholds["execution_time"]:
                    alert = PerformanceAlert(
                        plugin_id=plugin_id,
                        alert_type="consistently_slow",
                        severity="medium",
                        message=f"플러그인 평균 실행 시간이 높습니다: {avg_execution_time:.2f}초",
                        threshold=self.thresholds["execution_time"],
                        current_value=avg_execution_time,
                    )
                    self._save_alert(alert)
                    self._trigger_alert_callbacks(alert)

        except Exception as e:
            logger.error(f"성능 알림 체크 실패: {e}")

    def _cleanup_old_data(self):
        """오래된 데이터 정리"""
        try:
            # 30일 이전 데이터 삭제
            thirty_days_ago = datetime.now() - timedelta(days=30)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "DELETE FROM plugin_metrics WHERE timestamp < ?", (thirty_days_ago,)
                )
                conn.execute(
                    "DELETE FROM performance_alerts WHERE timestamp < ? AND resolved = TRUE",
                    (thirty_days_ago,),
                )
                conn.commit()

            logger.info("오래된 모니터링 데이터 정리 완료")

        except Exception as e:
            logger.error(f"데이터 정리 실패: {e}")

    def get_plugin_metrics(
        self, plugin_id: str, hours: int = 24
    ) -> List[PluginMetrics]:
        """플러그인 메트릭 조회"""
        try:
            since = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT * FROM plugin_metrics 
                    WHERE plugin_id = ? AND timestamp > ?
                    ORDER BY timestamp DESC
                """,
                    (plugin_id, since),
                )

                metrics = []
                for row in cursor.fetchall():
                    ts = row["timestamp"]
                    if isinstance(ts, str):
                        try:
                            ts_dt = datetime.fromisoformat(ts)
                        except Exception:
                            ts_dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
                    else:
                        ts_dt = ts
                    metrics.append(
                        PluginMetrics(
                            plugin_id=row["plugin_id"],
                            execution_time=row["execution_time"],
                            memory_usage=row["memory_usage"],
                            cpu_usage=row["cpu_usage"],
                            success=bool(row["success"]),
                            error_message=row["error_message"],
                            timestamp=ts_dt,
                            metadata=(
                                json.loads(row["metadata"]) if row["metadata"] else {}
                            ),
                        )
                    )

                return metrics

        except Exception as e:
            logger.error(f"메트릭 조회 실패: {e}")
            return []

    def get_performance_summary(
        self, plugin_id: str, hours: int = 24
    ) -> Dict[str, Any]:
        """성능 요약 정보 조회"""
        metrics = self.get_plugin_metrics(plugin_id, hours)

        if not metrics:
            return {
                "plugin_id": plugin_id,
                "total_executions": 0,
                "success_rate": 0.0,
                "avg_execution_time": 0.0,
                "avg_memory_usage": 0.0,
                "avg_cpu_usage": 0.0,
                "error_count": 0,
            }

        total_executions = len(metrics)
        success_count = sum(1 for m in metrics if m.success)
        success_rate = success_count / total_executions

        avg_execution_time = sum(m.execution_time for m in metrics) / total_executions
        avg_memory_usage = sum(m.memory_usage for m in metrics) / total_executions
        avg_cpu_usage = sum(m.cpu_usage for m in metrics) / total_executions
        error_count = total_executions - success_count

        return {
            "plugin_id": plugin_id,
            "total_executions": total_executions,
            "success_rate": success_rate,
            "avg_execution_time": avg_execution_time,
            "avg_memory_usage": avg_memory_usage,
            "avg_cpu_usage": avg_cpu_usage,
            "error_count": error_count,
        }

    def get_active_alerts(
        self, severity: Optional[str] = None
    ) -> List[PerformanceAlert]:
        """활성 알림 조회"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM performance_alerts WHERE resolved = FALSE"
                params = []

                if severity:
                    query += " AND severity = ?"
                    params.append(severity)

                query += " ORDER BY timestamp DESC"

                cursor = conn.execute(query, params)

                alerts = []
                for row in cursor.fetchall():
                    # timestamp 문자열을 datetime 객체로 변환
                    ts_str = row["timestamp"]
                    if isinstance(ts_str, str):
                        try:
                            ts_obj = datetime.fromisoformat(ts_str)
                        except ValueError:
                            ts_obj = datetime.now()
                    else:
                        ts_obj = datetime.now()

                    # 타입 안전성 강제 보장
                    alert = PerformanceAlert(
                        plugin_id=row["plugin_id"],
                        alert_type=row["alert_type"],
                        severity=row["severity"],
                        message=row["message"],
                        threshold=row["threshold"],
                        current_value=row["current_value"],
                        timestamp=ts_obj,
                    )
                    alerts.append(alert)  # pyright: ignore[reportArgumentType]

                return alerts

        except Exception as e:
            logger.error(f"알림 조회 실패: {e}")
            return []

    def resolve_alert(self, alert_id: int):
        """알림 해결 처리"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "UPDATE performance_alerts SET resolved = TRUE WHERE id = ?",
                    (alert_id,),
                )
                conn.commit()

            logger.info(f"알림 해결 처리 완료: ID {alert_id}")

        except Exception as e:
            logger.error(f"알림 해결 처리 실패: {e}")

    def update_thresholds(self, **kwargs):
        """임계값 업데이트"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                logger.info(f"임계값 업데이트: {key} = {value}")

    def export_metrics(
        self, output_path: str, plugin_id: Optional[str] = None, hours: int = 24
    ):
        """메트릭 데이터 내보내기"""
        try:
            since = datetime.now() - timedelta(hours=hours)

            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row

                query = "SELECT * FROM plugin_metrics WHERE timestamp > ?"
                params = [since]

                if plugin_id:
                    query += " AND plugin_id = ?"
                    params.append(plugin_id)

                query += " ORDER BY timestamp DESC"

                cursor = conn.execute(query, params)

                data = []
                for row in cursor.fetchall():
                    data.append(
                        {
                            "plugin_id": row["plugin_id"],
                            "execution_time": row["execution_time"],
                            "memory_usage": row["memory_usage"],
                            "cpu_usage": row["cpu_usage"],
                            "success": bool(row["success"]),
                            "error_message": row["error_message"],
                            "timestamp": row["timestamp"],
                            "metadata": (
                                json.loads(row["metadata"]) if row["metadata"] else {}
                            ),
                        }
                    )

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"메트릭 데이터 내보내기 완료: {output_path}")

        except Exception as e:
            logger.error(f"메트릭 데이터 내보내기 실패: {e}")


# 데코레이터로 플러그인 모니터링 적용
def monitor_plugin(monitor: PluginMonitor):
    """플러그인 모니터링 데코레이터"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.cpu_percent()

            success = False
            error_message = None

            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                error_message = str(e)
                raise
            finally:
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                end_cpu = psutil.cpu_percent()

                execution_time = end_time - start_time
                memory_usage = end_memory - start_memory
                # (2) cpu_usage 계산에서 리스트 연산 방지
                cpu_usage = (
                    float(start_cpu + end_cpu) / 2.0
                    if isinstance(start_cpu, (int, float))
                    and isinstance(end_cpu, (int, float))
                    else 0.0
                )

                # 플러그인 ID 추출 (첫 번째 인자가 플러그인 객체라고 가정)
                plugin_id = "unknown"
                if args and hasattr(args[0], "plugin_id"):
                    plugin_id = args[0].plugin_id
                elif "plugin_id" in kwargs:
                    plugin_id = kwargs["plugin_id"]

                metrics = PluginMetrics(
                    plugin_id=plugin_id,
                    execution_time=execution_time,
                    memory_usage=memory_usage,
                    cpu_usage=cpu_usage,
                    success=success,
                    error_message=error_message,
                    metadata={
                        "function_name": func.__name__,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs),
                    },
                )

                monitor.record_metrics(metrics)

        return wrapper

    return decorator


# CLI 인터페이스
def main():
    """CLI 메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="플러그인 모니터링 시스템")
    parser.add_argument(
        "--db-path", default="plugin_monitoring.db", help="데이터베이스 경로"
    )
    parser.add_argument("--start", action="store_true", help="모니터링 시작")
    parser.add_argument("--stop", action="store_true", help="모니터링 중지")
    parser.add_argument("--status", action="store_true", help="모니터링 상태 확인")
    parser.add_argument("--summary", metavar="PLUGIN_ID", help="플러그인 성능 요약")
    parser.add_argument(
        "--alerts",
        choices=["all", "critical", "high", "medium", "low"],
        help="알림 조회",
    )
    parser.add_argument(
        "--export", metavar="OUTPUT_PATH", help="메트릭 데이터 내보내기"
    )
    parser.add_argument("--hours", type=int, default=24, help="조회 기간 (시간)")

    args = parser.parse_args()

    monitor = PluginMonitor(args.db_path)

    if args.start:
        monitor.start_monitoring()
        print("모니터링이 시작되었습니다. Ctrl+C로 중지하세요.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()

    elif args.stop:
        monitor.stop_monitoring()
        print("모니터링이 중지되었습니다.")

    elif args.status:
        print(f"모니터링 상태: {'실행 중' if monitor.monitoring_active else '중지됨'}")
        print(f"데이터베이스: {args.db_path}")
        print(f"임계값: {monitor.thresholds}")

    elif args.summary:
        summary = monitor.get_performance_summary(args.summary, args.hours)
        print(f"\n=== {args.summary} 성능 요약 (최근 {args.hours}시간) ===")
        print(f"총 실행 횟수: {summary['total_executions']}")
        print(f"성공률: {summary['success_rate']:.2%}")
        print(f"평균 실행 시간: {summary['avg_execution_time']:.2f}초")
        print(f"평균 메모리 사용량: {summary['avg_memory_usage']:.2f}MB")
        print(f"평균 CPU 사용량: {summary['avg_cpu_usage']:.2f}%")
        print(f"오류 횟수: {summary['error_count']}")

    elif args.alerts:
        severity = None if args.alerts == "all" else args.alerts
        alerts = monitor.get_active_alerts(severity)
        print(f"\n=== 활성 알림 ({len(alerts)}개) ===")
        for alert in alerts:
            print(f"[{alert.severity.upper()}] {alert.plugin_id}: {alert.message}")
            print(f"  임계값: {alert.threshold}, 현재값: {alert.current_value}")
            print(f"  시간: {alert.timestamp}")
            print()

    elif args.export:
        monitor.export_metrics(args.export, hours=args.hours)
        print(f"메트릭 데이터가 {args.export}에 내보내졌습니다.")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
