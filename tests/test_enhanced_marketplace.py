#!/usr/bin/env python3
"""
고도화된 플러그인 마켓플레이스 시스템 테스트
- 검색/필터/정렬, 상세 정보, 설치/업데이트/삭제, 리뷰/평점, 통계/추천
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


class EnhancedMarketplaceTester:
    """고도화된 마켓플레이스 테스터"""

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

    def test_marketplace_stats(self) -> bool:
        """마켓플레이스 통계 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/stats"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    stats = data["data"]
                    required_fields = [
                        "total_plugins",
                        "total_downloads",
                        "average_rating",
                        "free_plugins",
                        "paid_plugins",
                        "categories",
                    ]

                    for field in required_fields:
                        if field not in stats:
                            self.log_test(
                                "마켓플레이스 통계", False, f"필수 필드 누락: {field}"
                            )
                            return False

                    self.log_test(
                        "마켓플레이스 통계",
                        True,
                        f"통계 조회 성공 - 플러그인: {stats['total_plugins']}, 다운로드: {stats['total_downloads']}",
                    )
                    return True
                else:
                    self.log_test("마켓플레이스 통계", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "마켓플레이스 통계", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("마켓플레이스 통계", False, f"예외 발생: {str(e)}")
            return False

    def test_categories(self) -> bool:
        """카테고리 목록 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/categories"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    categories = data["data"]
                    if isinstance(categories, list) and len(categories) > 0:
                        self.log_test(
                            "카테고리 목록",
                            True,
                            f"카테고리 {len(categories)}개 조회 성공: {categories}",
                        )
                        return True
                    else:
                        self.log_test("카테고리 목록", False, "카테고리가 비어있음")
                        return False
                else:
                    self.log_test("카테고리 목록", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "카테고리 목록", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("카테고리 목록", False, f"예외 발생: {str(e)}")
            return False

    def test_plugins_list(self) -> bool:
        """플러그인 목록 테스트"""
        try:
            # 기본 목록 조회
            response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/plugins"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    plugins = data["data"]
                    if isinstance(plugins, list):
                        self.log_test(
                            "플러그인 목록",
                            True,
                            f"플러그인 {len(plugins)}개 조회 성공",
                        )

                        # 검색 테스트
                        search_response = self.session.get(
                            f"{self.base_url}/api/enhanced-marketplace/plugins?search=레스토랑"
                        )
                        if search_response.status_code == 200:
                            search_data = search_response.json()
                            if search_data.get("success"):
                                self.log_test(
                                    "플러그인 검색", True, "검색 기능 정상 작동"
                                )

                        # 정렬 테스트
                        sort_response = self.session.get(
                            f"{self.base_url}/api/enhanced-marketplace/plugins?sort_by=rating&sort_order=desc"
                        )
                        if sort_response.status_code == 200:
                            sort_data = sort_response.json()
                            if sort_data.get("success"):
                                self.log_test(
                                    "플러그인 정렬", True, "정렬 기능 정상 작동"
                                )

                        return True
                    else:
                        self.log_test(
                            "플러그인 목록", False, "플러그인 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("플러그인 목록", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "플러그인 목록", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("플러그인 목록", False, f"예외 발생: {str(e)}")
            return False

    def test_plugin_detail(self) -> bool:
        """플러그인 상세 정보 테스트"""
        try:
            # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/plugins?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    plugin_id = list_data["data"][0]["id"]

                    # 상세 정보 조회
                    detail_response = self.session.get(
                        f"{self.base_url}/api/enhanced-marketplace/plugins/{plugin_id}"
                    )

                    if detail_response.status_code == 200:
                        detail_data = detail_response.json()
                        if detail_data.get("success") and "data" in detail_data:
                            plugin = detail_data["data"]
                            required_fields = [
                                "id",
                                "name",
                                "description",
                                "version",
                                "author",
                                "category",
                            ]

                            for field in required_fields:
                                if field not in plugin:
                                    self.log_test(
                                        "플러그인 상세",
                                        False,
                                        f"필수 필드 누락: {field}",
                                    )
                                    return False

                            self.log_test(
                                "플러그인 상세",
                                True,
                                f"플러그인 '{plugin['name']}' 상세 정보 조회 성공",
                            )
                            return True
                        else:
                            self.log_test(
                                "플러그인 상세", False, "응답 형식 오류", detail_data
                            )
                            return False
                    else:
                        self.log_test(
                            "플러그인 상세",
                            False,
                            f"HTTP 오류: {detail_response.status_code}",
                        )
                        return False
                else:
                    self.log_test("플러그인 상세", False, "테스트할 플러그인이 없음")
                    return False
            else:
                self.log_test(
                    "플러그인 상세",
                    False,
                    f"플러그인 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("플러그인 상세", False, f"예외 발생: {str(e)}")
            return False

    def test_plugin_reviews(self) -> bool:
        """플러그인 리뷰 테스트"""
        try:
            # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/plugins?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    plugin_id = list_data["data"][0]["id"]

                    # 리뷰 목록 조회
                    reviews_response = self.session.get(
                        f"{self.base_url}/api/enhanced-marketplace/plugins/{plugin_id}/reviews"
                    )

                    if reviews_response.status_code == 200:
                        reviews_data = reviews_response.json()
                        if reviews_data.get("success") and "data" in reviews_data:
                            reviews = reviews_data["data"]
                            self.log_test(
                                "플러그인 리뷰",
                                True,
                                f"리뷰 {len(reviews)}개 조회 성공",
                            )
                            return True
                        else:
                            self.log_test(
                                "플러그인 리뷰", False, "응답 형식 오류", reviews_data
                            )
                            return False
                    else:
                        self.log_test(
                            "플러그인 리뷰",
                            False,
                            f"HTTP 오류: {reviews_response.status_code}",
                        )
                        return False
                else:
                    self.log_test("플러그인 리뷰", False, "테스트할 플러그인이 없음")
                    return False
            else:
                self.log_test(
                    "플러그인 리뷰",
                    False,
                    f"플러그인 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("플러그인 리뷰", False, f"예외 발생: {str(e)}")
            return False

    def test_popular_plugins(self) -> bool:
        """인기 플러그인 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/popular?limit=5"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    plugins = data["data"]
                    if isinstance(plugins, list):
                        self.log_test(
                            "인기 플러그인",
                            True,
                            f"인기 플러그인 {len(plugins)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "인기 플러그인", False, "인기 플러그인 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("인기 플러그인", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "인기 플러그인", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("인기 플러그인", False, f"예외 발생: {str(e)}")
            return False

    def test_recommended_plugins(self) -> bool:
        """추천 플러그인 테스트"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/recommended?limit=5"
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success") and "data" in data:
                    plugins = data["data"]
                    if isinstance(plugins, list):
                        self.log_test(
                            "추천 플러그인",
                            True,
                            f"추천 플러그인 {len(plugins)}개 조회 성공",
                        )
                        return True
                    else:
                        self.log_test(
                            "추천 플러그인", False, "추천 플러그인 목록이 배열이 아님"
                        )
                        return False
                else:
                    self.log_test("추천 플러그인", False, "응답 형식 오류", data)
                    return False
            else:
                self.log_test(
                    "추천 플러그인", False, f"HTTP 오류: {response.status_code}"
                )
                return False

        except Exception as e:
            self.log_test("추천 플러그인", False, f"예외 발생: {str(e)}")
            return False

    def test_plugin_download(self) -> bool:
        """플러그인 다운로드 테스트 (로그인 필요)"""
        try:
            # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
            list_response = self.session.get(
                f"{self.base_url}/api/enhanced-marketplace/plugins?limit=1"
            )

            if list_response.status_code == 200:
                list_data = list_response.json()
                if list_data.get("success") and list_data["data"]:
                    plugin_id = list_data["data"][0]["id"]

                    # 다운로드 시도 (로그인 없이 401 예상)
                    download_response = self.session.post(
                        f"{self.base_url}/api/enhanced-marketplace/plugins/{plugin_id}/download",
                        json={"version": "latest"},
                    )

                    if download_response.status_code in [401, 403]:
                        self.log_test(
                            "플러그인 다운로드", True, "인증 필요 (예상된 동작)"
                        )
                        return True
                    elif download_response.status_code == 200:
                        download_data = download_response.json()
                        if download_data.get("success"):
                            self.log_test("플러그인 다운로드", True, "다운로드 성공")
                            return True
                        else:
                            self.log_test(
                                "플러그인 다운로드",
                                False,
                                "다운로드 실패",
                                download_data,
                            )
                            return False
                    else:
                        self.log_test(
                            "플러그인 다운로드",
                            False,
                            f"예상치 못한 HTTP 상태: {download_response.status_code}",
                        )
                        return False
                else:
                    self.log_test(
                        "플러그인 다운로드", False, "테스트할 플러그인이 없음"
                    )
                    return False
            else:
                self.log_test(
                    "플러그인 다운로드",
                    False,
                    f"플러그인 목록 조회 실패: {list_response.status_code}",
                )
                return False

        except Exception as e:
            self.log_test("플러그인 다운로드", False, f"예외 발생: {str(e)}")
            return False

    def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        print("🚀 고도화된 플러그인 마켓플레이스 시스템 테스트 시작")
        print("=" * 60)

        start_time = time.time()

        # 테스트 실행
        tests = [
            ("마켓플레이스 통계", self.test_marketplace_stats),
            ("카테고리 목록", self.test_categories),
            ("플러그인 목록", self.test_plugins_list),
            ("플러그인 상세", self.test_plugin_detail),
            ("플러그인 리뷰", self.test_plugin_reviews),
            ("인기 플러그인", self.test_popular_plugins),
            ("추천 플러그인", self.test_recommended_plugins),
            ("플러그인 다운로드", self.test_plugin_download),
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
        description="고도화된 플러그인 마켓플레이스 시스템 테스트"
    )
    parser.add_argument(
        "--url", default="http://localhost:5000", help="테스트할 서버 URL"
    )
    parser.add_argument("--output", help="결과를 JSON 파일로 저장")

    args = parser.parse_args()

    # 테스터 생성 및 실행
    tester = EnhancedMarketplaceTester(args.url)
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
