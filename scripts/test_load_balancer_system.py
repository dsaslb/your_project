#!/usr/bin/env python3
"""
로드 밸런서 시스템 테스트 스크립트

이 스크립트는 로드 밸런서 시스템의 주요 기능을 테스트합니다.
"""

import requests
import json
import time
import sys
import os
from datetime import datetime

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 로드 밸런서 API 기본 URL
LOAD_BALANCER_BASE_URL = "http://localhost:5000/api/load-balancer"

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
    """로드 밸런서 상태 확인 테스트"""
    print_test_header("로드 밸런서 상태 확인")
    
    try:
        response = requests.get(f"{LOAD_BALANCER_BASE_URL}/health")
        
        if response.status_code == 200:
            data = response.json()
            print_test_result("상태 확인", True, f"총 그룹: {data.get('data', {}).get('total_groups', 0)}")
            return True
        else:
            print_test_result("상태 확인", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("상태 확인", False, f"연결 오류: {str(e)}")
        return False

def test_get_stats():
    """로드 밸런서 통계 조회 테스트"""
    print_test_header("로드 밸런서 통계 조회")
    
    try:
        response = requests.get(f"{LOAD_BALANCER_BASE_URL}/stats")
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('data', {})
            print_test_result("통계 조회", True, 
                            f"그룹: {stats.get('total_groups', 0)}, "
                            f"서버: {stats.get('total_servers', 0)}, "
                            f"정상 서버: {stats.get('healthy_servers', 0)}")
            return True
        else:
            print_test_result("통계 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("통계 조회", False, f"연결 오류: {str(e)}")
        return False

def test_get_groups():
    """서버 그룹 조회 테스트"""
    print_test_header("서버 그룹 조회")
    
    try:
        response = requests.get(f"{LOAD_BALANCER_BASE_URL}/groups")
        
        if response.status_code == 200:
            data = response.json()
            groups = data.get('data', [])
            print_test_result("그룹 조회", True, f"총 {len(groups)}개 그룹")
            
            # 첫 번째 그룹 정보 출력
            if groups:
                first_group = groups[0]
                print(f"  첫 번째 그룹: {first_group.get('name')} ({first_group.get('algorithm')})")
                print(f"  서버 수: {len(first_group.get('servers', []))}")
            
            return True
        else:
            print_test_result("그룹 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("그룹 조회", False, f"연결 오류: {str(e)}")
        return False

def test_create_group():
    """서버 그룹 생성 테스트"""
    print_test_header("서버 그룹 생성")
    
    try:
        group_data = {
            "name": "테스트 그룹",
            "algorithm": "round_robin",
            "is_active": True
        }
        
        response = requests.post(f"{LOAD_BALANCER_BASE_URL}/groups", json=group_data)
        
        if response.status_code == 201:
            data = response.json()
            group_id = data.get('data', {}).get('group_id')
            print_test_result("그룹 생성", True, f"그룹 ID: {group_id}")
            return group_id
        else:
            print_test_result("그룹 생성", False, f"HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_test_result("그룹 생성", False, f"연결 오류: {str(e)}")
        return None

def test_add_server(group_id):
    """서버 추가 테스트"""
    print_test_header("서버 추가")
    
    if not group_id:
        print_test_result("서버 추가", False, "그룹 ID가 없습니다")
        return None
    
    try:
        server_data = {
            "name": "테스트 서버",
            "host": "localhost",
            "port": 8080,
            "protocol": "http",
            "weight": 100,
            "max_connections": 1000,
            "health_check_url": "/health"
        }
        
        response = requests.post(f"{LOAD_BALANCER_BASE_URL}/groups/{group_id}/servers", json=server_data)
        
        if response.status_code == 201:
            data = response.json()
            server_id = data.get('data', {}).get('server_id')
            print_test_result("서버 추가", True, f"서버 ID: {server_id}")
            return server_id
        else:
            print_test_result("서버 추가", False, f"HTTP {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print_test_result("서버 추가", False, f"연결 오류: {str(e)}")
        return None

def test_select_server(group_id):
    """서버 선택 테스트"""
    print_test_header("서버 선택")
    
    if not group_id:
        print_test_result("서버 선택", False, "그룹 ID가 없습니다")
        return False
    
    try:
        select_data = {
            "client_ip": "192.168.1.100",
            "session_id": "test_session_123"
        }
        
        response = requests.post(f"{LOAD_BALANCER_BASE_URL}/select-server/{group_id}", json=select_data)
        
        if response.status_code == 200:
            data = response.json()
            server_data = data.get('data', {})
            print_test_result("서버 선택", True, 
                            f"선택된 서버: {server_data.get('name')} ({server_data.get('host')}:{server_data.get('port')})")
            return True
        else:
            print_test_result("서버 선택", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("서버 선택", False, f"연결 오류: {str(e)}")
        return False

def test_get_metrics():
    """메트릭 조회 테스트"""
    print_test_header("메트릭 조회")
    
    try:
        response = requests.get(f"{LOAD_BALANCER_BASE_URL}/metrics?limit=10")
        
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('data', [])
            print_test_result("메트릭 조회", True, f"총 {len(metrics)}개 메트릭")
            return True
        else:
            print_test_result("메트릭 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("메트릭 조회", False, f"연결 오류: {str(e)}")
        return False

def test_get_config():
    """설정 조회 테스트"""
    print_test_header("설정 조회")
    
    try:
        response = requests.get(f"{LOAD_BALANCER_BASE_URL}/config")
        
        if response.status_code == 200:
            data = response.json()
            config = data.get('data', {})
            print_test_result("설정 조회", True, 
                            f"헬스 체크 간격: {config.get('health_check_interval')}초, "
                            f"세션 고정: {config.get('enable_sticky_sessions')}")
            return True
        else:
            print_test_result("설정 조회", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("설정 조회", False, f"연결 오류: {str(e)}")
        return False

def test_update_config():
    """설정 수정 테스트"""
    print_test_header("설정 수정")
    
    try:
        config_data = {
            "health_check_interval": 45,
            "health_check_timeout": 10,
            "max_failures": 5
        }
        
        response = requests.put(f"{LOAD_BALANCER_BASE_URL}/config", json=config_data)
        
        if response.status_code == 200:
            print_test_result("설정 수정", True, "설정이 업데이트되었습니다")
            return True
        else:
            print_test_result("설정 수정", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("설정 수정", False, f"연결 오류: {str(e)}")
        return False

def test_clear_sessions():
    """세션 정리 테스트"""
    print_test_header("세션 정리")
    
    try:
        response = requests.post(f"{LOAD_BALANCER_BASE_URL}/sessions/clear")
        
        if response.status_code == 200:
            print_test_result("세션 정리", True, "세션 매핑이 정리되었습니다")
            return True
        else:
            print_test_result("세션 정리", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("세션 정리", False, f"연결 오류: {str(e)}")
        return False

def test_clear_connections():
    """연결 수 정리 테스트"""
    print_test_header("연결 수 정리")
    
    try:
        response = requests.post(f"{LOAD_BALANCER_BASE_URL}/connections/clear")
        
        if response.status_code == 200:
            print_test_result("연결 수 정리", True, "연결 수 카운터가 정리되었습니다")
            return True
        else:
            print_test_result("연결 수 정리", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("연결 수 정리", False, f"연결 오류: {str(e)}")
        return False

def test_delete_server(server_id):
    """서버 삭제 테스트"""
    print_test_header("서버 삭제")
    
    if not server_id:
        print_test_result("서버 삭제", False, "서버 ID가 없습니다")
        return False
    
    try:
        response = requests.delete(f"{LOAD_BALANCER_BASE_URL}/servers/{server_id}")
        
        if response.status_code == 200:
            print_test_result("서버 삭제", True, "서버가 삭제되었습니다")
            return True
        else:
            print_test_result("서버 삭제", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("서버 삭제", False, f"연결 오류: {str(e)}")
        return False

def test_delete_group(group_id):
    """서버 그룹 삭제 테스트"""
    print_test_header("서버 그룹 삭제")
    
    if not group_id:
        print_test_result("그룹 삭제", False, "그룹 ID가 없습니다")
        return False
    
    try:
        response = requests.delete(f"{LOAD_BALANCER_BASE_URL}/groups/{group_id}")
        
        if response.status_code == 200:
            print_test_result("그룹 삭제", True, "서버 그룹이 삭제되었습니다")
            return True
        else:
            print_test_result("그룹 삭제", False, f"HTTP {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print_test_result("그룹 삭제", False, f"연결 오류: {str(e)}")
        return False

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 로드 밸런서 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 로드 밸런서 URL: {LOAD_BALANCER_BASE_URL}")
    
    # 테스트 결과 추적
    test_results = []
    created_group_id = None
    created_server_id = None
    
    # 기본 기능 테스트
    tests = [
        ("로드 밸런서 상태 확인", test_health_check),
        ("로드 밸런서 통계 조회", test_get_stats),
        ("서버 그룹 조회", test_get_groups),
        ("설정 조회", test_get_config),
        ("설정 수정", test_update_config),
        ("메트릭 조회", test_get_metrics),
        ("세션 정리", test_clear_sessions),
        ("연결 수 정리", test_clear_connections)
    ]
    
    # 기본 테스트 실행
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ 테스트 실행 중 오류 발생: {test_name} - {str(e)}")
            test_results.append((test_name, False))
    
    # 생성 테스트 (순서 중요)
    print("\n" + "="*60)
    print("생성 및 관리 테스트")
    print("="*60)
    
    # 그룹 생성
    try:
        created_group_id = test_create_group()
        test_results.append(("서버 그룹 생성", created_group_id is not None))
    except Exception as e:
        print(f"❌ 그룹 생성 테스트 오류: {str(e)}")
        test_results.append(("서버 그룹 생성", False))
    
    # 서버 추가
    if created_group_id:
        try:
            created_server_id = test_add_server(created_group_id)
            test_results.append(("서버 추가", created_server_id is not None))
        except Exception as e:
            print(f"❌ 서버 추가 테스트 오류: {str(e)}")
            test_results.append(("서버 추가", False))
    
    # 서버 선택
    if created_group_id:
        try:
            result = test_select_server(created_group_id)
            test_results.append(("서버 선택", result))
        except Exception as e:
            print(f"❌ 서버 선택 테스트 오류: {str(e)}")
            test_results.append(("서버 선택", False))
    
    # 정리 테스트 (역순)
    print("\n" + "="*60)
    print("정리 테스트")
    print("="*60)
    
    # 서버 삭제
    if created_server_id:
        try:
            result = test_delete_server(created_server_id)
            test_results.append(("서버 삭제", result))
        except Exception as e:
            print(f"❌ 서버 삭제 테스트 오류: {str(e)}")
            test_results.append(("서버 삭제", False))
    
    # 그룹 삭제
    if created_group_id:
        try:
            result = test_delete_group(created_group_id)
            test_results.append(("서버 그룹 삭제", result))
        except Exception as e:
            print(f"❌ 그룹 삭제 테스트 오류: {str(e)}")
            test_results.append(("서버 그룹 삭제", False))
    
    # 결과 요약
    print("\n" + "="*60)
    print("테스트 결과 요약")
    print("="*60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, result in test_results if result)
    failed_tests = total_tests - passed_tests
    
    print(f"📊 총 테스트: {total_tests}")
    print(f"✅ 통과: {passed_tests}")
    print(f"❌ 실패: {failed_tests}")
    print(f"📈 성공률: {(passed_tests/total_tests*100):.1f}%")
    
    print(f"\n📅 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 실패한 테스트 목록
    if failed_tests > 0:
        print("\n❌ 실패한 테스트:")
        for test_name, result in test_results:
            if not result:
                print(f"  - {test_name}")
    
    # 성공한 테스트 목록
    if passed_tests > 0:
        print("\n✅ 성공한 테스트:")
        for test_name, result in test_results:
            if result:
                print(f"  - {test_name}")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 테스트 실행 중 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1) 