#!/usr/bin/env python3
"""
플러그인 모니터링과 실시간 알림 시스템 테스트 스크립트
실제 플러그인 메트릭을 시뮬레이션하여 시스템 동작 확인
"""

import time
import random
import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PluginMonitoringTester:
    """플러그인 모니터링 테스터"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_plugins = [
            {
                "id": "restaurant_management",
                "name": "레스토랑 관리 플러그인",
                "baseline_cpu": 30.0,
                "baseline_memory": 45.0,
                "baseline_response": 0.8,
                "baseline_error": 2.0,
            },
            {
                "id": "inventory_system",
                "name": "재고 관리 시스템",
                "baseline_cpu": 25.0,
                "baseline_memory": 35.0,
                "baseline_response": 0.5,
                "baseline_error": 1.5,
            },
            {
                "id": "order_processing",
                "name": "주문 처리 시스템",
                "baseline_cpu": 40.0,
                "baseline_memory": 50.0,
                "baseline_response": 1.2,
                "baseline_error": 3.0,
            },
            {
                "id": "analytics_engine",
                "name": "분석 엔진",
                "baseline_cpu": 60.0,
                "baseline_memory": 70.0,
                "baseline_response": 2.0,
                "baseline_error": 5.0,
            },
        ]

        self.test_scenarios = [
            "normal",  # 정상 상태
            "high_cpu",  # CPU 사용률 높음
            "high_memory",  # 메모리 사용률 높음
            "high_error",  # 에러율 높음
            "slow_response",  # 응답시간 느림
            "critical",  # 심각한 문제
        ]

        self.current_scenario = "normal"
        self.scenario_duration = 0

    def generate_plugin_metrics(self, plugin: Dict[str, Any]) -> Dict[str, Any]:
        """플러그인 메트릭 생성"""
        try:
            # 시나리오에 따른 메트릭 조정
            if self.current_scenario == "normal":
                cpu_variation = random.uniform(-10, 10)
                memory_variation = random.uniform(-8, 8)
                response_variation = random.uniform(-0.3, 0.3)
                error_variation = random.uniform(-1, 1)

            elif self.current_scenario == "high_cpu":
                cpu_variation = random.uniform(30, 50)
                memory_variation = random.uniform(-5, 5)
                response_variation = random.uniform(-0.2, 0.2)
                error_variation = random.uniform(-0.5, 0.5)

            elif self.current_scenario == "high_memory":
                cpu_variation = random.uniform(-5, 5)
                memory_variation = random.uniform(25, 35)
                response_variation = random.uniform(-0.2, 0.2)
                error_variation = random.uniform(-0.5, 0.5)

            elif self.current_scenario == "high_error":
                cpu_variation = random.uniform(-5, 5)
                memory_variation = random.uniform(-5, 5)
                response_variation = random.uniform(-0.2, 0.2)
                error_variation = random.uniform(8, 15)

            elif self.current_scenario == "slow_response":
                cpu_variation = random.uniform(-5, 5)
                memory_variation = random.uniform(-5, 5)
                response_variation = random.uniform(3, 8)
                error_variation = random.uniform(-0.5, 0.5)

            elif self.current_scenario == "critical":
                cpu_variation = random.uniform(40, 60)
                memory_variation = random.uniform(30, 40)
                response_variation = random.uniform(5, 10)
                error_variation = random.uniform(15, 25)

            else:
                cpu_variation = random.uniform(-10, 10)
                memory_variation = random.uniform(-8, 8)
                response_variation = random.uniform(-0.3, 0.3)
                error_variation = random.uniform(-1, 1)

            # 메트릭 계산
            cpu_usage = max(0, min(100, plugin["baseline_cpu"] + cpu_variation))
            memory_usage = max(
                0, min(100, plugin["baseline_memory"] + memory_variation)
            )
            response_time = max(0.1, plugin["baseline_response"] + response_variation)
            error_rate = max(0, min(100, plugin["baseline_error"] + error_variation))

            # 요청 수 증가
            request_count = random.randint(100, 1000)

            # 가동시간 증가
            uptime = random.uniform(3600, 86400)  # 1시간 ~ 24시간

            return {
                "plugin_name": plugin["name"],
                "cpu_usage": round(cpu_usage, 2),
                "memory_usage": round(memory_usage, 2),
                "response_time": round(response_time, 2),
                "error_rate": round(error_rate, 2),
                "request_count": request_count,
                "uptime": round(uptime, 2),
                "last_activity": datetime.utcnow().isoformat(),
                "status": "active",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"메트릭 생성 실패: {e}")
            return {}

    def send_plugin_metrics(self, plugin_id: str, metrics: Dict[str, Any]) -> bool:
        """플러그인 메트릭 전송"""
        try:
            url = f"{self.base_url}/api/enhanced-alerts/plugins/{plugin_id}/metrics"

            response = requests.post(
                url,
                json=metrics,
                headers={"Content-Type": "application/json"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.debug(f"플러그인 {plugin_id} 메트릭 전송 성공")
                    return True
                else:
                    logger.warning(
                        f"플러그인 {plugin_id} 메트릭 전송 실패: {data.get('error')}"
                    )
                    return False
            else:
                logger.error(
                    f"플러그인 {plugin_id} 메트릭 전송 실패: HTTP {response.status_code}"
                )
                return False

        except Exception as e:
            logger.error(f"플러그인 {plugin_id} 메트릭 전송 중 오류: {e}")
            return False

    def get_alerts(self) -> Dict[str, Any]:
        """알림 목록 조회"""
        try:
            url = f"{self.base_url}/api/enhanced-alerts/alerts"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"알림 조회 실패: HTTP {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"알림 조회 중 오류: {e}")
            return {}

    def get_alert_statistics(self) -> Dict[str, Any]:
        """알림 통계 조회"""
        try:
            url = f"{self.base_url}/api/enhanced-alerts/alerts/statistics"

            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"알림 통계 조회 실패: HTTP {response.status_code}")
                return {}

        except Exception as e:
            logger.error(f"알림 통계 조회 중 오류: {e}")
            return {}

    def send_test_alert(
        self, title: str, message: str, plugin_id: Optional[str] = None
    ) -> bool:
        """테스트 알림 발송"""
        try:
            url = f"{self.base_url}/api/enhanced-alerts/test-alert"

            data = {"title": title, "message": message}

            if plugin_id:
                data["plugin_id"] = plugin_id

            response = requests.post(
                url, json=data, headers={"Content-Type": "application/json"}, timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    logger.info(f"테스트 알림 발송 성공: {title}")
                    return True
                else:
                    logger.warning(f"테스트 알림 발송 실패: {data.get('error')}")
                    return False
            else:
                logger.error(f"테스트 알림 발송 실패: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"테스트 알림 발송 중 오류: {e}")
            return False

    def change_scenario(self, scenario: str, duration: int = 300):
        """테스트 시나리오 변경"""
        if scenario in self.test_scenarios:
            self.current_scenario = scenario
            self.scenario_duration = duration
            logger.info(f"테스트 시나리오 변경: {scenario} (지속시간: {duration}초)")
        else:
            logger.warning(f"알 수 없는 시나리오: {scenario}")

    def run_test_cycle(self, duration: int = 3600):
        """테스트 사이클 실행"""
        logger.info(f"플러그인 모니터링 테스트 시작 (지속시간: {duration}초)")

        start_time = time.time()
        cycle_count = 0

        try:
            while time.time() - start_time < duration:
                cycle_count += 1
                current_time = time.time()

                # 시나리오 지속시간 체크
                if self.scenario_duration > 0:
                    if current_time - start_time > self.scenario_duration:
                        # 정상 상태로 복귀
                        self.change_scenario("normal", 0)

                logger.info(
                    f"테스트 사이클 {cycle_count} 시작 (시나리오: {self.current_scenario})"
                )

                # 각 플러그인에 대해 메트릭 생성 및 전송
                for plugin in self.test_plugins:
                    metrics = self.generate_plugin_metrics(plugin)
                    if metrics:
                        success = self.send_plugin_metrics(plugin["id"], metrics)
                        if success:
                            logger.debug(f"플러그인 {plugin['name']} 메트릭 전송 완료")
                        else:
                            logger.warning(
                                f"플러그인 {plugin['name']} 메트릭 전송 실패"
                            )

                # 알림 통계 출력 (10번째 사이클마다)
                if cycle_count % 10 == 0:
                    stats = self.get_alert_statistics()
                    if stats.get("success"):
                        statistics = stats.get("statistics", {})
                        logger.info(
                            f"알림 통계 - 활성: {statistics.get('active_alerts', 0)}, "
                            f"해결됨: {statistics.get('resolved_alerts', 0)}, "
                            f"총계: {statistics.get('total_alerts', 0)}"
                        )

                # 30초 대기
                time.sleep(30)

        except KeyboardInterrupt:
            logger.info("테스트 중단됨")
        except Exception as e:
            logger.error(f"테스트 실행 중 오류: {e}")
        finally:
            logger.info(f"테스트 완료 - 총 {cycle_count}개 사이클 실행")

    def run_scenario_test(self):
        """시나리오별 테스트 실행"""
        logger.info("시나리오별 테스트 시작")

        scenarios = [
            ("normal", 60),
            ("high_cpu", 120),
            ("high_memory", 120),
            ("high_error", 120),
            ("slow_response", 120),
            ("critical", 180),
            ("normal", 60),
        ]

        for scenario, duration in scenarios:
            logger.info(f"시나리오 '{scenario}' 시작 (지속시간: {duration}초)")
            self.change_scenario(scenario, duration)

            start_time = time.time()
            while time.time() - start_time < duration:
                # 각 플러그인에 대해 메트릭 생성 및 전송
                for plugin in self.test_plugins:
                    metrics = self.generate_plugin_metrics(plugin)
                    if metrics:
                        self.send_plugin_metrics(plugin["id"], metrics)

                # 30초 대기
                time.sleep(30)

            # 시나리오 종료 후 알림 상태 확인
            stats = self.get_alert_statistics()
            if stats.get("success"):
                statistics = stats.get("statistics", {})
                logger.info(
                    f"시나리오 '{scenario}' 완료 - "
                    f"활성 알림: {statistics.get('active_alerts', 0)}"
                )

    def run_manual_test(self):
        """수동 테스트 실행"""
        logger.info("수동 테스트 시작")

        # 1. 정상 상태 메트릭 전송
        logger.info("1. 정상 상태 메트릭 전송")
        self.change_scenario("normal")
        for plugin in self.test_plugins:
            metrics = self.generate_plugin_metrics(plugin)
            self.send_plugin_metrics(plugin["id"], metrics)

        time.sleep(10)

        # 2. CPU 사용률 높은 상태
        logger.info("2. CPU 사용률 높은 상태")
        self.change_scenario("high_cpu")
        for plugin in self.test_plugins:
            metrics = self.generate_plugin_metrics(plugin)
            self.send_plugin_metrics(plugin["id"], metrics)

        time.sleep(10)

        # 3. 테스트 알림 발송
        logger.info("3. 테스트 알림 발송")
        self.send_test_alert(
            "테스트 알림", "이것은 수동 테스트 알림입니다.", "restaurant_management"
        )

        time.sleep(10)

        # 4. 알림 상태 확인
        logger.info("4. 알림 상태 확인")
        alerts = self.get_alerts()
        if alerts.get("success"):
            alert_count = len(alerts.get("alerts", []))
            logger.info(f"현재 활성 알림 수: {alert_count}")

        stats = self.get_alert_statistics()
        if stats.get("success"):
            statistics = stats.get("statistics", {})
            logger.info(f"알림 통계: {statistics}")

        logger.info("수동 테스트 완료")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="플러그인 모니터링 테스트")
    parser.add_argument("--url", default="http://localhost:5000", help="API 서버 URL")
    parser.add_argument(
        "--mode",
        choices=["cycle", "scenario", "manual"],
        default="manual",
        help="테스트 모드",
    )
    parser.add_argument(
        "--duration", type=int, default=3600, help="테스트 지속시간 (초)"
    )

    args = parser.parse_args()

    tester = PluginMonitoringTester(args.url)

    if args.mode == "cycle":
        tester.run_test_cycle(args.duration)
    elif args.mode == "scenario":
        tester.run_scenario_test()
    elif args.mode == "manual":
        tester.run_manual_test()
    else:
        logger.error(f"알 수 없는 테스트 모드: {args.mode}")


if __name__ == "__main__":
    main()
