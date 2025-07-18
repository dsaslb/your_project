#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 최적화 스크립트
시스템 성능을 모니터링하고 최적화하는 도구
"""

import os
import sys
import time
import psutil
import sqlite3
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import queue

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/performance_optimizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    def __init__(self):
        self.metrics_queue = queue.Queue()
        self.optimization_rules = self.load_optimization_rules()
        self.performance_thresholds = {
            "cpu_usage": 80.0,  # CPU 사용률 임계값
            "memory_usage": 85.0,  # 메모리 사용률 임계값
            "disk_usage": 90.0,  # 디스크 사용률 임계값
            "response_time": 2.0,  # 응답시간 임계값 (초)
            "error_rate": 5.0,  # 에러율 임계값 (%)
        }

    def load_optimization_rules(self) -> Dict:
        """최적화 규칙 로드"""
        rules_file = "config/performance_rules.json"
        if os.path.exists(rules_file):
            try:
                with open(rules_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"최적화 규칙 로드 실패: {e}")

        # 기본 규칙
        return {
            "database": {
                "vacuum_interval": 24,  # 24시간마다 VACUUM
                "analyze_interval": 6,  # 6시간마다 ANALYZE
                "cache_size": 10000,  # SQLite 캐시 크기
                "temp_store": "memory",  # 임시 테이블을 메모리에 저장
            },
            "cache": {
                "max_size": 1000,  # 최대 캐시 항목 수
                "ttl": 3600,  # 캐시 TTL (초)
                "cleanup_interval": 300,  # 정리 간격 (초)
            },
            "logging": {
                "max_file_size": 10,  # 최대 로그 파일 크기 (MB)
                "backup_count": 5,  # 백업 파일 수
                "cleanup_interval": 24,  # 정리 간격 (시간)
            },
        }

    def collect_system_metrics(self) -> Dict:
        """시스템 메트릭 수집"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            metrics = {
                "timestamp": datetime.now().isoformat(),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_free": disk.free,
                "network_io": self.get_network_io(),
                "process_count": len(psutil.pids()),
            }

            self.metrics_queue.put(metrics)
            return metrics

        except Exception as e:
            logger.error(f"시스템 메트릭 수집 실패: {e}")
            return {}

    def get_network_io(self) -> Dict:
        """네트워크 I/O 정보 수집"""
        try:
            net_io = psutil.net_io_counters()
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
            }
        except Exception as e:
            logger.error(f"네트워크 I/O 수집 실패: {e}")
            return {}

    def optimize_database(self):
        """데이터베이스 최적화"""
        try:
            db_files = [
                "marketplace.db",
                "plugin_monitoring.db",
                "advanced_monitoring.db",
                "alerts.db",
                "security_monitor.db",
            ]

            for db_file in db_files:
                if os.path.exists(db_file):
                    self.optimize_sqlite_db(db_file)

        except Exception as e:
            logger.error(f"데이터베이스 최적화 실패: {e}")

    def optimize_sqlite_db(self, db_path: str):
        """SQLite 데이터베이스 최적화"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            # 설정 최적화
            cursor.execute(
                "PRAGMA cache_size = ?",
                (self.optimization_rules["database"]["cache_size"],),
            )
            cursor.execute(
                "PRAGMA temp_store = ?",
                (self.optimization_rules["database"]["temp_store"],),
            )
            cursor.execute("PRAGMA synchronous = NORMAL")
            cursor.execute("PRAGMA journal_mode = WAL")

            # 인덱스 분석
            cursor.execute("ANALYZE")

            # VACUUM (마지막 VACUUM 이후 24시간 경과 시)
            last_vacuum_file = f"{db_path}.last_vacuum"
            should_vacuum = False

            if os.path.exists(last_vacuum_file):
                with open(last_vacuum_file, "r") as f:
                    last_vacuum = datetime.fromisoformat(f.read().strip())
                if datetime.now() - last_vacuum > timedelta(
                    hours=self.optimization_rules["database"]["vacuum_interval"]
                ):
                    should_vacuum = True
            else:
                should_vacuum = True

            if should_vacuum:
                logger.info(f"{db_path} VACUUM 실행 중...")
                cursor.execute("VACUUM")
                with open(last_vacuum_file, "w") as f:
                    f.write(datetime.now().isoformat())
                logger.info(f"{db_path} VACUUM 완료")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"{db_path} 최적화 실패: {e}")

    def cleanup_logs(self):
        """로그 파일 정리"""
        try:
            log_dir = "logs"
            if not os.path.exists(log_dir):
                return

            max_size = (
                self.optimization_rules["logging"]["max_file_size"] * 1024 * 1024
            )  # MB to bytes
            backup_count = self.optimization_rules["logging"]["backup_count"]

            for filename in os.listdir(log_dir):
                if filename.endswith(".log"):
                    filepath = os.path.join(log_dir, filename)
                    file_size = os.path.getsize(filepath)

                    if file_size > max_size:
                        # 로그 파일 압축 및 백업
                        self.rotate_log_file(filepath, backup_count)

        except Exception as e:
            logger.error(f"로그 정리 실패: {e}")

    def rotate_log_file(self, filepath: str, backup_count: int):
        """로그 파일 로테이션"""
        try:
            import gzip
            import shutil

            # 기존 백업 파일들 삭제
            for i in range(backup_count, 0, -1):
                old_backup = f"{filepath}.{i}.gz"
                if os.path.exists(old_backup):
                    os.remove(old_backup)

            # 새 백업 생성
            with open(filepath, "rb") as f_in:
                with gzip.open(f"{filepath}.1.gz", "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 원본 파일 비우기
            with open(filepath, "w") as f:
                f.write("")

            logger.info(f"로그 파일 로테이션 완료: {filepath}")

        except Exception as e:
            logger.error(f"로그 파일 로테이션 실패: {e}")

    def optimize_cache(self):
        """캐시 최적화"""
        try:
            cache_dir = "cache"
            if not os.path.exists(cache_dir):
                return

            max_age = self.optimization_rules["cache"]["ttl"]
            cutoff_time = datetime.now() - timedelta(seconds=max_age)

            for filename in os.listdir(cache_dir):
                filepath = os.path.join(cache_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        logger.info(f"오래된 캐시 파일 삭제: {filepath}")

        except Exception as e:
            logger.error(f"캐시 최적화 실패: {e}")

    def check_performance_alerts(self, metrics: Dict) -> List[str]:
        """성능 알림 확인"""
        alerts = []

        if metrics.get("cpu_usage", 0) > self.performance_thresholds["cpu_usage"]:
            alerts.append(f"CPU 사용률이 높습니다: {metrics['cpu_usage']:.1f}%")

        if metrics.get("memory_usage", 0) > self.performance_thresholds["memory_usage"]:
            alerts.append(f"메모리 사용률이 높습니다: {metrics['memory_usage']:.1f}%")

        if metrics.get("disk_usage", 0) > self.performance_thresholds["disk_usage"]:
            alerts.append(f"디스크 사용률이 높습니다: {metrics['disk_usage']:.1f}%")

        return alerts

    def generate_performance_report(self) -> Dict:
        """성능 보고서 생성"""
        try:
            # 최근 메트릭 수집
            metrics_list = []
            while not self.metrics_queue.empty():
                try:
                    metrics_list.append(self.metrics_queue.get_nowait())
                except queue.Empty:
                    break

            if not metrics_list:
                return {}

            # 통계 계산
            cpu_usage = [m.get("cpu_usage", 0) for m in metrics_list]
            memory_usage = [m.get("memory_usage", 0) for m in metrics_list]

            report = {
                "timestamp": datetime.now().isoformat(),
                "metrics_count": len(metrics_list),
                "cpu": {
                    "average": sum(cpu_usage) / len(cpu_usage),
                    "max": max(cpu_usage),
                    "min": min(cpu_usage),
                },
                "memory": {
                    "average": sum(memory_usage) / len(memory_usage),
                    "max": max(memory_usage),
                    "min": min(memory_usage),
                },
                "alerts": (
                    self.check_performance_alerts(metrics_list[-1])
                    if metrics_list
                    else []
                ),
            }

            # 보고서 저장
            report_file = f"logs/performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            return report

        except Exception as e:
            logger.error(f"성능 보고서 생성 실패: {e}")
            return {}

    def run_optimization_cycle(self):
        """최적화 사이클 실행"""
        logger.info("성능 최적화 사이클 시작")

        # 시스템 메트릭 수집
        metrics = self.collect_system_metrics()

        # 성능 알림 확인
        alerts = self.check_performance_alerts(metrics)
        if alerts:
            for alert in alerts:
                logger.warning(f"성능 알림: {alert}")

        # 데이터베이스 최적화
        self.optimize_database()

        # 로그 정리
        self.cleanup_logs()

        # 캐시 최적화
        self.optimize_cache()

        # 성능 보고서 생성
        report = self.generate_performance_report()

        logger.info("성능 최적화 사이클 완료")
        return report


def main():
    """메인 함수"""
    optimizer = PerformanceOptimizer()

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "optimize":
            optimizer.run_optimization_cycle()
        elif command == "metrics":
            metrics = optimizer.collect_system_metrics()
            print(json.dumps(metrics, indent=2, ensure_ascii=False))
        elif command == "report":
            report = optimizer.generate_performance_report()
            print(json.dumps(report, indent=2, ensure_ascii=False))
        elif command == "monitor":
            # 지속적 모니터링
            while True:
                optimizer.run_optimization_cycle()
                time.sleep(300)  # 5분마다 실행
        else:
            print(
                "사용법: python performance_optimizer.py [optimize|metrics|report|monitor]"
            )
    else:
        # 기본 실행: 한 번 최적화
        optimizer.run_optimization_cycle()


if __name__ == "__main__":
    main()
