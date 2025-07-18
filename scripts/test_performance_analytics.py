#!/usr/bin/env python3
"""
성능 분석 시스템 테스트 스크립트
운영 데이터 기반 성능 분석 및 튜닝 시스템의 기능을 테스트
"""

import requests
import time
import random
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List


class PerformanceAnalyticsTester:
    """성능 분석 시스템 테스터"""

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
            "timestamp": datetime.now().isoformat(),
            "data": data,
        }
        self.test_results.append(result)

        status = "✅ 성공" if success else "❌ 실패"
        print(f"[{status}] {test_name}: {message}")

        if data and not success:
            print(f"   데이터: {json.dumps(data, indent=2, ensure_ascii=False)}")

    def test_analytics_start_stop(self) -> bool:
        """분석 시스템 시작/중지 테스트"""
        try:
            # 시작 테스트
            response = self.session.post(f"{self.base_url}/api/performance/start")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "분석 시스템 시작", False, data.get("error", "알 수 없는 오류")
                )
                return False

            self.log_test(
                "분석 시스템 시작", True, "분석 시스템이 성공적으로 시작되었습니다"
            )

            # 잠시 대기
            time.sleep(2)

            # 중지 테스트
            response = self.session.post(f"{self.base_url}/api/performance/stop")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "분석 시스템 중지", False, data.get("error", "알 수 없는 오류")
                )
                return False

            self.log_test(
                "분석 시스템 중지", True, "분석 시스템이 성공적으로 중지되었습니다"
            )
            return True

        except Exception as e:
            self.log_test("분석 시스템 시작/중지", False, f"예외 발생: {e}")
            return False

    def test_metric_collection(self) -> bool:
        """메트릭 수집 테스트"""
        try:
            # 다양한 메트릭 수집 테스트
            test_metrics = [
                {
                    "metric_type": "response_time",
                    "value": random.uniform(0.1, 5.0),
                    "plugin_id": "test_plugin_1",
                    "component": "api",
                },
                {
                    "metric_type": "memory_usage",
                    "value": random.uniform(30.0, 95.0),
                    "plugin_id": "test_plugin_2",
                    "component": "system",
                },
                {
                    "metric_type": "cpu_usage",
                    "value": random.uniform(20.0, 90.0),
                    "plugin_id": "test_plugin_3",
                    "component": "processor",
                },
                {
                    "metric_type": "error_rate",
                    "value": random.uniform(0.0, 20.0),
                    "plugin_id": "test_plugin_4",
                    "component": "error_handler",
                },
            ]

            success_count = 0
            for i, metric in enumerate(test_metrics):
                response = self.session.post(
                    f"{self.base_url}/api/performance/collect", json=metric
                )
                data = response.json()

                if data.get("success"):
                    success_count += 1
                    self.log_test(
                        f"메트릭 수집 {i+1}", True, f"{metric['metric_type']} 수집 성공"
                    )
                else:
                    self.log_test(
                        f"메트릭 수집 {i+1}",
                        False,
                        data.get("error", "알 수 없는 오류"),
                    )

            return success_count == len(test_metrics)

        except Exception as e:
            self.log_test("메트릭 수집", False, f"예외 발생: {e}")
            return False

    def test_performance_analysis(self) -> bool:
        """성능 분석 테스트"""
        try:
            # 분석 수행
            response = self.session.post(
                f"{self.base_url}/api/performance/analyze", json={"period_hours": 1}
            )
            data = response.json()

            if not data.get("success"):
                self.log_test("성능 분석", False, data.get("error", "알 수 없는 오류"))
                return False

            analysis_data = data.get("data", {})

            # 분석 결과 검증
            required_fields = [
                "analysis_id",
                "health_score",
                "metrics_summary",
                "bottlenecks",
                "recommendations",
            ]
            missing_fields = [
                field for field in required_fields if field not in analysis_data
            ]

            if missing_fields:
                self.log_test("성능 분석", False, f"필수 필드 누락: {missing_fields}")
                return False

            self.log_test(
                "성능 분석",
                True,
                f"분석 완료 (건강도: {analysis_data['health_score']:.1f})",
            )
            return True

        except Exception as e:
            self.log_test("성능 분석", False, f"예외 발생: {e}")
            return False

    def test_performance_report(self) -> bool:
        """성능 리포트 테스트"""
        try:
            # 리포트 조회
            response = self.session.get(f"{self.base_url}/api/performance/report")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "성능 리포트", False, data.get("error", "알 수 없는 오류")
                )
                return False

            report_data = data.get("data", {})

            # 리포트 데이터 검증
            if "analysis_id" not in report_data:
                self.log_test("성능 리포트", False, "분석 ID가 없습니다")
                return False

            self.log_test(
                "성능 리포트",
                True,
                f"리포트 조회 성공 (ID: {report_data['analysis_id']})",
            )
            return True

        except Exception as e:
            self.log_test("성능 리포트", False, f"예외 발생: {e}")
            return False

    def test_optimization_suggestions(self) -> bool:
        """최적화 제안사항 테스트"""
        try:
            # 제안사항 조회
            response = self.session.get(f"{self.base_url}/api/performance/suggestions")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "최적화 제안사항", False, data.get("error", "알 수 없는 오류")
                )
                return False

            suggestions_data = data.get("data", {})
            suggestions = suggestions_data.get("suggestions", [])

            self.log_test(
                "최적화 제안사항", True, f"제안사항 {len(suggestions)}개 조회 성공"
            )
            return True

        except Exception as e:
            self.log_test("최적화 제안사항", False, f"예외 발생: {e}")
            return False

    def test_metrics_summary(self) -> bool:
        """메트릭 요약 테스트"""
        try:
            # 메트릭 요약 조회
            response = self.session.get(f"{self.base_url}/api/performance/metrics")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "메트릭 요약", False, data.get("error", "알 수 없는 오류")
                )
                return False

            metrics_data = data.get("data", {})
            key_metrics = metrics_data.get("key_metrics", {})

            # 주요 메트릭 검증
            expected_metrics = [
                "avg_response_time",
                "avg_memory_usage",
                "avg_cpu_usage",
                "avg_error_rate",
            ]
            missing_metrics = [
                metric for metric in expected_metrics if metric not in key_metrics
            ]

            if missing_metrics:
                self.log_test("메트릭 요약", False, f"누락된 메트릭: {missing_metrics}")
                return False

            self.log_test("메트릭 요약", True, "메트릭 요약 조회 성공")
            return True

        except Exception as e:
            self.log_test("메트릭 요약", False, f"예외 발생: {e}")
            return False

    def test_bottlenecks(self) -> bool:
        """병목 지점 테스트"""
        try:
            # 병목 지점 조회
            response = self.session.get(f"{self.base_url}/api/performance/bottlenecks")
            data = response.json()

            if not data.get("success"):
                self.log_test("병목 지점", False, data.get("error", "알 수 없는 오류"))
                return False

            bottlenecks_data = data.get("data", {})
            bottlenecks = bottlenecks_data.get("bottlenecks", [])

            self.log_test(
                "병목 지점", True, f"병목 지점 {len(bottlenecks)}개 조회 성공"
            )
            return True

        except Exception as e:
            self.log_test("병목 지점", False, f"예외 발생: {e}")
            return False

    def test_trends(self) -> bool:
        """트렌드 분석 테스트"""
        try:
            # 트렌드 조회
            response = self.session.get(f"{self.base_url}/api/performance/trends")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "트렌드 분석", False, data.get("error", "알 수 없는 오류")
                )
                return False

            trends_data = data.get("data", {})
            trends = trends_data.get("trends", {})

            self.log_test("트렌드 분석", True, f"트렌드 {len(trends)}개 조회 성공")
            return True

        except Exception as e:
            self.log_test("트렌드 분석", False, f"예외 발생: {e}")
            return False

    def test_analytics_status(self) -> bool:
        """분석 시스템 상태 테스트"""
        try:
            # 상태 조회
            response = self.session.get(f"{self.base_url}/api/performance/status")
            data = response.json()

            if not data.get("success"):
                self.log_test(
                    "분석 시스템 상태", False, data.get("error", "알 수 없는 오류")
                )
                return False

            status_data = data.get("data", {})

            # 상태 정보 검증
            required_fields = [
                "running",
                "analysis_count",
                "metrics_storage",
                "config",
                "thresholds",
            ]
            missing_fields = [
                field for field in required_fields if field not in status_data
            ]

            if missing_fields:
                self.log_test(
                    "분석 시스템 상태", False, f"필수 필드 누락: {missing_fields}"
                )
                return False

            self.log_test(
                "분석 시스템 상태",
                True,
                f"상태 조회 성공 (실행중: {status_data['running']})",
            )
            return True

        except Exception as e:
            self.log_test("분석 시스템 상태", False, f"예외 발생: {e}")
            return False

    def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        print("🚀 성능 분석 시스템 종합 테스트 시작")
        print("=" * 60)

        # 테스트 시나리오
        test_scenarios = [
            ("분석 시스템 시작/중지", self.test_analytics_start_stop),
            ("메트릭 수집", self.test_metric_collection),
            ("성능 분석", self.test_performance_analysis),
            ("성능 리포트", self.test_performance_report),
            ("최적화 제안사항", self.test_optimization_suggestions),
            ("메트릭 요약", self.test_metrics_summary),
            ("병목 지점", self.test_bottlenecks),
            ("트렌드 분석", self.test_trends),
            ("분석 시스템 상태", self.test_analytics_status),
        ]

        # 테스트 실행
        results = {}
        for test_name, test_func in test_scenarios:
            try:
                success = test_func()
                results[test_name] = success
            except Exception as e:
                self.log_test(test_name, False, f"테스트 실행 중 예외: {e}")
                results[test_name] = False

        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)

        total_tests = len(test_scenarios)
        passed_tests = sum(1 for success in results.values() if success)
        failed_tests = total_tests - passed_tests

        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")

        # 실패한 테스트 목록
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for test_name, success in results.items():
                if not success:
                    print(f"  - {test_name}")

        # 상세 결과 저장
        test_summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "success_rate": (passed_tests / total_tests) * 100,
            "results": results,
            "detailed_results": self.test_results,
        }

        # 결과 파일 저장
        with open(
            "performance_analytics_test_results.json", "w", encoding="utf-8"
        ) as f:
            json.dump(test_summary, f, indent=2, ensure_ascii=False)

        print(
            f"\n📄 상세 결과가 'performance_analytics_test_results.json'에 저장되었습니다"
        )

        return test_summary


def main():
    """메인 함수"""
    import argparse

    parser = argparse.ArgumentParser(description="성능 분석 시스템 테스트")
    parser.add_argument(
        "--url", default="http://localhost:5000", help="테스트할 서버 URL"
    )
    parser.add_argument(
        "--output",
        default="performance_analytics_test_results.json",
        help="결과 파일 경로",
    )

    args = parser.parse_args()

    # 테스터 생성 및 실행
    tester = PerformanceAnalyticsTester(args.base_url)
    results = tester.run_comprehensive_test()

    # 종료 코드 설정
    exit_code = 0 if results["failed_tests"] == 0 else 1
    exit(exit_code)


if __name__ == "__main__":
    main()
