#!/usr/bin/env python3
"""
AI 시스템 최적화 스크립트
성능 모니터링, 자동 튜닝, 리소스 관리, 백업 및 복구, 배포 자동화
"""

import os
import sys
import time
import json
import logging
import subprocess
import psutil
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import shutil
import zipfile
import tarfile
from pathlib import Path
import yaml
import schedule

# AI 시스템 최적화 중지됨 (서버는 계속 실행)
raise SystemExit("AI 시스템 최적화 중지: 자동 튜닝 기능이 비활성화되었습니다.")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/ai_optimizer.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """시스템 메트릭"""

    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    process_count: int
    timestamp: datetime


@dataclass
class OptimizationAction:
    """최적화 액션"""

    action_type: str
    description: str
    impact: str  # low, medium, high
    execution_time: float
    success: bool
    timestamp: datetime


class SystemMonitor:
    """시스템 모니터링"""

    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "process_count": 1000,
        }

    def collect_metrics(self) -> SystemMetrics:
        """시스템 메트릭 수집"""
        try:
            # CPU 사용률
            cpu_usage = psutil.cpu_percent(interval=1)

            # 메모리 사용률
            memory = psutil.virtual_memory()
            memory_usage = memory.percent

            # 디스크 사용률
            disk = psutil.disk_usage("/")
            disk_usage = disk.percent

            # 네트워크 I/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv,
            }

            # 프로세스 수
            process_count = len(psutil.pids())

            metrics = SystemMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                process_count=process_count,
                timestamp=datetime.utcnow(),
            )

            self.metrics_history.append(metrics)

            # 최근 1000개만 유지
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]

            return metrics

        except Exception as e:
            logger.error(f"메트릭 수집 실패: {e}")
            return None

    def check_alerts(self, metrics: SystemMetrics) -> List[str]:
        """알림 확인"""
        alerts = []

        if metrics.cpu_usage > self.alert_thresholds["cpu_usage"]:
            alerts.append(f"CPU 사용률 높음: {metrics.cpu_usage:.1f}%")

        if metrics.memory_usage > self.alert_thresholds["memory_usage"]:
            alerts.append(f"메모리 사용률 높음: {metrics.memory_usage:.1f}%")

        if metrics.disk_usage > self.alert_thresholds["disk_usage"]:
            alerts.append(f"디스크 사용률 높음: {metrics.disk_usage:.1f}%")

        if metrics.process_count > self.alert_thresholds["process_count"]:
            alerts.append(f"프로세스 수 많음: {metrics.process_count}")

        return alerts

    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        if not self.metrics_history:
            return {}

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        recent_metrics = [m for m in self.metrics_history if m.timestamp > cutoff_time]

        if not recent_metrics:
            return {}

        # 평균값 계산
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m.disk_usage for m in recent_metrics) / len(recent_metrics)

        # 트렌드 분석
        if len(recent_metrics) > 1:
            cpu_trend = recent_metrics[-1].cpu_usage - recent_metrics[0].cpu_usage
            memory_trend = (
                recent_metrics[-1].memory_usage - recent_metrics[0].memory_usage
            )
            disk_trend = recent_metrics[-1].disk_usage - recent_metrics[0].disk_usage
        else:
            cpu_trend = memory_trend = disk_trend = 0

        return {
            "period_hours": hours,
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory,
            "avg_disk_usage": avg_disk,
            "cpu_trend": cpu_trend,
            "memory_trend": memory_trend,
            "disk_trend": disk_trend,
            "data_points": len(recent_metrics),
        }


