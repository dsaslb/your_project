#!/usr/bin/env python3
"""
플러그인 모니터링 시스템 시작 스크립트
"""

import sys
import os
import logging
import time
import threading
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.backend.plugin_monitoring import plugin_monitor
from core.backend.realtime_alert_server import start_alert_server, stop_alert_server

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/plugin_monitoring.log"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def simulate_plugin_metrics():
    """테스트용 플러그인 메트릭 시뮬레이션"""
    import random

    # 샘플 플러그인 등록
    sample_plugins = [
        ("analytics_plugin", "분석 플러그인"),
        ("notification_plugin", "알림 플러그인"),
        ("reporting_plugin", "리포팅 플러그인"),
        ("security_plugin", "보안 플러그인"),
        ("backup_plugin", "백업 플러그인"),
    ]

    for plugin_id, plugin_name in sample_plugins:
        plugin_monitor.register_plugin(plugin_id, plugin_name)

    logger.info(f"{len(sample_plugins)}개의 샘플 플러그인 등록됨")

    # 메트릭 시뮬레이션 루프
    while True:
        try:
            for plugin_id, plugin_name in sample_plugins:
                # 랜덤 메트릭 생성
                metrics = {
                    "cpu_usage": random.uniform(10, 95),  # 10-95%
                    "memory_usage": random.uniform(20, 90),  # 20-90%
                    "response_time": random.uniform(0.1, 8.0),  # 0.1-8초
                    "error_count": random.randint(0, 10),
                    "request_count": random.randint(10, 100),
                    "uptime": random.uniform(100, 86400),  # 100초-24시간
                }

                # 메트릭 업데이트
                plugin_monitor.update_metrics(plugin_id, metrics)

            # 30초 대기
            time.sleep(30)

        except KeyboardInterrupt:
            logger.info("메트릭 시뮬레이션 중지")
            break
        except Exception as e:
            logger.error(f"메트릭 시뮬레이션 오류: {e}")
            time.sleep(60)


def main():
    """메인 함수"""
    try:
        logger.info("플러그인 모니터링 시스템 시작")

        # 로그 디렉토리 생성
        os.makedirs("logs", exist_ok=True)

        # 플러그인 모니터링 시작
        plugin_monitor.start_monitoring()
        logger.info("플러그인 모니터링 시작됨")

        # WebSocket 알림 서버 시작
        alert_server_thread = start_alert_server()
        logger.info("WebSocket 알림 서버 시작됨")

        # 테스트용 메트릭 시뮬레이션 시작 (별도 스레드)
        simulation_thread = threading.Thread(
            target=simulate_plugin_metrics, daemon=True
        )
        simulation_thread.start()
        logger.info("메트릭 시뮬레이션 시작됨")

        # 메인 루프
        try:
            while True:
                # 현재 상태 출력
                active_alerts = plugin_monitor.get_active_alerts()
                all_metrics = plugin_monitor.get_all_metrics()

                logger.info(f"활성 알림: {len(active_alerts)}개")
                logger.info(f"모니터링 중인 플러그인: {len(all_metrics)}개")

                # 활성 알림이 있으면 출력
                for alert in active_alerts:
                    logger.warning(f"알림: {alert.plugin_name} - {alert.message}")

                # 60초 대기
                time.sleep(60)

        except KeyboardInterrupt:
            logger.info("사용자에 의해 중지됨")

    except Exception as e:
        logger.error(f"시스템 시작 오류: {e}")
        return 1
    finally:
        # 정리 작업
        logger.info("시스템 정리 중...")
        plugin_monitor.stop_monitoring()
        stop_alert_server()
        logger.info("플러그인 모니터링 시스템 종료")

    return 0


if __name__ == "__main__":
    exit(main())
