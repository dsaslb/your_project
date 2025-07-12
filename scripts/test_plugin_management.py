#!/usr/bin/env python3
"""
플러그인 관리 기능 테스트 스크립트
플러그인 등록, 설치, 설정, 로그, 메트릭, 이력 등 모든 관리 기능을 테스트합니다.
"""

import requests
import json
import time
import os
from datetime import datetime, timedelta

# 서버 설정
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# 테스트 데이터
TEST_PLUGIN_METADATA = {
    "plugin_id": "test_plugin_management",
    "name": "테스트 플러그인 관리",
    "version": "1.0.0",
    "description": "플러그인 관리 기능 테스트용 플러그인",
    "author": "Test Author",
    "category": "management",
    "dependencies": [],
    "permissions": ["read", "write"]
}

def test_plugin_list():
    """플러그인 목록 조회 테스트"""
    print("\n=== 플러그인 목록 조회 테스트 ===")
    
    try:
        # 기본 목록 조회
        response = requests.get(f"{API_BASE}/plugins")
        print(f"기본 목록 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"플러그인 수: {data.get('pagination', {}).get('total_count', 0)}")
            print(f"페이지 정보: {data.get('pagination', {})}")
        else:
            print(f"오류: {response.text}")
        
        # 필터링 테스트
        params = {
            'category': 'management',
            'enabled': 'true',
            'page': 1,
            'per_page': 5
        }
        response = requests.get(f"{API_BASE}/plugins", params=params)
        print(f"필터링 목록 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"필터링된 플러그인 수: {len(data.get('plugins', []))}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 목록 조회 테스트 실패: {e}")
        return False

def test_plugin_scan():
    """플러그인 스캔 테스트"""
    print("\n=== 플러그인 스캔 테스트 ===")
    
    try:
        response = requests.post(f"{API_BASE}/plugins/scan")
        print(f"플러그인 스캔: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"스캔 결과: {data}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 스캔 테스트 실패: {e}")
        return False

def test_plugin_status():
    """플러그인 상태 조회 테스트"""
    print("\n=== 플러그인 상태 조회 테스트 ===")
    
    try:
        response = requests.get(f"{API_BASE}/plugins/status")
        print(f"플러그인 상태 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"전체 플러그인 수: {data.get('status', {}).get('total_plugins', 0)}")
            print(f"활성화된 플러그인 수: {data.get('status', {}).get('enabled_plugins', 0)}")
            print(f"비활성화된 플러그인 수: {data.get('status', {}).get('disabled_plugins', 0)}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 상태 조회 테스트 실패: {e}")
        return False

def test_plugin_detail():
    """플러그인 상세 정보 조회 테스트"""
    print("\n=== 플러그인 상세 정보 조회 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}")
                print(f"플러그인 상세 조회 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"플러그인 이름: {data.get('name', 'N/A')}")
                    print(f"버전: {data.get('version', 'N/A')}")
                    print(f"카테고리: {data.get('category', 'N/A')}")
                    print(f"활성화 상태: {data.get('enabled', 'N/A')}")
                else:
                    print(f"오류: {response.text}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 상세 정보 조회 테스트 실패: {e}")
        return False

def test_plugin_enable_disable():
    """플러그인 활성화/비활성화 테스트"""
    print("\n=== 플러그인 활성화/비활성화 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                current_enabled = plugins[0]['enabled']
                
                # 현재 상태와 반대로 변경
                action = 'disable' if current_enabled else 'enable'
                response = requests.post(f"{API_BASE}/plugins/{plugin_id}/{action}")
                print(f"플러그인 {action} ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"결과: {data.get('message', 'N/A')}")
                    
                    # 다시 원래 상태로 복원
                    restore_action = 'enable' if current_enabled else 'disable'
                    response = requests.post(f"{API_BASE}/plugins/{plugin_id}/{restore_action}")
                    print(f"상태 복원 ({restore_action}): {response.status_code}")
                else:
                    print(f"오류: {response.text}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 활성화/비활성화 테스트 실패: {e}")
        return False

def test_plugin_reload():
    """플러그인 재로드 테스트"""
    print("\n=== 플러그인 재로드 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                response = requests.post(f"{API_BASE}/plugins/{plugin_id}/reload")
                print(f"플러그인 재로드 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"결과: {data.get('message', 'N/A')}")
                else:
                    print(f"오류: {response.text}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 재로드 테스트 실패: {e}")
        return False

def test_plugin_logs():
    """플러그인 로그 조회 테스트"""
    print("\n=== 플러그인 로그 조회 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                
                # 기본 로그 조회
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/logs")
                print(f"플러그인 로그 조회 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"로그 수: {len(data.get('logs', []))}")
                    print(f"요약: {data.get('summary', {})}")
                else:
                    print(f"오류: {response.text}")
                
                # 필터링된 로그 조회
                params = {
                    'level': 'info',
                    'page': 1,
                    'per_page': 10
                }
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/logs", params=params)
                print(f"필터링된 로그 조회: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"필터링된 로그 수: {len(data.get('logs', []))}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 로그 조회 테스트 실패: {e}")
        return False

def test_plugin_metrics():
    """플러그인 메트릭 조회 테스트"""
    print("\n=== 플러그인 메트릭 조회 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                
                # 기본 메트릭 조회
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/metrics")
                print(f"플러그인 메트릭 조회 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    metrics = data.get('metrics', {})
                    print(f"CPU 사용률: {metrics.get('cpu_usage', {}).get('current', 'N/A')}%")
                    print(f"메모리 사용률: {metrics.get('memory_usage', {}).get('current', 'N/A')}MB")
                    print(f"응답 시간: {metrics.get('response_time', {}).get('current', 'N/A')}ms")
                    print(f"오류율: {metrics.get('error_rate', 'N/A')}%")
                else:
                    print(f"오류: {response.text}")
                
                # 시간 범위별 메트릭 조회
                params = {'time_range': '24h'}
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/metrics", params=params)
                print(f"24시간 메트릭 조회: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"시간 범위: {data.get('time_range', 'N/A')}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 메트릭 조회 테스트 실패: {e}")
        return False

def test_installation_history():
    """설치 이력 조회 테스트"""
    print("\n=== 설치 이력 조회 테스트 ===")
    
    try:
        # 기본 이력 조회
        response = requests.get(f"{API_BASE}/plugins/history")
        print(f"설치 이력 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"이력 수: {len(data.get('history', []))}")
            print(f"요약: {data.get('summary', {})}")
        else:
            print(f"오류: {response.text}")
        
        # 필터링된 이력 조회
        params = {
            'action': 'install',
            'page': 1,
            'per_page': 10
        }
        response = requests.get(f"{API_BASE}/plugins/history", params=params)
        print(f"필터링된 이력 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"필터링된 이력 수: {len(data.get('history', []))}")
        
        return True
        
    except Exception as e:
        print(f"설치 이력 조회 테스트 실패: {e}")
        return False

def test_plugin_config():
    """플러그인 설정 조회/수정 테스트"""
    print("\n=== 플러그인 설정 조회/수정 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                
                # 설정 조회
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/config")
                print(f"플러그인 설정 조회 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"설정: {data.get('config', {})}")
                else:
                    print(f"오류: {response.text}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 설정 조회/수정 테스트 실패: {e}")
        return False

def test_plugin_schema():
    """플러그인 스키마 조회 테스트"""
    print("\n=== 플러그인 스키마 조회 테스트 ===")
    
    try:
        # 먼저 플러그인 목록을 가져와서 첫 번째 플러그인 ID 사용
        response = requests.get(f"{API_BASE}/plugins")
        if response.status_code == 200:
            data = response.json()
            plugins = data.get('plugins', [])
            
            if plugins:
                plugin_id = plugins[0]['id']
                
                # 스키마 조회
                response = requests.get(f"{API_BASE}/plugins/{plugin_id}/schema")
                print(f"플러그인 스키마 조회 ({plugin_id}): {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"스키마 필드 수: {len(data.get('schema', []))}")
                else:
                    print(f"오류: {response.text}")
            else:
                print("테스트할 플러그인이 없습니다.")
        else:
            print(f"플러그인 목록 조회 실패: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 스키마 조회 테스트 실패: {e}")
        return False

def test_plugin_market():
    """플러그인 마켓 조회 테스트"""
    print("\n=== 플러그인 마켓 조회 테스트 ===")
    
    try:
        response = requests.get(f"{API_BASE}/plugins/market")
        print(f"플러그인 마켓 조회: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"마켓 플러그인 수: {len(data.get('plugins', []))}")
        else:
            print(f"오류: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"플러그인 마켓 조회 테스트 실패: {e}")
        return False

def main():
    """메인 테스트 함수"""
    print("플러그인 관리 기능 테스트 시작")
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
        ("플러그인 목록 조회", test_plugin_list),
        ("플러그인 스캔", test_plugin_scan),
        ("플러그인 상태 조회", test_plugin_status),
        ("플러그인 상세 정보 조회", test_plugin_detail),
        ("플러그인 활성화/비활성화", test_plugin_enable_disable),
        ("플러그인 재로드", test_plugin_reload),
        ("플러그인 로그 조회", test_plugin_logs),
        ("플러그인 메트릭 조회", test_plugin_metrics),
        ("설치 이력 조회", test_installation_history),
        ("플러그인 설정 조회", test_plugin_config),
        ("플러그인 스키마 조회", test_plugin_schema),
        ("플러그인 마켓 조회", test_plugin_market),
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