class AutoTuner:
    """자동 튜닝 시스템"""

    def __init__(self):
        self.tuning_history = []
        self.optimization_rules = {
            "high_cpu": self._optimize_high_cpu,
            "high_memory": self._optimize_high_memory,
            "high_disk": self._optimize_high_disk,
            "process_cleanup": self._optimize_process_cleanup,
        }

    def analyze_and_tune(self, metrics: SystemMetrics) -> List[OptimizationAction]:
        """분석 및 튜닝"""
        actions = []

        # CPU 최적화
        if metrics.cpu_usage > 80:
            action = self._optimize_high_cpu(metrics)
            if action:
                actions.append(action)

        # 메모리 최적화
        if metrics.memory_usage > 85:
            action = self._optimize_high_memory(metrics)
            if action:
                actions.append(action)

        # 디스크 최적화
        if metrics.disk_usage > 90:
            action = self._optimize_high_disk(metrics)
            if action:
                actions.append(action)

        # 프로세스 정리
        if metrics.process_count > 1000:
            action = self._optimize_process_cleanup(metrics)
            if action:
                actions.append(action)

        return actions

    def _optimize_high_cpu(
        self, metrics: SystemMetrics
    ) -> Optional[OptimizationAction]:
        """높은 CPU 사용률 최적화"""
        try:
            start_time = time.time()

            # 무거운 프로세스 찾기
            heavy_processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent"]):
                try:
                    if proc.info["cpu_percent"] > 10:  # 10% 이상 사용하는 프로세스
                        heavy_processes.append(proc.info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # CPU 사용률이 높은 프로세스 재시작
            restarted_count = 0
            for proc_info in heavy_processes[:5]:  # 상위 5개만
                try:
                    proc = psutil.Process(proc_info["pid"])
                    if proc.cpu_percent() > 20:  # 20% 이상이면 재시작
                        proc.terminate()
                        restarted_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            execution_time = time.time() - start_time

            action = OptimizationAction(
                action_type="cpu_optimization",
                description=f"높은 CPU 사용률 최적화 (재시작된 프로세스: {restarted_count}개)",
                impact="medium",
                execution_time=execution_time,
                success=restarted_count > 0,
                timestamp=datetime.utcnow(),
            )

            self.tuning_history.append(action)
            return action

        except Exception as e:
            logger.error(f"CPU 최적화 실패: {e}")
            return None

    def _optimize_high_memory(
        self, metrics: SystemMetrics
    ) -> Optional[OptimizationAction]:
        """높은 메모리 사용률 최적화"""
        try:
            start_time = time.time()

            # 메모리 사용량이 높은 프로세스 찾기
            memory_hogs = []
            for proc in psutil.process_iter(["pid", "name", "memory_info"]):
                try:
                    mem_info = proc.info["memory_info"]
                    if mem_info.rss > 100 * 1024 * 1024:  # 100MB 이상
                        memory_hogs.append(
                            {
                                "pid": proc.info["pid"],
                                "name": proc.info["name"],
                                "memory_mb": mem_info.rss / 1024 / 1024,
                            }
                        )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # 메모리 캐시 정리
            if os.name == "posix":  # Linux/Unix
                try:
                    subprocess.run(["sync"], check=True)
                    with open("/proc/sys/vm/drop_caches", "w") as f:
                        f.write("3")
                except Exception as e:
                    logger.warning(f"메모리 캐시 정리 실패: {e}")

            execution_time = time.time() - start_time

            action = OptimizationAction(
                action_type="memory_optimization",
                description=f"메모리 최적화 (대용량 프로세스: {len(memory_hogs)}개)",
                impact="medium",
                execution_time=execution_time,
                success=True,
                timestamp=datetime.utcnow(),
            )

            self.tuning_history.append(action)
            return action

        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return None

    def _optimize_high_disk(
        self, metrics: SystemMetrics
    ) -> Optional[OptimizationAction]:
        """높은 디스크 사용률 최적화"""
        try:
            start_time = time.time()

            # 임시 파일 정리
            temp_dirs = ["/tmp", "/var/tmp", "temp", "logs"]
            cleaned_files = 0

            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    for root, dirs, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            try:
                                # 7일 이상 된 파일 삭제
                                if (
                                    os.path.getmtime(file_path)
                                    < time.time() - 7 * 24 * 3600
                                ):
                                    os.remove(file_path)
                                    cleaned_files += 1
                            except (OSError, PermissionError):
                                continue

            execution_time = time.time() - start_time

            action = OptimizationAction(
                action_type="disk_optimization",
                description=f"디스크 최적화 (정리된 파일: {cleaned_files}개)",
                impact="low",
                execution_time=execution_time,
                success=cleaned_files > 0,
                timestamp=datetime.utcnow(),
            )

            self.tuning_history.append(action)
            return action

        except Exception as e:
            logger.error(f"디스크 최적화 실패: {e}")
            return None

    def _optimize_process_cleanup(
        self, metrics: SystemMetrics
    ) -> Optional[OptimizationAction]:
        """프로세스 정리"""
        try:
            start_time = time.time()

            # 좀비 프로세스 정리
            zombie_count = 0
            for proc in psutil.process_iter(["pid", "status"]):
                try:
                    if proc.info["status"] == "zombie":
                        zombie_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            execution_time = time.time() - start_time

            action = OptimizationAction(
                action_type="process_cleanup",
                description=f"프로세스 정리 (좀비 프로세스: {zombie_count}개)",
                impact="low",
                execution_time=execution_time,
                success=True,
                timestamp=datetime.utcnow(),
            )

            self.tuning_history.append(action)
            return action

        except Exception as e:
            logger.error(f"프로세스 정리 실패: {e}")
            return None


class BackupManager:
    """백업 및 복구 관리"""

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self, source_paths: List[str], backup_name: str = None) -> str:
        """백업 생성"""
        try:
            if not backup_name:
                backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            backup_path = self.backup_dir / f"{backup_name}.tar.gz"

            with tarfile.open(backup_path, "w:gz") as tar:
                for source_path in source_paths:
                    if os.path.exists(source_path):
                        tar.add(source_path, arcname=os.path.basename(source_path))

            logger.info(f"백업 생성 완료: {backup_path}")
            return str(backup_path)

        except Exception as e:
            logger.error(f"백업 생성 실패: {e}")
            return None

    def restore_backup(self, backup_path: str, restore_dir: str = ".") -> bool:
        """백업 복구"""
        try:
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(restore_dir)

            logger.info(f"백업 복구 완료: {backup_path}")
            return True

        except Exception as e:
            logger.error(f"백업 복구 실패: {e}")
            return False

    def list_backups(self) -> List[Dict[str, Any]]:
        """백업 목록 조회"""
        backups = []

        for backup_file in self.backup_dir.glob("*.tar.gz"):
            stat = backup_file.stat()
            backups.append(
                {
                    "name": backup_file.name,
                    "size_mb": stat.st_size / 1024 / 1024,
                    "created_at": datetime.fromtimestamp(stat.st_mtime),
                    "path": str(backup_file),
                }
            )

        return sorted(backups, key=lambda x: x["created_at"], reverse=True)

    def cleanup_old_backups(self, keep_days: int = 30) -> int:
        """오래된 백업 정리"""
        cutoff_time = datetime.utcnow() - timedelta(days=keep_days)
        deleted_count = 0

        for backup_file in self.backup_dir.glob("*.tar.gz"):
            stat = backup_file.stat()
            if datetime.fromtimestamp(stat.st_mtime) < cutoff_time:
                try:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"오래된 백업 삭제: {backup_file}")
                except Exception as e:
                    logger.error(f"백업 삭제 실패: {e}")

        return deleted_count


