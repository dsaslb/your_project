#!/usr/bin/env python3
"""
데이터 분석 시스템 테스트 스크립트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"

class AnalyticsSystemTester:
    def __init__(self):
        self.session = requests.Session()

    def print_test_result(self, test_name, success, message=""):
        """테스트 결과 출력"""
        status = "✅ 성공" if success else "❌ 실패"
        print(f"{test_name}: {status}")
        if message:
            print(f"  └─ {message}")
        print()

    def test_health_check(self):
        """분석 시스템 상태 확인 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test_result(
                    "분석 시스템 상태 확인",
                    True,
                    f"총 분석: {data.get('data', {}).get('total_analyses', 0)}개"
                )
                return True
            else:
                self.print_test_result("분석 시스템 상태 확인", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("분석 시스템 상태 확인", False, f"오류: {str(e)}")
            return False

    def test_analytics_summary(self):
        """분석 요약 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/summary")
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    summary = data.get('data', {})
                    self.print_test_result(
                        "분석 요약 조회",
                        True,
                        f"총 분석: {summary.get('total_analyses', 0)}개, 모델: {summary.get('total_models', 0)}개"
                    )
                    return True
                else:
                    self.print_test_result("분석 요약 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("분석 요약 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("분석 요약 조회", False, f"오류: {str(e)}")
            return False

    def test_trend_analysis(self):
        """트렌드 분석 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/trends", json={
                "data_source": "sales",
                "metric": "daily_sales",
                "time_period": "30d"
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results = data.get('data', {}).get('results', {})
                    self.print_test_result(
                        "트렌드 분석",
                        True,
                        f"방향: {results.get('trend_direction')}, 강도: {results.get('trend_strength', 0):.2f}"
                    )
                    return True
                else:
                    self.print_test_result("트렌드 분석", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("트렌드 분석", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("트렌드 분석", False, f"오류: {str(e)}")
            return False

    def test_sales_prediction(self):
        """매출 예측 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/predictions/sales", json={
                "days_ahead": 30
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    prediction_data = data.get('data', {})
                    self.print_test_result(
                        "매출 예측",
                        True,
                        f"총 예측: {prediction_data.get('total_predicted_sales', 0):,.0f}원, 정확도: {prediction_data.get('model_accuracy', 0)*100:.1f}%"
                    )
                    return True
                else:
                    self.print_test_result("매출 예측", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("매출 예측", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("매출 예측", False, f"오류: {str(e)}")
            return False

    def test_correlation_analysis(self):
        """상관관계 분석 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/correlations", json={
                "data_source": "business_data",
                "variables": ["sales", "advertising", "price", "customer_satisfaction"]
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results = data.get('data', {}).get('results', {})
                    strong_correlations = results.get('strong_correlations', [])
                    self.print_test_result(
                        "상관관계 분석",
                        True,
                        f"강한 상관관계: {len(strong_correlations)}개, 샘플 크기: {results.get('sample_size', 0)}"
                    )
                    return True
                else:
                    self.print_test_result("상관관계 분석", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("상관관계 분석", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("상관관계 분석", False, f"오류: {str(e)}")
            return False

    def test_clustering_analysis(self):
        """클러스터링 분석 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/clustering", json={
                "data_source": "customer_data",
                "features": ["purchase_frequency", "avg_order_value", "customer_lifetime"],
                "n_clusters": 3
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results = data.get('data', {}).get('results', {})
                    n_clusters = results.get('n_clusters', 0)
                    cluster_characteristics = results.get('cluster_characteristics', {})
                    self.print_test_result(
                        "클러스터링 분석",
                        True,
                        f"클러스터: {n_clusters}개, 특성: {len(results.get('features', []))}개"
                    )
                    return True
                else:
                    self.print_test_result("클러스터링 분석", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("클러스터링 분석", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("클러스터링 분석", False, f"오류: {str(e)}")
            return False

    def test_anomaly_detection(self):
        """이상 탐지 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/anomalies", json={
                "data_source": "system_logs",
                "metric": "response_time",
                "threshold": 2.0
            })

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    results = data.get('data', {}).get('results', {})
                    total_anomalies = results.get('total_anomalies', 0)
                    data_points = results.get('data_points', 0)
                    self.print_test_result(
                        "이상 탐지",
                        True,
                        f"이상: {total_anomalies}개, 데이터 포인트: {data_points}개"
                    )
                    return True
                else:
                    self.print_test_result("이상 탐지", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("이상 탐지", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("이상 탐지", False, f"오류: {str(e)}")
            return False

    def test_get_insights(self):
        """인사이트 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/insights?limit=10")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    insights = data.get('data', [])
                    self.print_test_result(
                        "인사이트 조회",
                        True,
                        f"총 {len(insights)}개의 인사이트"
                    )
                    return True
                else:
                    self.print_test_result("인사이트 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("인사이트 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("인사이트 조회", False, f"오류: {str(e)}")
            return False

    def test_generate_insights(self):
        """인사이트 생성 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/insights/generate")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    insights = data.get('data', [])
                    self.print_test_result(
                        "인사이트 생성",
                        True,
                        f"{len(insights)}개의 인사이트가 생성되었습니다"
                    )
                    return True
                else:
                    self.print_test_result("인사이트 생성", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("인사이트 생성", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("인사이트 생성", False, f"오류: {str(e)}")
            return False

    def test_get_realtime_metrics(self):
        """실시간 메트릭 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/realtime?limit=10")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    metrics = data.get('data', [])
                    self.print_test_result(
                        "실시간 메트릭 조회",
                        True,
                        f"총 {len(metrics)}개의 메트릭"
                    )
                    return True
                else:
                    self.print_test_result("실시간 메트릭 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("실시간 메트릭 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("실시간 메트릭 조회", False, f"오류: {str(e)}")
            return False

    def test_update_realtime_metrics(self):
        """실시간 메트릭 업데이트 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/realtime/update")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    metrics_count = data.get('data', {}).get('metrics_count', 0)
                    self.print_test_result(
                        "실시간 메트릭 업데이트",
                        True,
                        f"업데이트된 메트릭: {metrics_count}개"
                    )
                    return True
                else:
                    self.print_test_result("실시간 메트릭 업데이트", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("실시간 메트릭 업데이트", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("실시간 메트릭 업데이트", False, f"오류: {str(e)}")
            return False

    def test_get_prediction_models(self):
        """예측 모델 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/models")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    models = data.get('data', [])
                    self.print_test_result(
                        "예측 모델 조회",
                        True,
                        f"총 {len(models)}개의 모델"
                    )
                    return True
                else:
                    self.print_test_result("예측 모델 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("예측 모델 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("예측 모델 조회", False, f"오류: {str(e)}")
            return False

    def test_create_prediction_model(self):
        """예측 모델 생성 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/models", json={
                "name": "테스트 예측 모델",
                "type": "sales",
                "algorithm": "linear_regression",
                "features": ["month", "day_of_week", "holiday"],
                "target": "sales_amount"
            })

            if response.status_code == 201:
                data = response.json()
                if data.get('status') == 'success':
                    model_id = data.get('data', {}).get('model_id')
                    self.print_test_result(
                        "예측 모델 생성",
                        True,
                        f"모델 ID: {model_id}"
                    )
                    return True
                else:
                    self.print_test_result("예측 모델 생성", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("예측 모델 생성", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("예측 모델 생성", False, f"오류: {str(e)}")
            return False

    def test_get_analysis_results(self):
        """분석 결과 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/analytics/analyses?limit=10")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    analyses = data.get('data', [])
                    self.print_test_result(
                        "분석 결과 조회",
                        True,
                        f"총 {len(analyses)}개의 분석 결과"
                    )
                    return True
                else:
                    self.print_test_result("분석 결과 조회", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("분석 결과 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("분석 결과 조회", False, f"오류: {str(e)}")
            return False

    def test_clear_cache(self):
        """캐시 정리 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/analytics/cache/clear")

            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    self.print_test_result(
                        "캐시 정리",
                        True,
                        "분석 캐시가 정리되었습니다"
                    )
                    return True
                else:
                    self.print_test_result("캐시 정리", False, data.get('message', '알 수 없는 오류'))
                    return False
            else:
                self.print_test_result("캐시 정리", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("캐시 정리", False, f"오류: {str(e)}")
            return False

    def run_all_tests(self):
        """모든 테스트 실행"""
        print("📊 데이터 분석 시스템 테스트 시작")
        print("=" * 50)

        tests = [
            ("시스템 상태 확인", self.test_health_check),
            ("분석 요약 조회", self.test_analytics_summary),
            ("트렌드 분석", self.test_trend_analysis),
            ("매출 예측", self.test_sales_prediction),
            ("상관관계 분석", self.test_correlation_analysis),
            ("클러스터링 분석", self.test_clustering_analysis),
            ("이상 탐지", self.test_anomaly_detection),
            ("인사이트 조회", self.test_get_insights),
            ("인사이트 생성", self.test_generate_insights),
            ("실시간 메트릭 조회", self.test_get_realtime_metrics),
            ("실시간 메트릭 업데이트", self.test_update_realtime_metrics),
            ("예측 모델 조회", self.test_get_prediction_models),
            ("예측 모델 생성", self.test_create_prediction_model),
            ("분석 결과 조회", self.test_get_analysis_results),
            ("캐시 정리", self.test_clear_cache),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                time.sleep(0.5)  # API 호출 간격
            except Exception as e:
                self.print_test_result(test_name, False, f"테스트 실행 오류: {str(e)}")

        print("=" * 50)
        print(f"📊 테스트 결과: {passed}/{total} 통과")

        if passed == total:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")

        return passed == total

def main():
    """메인 함수"""
    print("데이터 분석 시스템 테스트를 시작합니다...")
    print(f"테스트 대상 URL: {BASE_URL}")
    print()

    tester = AnalyticsSystemTester()
    success = tester.run_all_tests()

    if success:
        print("\n✅ 데이터 분석 시스템이 정상적으로 작동합니다!")
    else:
        print("\n❌ 데이터 분석 시스템에 문제가 있습니다. 로그를 확인해주세요.")

    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 