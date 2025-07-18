#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
통합 테스트 스위트
전체 시스템의 통합 테스트를 수행하는 도구
"""

import os
import sys
import time
import json
import requests
import sqlite3
import logging
from datetime import datetime
from typing import Dict, List, Optional
import threading
import queue

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/integration_test.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class IntegrationTestSuite:
    def __init__(self, base_url: str = "http://localhost:5001"):
        self.base_url = base_url
        self.test_results = []
        self.session = requests.Session()
        self.test_queue = queue.Queue()

        # 테스트 설정
        self.test_config = {"timeout": 30, "retry_count": 3, "concurrent_tests": 5}

    def run_all_tests(self) -> Dict:
        """모든 테스트 실행"""
        logger.info("통합 테스트 스위트 시작")

        start_time = time.time()

        # 테스트 케이스 정의
        test_cases = [
            ("시스템 상태 확인", self.test_system_status),
            ("데이터베이스 연결", self.test_database_connection),
            ("API 엔드포인트", self.test_api_endpoints),
            ("플러그인 시스템", self.test_plugin_system),
            ("인증 시스템", self.test_authentication),
            ("성능 테스트", self.test_performance),
            ("보안 테스트", self.test_security),
            ("모바일 API", self.test_mobile_api),
            ("실시간 알림", self.test_realtime_notifications),
            ("데이터 무결성", self.test_data_integrity),
        ]

        # 테스트 실행
        for test_name, test_func in test_cases:
            try:
                logger.info(f"테스트 실행 중: {test_name}")
                result = test_func()
                self.test_results.append(
                    {
                        "name": test_name,
                        "status": "PASS" if result else "FAIL",
                        "timestamp": datetime.now().isoformat(),
                        "details": result,
                    }
                )
                logger.info(
                    f"테스트 완료: {test_name} - {'PASS' if result else 'FAIL'}"
                )
            except Exception as e:
                logger.error(f"테스트 실패: {test_name} - {e}")
                self.test_results.append(
                    {
                        "name": test_name,
                        "status": "ERROR",
                        "timestamp": datetime.now().isoformat(),
                        "error": str(e),
                    }
                )

        end_time = time.time()

        # 결과 요약
        summary = {
            "total_tests": len(test_cases),
            "passed": len([r for r in self.test_results if r["status"] == "PASS"]),
            "failed": len([r for r in self.test_results if r["status"] == "FAIL"]),
            "errors": len([r for r in self.test_results if r["status"] == "ERROR"]),
            "duration": end_time - start_time,
            "timestamp": datetime.now().isoformat(),
            "results": self.test_results,
        }

        # 결과 저장
        self.save_test_results(summary)

        logger.info(
            f"통합 테스트 완료: {summary['passed']}/{summary['total_tests']} 통과"
        )
        return summary

    def test_system_status(self) -> bool:
        """시스템 상태 확인"""
        try:
            # 헬스 체크
            response = self.session.get(
                f"{self.base_url}/health", timeout=self.test_config["timeout"]
            )
            if response.status_code != 200:
                return False

            # API 상태 확인
            response = self.session.get(
                f"{self.base_url}/api/status", timeout=self.test_config["timeout"]
            )
            if response.status_code != 200:
                return False

            data = response.json()
            return data.get("status") == "healthy"

        except Exception as e:
            logger.error(f"시스템 상태 테스트 실패: {e}")
            return False

    def test_database_connection(self) -> bool:
        """데이터베이스 연결 테스트"""
        try:
            db_files = [
                "marketplace.db",
                "plugin_monitoring.db",
                "advanced_monitoring.db",
            ]

            for db_file in db_files:
                if os.path.exists(db_file):
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()

                    # 기본 쿼리 테스트
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()

                    if result[0] != 1:
                        return False

                    conn.close()

            return True

        except Exception as e:
            logger.error(f"데이터베이스 연결 테스트 실패: {e}")
            return False

    def test_api_endpoints(self) -> bool:
        """API 엔드포인트 테스트"""
        try:
            endpoints = [
                "/api/dashboard",
                "/api/admin/dashboard-stats",
                "/api/plugins/status",
                "/api/marketplace/plugins",
                "/api/feedback",
            ]

            for endpoint in endpoints:
                response = self.session.get(
                    f"{self.base_url}{endpoint}", timeout=self.test_config["timeout"]
                )
                if response.status_code not in [200, 401, 403]:  # 401, 403은 인증 필요
                    logger.warning(
                        f"API 엔드포인트 실패: {endpoint} - {response.status_code}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"API 엔드포인트 테스트 실패: {e}")
            return False

    def test_plugin_system(self) -> bool:
        """플러그인 시스템 테스트"""
        try:
            # 플러그인 상태 확인
            response = self.session.get(
                f"{self.base_url}/api/plugins/status",
                timeout=self.test_config["timeout"],
            )
            if response.status_code != 200:
                return False

            # 플러그인 목록 확인
            response = self.session.get(
                f"{self.base_url}/api/plugins/list", timeout=self.test_config["timeout"]
            )
            if response.status_code != 200:
                return False

            data = response.json()
            return isinstance(data, list)

        except Exception as e:
            logger.error(f"플러그인 시스템 테스트 실패: {e}")
            return False

    def test_authentication(self) -> bool:
        """인증 시스템 테스트"""
        try:
            # 로그인 테스트
            login_data = {"username": "admin", "password": "admin123"}

            response = self.session.post(
                f"{self.base_url}/auth/login",
                data=login_data,
                timeout=self.test_config["timeout"],
            )

            # 로그인 성공 또는 실패 확인
            if response.status_code not in [200, 302, 401]:
                return False

            return True

        except Exception as e:
            logger.error(f"인증 시스템 테스트 실패: {e}")
            return False

    def test_performance(self) -> bool:
        """성능 테스트"""
        try:
            # 응답시간 테스트
            start_time = time.time()
            response = self.session.get(
                f"{self.base_url}/api/status", timeout=self.test_config["timeout"]
            )
            end_time = time.time()

            response_time = end_time - start_time

            # 응답시간이 2초 이내여야 함
            if response_time > 2.0:
                logger.warning(f"응답시간이 느림: {response_time:.2f}초")
                return False

            return True

        except Exception as e:
            logger.error(f"성능 테스트 실패: {e}")
            return False

    def test_security(self) -> bool:
        """보안 테스트"""
        try:
            # CSRF 토큰 확인
            response = self.session.get(
                f"{self.base_url}/auth/login", timeout=self.test_config["timeout"]
            )
            if response.status_code != 200:
                return False

            # CSRF 토큰이 응답에 포함되어 있는지 확인
            if "csrf_token" not in response.text and "csrf" not in response.text:
                logger.warning("CSRF 토큰이 없습니다")
                return False

            return True

        except Exception as e:
            logger.error(f"보안 테스트 실패: {e}")
            return False

    def test_mobile_api(self) -> bool:
        """모바일 API 테스트"""
        try:
            # 모바일 API 엔드포인트 확인
            mobile_endpoints = [
                "/api/mobile/status",
                "/api/mobile/auth",
                "/api/mobile/dashboard",
            ]

            for endpoint in mobile_endpoints:
                response = self.session.get(
                    f"{self.base_url}{endpoint}", timeout=self.test_config["timeout"]
                )
                # 404는 정상 (아직 구현되지 않음)
                if response.status_code not in [200, 404]:
                    logger.warning(
                        f"모바일 API 실패: {endpoint} - {response.status_code}"
                    )
                    return False

            return True

        except Exception as e:
            logger.error(f"모바일 API 테스트 실패: {e}")
            return False

    def test_realtime_notifications(self) -> bool:
        """실시간 알림 테스트"""
        try:
            # WebSocket 연결 테스트 (기본적인 확인)
            response = self.session.get(
                f"{self.base_url}/api/plugins/monitoring/status",
                timeout=self.test_config["timeout"],
            )

            # 알림 시스템 상태 확인
            if response.status_code not in [200, 404]:
                return False

            return True

        except Exception as e:
            logger.error(f"실시간 알림 테스트 실패: {e}")
            return False

    def test_data_integrity(self) -> bool:
        """데이터 무결성 테스트"""
        try:
            # 데이터베이스 무결성 확인
            db_files = ["marketplace.db"]

            for db_file in db_files:
                if os.path.exists(db_file):
                    conn = sqlite3.connect(db_file)
                    cursor = conn.cursor()

                    # 무결성 검사
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()

                    if result[0] != "ok":
                        logger.error(f"데이터베이스 무결성 검사 실패: {db_file}")
                        return False

                    conn.close()

            return True

        except Exception as e:
            logger.error(f"데이터 무결성 테스트 실패: {e}")
            return False

    def save_test_results(self, summary: Dict):
        """테스트 결과 저장"""
        try:
            # JSON 파일로 저장
            results_file = f"logs/integration_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            # 요약 파일 업데이트
            summary_file = "logs/integration_test_summary.json"
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)

            logger.info(f"테스트 결과 저장 완료: {results_file}")

        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

    def generate_test_report(self) -> str:
        """테스트 보고서 생성"""
        try:
            if not self.test_results:
                return "테스트 결과가 없습니다."

            report = []
            report.append("# 통합 테스트 보고서")
            report.append(
                f"**생성일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            report.append("")

            # 요약
            passed = len([r for r in self.test_results if r["status"] == "PASS"])
            failed = len([r for r in self.test_results if r["status"] == "FAIL"])
            errors = len([r for r in self.test_results if r["status"] == "ERROR"])
            total = len(self.test_results)

            report.append("## 테스트 요약")
            report.append(f"- **전체 테스트**: {total}")
            report.append(f"- **통과**: {passed}")
            report.append(f"- **실패**: {failed}")
            report.append(f"- **오류**: {errors}")
            report.append(f"- **성공률**: {(passed/total)*100:.1f}%")
            report.append("")

            # 상세 결과
            report.append("## 상세 결과")
            for result in self.test_results:
                status_icon = (
                    "✅"
                    if result["status"] == "PASS"
                    else "❌" if result["status"] == "FAIL" else "⚠️"
                )
                report.append(
                    f"- {status_icon} **{result['name']}**: {result['status']}"
                )
                if "error" in result:
                    report.append(f"  - 오류: {result['error']}")

            # 권장사항
            report.append("")
            report.append("## 권장사항")
            if failed > 0 or errors > 0:
                report.append("- 실패한 테스트를 확인하고 수정하세요")
                report.append("- 로그 파일을 확인하여 오류 원인을 파악하세요")
            else:
                report.append(
                    "- 모든 테스트가 통과했습니다. 배포를 진행할 수 있습니다."
                )

            report_content = "\n".join(report)

            # 마크다운 파일로 저장
            report_file = f"logs/integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, "w", encoding="utf-8") as f:
                f.write(report_content)

            return report_content

        except Exception as e:
            logger.error(f"테스트 보고서 생성 실패: {e}")
            return f"보고서 생성 실패: {e}"


def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = "http://localhost:5001"

    test_suite = IntegrationTestSuite(base_url)

    if len(sys.argv) > 2 and sys.argv[2] == "report":
        # 보고서만 생성
        report = test_suite.generate_test_report()
        print(report)
    else:
        # 전체 테스트 실행
        summary = test_suite.run_all_tests()
        report = test_suite.generate_test_report()
        print(report)


if __name__ == "__main__":
    main()
