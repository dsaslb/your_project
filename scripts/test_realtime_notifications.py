#!/usr/bin/env python3
"""
실시간 알림 시스템 테스트 스크립트
알림 생성, 전송, 채널별 테스트
"""

import requests
import json
import time
import logging
import os
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RealtimeNotificationsTester:
    """실시간 알림 시스템 테스터"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []

    def login(self, username: str = "admin", password: str = "admin123") -> bool:
        """관리자 로그인"""
        try:
            login_data = {"username": username, "password": password}
            response = self.session.post(
                f"{self.base_url}/api/auth/login", json=login_data
            )
            if response.status_code == 200:
                logger.info("관리자 로그인 성공")
                return True
            else:
                logger.error(f"로그인 실패: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"로그인 중 오류: {e}")
            return False

    def test_notification_creation(self) -> Dict[str, Any]:
        """알림 생성 테스트"""
        try:
            logger.info("알림 생성 테스트 시작")

            notification_data = {
                "channel_id": "system",
                "title": "테스트 알림",
                "message": "실시간 알림 시스템 자동화 테스트입니다.",
                "type": "info",
            }

            response = self.session.post(
                f"{self.base_url}/api/notifications/send", json=notification_data
            )

            if response.status_code == 200:
                data = response.json()
                logger.info("알림 생성 성공")
                logger.info(f"알림 ID: {data.get('notification_id')}")
                return {"success": True, "data": data, "message": "알림 생성 성공"}
            else:
                logger.error(f"알림 생성 실패: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "알림 생성 실패",
                }

        except Exception as e:
            logger.error(f"알림 생성 테스트 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "알림 생성 테스트 중 오류 발생",
            }

    def test_notification_list(self) -> Dict[str, Any]:
        """알림 목록 조회 테스트"""
        try:
            logger.info("알림 목록 조회 테스트 시작")

            response = self.session.get(f"{self.base_url}/api/notifications/user")

            if response.status_code == 200:
                data = response.json()
                notifications = data.get("notifications", [])
                logger.info(f"알림 목록 조회 성공: {len(notifications)}개")

                for notif in notifications[:3]:  # 처음 3개만 로그
                    logger.info(
                        f"  - {notif.get('title', notif.get('message'))} ({notif.get('type')})"
                    )

                return {
                    "success": True,
                    "data": data,
                    "message": f"알림 목록 조회 성공 ({len(notifications)}개)",
                }
            else:
                logger.error(f"알림 목록 조회 실패: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "알림 목록 조회 실패",
                }

        except Exception as e:
            logger.error(f"알림 목록 조회 테스트 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "알림 목록 조회 테스트 중 오류 발생",
            }

    def test_notification_channels(self) -> Dict[str, Any]:
        """알림 채널 테스트"""
        try:
            logger.info("알림 채널 테스트 시작")

            response = self.session.get(f"{self.base_url}/api/notifications/channels")

            if response.status_code == 200:
                data = response.json()
                channels = data.get("channels", [])
                logger.info(f"알림 채널 조회 성공: {len(channels)}개")

                for channel in channels:
                    logger.info(
                        f"  - {channel.get('name')} ({channel.get('type')}): {channel.get('enabled')}"
                    )

                return {
                    "success": True,
                    "data": data,
                    "message": f"알림 채널 조회 성공 ({len(channels)}개)",
                }
            else:
                logger.error(f"알림 채널 조회 실패: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "알림 채널 조회 실패",
                }

        except Exception as e:
            logger.error(f"알림 채널 테스트 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "알림 채널 테스트 중 오류 발생",
            }

    def test_notification_templates(self) -> Dict[str, Any]:
        """알림 템플릿 테스트"""
        try:
            logger.info("알림 템플릿 테스트 시작")

            response = self.session.get(f"{self.base_url}/api/notifications/templates")

            if response.status_code == 200:
                data = response.json()
                templates = data.get("templates", [])
                logger.info(f"알림 템플릿 조회 성공: {len(templates)}개")

                for template in templates:
                    logger.info(
                        f"  - {template.get('name')} ({template.get('category')})"
                    )

                return {
                    "success": True,
                    "data": data,
                    "message": f"알림 템플릿 조회 성공 ({len(templates)}개)",
                }
            else:
                logger.error(f"알림 템플릿 조회 실패: {response.status_code}")
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": "알림 템플릿 조회 실패",
                }

        except Exception as e:
            logger.error(f"알림 템플릿 테스트 중 오류: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "알림 템플릿 테스트 중 오류 발생",
            }

    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== 실시간 알림 시스템 종합 테스트 시작 ===")

        # 로그인
        if not self.login():
            return {
                "success": False,
                "error": "로그인 실패",
                "message": "로그인에 실패하여 테스트를 중단합니다.",
            }

        tests = [
            ("알림 생성", self.test_notification_creation),
            ("알림 목록", self.test_notification_list),
            ("알림 채널", self.test_notification_channels),
            ("알림 템플릿", self.test_notification_templates),
        ]

        results = []
        success_count = 0

        for test_name, test_func in tests:
            logger.info(f"\n--- {test_name} 테스트 ---")
            result = test_func()
            results.append({"test_name": test_name, "result": result})

            if result["success"]:
                logger.info(f"✅ {test_name} 테스트 성공")
                success_count += 1
            else:
                logger.error(
                    f"❌ {test_name} 테스트 실패: {result.get('message', '알 수 없는 오류')}"
                )

        # 결과 요약
        total_tests = len(tests)
        success_rate = (success_count / total_tests) * 100

        logger.info(f"\n=== 테스트 결과 요약 ===")
        logger.info(f"총 테스트: {total_tests}개")
        logger.info(f"성공: {success_count}개")
        logger.info(f"실패: {total_tests - success_count}개")
        logger.info(f"성공률: {success_rate:.1f}%")

        if success_count == total_tests:
            logger.info("🎉 모든 테스트가 성공했습니다!")
        else:
            logger.warning("⚠️ 일부 테스트가 실패했습니다.")

        return {
            "success": success_count == total_tests,
            "total_tests": total_tests,
            "success_count": success_count,
            "success_rate": success_rate,
            "results": results,
            "timestamp": datetime.now().isoformat(),
        }

    def save_test_results(
        self, results: Dict[str, Any], filename: str = None
    ):  # pyright: ignore
        """테스트 결과 저장"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"realtime_notifications_test_results_{timestamp}.json"

        try:
            # 기존 테스트 결과 파일들 정리 (7일 이상 된 파일 삭제)
            self.cleanup_old_test_files()

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")

    def cleanup_old_test_files(self, days_to_keep: int = 7):
        """7일 이상 된 테스트 결과 파일들을 자동으로 삭제"""
        try:
            import glob
            from datetime import datetime, timedelta

            # 현재 디렉토리에서 테스트 결과 파일들 찾기
            pattern = "realtime_notifications_test_results_*.json"
            files = glob.glob(pattern)

            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            deleted_count = 0

            for file_path in files:
                try:
                    # 파일명에서 날짜 추출 (YYYYMMDD_HHMMSS 형식)
                    filename = os.path.basename(file_path)
                    date_str = filename.replace(
                        "realtime_notifications_test_results_", ""
                    ).replace(".json", "")
                    file_date = datetime.strptime(date_str, "%Y%m%d_%H%M%S")

                    if file_date < cutoff_date:
                        os.remove(file_path)
                        deleted_count += 1
                        logger.info(f"오래된 테스트 파일 삭제: {filename}")
                except Exception as e:
                    logger.warning(f"파일 삭제 중 오류 ({file_path}): {e}")

            if deleted_count > 0:
                logger.info(
                    f"총 {deleted_count}개의 오래된 테스트 파일이 정리되었습니다."
                )

        except Exception as e:
            logger.error(f"테스트 파일 정리 중 오류: {e}")


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="실시간 알림 시스템 테스트")
    parser.add_argument(
        "--base-url", default="http://localhost:5000", help="서버 기본 URL"
    )
    parser.add_argument("--save-results", action="store_true", help="테스트 결과 저장")
    args = parser.parse_args()

    tester = RealtimeNotificationsTester(args.base_url)
    results = tester.run_all_tests()

    if args.save_results:
        tester.save_test_results(results)


if __name__ == "__main__":
    main()
