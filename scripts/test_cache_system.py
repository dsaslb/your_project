#!/usr/bin/env python3
"""
캐시 관리 시스템 테스트 스크립트

이 스크립트는 캐시 관리 시스템의 주요 기능을 테스트합니다.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api/cache"

def print_test_header(name):
    print(f"\n{'='*60}\n테스트: {name}\n{'='*60}")

def print_test_result(name, success, msg=""):
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{name}: {status}")
    if msg:
        print(f"  메시지: {msg}")

def test_health():
    print_test_header("시스템 상태 확인")
    try:
        r = requests.get(f"{BASE_URL}/health")
        if r.status_code == 200:
            data = r.json()
            print_test_result("상태 확인", True, f"총 항목: {data.get('data', {}).get('total_items', 0)}")
            return True
        else:
            print_test_result("상태 확인", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("상태 확인", False, str(e))
        return False

def test_set_cache():
    print_test_header("캐시 설정")
    try:
        # 메모리 캐시 설정
        data = {
            "key": "test:memory:1",
            "value": {"name": "테스트", "type": "memory"},
            "ttl": 3600,
            "cache_type": "memory",
            "tags": ["test", "memory"]
        }
        r = requests.post(f"{BASE_URL}/set", json=data)
        if r.status_code == 201:
            print_test_result("메모리 캐시 설정", True, f"키: {data['key']}")
        else:
            print_test_result("메모리 캐시 설정", False, f"HTTP {r.status_code}")
            return False

        # 디스크 캐시 설정
        data = {
            "key": "test:disk:1",
            "value": {"name": "테스트", "type": "disk"},
            "ttl": 7200,
            "cache_type": "disk",
            "tags": ["test", "disk"]
        }
        r = requests.post(f"{BASE_URL}/set", json=data)
        if r.status_code == 201:
            print_test_result("디스크 캐시 설정", True, f"키: {data['key']}")
        else:
            print_test_result("디스크 캐시 설정", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("캐시 설정", False, str(e))
        return False

def test_get_cache():
    print_test_header("캐시 조회")
    try:
        # 메모리 캐시 조회
        r = requests.get(f"{BASE_URL}/get/test:memory:1")
        if r.status_code == 200:
            data = r.json()
            print_test_result("메모리 캐시 조회", True, f"값: {data.get('data', {}).get('value', {})}")
        else:
            print_test_result("메모리 캐시 조회", False, f"HTTP {r.status_code}")
            return False

        # 디스크 캐시 조회
        r = requests.get(f"{BASE_URL}/get/test:disk:1")
        if r.status_code == 200:
            data = r.json()
            print_test_result("디스크 캐시 조회", True, f"값: {data.get('data', {}).get('value', {})}")
        else:
            print_test_result("디스크 캐시 조회", False, f"HTTP {r.status_code}")
            return False

        # 존재하지 않는 키 조회
        r = requests.get(f"{BASE_URL}/get/nonexistent:key")
        if r.status_code == 404:
            print_test_result("존재하지 않는 키 조회", True, "예상대로 404 반환")
        else:
            print_test_result("존재하지 않는 키 조회", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("캐시 조회", False, str(e))
        return False

def test_tags():
    print_test_header("태그 기반 검색")
    try:
        # 태그로 검색
        r = requests.post(f"{BASE_URL}/tags", json={"tags": ["test"]})
        if r.status_code == 200:
            data = r.json()
            count = data.get('data', {}).get('count', 0)
            print_test_result("태그 검색", True, f"검색된 항목: {count}개")
        else:
            print_test_result("태그 검색", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("태그 검색", False, str(e))
        return False

def test_stats():
    print_test_header("캐시 통계")
    try:
        r = requests.get(f"{BASE_URL}/stats")
        if r.status_code == 200:
            data = r.json()
            stats = data.get('data', {})
            print_test_result("통계 조회", True, 
                            f"총 항목: {stats.get('total_items', 0)}, "
                            f"히트율: {stats.get('hit_rate', 0):.1f}%")
        else:
            print_test_result("통계 조회", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("통계 조회", False, str(e))
        return False

def test_keys():
    print_test_header("키 목록 조회")
    try:
        r = requests.get(f"{BASE_URL}/keys")
        if r.status_code == 200:
            data = r.json()
            keys = data.get('data', {})
            print_test_result("키 목록 조회", True, 
                            f"메모리: {len(keys.get('memory_keys', []))}, "
                            f"디스크: {len(keys.get('disk_keys', []))}")
        else:
            print_test_result("키 목록 조회", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("키 목록 조회", False, str(e))
        return False

def test_config():
    print_test_header("설정 조회")
    try:
        r = requests.get(f"{BASE_URL}/config")
        if r.status_code == 200:
            data = r.json()
            config = data.get('data', {})
            print_test_result("설정 조회", True, 
                            f"기본 TTL: {config.get('default_ttl', 0)}초")
        else:
            print_test_result("설정 조회", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("설정 조회", False, str(e))
        return False

def test_delete_cache():
    print_test_header("캐시 삭제")
    try:
        # 개별 항목 삭제
        r = requests.delete(f"{BASE_URL}/delete/test:memory:1")
        if r.status_code == 200:
            print_test_result("개별 항목 삭제", True, "메모리 캐시 항목 삭제됨")
        else:
            print_test_result("개별 항목 삭제", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("캐시 삭제", False, str(e))
        return False

def test_clear_cache():
    print_test_header("캐시 전체 삭제")
    try:
        # 메모리 캐시만 삭제
        r = requests.post(f"{BASE_URL}/clear", json={"cache_type": "memory"})
        if r.status_code == 200:
            print_test_result("메모리 캐시 전체 삭제", True, "메모리 캐시 삭제됨")
        else:
            print_test_result("메모리 캐시 전체 삭제", False, f"HTTP {r.status_code}")
            return False

        return True
    except Exception as e:
        print_test_result("캐시 전체 삭제", False, str(e))
        return False

def run_all_tests():
    print("🚀 캐시 관리 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    results.append(test_health())
    results.append(test_set_cache())
    results.append(test_get_cache())
    results.append(test_tags())
    results.append(test_stats())
    results.append(test_keys())
    results.append(test_config())
    results.append(test_delete_cache())
    results.append(test_clear_cache())
    
    print("\n테스트 결과:")
    print(f"✅ 성공: {results.count(True)} / {len(results)}")
    print(f"❌ 실패: {results.count(False)} / {len(results)}")
    print(f"📅 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all(results):
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    run_all_tests() 