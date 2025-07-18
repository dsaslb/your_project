#!/usr/bin/env python3
"""
고도화된 플러그인 보안 모니터링 시스템 테스트
- 취약점 스캔, 악성코드 감지, 권한 모니터링, 보안 이벤트 추적, 자동 대응
"""

import sys
import os
import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Any

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EnhancedSecurityTester:
    """고도화된 보안 모니터링 테스터"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def log_test(
        self, test_name: str, success: bool, message: str = "", data: Any = None
    ):
        """테스트 결과 로깅"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ 성공" if success else "❌ 실패"
        print(f"{status} - {test_name}: {message}")

        if data and not success:
            print(f"   데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")

    def test_security_summary(self) -> bool:
        """보안 요약 정보 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/summary"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    summary = data["data"]
                    required_fields = [
                        "open_vulnerabilities",
                        "active_malware",
                        "unresolved_events",
                        "critical_plugins",
                        "high_risk_plugins",
                    ]

                    for field in required_fields:
                        if field not in summary:
                            self.log_test(
                                "보안 요약", False, f"필수 필드 누락: {field}"
                            )
                            return False

                    self.log_test(
                        "보안 요약",
                        True,
                        f"보안 요약 조회 성공 - 취약점: {summary['open_vulnerabilities']}, 악성코드: {summary['active_malware']}",
                    )
                    return True
                else:
                    self.log_test("보안 요약", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test("보안 요약", False, f"HTTP 오류: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("보안 요약", False, f"예외 발생: {str(e)}")
            return False

    def test_vulnerabilities_list(self) -> bool:
        """취약점 목록 조회 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/vulnerabilities?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    vulnerabilities = data["data"]
                    if isinstance(vulnerabilities, list):
                        self.log_test(
                            "취약점 목록",
                            True,
                            f"취약점 {len(vulnerabilities)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test("취약점 목록", False, "취약점 목록이 배열이 아님")
                        return False
                else:
                    self.log_test("취약점 목록", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "취약점 목록", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("취약점 목록", False, f"예외 발생: {str(e)}")
            return False

    def test_malware_detections(self) -> bool:
        """악성코드 감지 목록 조회 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/malware?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    malware_detections = data["data"]
                    if isinstance(malware_detections, list):
                        self.log_test(
                            "악성코드 감지",
                            True,
                            f"악성코드 감지 {len(malware_detections)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "악성코드 감지", False, "악성코드 감지 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("악성코드 감지", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "악성코드 감지", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("악성코드 감지", False, f"예외 발생: {str(e)}")
            return False

    def test_security_events(self) -> bool:
        """보안 이벤트 목록 조회 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/events?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    security_events = data["data"]
                    if isinstance(security_events, list):
                        self.log_test(
                            "보안 이벤트",
                            True,
                            f"보안 이벤트 {len(security_events)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "보안 이벤트", False, "보안 이벤트 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("보안 이벤트", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "보안 이벤트", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("보안 이벤트", False, f"예외 발생: {str(e)}")
            return False

    def test_security_profiles(self) -> bool:
        """보안 프로필 목록 조회 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/profiles?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    security_profiles = data["data"]
                    if isinstance(security_profiles, list):
                        self.log_test(
                            "보안 프로필",
                            True,
                            f"보안 프로필 {len(security_profiles)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "보안 프로필", False, "보안 프로필 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("보안 프로필", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "보안 프로필", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("보안 프로필", False, f"예외 발생: {str(e)}")
            return False

    def test_scan_history(self) -> bool:
        """스캔 이력 조회 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-security/scans?limit=10"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    scan_history = data["data"]
                    if isinstance(scan_history, list):
                        self.log_test(
                            "스캔 이력",
                            True,
                            f"스캔 이력 {len(scan_history)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "스캔 이력", False, "스캔 이력 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("스캔 이력", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test("스캔 이력", False, f"HTTP 오류: {response.status_code}")
                return False

        except Exception as e:
            self.log_test("스캔 이력", False, f"예외 발생: {str(e)}")
            return False

    def test_security_scan_start(self) -> bool:
        """보안 스캔 시작 테스트 (로그인 필요)"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/enhanced-security/scan/start",
                json={"plugin_id": "test_plugin"},
            )

            if response.status_code in [401, 403]:
                self.log_test("보안 스캔 시작", True, "인증 필요 (예상된 동작)")
                return True
            elif response.status_code == 200:
                scan_data = response.json()
                if scan_data.get("success"):
                    self.log_test("보안 스캔 시작", True, "보안 스캔 시작 성공")
                    return True
                else:
                    self.log_test(
                        "보안 스캔 시작", False, "보안 스캔 시작 실패", scan_data
                    )
                    return False
            else:
                self.log_test(
                    "보안 스캔 시작",
                    False,
                    f"예상치 못한 HTTP 상태: {response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("보안 스캔 시작", False, f"예외 발생: {str(e)}")
            return False

    def test_monitoring_control(self) -> bool:
        """모니터링 제어 테스트 (로그인 필요)"""
        try:
            # 모니터링 시작 시도
            start_response = self.session.post(
                f"{self.base_url}/api/enhanced-security/monitoring/start"
            )

            if start_response.status_code in [401, 403]:
                self.log_test("모니터링 제어", True, "인증 필요 (예상된 동작)")
                return True
            elif start_response.status_code == 200:
                start_data = start_response.json()
                if start_data.get("success"):
                    # 모니터링 중지 시도
                    stop_response = self.session.post(
                        f"{self.base_url}/api/enhanced-security/monitoring/stop"
                    )
                    if stop_response.status_code == 200:
                        stop_data = stop_response.json()
                        if stop_data.get("success"):
                            self.log_test(
                                "모니터링 제어", True, "모니터링 시작/중지 성공"
                            )
                            return True
                        else:
                            self.log_test(
                                "모니터링 제어", False, "모니터링 중지 실패", stop_data
                            )
                            return False
                    else:
                        self.log_test(
                            "모니터링 제어",
                            False,
                            f"모니터링 중지 HTTP 오류: {stop_response.status_code}",
                        )
                        return False
                else:
                    self.log_test(
                        "모니터링 제어", False, "모니터링 시작 실패", start_data
                    )
                    return False
            else:
                self.log_test(
                    "모니터링 제어",
                    False,
                    f"모니터링 시작 HTTP 오류: {start_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("모니터링 제어", False, f"예외 발생: {str(e)}")
            return False

    def test_vulnerability_status_update(self) -> bool:
        """취약점 상태 업데이트 테스트 (로그인 필요)"""
        try:
            # 먼저 취약점 목록을 가져와서 첫 번째 취약점 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-security/vulnerabilities?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    vuln_id = list_data["data"][0]["id"]

                    # 상태 업데이트 시도
                    update_response = self.session.put(
                        f"{self.base_url}/api/enhanced-security/vulnerabilities/{vuln_id}/status",
                        json={"status": "fixed"},
                    )

                    if update_response.status_code in [401, 403]:
                        self.log_test(
                            "취약점 상태 업데이트", True, "인증 필요 (예상된 동작)"
                        )
                        return True
                    elif update_response.status_code == 200:
                        update_data = update_response.json()
                        if update_data.get("success"):
                            self.log_test(
                                "취약점 상태 업데이트",
                                True,
                                "취약점 상태 업데이트 성공",
                            )
                            return True
                        else:
                            self.log_test(
                                "취약점 상태 업데이트",
                                False,
                                "취약점 상태 업데이트 실패",
                                update_data,
                            )
                            return False
                    else:
                        self.log_test(
                            "취약점 상태 업데이트",
                            False,
                            f"HTTP 오류: {update_response.status_code}",
                        )
                        return False
                else:
                    self.log_test(
                        "취약점 상태 업데이트", False, "테스트할 취약점이 없음"
                    )
                    return False
            else:
                self.log_test(
                    "취약점 상태 업데이트",
                    False,
                    f"취약점 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("취약점 상태 업데이트", False, f"예외 발생: {str(e)}")
            return False

    def test_malware_quarantine(self) -> bool:
        """악성코드 격리 테스트 (로그인 필요)"""
        try:
            # 먼저 악성코드 감지 목록을 가져와서 첫 번째 감지 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-security/malware?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    detection_id = list_data["data"][0]["id"]

                    # 격리 시도
                    quarantine_response = self.session.post(
                        f"{self.base_url}/api/enhanced-security/malware/{detection_id}/quarantine"
                    )

                    if quarantine_response.status_code in [401, 403]:
                        self.log_test("악성코드 격리", True, "인증 필요 (예상된 동작)")
                        return True
                    elif quarantine_response.status_code == 200:
                        quarantine_data = quarantine_response.json()
                        if quarantine_data.get("success"):
                            self.log_test("악성코드 격리", True, "악성코드 격리 성공")
                            return True
                        else:
                            self.log_test(
                                "악성코드 격리",
                                False,
                                "악성코드 격리 실패",
                                quarantine_data,
                            )
                            return False
                    else:
                        self.log_test(
                            "악성코드 격리",
                            False,
                            f"HTTP 오류: {quarantine_response.status_code}",
                        )
                        return False
                else:
                    self.log_test(
                        "악성코드 격리", False, "테스트할 악성코드 감지가 없음"
                    )
                    return False
            else:
                self.log_test(
                    "악성코드 격리",
                    False,
                    f"악성코드 감지 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("악성코드 격리", False, f"예외 발생: {str(e)}")
            return False

    def test_security_event_resolution(self) -> bool:
        """보안 이벤트 해결 테스트 (로그인 필요)"""
        try:
            # 먼저 보안 이벤트 목록을 가져와서 첫 번째 이벤트 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-security/events?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    event_id = list_data["data"][0]["id"]

                    # 이벤트 해결 시도
                    resolve_response = self.session.post(
                        f"{self.base_url}/api/enhanced-security/events/{event_id}/resolve",
                        json={"resolution_notes": "테스트 해결"},
                    )

                    if resolve_response.status_code in [401, 403]:
                        self.log_test(
                            "보안 이벤트 해결", True, "인증 필요 (예상된 동작)"
                        )
                        return True
                    elif resolve_response.status_code == 200:
                        resolve_data = resolve_response.json()
                        if resolve_data.get("success"):
                            self.log_test(
                                "보안 이벤트 해결", True, "보안 이벤트 해결 성공"
                            )
                            return True
                        else:
                            self.log_test(
                                "보안 이벤트 해결",
                                False,
                                "보안 이벤트 해결 실패",
                                resolve_data,
                            )
                            return False
                    else:
                        self.log_test(
                            "보안 이벤트 해결",
                            False,
                            f"HTTP 오류: {resolve_response.status_code}",
                        )
                        return False
                else:
                    self.log_test(
                        "보안 이벤트 해결", False, "테스트할 보안 이벤트가 없음"
                    )
                    return False
            else:
                self.log_test(
                    "보안 이벤트 해결",
                    False,
                    f"보안 이벤트 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("보안 이벤트 해결", False, f"예외 발생: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("🛡️ 고도화된 플러그인 보안 모니터링 시스템 테스트 시작")
        print("=" * 60)

        start_time = time.time()

        # 테스트 실행
        tests = [
            ("보안 요약", self.test_security_summary),
            ("취약점 목록", self.test_vulnerabilities_list),
            ("악성코드 감지", self.test_malware_detections),
            ("보안 이벤트", self.test_security_events),
            ("보안 프로필", self.test_security_profiles),
            ("스캔 이력", self.test_scan_history),
            ("보안 스캔 시작", self.test_security_scan_start),
            ("모니터링 제어", self.test_monitoring_control),
            ("취약점 상태 업데이트", self.test_vulnerability_status_update),
            ("악성코드 격리", self.test_malware_quarantine),
            ("보안 이벤트 해결", self.test_security_event_resolution),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # API 호출 간격
            except Exception as e:
                self.log_test(test_name, False, f"테스트 실행 중 예외: {str(e)}")

        end_time = time.time()
        duration = end_time - start_time

        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"총 테스트: {total}")
        print(f"성공: {passed}")
        print(f"실패: {total - passed}")
        print(f"성공률: {(passed/total)*100:.1f}%")
        print(f"소요 시간: {duration:.2f}초")

        # 실패한 테스트 목록
        failed_tests = [result for result in self.test_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ 실패한 테스트 ({len(failed_tests)}개):")
            for result in failed_tests:
                print(f"  - {result['test_name']}: {result['message']}")

        return {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": (passed / total) * 100,
            "duration": duration,
            "results": self.test_results,
        }


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(
        description="고도화된 플러그인 보안 모니터링 시스템 테스트"
    )
    parser.add_argument(
        "--url", default="http://localhost:5000", help="테스트할 서버 URL"
    )
    parser.add_argument("--output", help="결과를 JSON 파일로 저장")

    args = parser.parse_args()

    # 테스터 생성 및 실행
    tester = EnhancedSecurityTester(args.url)
    results = tester.run_all_tests()

    # 결과 저장
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n💾 테스트 결과가 {args.output}에 저장되었습니다.")

    # 종료 코드
    if results["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