class DeploymentAutomator:
    """배포 자동화"""

    def __init__(self, config_file: str = "deployment_config.yaml"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """설정 파일 로드"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return yaml.safe_load(f)
            else:
                # 기본 설정
                default_config = {
                    "deployment": {
                        "source_dir": "src",
                        "backup_before_deploy": True,
                        "restart_services": True,
                        "health_check_url": "http://localhost:5000/health",
                    },
                    "services": ["your_program", "ai_server"],
                }

                with open(self.config_file, "w") as f:
                    yaml.dump(default_config, f)

                return default_config

        except Exception as e:
            logger.error(f"설정 파일 로드 실패: {e}")
            return {}

    def deploy(self, version: str = None) -> bool:
        """배포 실행"""
        try:
            if not version:
                version = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

            logger.info(f"배포 시작: {version}")

            # 1. 백업 생성
            if self.config.get("deployment", {}).get("backup_before_deploy", True):
                backup_manager = BackupManager()
                source_paths = [self.config["deployment"]["source_dir"]]
                backup_path = backup_manager.create_backup(
                    source_paths, f"pre_deploy_{version}"
                )

            # 2. 서비스 중지
            if self.config.get("deployment", {}).get("restart_services", True):
                self._stop_services()

            # 3. 코드 업데이트 (실제로는 git pull 또는 파일 복사)
            logger.info("코드 업데이트 중...")
            time.sleep(2)  # 시뮬레이션

            # 4. 서비스 재시작
            if self.config.get("deployment", {}).get("restart_services", True):
                self._start_services()

            # 5. 헬스 체크
            health_check_url = self.config.get("deployment", {}).get("health_check_url")
            if health_check_url:
                success = self._health_check(health_check_url)
                if not success:
                    logger.error("헬스 체크 실패")
                    return False

            logger.info(f"배포 완료: {version}")
            return True

        except Exception as e:
            logger.error(f"배포 실패: {e}")
            return False

    def _stop_services(self):
        """서비스 중지"""
        services = self.config.get("services", [])

        for service in services:
            try:
                if os.name == "posix":
                    subprocess.run(["systemctl", "stop", service], check=True)
                else:
                    subprocess.run(["net", "stop", service], check=True)
                logger.info(f"서비스 중지: {service}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"서비스 중지 실패: {service} - {e}")

    def _start_services(self):
        """서비스 시작"""
        services = self.config.get("services", [])

        for service in services:
            try:
                if os.name == "posix":
                    subprocess.run(["systemctl", "start", service], check=True)
                else:
                    subprocess.run(["net", "start", service], check=True)
                logger.info(f"서비스 시작: {service}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"서비스 시작 실패: {service} - {e}")

    def _health_check(self, url: str, timeout: int = 30) -> bool:
        """헬스 체크"""
        try:
            import requests

            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"헬스 체크 실패: {e}")
            return False


class AISystemOptimizer:
    """AI 시스템 최적화 메인 클래스"""

    def __init__(self):
        self.monitor = SystemMonitor()
        self.tuner = AutoTuner()
        self.backup_manager = BackupManager()
        self.deployment_automator = DeploymentAutomator()
        self.running = False

    def start_monitoring(self, interval_seconds: int = 60):
        """모니터링 시작"""
        self.running = True

        def monitor_loop():
            while self.running:
                try:
                    # 메트릭 수집
                    metrics = self.monitor.collect_metrics()

                    if metrics:
                        # 알림 확인
                        alerts = self.monitor.check_alerts(metrics)
                        if alerts:
                            for alert in alerts:
                                logger.warning(f"시스템 알림: {alert}")

                        # 자동 튜닝
                        actions = self.tuner.analyze_and_tune(metrics)
                        for action in actions:
                            logger.info(f"최적화 액션: {action.description}")

                except Exception as e:
                    logger.error(f"모니터링 루프 오류: {e}")

                time.sleep(interval_seconds)

        # 백그라운드 스레드로 실행
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()

        logger.info("AI 시스템 모니터링 시작")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.running = False
        logger.info("AI 시스템 모니터링 중지")

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        current_metrics = self.monitor.collect_metrics()

        return {
            "current_metrics": {
                "cpu_usage": current_metrics.cpu_usage if current_metrics else 0,
                "memory_usage": current_metrics.memory_usage if current_metrics else 0,
                "disk_usage": current_metrics.disk_usage if current_metrics else 0,
                "process_count": (
                    current_metrics.process_count if current_metrics else 0
                ),
            },
            "performance_trends": self.monitor.get_performance_trends(),
            "recent_optimizations": [
                {
                    "action_type": action.action_type,
                    "description": action.description,
                    "success": action.success,
                    "timestamp": action.timestamp.isoformat(),
                }
                for action in self.tuner.tuning_history[-10:]  # 최근 10개
            ],
            "backups": self.backup_manager.list_backups()[:5],  # 최근 5개
        }

    def create_system_backup(self) -> str:
        """시스템 백업 생성"""
        source_paths = ["src", "api", "models", "config", "templates", "static"]

        return self.backup_manager.create_backup(source_paths)

    def deploy_update(self, version: str = None) -> bool:
        """시스템 업데이트 배포"""
        return self.deployment_automator.deploy(version)


def main():
    """메인 함수"""
    optimizer = AISystemOptimizer()

    # 스케줄링 설정
    schedule.every(5).minutes.do(optimizer.monitor.collect_metrics)
    schedule.every().day.at("02:00").do(optimizer.create_system_backup)
    schedule.every().week.do(optimizer.backup_manager.cleanup_old_backups)

    try:
        # 모니터링 시작
        optimizer.start_monitoring()

        # 스케줄러 루프
        while True:
            schedule.run_pending()
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("AI 시스템 최적화 중지")
        optimizer.stop_monitoring()
    except Exception as e:
        logger.error(f"AI 시스템 최적화 오류: {e}")
        optimizer.stop_monitoring()


if __name__ == "__main__":
    main()
