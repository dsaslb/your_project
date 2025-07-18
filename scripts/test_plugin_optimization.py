#!/usr/bin/env python3
"""
플러그인 성능 최적화 자동화 API 테스트 스크립트
"""
import requests
import time
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:5000"


class PluginOptimizationTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()

    def test_suggestions(self):
        logger.info("[1] 최적화 제안 목록 조회")
        try:
            r = self.session.get(f"{self.base_url}/api/plugin-optimization/suggestions")
            data = r.json()
            assert data["success"], data.get("message")
            logger.info(f"  - 제안 개수: {len(data['data'])}")
            if data["data"]:
                logger.info(f"  - 첫 제안: {data['data'][0]}")
            return data["data"]
        except Exception as e:
            logger.error(f"제안 목록 조회 실패: {e}")
            return []

    def test_execute(self, suggestion_id):
        logger.info(f"[2] 최적화 제안 실행: {suggestion_id}")
        try:
            r = self.session.post(
                f"{self.base_url}/api/plugin-optimization/execute/{suggestion_id}"
            )
            data = r.json()
            assert data["success"], data.get("message")
            logger.info(f"  - 실행 결과: {data['message']}")
            return True
        except Exception as e:
            logger.error(f"제안 실행 실패: {e}")
            return False

    def test_history(self):
        logger.info("[3] 최적화 실행 이력 조회")
        try:
            r = self.session.get(f"{self.base_url}/api/plugin-optimization/history")
            data = r.json()
            assert data["success"], data.get("message")
            logger.info(f"  - 이력 개수: {len(data['data'])}")
            if data["data"]:
                logger.info(f"  - 첫 이력: {data['data'][0]}")
            return data["data"]
        except Exception as e:
            logger.error(f"이력 조회 실패: {e}")
            return []

    def run(self):
        suggestions = self.test_suggestions()
        if suggestions:
            first_id = suggestions[0]["id"]
            self.test_execute(first_id)
            time.sleep(1)
        self.test_history()
        logger.info("테스트 완료!")


if __name__ == "__main__":
    PluginOptimizationTester().run()
