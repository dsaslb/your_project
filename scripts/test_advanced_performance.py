#!/usr/bin/env python3
"""
고도화된 성능 분석 기능 테스트 스크립트
실시간 성능 모니터링, 예측 분석, 자동 튜닝 등의 고급 기능을 테스트합니다.
"""

import requests
import json
import time
from datetime import datetime, timedelta

# 서버 설정
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api/advanced-performance"

def test_start_analytics():
    """성능 분석 시작 테스트"""
    print("\n=== 성능 분석 시작 테스트 ===")
    
    try:
        response = requests.post(f"{API_BASE}/start")
        print(f"성능 분석 시작: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"결과: {data}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"성능 분석 시작 테스트 실패: {e}")
        return False

def test_stop_analytics():
    """성능 분석 중지 테스트"""
    print("\n=== 성능 분석 중지 테스트 ===")
    
    try:
        response = requests.post(f"{API_BASE}/stop")
        print(f"성능 분석 중지: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"결과: {data}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"성능 분석 중지 테스트 실패: {e}")
        return False

def test_current_metrics():
    """현재 성능 메트릭 조회 테스트"""
    print("\n=== 현재 성능 메트릭 조회 테스트 ===")
    
    try:
        response = requests.get(f"{API_BASE}/metrics/current")
        print(f"현재 메트릭 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                metrics = data.get('data', {})
                print(f"CPU 사용률: {metrics.get('cpu_usage', 'N/A')}%")
                print(f"메모리 사용률: {metrics.get('memory_usage', 'N/A')}%")
                print(f"디스크 사용률: {metrics.get('disk_usage', 'N/A')}%")
                print(f"응답 시간: {metrics.get('response_time', 'N/A')}ms")
                print(f"오류율: {metrics.get('error_rate', 'N/A')}%")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"현재 메트릭 조회 테스트 실패: {e}")
        return False

