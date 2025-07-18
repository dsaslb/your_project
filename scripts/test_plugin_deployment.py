#!/usr/bin/env python3
"""
플러그인 배포 테스트
"""

import json
import logging
import requests
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PluginDeploymentTester:
    """플러그인 배포 테스트"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {}

    def test_plugin_upload(self, plugin_file: str) -> Dict[str, Any]:
        """플러그인 업로드 테스트"""
        try:
            with open(plugin_file, "rb") as f:
                files = {"plugin": f}
                response = requests.post(
                    f"{self.base_url}/api/admin/plugin-management/upload",
                    files=files,
                    timeout=30,
                )

            result = {
                "test_type": "upload",
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["upload"] = result
            return result

        except Exception as e:
            result = {"test_type": "upload", "success": False, "error": str(e)}
            self.test_results["upload"] = result
            return result

    def test_plugin_installation(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 설치 테스트"""
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/plugin-management/install/{plugin_name}",
                timeout=30,
            )

            result = {
                "test_type": "installation",
                "plugin_name": plugin_name,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["installation"] = result
            return result

        except Exception as e:
            result = {
                "test_type": "installation",
                "plugin_name": plugin_name,
                "success": False,
                "error": str(e),
            }
            self.test_results["installation"] = result
            return result

    def test_plugin_activation(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 활성화 테스트"""
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/plugin-management/activate/{plugin_name}",
                timeout=30,
            )

            result = {
                "test_type": "activation",
                "plugin_name": plugin_name,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["activation"] = result
            return result

        except Exception as e:
            result = {
                "test_type": "activation",
                "plugin_name": plugin_name,
                "success": False,
                "error": str(e),
            }
            self.test_results["activation"] = result
            return result

    def test_plugin_functionality(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 기능 테스트"""
        try:
            # 플러그인 API 엔드포인트 테스트
            response = requests.get(
                f"{self.base_url}/api/plugins/{plugin_name}/status", timeout=10
            )

            result = {
                "test_type": "functionality",
                "plugin_name": plugin_name,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["functionality"] = result
            return result

        except Exception as e:
            result = {
                "test_type": "functionality",
                "plugin_name": plugin_name,
                "success": False,
                "error": str(e),
            }
            self.test_results["functionality"] = result
            return result

    def test_plugin_deactivation(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 비활성화 테스트"""
        try:
            response = requests.post(
                f"{self.base_url}/api/admin/plugin-management/deactivate/{plugin_name}",
                timeout=30,
            )

            result = {
                "test_type": "deactivation",
                "plugin_name": plugin_name,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["deactivation"] = result
            return result

        except Exception as e:
            result = {
                "test_type": "deactivation",
                "plugin_name": plugin_name,
                "success": False,
                "error": str(e),
            }
            self.test_results["deactivation"] = result
            return result

    def test_plugin_uninstallation(self, plugin_name: str) -> Dict[str, Any]:
        """플러그인 제거 테스트"""
        try:
            response = requests.delete(
                f"{self.base_url}/api/admin/plugin-management/uninstall/{plugin_name}",
                timeout=30,
            )

            result = {
                "test_type": "uninstallation",
                "plugin_name": plugin_name,
                "success": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "response_data": (
                    response.json() if response.status_code == 200 else None
                ),
            }

            self.test_results["uninstallation"] = result
            return result

        except Exception as e:
            result = {
                "test_type": "uninstallation",
                "plugin_name": plugin_name,
                "success": False,
                "error": str(e),
            }
            self.test_results["uninstallation"] = result
            return result

    def run_full_deployment_test(
        self, plugin_file: str, plugin_name: str
    ) -> Dict[str, Any]:
        """전체 배포 테스트 실행"""
        logger.info(f"플러그인 배포 테스트 시작: {plugin_name}")

        test_sequence = [
            ("upload", lambda: self.test_plugin_upload(plugin_file)),
            ("installation", lambda: self.test_plugin_installation(plugin_name)),
            ("activation", lambda: self.test_plugin_activation(plugin_name)),
            ("functionality", lambda: self.test_plugin_functionality(plugin_name)),
            ("deactivation", lambda: self.test_plugin_deactivation(plugin_name)),
            ("uninstallation", lambda: self.test_plugin_uninstallation(plugin_name)),
        ]

        results = {}
        overall_success = True

        for step_name, test_func in test_sequence:
            logger.info(f"테스트 단계: {step_name}")
            result = test_func()
            results[step_name] = result

            if not result.get("success", False):
                overall_success = False
                logger.error(
                    f"테스트 실패: {step_name} - {result.get('error', 'Unknown error')}"
                )
                break

        # 전체 테스트 결과
        full_test_result = {
            "plugin_name": plugin_name,
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
        successful_tests = len([r for r in results.values() if r.get("success", False)])

        response_times = []
        for result in results.values():
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
            filename = f"plugin_deployment_test_{timestamp}.json"

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

        print("\n=== 플러그인 배포 테스트 결과 ===")
        print(f"플러그인: {full_test['plugin_name']}")
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
    print("플러그인 배포 테스트 시작")

    # 테스트할 플러그인 정보
    plugin_file = "plugins/sample_plugin.zip"  # 실제 플러그인 파일 경로
    plugin_name = "sample_plugin"

    # 테스터 인스턴스 생성
    tester = PluginDeploymentTester()

    # 전체 배포 테스트 실행
    tester.run_full_deployment_test(plugin_file, plugin_name)

    # 결과 출력
    tester.print_test_summary()

    # 결과 저장
    filename = tester.save_test_results()

    print(f"\n테스트 결과가 {filename}에 저장되었습니다.")
    print("플러그인 배포 테스트 완료")


if __name__ == "__main__":
    main()
