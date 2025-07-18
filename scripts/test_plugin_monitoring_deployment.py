#!/usr/bin/env python3
"""
플러그인 모니터링 배포 테스트
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginMonitoringDeploymentTester:
    """플러그인 모니터링 배포 테스트"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {}

    def test_monitoring_api_endpoints(self) -> Dict[str, Any]:
        """모니터링 API 엔드포인트 테스트"""
        endpoints = [
            "/api/admin/plugin-monitoring/status",
            "/api/admin/plugin-monitoring/metrics",
            "/api/admin/plugin-monitoring/performance",
            "/api/admin/plugin-monitoring/health",
            "/api/admin/plugin-monitoring/dashboard",
        ]

        results = {}
        overall_success = True

        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)

                result = {
                    "endpoint": endpoint,
                    "success": response.status_code == 200,
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "response_size": len(response.content),
                }

                if response.status_code == 200:
                    try:
                        result["response_data"] = response.json()
                    except:
                        result["response_data"] = None
                else:
                    result["error"] = response.text
                    overall_success = False

                results[endpoint] = result

            except Exception as e:
                result = {"endpoint": endpoint, "success": False, "error": str(e)}
                results[endpoint] = result
                overall_success = False

        api_test_result = {
            "test_type": "api_endpoints",
            "overall_success": overall_success,
            "total_endpoints": len(endpoints),
            "successful_endpoints": len(
                [r for r in results.values() if r.get("success", False)]
            ),
            "results": results,
        }

        self.test_results["api_endpoints"] = api_test_result
        return api_test_result

    def test_monitoring_data_collection(self) -> Dict[str, Any]:
        """모니터링 데이터 수집 테스트"""
        try:
            # 메트릭 수집 API 호출
            response = requests.post(
                f"{self.base_url}/api/admin/plugin-monitoring/collect-metrics",
                timeout=30,
            )

            result = {
                "test_type": "data_collection",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if response.status_code == 200:
                result["response_data"] = response.json()
            else:
                result["error"] = response.text

            self.test_results["data_collection"] = result
            return result

        except Exception as e:
            result = {"test_type": "data_collection", "success": False, "error": str(e)}
            self.test_results["data_collection"] = result
            return result

    def test_monitoring_alerts(self) -> Dict[str, Any]:
        """모니터링 알림 테스트"""
        try:
            # 알림 설정 테스트
            alert_config = {
                "cpu_threshold": 80,
                "memory_threshold": 85,
                "response_time_threshold": 5000,
            }

            response = requests.post(
                f"{self.base_url}/api/admin/plugin-monitoring/alerts/config",
                json=alert_config,
                timeout=10,
            )

            result = {
                "test_type": "alerts",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if response.status_code == 200:
                result["response_data"] = response.json()
            else:
                result["error"] = response.text

            self.test_results["alerts"] = result
            return result

        except Exception as e:
            result = {"test_type": "alerts", "success": False, "error": str(e)}
            self.test_results["alerts"] = result
            return result

    def test_monitoring_dashboard(self) -> Dict[str, Any]:
        """모니터링 대시보드 테스트"""
        try:
            # 대시보드 데이터 요청
            response = requests.get(
                f"{self.base_url}/api/admin/plugin-monitoring/dashboard", timeout=10
            )

            result = {
                "test_type": "dashboard",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if response.status_code == 200:
                dashboard_data = response.json()
                result["response_data"] = dashboard_data

                # 대시보드 데이터 검증
                required_fields = ["plugins", "metrics", "alerts", "performance"]
                missing_fields = [
                    field for field in required_fields if field not in dashboard_data
                ]

                if missing_fields:
                    result["validation_warnings"] = f"Missing fields: {missing_fields}"
                else:
                    result["validation_success"] = True
            else:
                result["error"] = response.text

            self.test_results["dashboard"] = result
            return result

        except Exception as e:
            result = {"test_type": "dashboard", "success": False, "error": str(e)}
            self.test_results["dashboard"] = result
            return result

    def test_monitoring_performance(self) -> Dict[str, Any]:
        """모니터링 성능 테스트"""
        try:
            # 성능 테스트 API 호출
            response = requests.post(
                f"{self.base_url}/api/admin/plugin-monitoring/performance-test",
                timeout=60,
            )

            result = {
                "test_type": "performance",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
            }

            if response.status_code == 200:
                performance_data = response.json()
                result["response_data"] = performance_data

                # 성능 메트릭 검증
                if "metrics" in performance_data:
                    metrics = performance_data["metrics"]
                    result["performance_metrics"] = {
                        "avg_response_time": metrics.get("avg_response_time", 0),
                        "max_response_time": metrics.get("max_response_time", 0),
                        "throughput": metrics.get("throughput", 0),
                        "error_rate": metrics.get("error_rate", 0),
                    }
            else:
                result["error"] = response.text

            self.test_results["performance"] = result
            return result

        except Exception as e:
            result = {"test_type": "performance", "success": False, "error": str(e)}
            self.test_results["performance"] = result
            return result

    def run_full_monitoring_test(self) -> Dict[str, Any]:
        """전체 모니터링 테스트 실행"""
        logger.info("플러그인 모니터링 배포 테스트 시작")

        test_sequence = [
            ("api_endpoints", self.test_monitoring_api_endpoints),
            ("data_collection", self.test_monitoring_data_collection),
            ("alerts", self.test_monitoring_alerts),
            ("dashboard", self.test_monitoring_dashboard),
            ("performance", self.test_monitoring_performance),
        ]

        results = {}
        overall_success = True

        for test_name, test_func in test_sequence:
            logger.info(f"테스트 실행: {test_name}")
            test_result = test_func()
            results[test_name] = test_result

            if not test_result.get("success", False) and not test_result.get(
                "overall_success", False
            ):
                overall_success = False
                logger.error(f"테스트 실패: {test_name}")

        # 전체 테스트 결과
        full_test_result = {
            "overall_success": overall_success,
            "test_timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": self._generate_test_summary(results),
        }

        self.test_results["full_test"] = full_test_result
        return full_test_result

    def _generate_test_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """테스트 결과 요약"""
        total_tests = len(results)
        successful_tests = 0
        response_times = []

        for result in results.values():
            if result.get("success", False) or result.get("overall_success", False):
                successful_tests += 1

            if "response_time" in result:
                response_times.append(result["response_time"])

        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": (
                (successful_tests / total_tests) * 100 if total_tests > 0 else 0
            ),
            "avg_response_time": (
                sum(response_times) / len(response_times) if response_times else 0
            ),
            "max_response_time": max(response_times) if response_times else 0,
        }

        return summary

    def save_test_results(self, filename: str = "") -> str:
        """테스트 결과 저장"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"plugin_monitoring_deployment_test_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        logger.info(f"테스트 결과 저장됨: {filename}")
        return filename

    def print_test_summary(self):
        """테스트 결과 요약 출력"""
        if "full_test" not in self.test_results:
            logger.warning("전체 테스트 결과가 없습니다.")
            return

        full_test = self.test_results["full_test"]
        summary = full_test.get("summary", {})

        print("\n=== 플러그인 모니터링 배포 테스트 결과 ===")
        print(f"전체 성공: {'예' if full_test['overall_success'] else '아니오'}")
        print(f"테스트 시간: {full_test['test_timestamp']}")
        print(f"총 테스트 수: {summary.get('total_tests', 0)}")
        print(f"성공한 테스트: {summary.get('successful_tests', 0)}")
        print(f"실패한 테스트: {summary.get('failed_tests', 0)}")
        print(f"성공률: {summary.get('success_rate', 0):.1f}%")
        print(f"평균 응답 시간: {summary.get('avg_response_time', 0):.3f}초")
        print(f"최대 응답 시간: {summary.get('max_response_time', 0):.3f}초")
        print("=" * 50)


def main():
    """메인 실행 함수"""
    print("플러그인 모니터링 배포 테스트 시작")

    # 테스터 인스턴스 생성
    tester = PluginMonitoringDeploymentTester()

    # 전체 모니터링 테스트 실행
    tester.run_full_monitoring_test()

    # 결과 출력
    tester.print_test_summary()

    # 결과 저장
    filename = tester.save_test_results()

    print(f"\n테스트 결과가 {filename}에 저장되었습니다.")
    print("플러그인 모니터링 배포 테스트 완료")


if __name__ == "__main__":
    main()