def test_metrics_history():
    """성능 메트릭 이력 조회 테스트"""
    print("\n=== 성능 메트릭 이력 조회 테스트 ===")
    
    try:
        # 24시간 이력 조회
        response = requests.get(f"{API_BASE}/metrics/history?hours=24")
        print(f"메트릭 이력 조회 (24시간): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                history_data = data.get('data', {})
                print(f"이력 수: {history_data.get('count', 0)}")
                print(f"조회 시간 범위: {history_data.get('hours', 0)}시간")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        # 1시간 이력 조회
        response = requests.get(f"{API_BASE}/metrics/history?hours=1")
        print(f"메트릭 이력 조회 (1시간): {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                history_data = data.get('data', {})
                print(f"이력 수: {history_data.get('count', 0)}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"메트릭 이력 조회 테스트 실패: {e}")
        return False

def test_alerts():
    """성능 알림 조회 테스트"""
    print("\n=== 성능 알림 조회 테스트 ===")
    
    try:
        # 전체 알림 조회
        response = requests.get(f"{API_BASE}/alerts")
        print(f"전체 알림 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                alerts_data = data.get('data', {})
                print(f"전체 알림 수: {alerts_data.get('count', 0)}")
                print(f"심각한 알림 수: {alerts_data.get('critical_count', 0)}")
                print(f"경고 알림 수: {alerts_data.get('warning_count', 0)}")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        # 심각한 알림만 조회
        response = requests.get(f"{API_BASE}/alerts?severity=critical")
        print(f"심각한 알림 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                alerts_data = data.get('data', {})
                print(f"심각한 알림 수: {alerts_data.get('count', 0)}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"알림 조회 테스트 실패: {e}")
        return False

def test_predictions():
    """성능 예측 조회 테스트"""
    print("\n=== 성능 예측 조회 테스트 ===")
    
    try:
        # 전체 예측 조회
        response = requests.get(f"{API_BASE}/predictions")
        print(f"전체 예측 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                predictions_data = data.get('data', {})
                print(f"전체 예측 수: {predictions_data.get('count', 0)}")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        # CPU 예측만 조회
        response = requests.get(f"{API_BASE}/predictions?type=cpu_usage")
        print(f"CPU 예측 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                predictions_data = data.get('data', {})
                print(f"CPU 예측 수: {predictions_data.get('count', 0)}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"예측 조회 테스트 실패: {e}")
        return False

def test_tuning_suggestions():
    """튜닝 제안 조회 테스트"""
    print("\n=== 튜닝 제안 조회 테스트 ===")
    
    try:
        response = requests.get(f"{API_BASE}/tuning/suggestions")
        print(f"튜닝 제안 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                suggestions_data = data.get('data', {})
                print(f"튜닝 제안 수: {suggestions_data.get('count', 0)}")
                
                suggestions = suggestions_data.get('suggestions', [])
                for suggestion in suggestions[:3]:  # 처음 3개만 출력
                    print(f"  - {suggestion.get('tuning_type')}: {suggestion.get('description', 'N/A')}")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"튜닝 제안 조회 테스트 실패: {e}")
        return False

def test_thresholds():
    """성능 임계치 관리 테스트"""
    print("\n=== 성능 임계치 관리 테스트 ===")
    
    try:
        # 현재 임계치 조회
        response = requests.get(f"{API_BASE}/thresholds")
        print(f"현재 임계치 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                thresholds = data.get('data', {})
                print(f"현재 임계치: {thresholds}")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        # 임계치 업데이트
        new_thresholds = {
            'cpu_usage': 85.0,
            'memory_usage': 90.0,
            'response_time': 1500.0
        }
        
        response = requests.put(f"{API_BASE}/thresholds", json=new_thresholds)
        print(f"임계치 업데이트: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"결과: {data}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"임계치 관리 테스트 실패: {e}")
        return False

def test_dashboard():
    """성능 분석 대시보드 테스트"""
    print("\n=== 성능 분석 대시보드 테스트 ===")
    
    try:
        response = requests.get(f"{API_BASE}/dashboard")
        print(f"대시보드 데이터 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                dashboard_data = data.get('data', {})
                
                print(f"모니터링 상태: {'활성화' if dashboard_data.get('monitoring_status', {}).get('active') else '비활성화'}")
                
                alerts_summary = dashboard_data.get('alerts_summary', {})
                print(f"알림 요약: 전체 {alerts_summary.get('total', 0)}개, 심각 {alerts_summary.get('critical', 0)}개, 경고 {alerts_summary.get('warning', 0)}개")
                
                predictions_summary = dashboard_data.get('predictions_summary', {})
                print(f"예측 요약: 전체 {predictions_summary.get('total', 0)}개, CPU {predictions_summary.get('cpu_predictions', 0)}개, 메모리 {predictions_summary.get('memory_predictions', 0)}개")
                
                tuning_summary = dashboard_data.get('tuning_summary', {})
                print(f"튜닝 요약: 전체 {tuning_summary.get('total_suggestions', 0)}개, 적용됨 {tuning_summary.get('applied_suggestions', 0)}개, 대기중 {tuning_summary.get('pending_suggestions', 0)}개")
                
                current_metrics = dashboard_data.get('current_metrics', {})
                if current_metrics:
                    print(f"현재 메트릭: CPU {current_metrics.get('cpu_usage', 'N/A')}%, 메모리 {current_metrics.get('memory_usage', 'N/A')}%")
            else:
                print(f"오류: {data.get('error', 'Unknown error')}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"대시보드 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("고도화된 성능 분석 기능 테스트 시작")
    print("=" * 50)
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("서버가 실행되지 않았습니다. 먼저 서버를 시작해주세요.")
            return
    except Exception as e:
        print(f"서버 연결 실패: {e}")
        return
    
    test_results = []
    
    # 각 테스트 실행
    tests = [
        ("성능 분석 시작", test_start_analytics),
        ("현재 성능 메트릭 조회", test_current_metrics),
        ("성능 메트릭 이력 조회", test_metrics_history),
        ("성능 알림 조회", test_alerts),
        ("성능 예측 조회", test_predictions),
        ("튜닝 제안 조회", test_tuning_suggestions),
        ("성능 임계치 관리", test_thresholds),
        ("성능 분석 대시보드", test_dashboard),
        ("성능 분석 중지", test_stop_analytics),
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"{test_name} 테스트 중 예외 발생: {e}")
            test_results.append((test_name, False))
    
    # 결과 요약
    print("\n" + "=" * 50)
    print("테스트 결과 요약")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in test_results:
        status = "성공" if result else "실패"
        print(f"{test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n전체 테스트: {len(test_results)}개")
    print(f"성공: {success_count}개")
    print(f"실패: {len(test_results) - success_count}개")
    print(f"성공률: {(success_count / len(test_results) * 100):.1f}%")
    
    if success_count == len(test_results):
        print("\n🎉 모든 테스트가 성공했습니다!")
    else:
        print(f"\n⚠️  {len(test_results) - success_count}개 테스트가 실패했습니다.")

if __name__ == "__main__":
    main() 