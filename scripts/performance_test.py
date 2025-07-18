#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
성능 테스트 스크립트
Redis 없이도 작동하는 기본 성능 테스트
"""

import requests
import time
import json
import statistics
from datetime import datetime
from typing import Dict, List, Any
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTester:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.results = {}

    def test_endpoint(
        self,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
        headers: Dict = None,
        iterations: int = 10,
    ) -> Dict[str, Any]:
        """엔드포인트 성능 테스트"""
        url = f"{self.base_url}{endpoint}"
        response_times = []
        success_count = 0
        error_count = 0
        errors = []

        logger.info(f"테스트 중: {method} {endpoint}")

        for i in range(iterations):
            try:
                start_time = time.time()

                if method.upper() == "GET":
                    response = requests.get(url, headers=headers, timeout=10)
                elif method.upper() == "POST":
                    response = requests.post(
                        url, json=data, headers=headers, timeout=10
                    )
                else:
                    raise ValueError(f"지원하지 않는 HTTP 메서드: {method}")

                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # ms로 변환

                if response.status_code < 400:
                    success_count += 1
                    response_times.append(response_time)
                else:
                    error_count += 1
                    errors.append(f"HTTP {response.status_code}: {response.text}")

            except requests.exceptions.Timeout:
                error_count += 1
                errors.append("Timeout (10초 초과)")
            except Exception as e:
                error_count += 1
                errors.append(f"오류: {str(e)}")

        # 통계 계산
        if response_times:
            avg_time = statistics.mean(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            median_time = statistics.median(response_times)
        else:
            avg_time = min_time = max_time = median_time = 0

        result = {
            "endpoint": endpoint,
            "method": method,
            "iterations": iterations,
            "success_count": success_count,
            "error_count": error_count,
            "success_rate": (success_count / iterations) * 100,
            "response_times": {
                "average_ms": round(avg_time, 2),
                "min_ms": round(min_time, 2),
                "max_ms": round(max_time, 2),
                "median_ms": round(median_time, 2),
            },
            "performance_grade": self._grade_performance(avg_time),
            "errors": errors[:5],  # 최대 5개 오류만 표시
        }

        return result

    def _grade_performance(self, avg_time_ms: float) -> str:
        """성능 등급 평가"""
        if avg_time_ms < 500:
            return "A+ (우수)"
        elif avg_time_ms < 1000:
            return "A (양호)"
        elif avg_time_ms < 2000:
            return "B (보통)"
        elif avg_time_ms < 5000:
            return "C (느림)"
        else:
            return "D (매우 느림)"

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 성능 테스트 실행"""
        logger.info("=== Your Program 성능 테스트 시작 ===")

        test_cases = [
            {"endpoint": "/health", "method": "GET", "iterations": 20},
            {"endpoint": "/api/status", "method": "GET", "iterations": 15},
            {
                "endpoint": "/api/plugin-system/health",
                "method": "GET",
                "iterations": 10,
            },
            {"endpoint": "/api/performance/health", "method": "GET", "iterations": 10},
            {
                "endpoint": "/api/auth/login",
                "method": "POST",
                "data": {"username": "admin", "password": "admin123"},
                "iterations": 5,
            },
        ]

        results = []
        total_success = 0
        total_errors = 0
        all_response_times = []

        for test_case in test_cases:
            result = self.test_endpoint(**test_case)
            results.append(result)

            total_success += result["success_count"]
            total_errors += result["error_count"]
            all_response_times.extend(
                [r for r in result["response_times"].values() if r > 0]
            )

            # 결과 출력
            logger.info(
                f"✅ {result['endpoint']}: {result['performance_grade']} "
                f"(평균: {result['response_times']['average_ms']}ms)"
            )

        # 전체 통계
        overall_stats = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(test_cases),
            "total_success": total_success,
            "total_errors": total_errors,
            "overall_success_rate": (
                (total_success / (total_success + total_errors)) * 100
                if (total_success + total_errors) > 0
                else 0
            ),
            "average_response_time": (
                round(statistics.mean(all_response_times), 2)
                if all_response_times
                else 0
            ),
            "max_response_time": max(all_response_times) if all_response_times else 0,
            "performance_issues": [],
        }

        # 성능 이슈 확인
        for result in results:
            if result["response_times"]["average_ms"] > 2000:
                overall_stats["performance_issues"].append(
                    {
                        "endpoint": result["endpoint"],
                        "issue": f"응답 시간이 2초 초과: {result['response_times']['average_ms']}ms",
                    }
                )

            if result["success_rate"] < 80:
                overall_stats["performance_issues"].append(
                    {
                        "endpoint": result["endpoint"],
                        "issue": f"성공률이 낮음: {result['success_rate']:.1f}%",
                    }
                )

        # 최종 결과
        final_result = {
            "overall_stats": overall_stats,
            "detailed_results": results,
            "summary": self._generate_summary(overall_stats, results),
        }

        return final_result

    def _generate_summary(self, overall_stats: Dict, results: List[Dict]) -> str:
        """테스트 결과 요약 생성"""
        summary = f"""
=== Your Program 성능 테스트 결과 ===
테스트 시간: {overall_stats['timestamp']}
총 테스트 수: {overall_stats['total_tests']}
전체 성공률: {overall_stats['overall_success_rate']:.1f}%
평균 응답 시간: {overall_stats['average_response_time']}ms
최대 응답 시간: {overall_stats['max_response_time']}ms

성능 이슈: {len(overall_stats['performance_issues'])}개
"""

        if overall_stats["performance_issues"]:
            summary += "\n🚨 발견된 성능 이슈:\n"
            for issue in overall_stats["performance_issues"]:
                summary += f"  - {issue['endpoint']}: {issue['issue']}\n"
        else:
            summary += "\n✅ 성능 이슈 없음\n"

        return summary


def main():
    """메인 실행 함수"""
    tester = PerformanceTester()

    try:
        result = tester.run_comprehensive_test()

        # 결과 출력
        print(result["summary"])

        # 상세 결과를 JSON 파일로 저장
        with open("performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(
            f"\n📊 상세 결과가 'performance_test_results.json' 파일에 저장되었습니다."
        )

        # 성능 등급별 분류
        print("\n📈 엔드포인트별 성능 등급:")
        for test_result in result["detailed_results"]:
            grade = test_result["performance_grade"]
            endpoint = test_result["endpoint"]
            avg_time = test_result["response_times"]["average_ms"]
            print(f"  {grade:<12} - {endpoint} ({avg_time}ms)")

    except Exception as e:
        logger.error(f"성능 테스트 실행 중 오류 발생: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
