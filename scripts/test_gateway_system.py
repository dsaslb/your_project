#!/usr/bin/env python3
"""
API 게이트웨이 시스템 테스트 스크립트

이 스크립트는 게이트웨이 시스템의 주요 기능을 테스트합니다.
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 게이트웨이 API 기본 URL
GATEWAY_BASE_URL = "http://localhost:5000/api/gateway"

def print_test_header(test_name):
    """테스트 헤더 출력"""
    print(f"\n{'='*60}")
    print(f"테스트: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, message=""):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{test_name}: {status}")
    if message:
        print(f"  메시지: {message}")

def test_health_check():
    """게이트웨이 상태 확인 테스트"""
    print_test_header("게이트웨이 상태 확인")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print_test_result("상태 확인", True, f"총 라우트: {data.get('data', {}).get('total_routes', 0)}")
            return True
        else:
            print_test_result("상태 확인", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("상태 확인", False, f"연결 오류: {str(e)}")
        return False

def test_get_stats():
    """게이트웨이 통계 조회 테스트"""
    print_test_header("게이트웨이 통계 조회")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            
            print_test_result("통계 조회", True)
            print(f"  총 라우트: {stats.get('total_routes', 0)}")
            print(f"  활성 라우트: {stats.get('active_routes', 0)}")
            print(f"  총 메트릭: {stats.get('total_metrics', 0)}")
            
            if 'requests_last_hour' in stats:
                print(f"  최근 1시간 요청: {stats['requests_last_hour']}")
            if 'avg_response_time' in stats:
                print(f"  평균 응답 시간: {stats['avg_response_time']:.2f}ms")
            if 'success_rate' in stats:
                print(f"  성공률: {stats['success_rate']:.1f}%")
            
            return True
        else:
            print_test_result("통계 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("통계 조회", False, f"연결 오류: {str(e)}")
        return False

def test_get_routes():
    """API 라우트 조회 테스트"""
    print_test_header("API 라우트 조회")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/routes")
        
        if response.status_code == 200:
            data = response.json()
            routes = data.get('data', [])
            
            print_test_result("라우트 조회", True, f"총 {len(routes)}개 라우트")
            
            for route in routes[:5]:  # 처음 5개만 출력
                print(f"  - {route['name']}: {route['method']} {route['path']}")
            
            if len(routes) > 5:
                print(f"  ... 및 {len(routes) - 5}개 더")
            
            return True
        else:
            print_test_result("라우트 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("라우트 조회", False, f"연결 오류: {str(e)}")
        return False

def test_create_route():
    """API 라우트 생성 테스트"""
    print_test_header("API 라우트 생성")
    
    try:
        # 테스트용 라우트 데이터
        test_route = {
            "name": "테스트 API",
            "path": "/api/test",
            "method": "GET",
            "target_url": "http://localhost:5001/api/test",
            "service_name": "test-service",
            "is_active": True,
            "requires_auth": False
        }
        
        response = requests.post(
            f"{GATEWAY_BASE_URL}/routes",
            json=test_route,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            data = response.json()
            route_id = data.get('data', {}).get('route_id')
            print_test_result("라우트 생성", True, f"라우트 ID: {route_id}")
            
            # 생성된 라우트 삭제 (정리)
            delete_response = requests.delete(f"{GATEWAY_BASE_URL}/routes/{route_id}")
            if delete_response.status_code == 200:
                print_test_result("라우트 정리", True)
            else:
                print_test_result("라우트 정리", False, f"HTTP {delete_response.status_code}")
            
            return True
        else:
            print_test_result("라우트 생성", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("라우트 생성", False, f"연결 오류: {str(e)}")
        return False

def test_get_metrics():
    """API 메트릭 조회 테스트"""
    print_test_header("API 메트릭 조회")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/metrics?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('data', [])
            
            print_test_result("메트릭 조회", True, f"총 {len(metrics)}개 메트릭")
            
            for metric in metrics[:3]:  # 처음 3개만 출력
                print(f"  - {metric['method']} {metric['path']}: {metric['status_code']} ({metric['response_time']:.2f}ms)")
            
            if len(metrics) > 3:
                print(f"  ... 및 {len(metrics) - 3}개 더")
            
            return True
        else:
            print_test_result("메트릭 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("메트릭 조회", False, f"연결 오류: {str(e)}")
        return False

def test_get_metrics_summary():
    """API 메트릭 요약 조회 테스트"""
    print_test_header("API 메트릭 요약 조회")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/metrics/summary?hours=24")
        
        if response.status_code == 200:
            data = response.json()
            summary = data.get('data', {})
            
            print_test_result("메트릭 요약 조회", True)
            print(f"  총 요청: {summary.get('total_requests', 0)}")
            print(f"  평균 응답 시간: {summary.get('avg_response_time', 0):.2f}ms")
            print(f"  성공률: {summary.get('success_rate', 0):.1f}%")
            
            # 상태 코드 분포
            status_dist = summary.get('status_code_distribution', {})
            if status_dist:
                print("  상태 코드 분포:")
                for status, count in status_dist.items():
                    print(f"    {status}: {count}")
            
            # 상위 라우트
            top_routes = summary.get('top_routes', [])
            if top_routes:
                print("  상위 라우트:")
                for route in top_routes[:3]:
                    print(f"    {route['name']}: {route['count']}회")
            
            return True
        else:
            print_test_result("메트릭 요약 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("메트릭 요약 조회", False, f"연결 오류: {str(e)}")
        return False

def test_get_config():
    """게이트웨이 설정 조회 테스트"""
    print_test_header("게이트웨이 설정 조회")
    
    try:
        response = requests.get(f"{GATEWAY_BASE_URL}/config")
        
        if response.status_code == 200:
            data = response.json()
            config = data.get('data', {})
            
            print_test_result("설정 조회", True)
            print(f"  데이터 디렉토리: {config.get('data_dir', 'N/A')}")
            print(f"  속도 제한 윈도우: {config.get('rate_limit_window', 'N/A')}초")
            print(f"  최대 요청 수: {config.get('rate_limit_max_requests', 'N/A')}")
            print(f"  속도 제한 활성화: {config.get('enable_rate_limiting', 'N/A')}")
            print(f"  로깅 활성화: {config.get('enable_logging', 'N/A')}")
            
            return True
        else:
            print_test_result("설정 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("설정 조회", False, f"연결 오류: {str(e)}")
        return False

def test_update_config():
    """게이트웨이 설정 수정 테스트"""
    print_test_header("게이트웨이 설정 수정")
    
    try:
        # 설정 업데이트
        config_update = {
            "rate_limit_window": 1800,  # 30분으로 변경
            "rate_limit_max_requests": 500
        }
        
        response = requests.put(
            f"{GATEWAY_BASE_URL}/config",
            json=config_update,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print_test_result("설정 수정", True)
            
            # 원래 설정으로 복원
            restore_config = {
                "rate_limit_window": 3600,
                "rate_limit_max_requests": 1000
            }
            
            restore_response = requests.put(
                f"{GATEWAY_BASE_URL}/config",
                json=restore_config,
                headers={"Content-Type": "application/json"}
            )
            
            if restore_response.status_code == 200:
                print_test_result("설정 복원", True)
            else:
                print_test_result("설정 복원", False, f"HTTP {restore_response.status_code}")
            
            return True
        else:
            print_test_result("설정 수정", False, f"HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("설정 수정", False, f"연결 오류: {str(e)}")
        return False

def test_clear_cache():
    """캐시 정리 테스트"""
    print_test_header("캐시 정리")
    
    try:
        response = requests.post(f"{GATEWAY_BASE_URL}/cache/clear")
        
        if response.status_code == 200:
            data = response.json()
            cleared_at = data.get('data', {}).get('cleared_at')
            print_test_result("캐시 정리", True, f"정리 시간: {cleared_at}")
            return True
        else:
            print_test_result("캐시 정리", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("캐시 정리", False, f"연결 오류: {str(e)}")
        return False

def test_clear_rate_limit():
    """속도 제한 데이터 정리 테스트"""
    print_test_header("속도 제한 데이터 정리")
    
    try:
        response = requests.post(f"{GATEWAY_BASE_URL}/rate-limit/clear")
        
        if response.status_code == 200:
            data = response.json()
            cleared_at = data.get('data', {}).get('cleared_at')
            print_test_result("속도 제한 데이터 정리", True, f"정리 시간: {cleared_at}")
            return True
        else:
            print_test_result("속도 제한 데이터 정리", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("속도 제한 데이터 정리", False, f"연결 오류: {str(e)}")
        return False

def test_proxy_request():
    """프록시 요청 테스트"""
    print_test_header("프록시 요청 테스트")
    
    try:
        # 존재하지 않는 경로로 테스트 (404 예상)
        response = requests.get(f"{GATEWAY_BASE_URL}/proxy/nonexistent")
        
        if response.status_code == 404:
            print_test_result("프록시 요청 (404)", True, "예상된 404 응답")
            return True
        else:
            print_test_result("프록시 요청", False, f"예상과 다른 HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("프록시 요청", False, f"연결 오류: {str(e)}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 API 게이트웨이 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 게이트웨이 URL: {GATEWAY_BASE_URL}")
    
    # 테스트 목록
    tests = [
        ("게이트웨이 상태 확인", test_health_check),
        ("게이트웨이 통계 조회", test_get_stats),
        ("API 라우트 조회", test_get_routes),
        ("API 라우트 생성", test_create_route),
        ("API 메트릭 조회", test_get_metrics),
        ("API 메트릭 요약 조회", test_get_metrics_summary),
        ("게이트웨이 설정 조회", test_get_config),
        ("게이트웨이 설정 수정", test_update_config),
        ("캐시 정리", test_clear_cache),
        ("속도 제한 데이터 정리", test_clear_rate_limit),
        ("프록시 요청 테스트", test_proxy_request)
    ]
    
    # 테스트 실행
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: 예외 발생 - {str(e)}")
            failed += 1
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공: {passed}개")
    print(f"❌ 실패: {failed}개")
    print(f"📈 총 테스트: {passed + failed}개")
    
    if failed == 0:
        print("🎉 모든 테스트가 성공했습니다!")
        return True
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
        return False

def main():
    """메인 함수"""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 테스트 실행 중 오류 발생: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 