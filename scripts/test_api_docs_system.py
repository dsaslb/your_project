#!/usr/bin/env python3
"""
API 문서 시스템 테스트 스크립트

이 스크립트는 API 문서 시스템의 주요 기능을 테스트합니다.
"""

import requests
import json
import time
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api/docs"

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
            print_test_result("상태 확인", True, f"제목: {data.get('data', {}).get('title', 'N/A')}")
            return True
        else:
            print_test_result("상태 확인", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("상태 확인", False, str(e))
        return False

def test_generate_docs():
    print_test_header("문서 생성")
    try:
        r = requests.post(f"{BASE_URL}/generate")
        if r.status_code == 200:
            data = r.json()
            print_test_result("문서 생성", True, f"생성 시간: {data.get('data', {}).get('generated_at', 'N/A')}")
            return True
        else:
            print_test_result("문서 생성", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("문서 생성", False, str(e))
        return False

def test_list_files():
    print_test_header("파일 목록 조회")
    try:
        r = requests.get(f"{BASE_URL}/files")
        if r.status_code == 200:
            data = r.json()
            files = data.get('data', {}).get('files', [])
            print_test_result("파일 목록 조회", True, f"파일 수: {len(files)}개")
            
            # 파일 타입별 통계
            file_types = {}
            for file in files:
                file_type = file.get('type', 'Unknown')
                if file_type not in file_types:
                    file_types[file_type] = 0
                file_types[file_type] += 1
            
            for file_type, count in file_types.items():
                print(f"  {file_type}: {count}개")
            
            return True
        else:
            print_test_result("파일 목록 조회", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("파일 목록 조회", False, str(e))
        return False

def test_openapi_spec():
    print_test_header("OpenAPI 스펙 조회")
    try:
        r = requests.get(f"{BASE_URL}/openapi")
        if r.status_code == 200:
            spec = r.json()
            info = spec.get('info', {})
            paths = spec.get('paths', {})
            print_test_result("OpenAPI 스펙 조회", True, 
                            f"제목: {info.get('title', 'N/A')}, "
                            f"엔드포인트: {len(paths)}개")
            return True
        else:
            print_test_result("OpenAPI 스펙 조회", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("OpenAPI 스펙 조회", False, str(e))
        return False

def test_swagger_ui():
    print_test_header("Swagger UI 접근")
    try:
        r = requests.get(f"{BASE_URL}/swagger")
        if r.status_code == 200:
            content = r.text
            if "swagger-ui" in content and "openapi" in content:
                print_test_result("Swagger UI 접근", True, "HTML 페이지 로드됨")
                return True
            else:
                print_test_result("Swagger UI 접근", False, "올바른 HTML 내용이 아님")
                return False
        else:
            print_test_result("Swagger UI 접근", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("Swagger UI 접근", False, str(e))
        return False

def test_redoc_ui():
    print_test_header("ReDoc UI 접근")
    try:
        r = requests.get(f"{BASE_URL}/redoc")
        if r.status_code == 200:
            content = r.text
            if "redoc" in content and "spec-url" in content:
                print_test_result("ReDoc UI 접근", True, "HTML 페이지 로드됨")
                return True
            else:
                print_test_result("ReDoc UI 접근", False, "올바른 HTML 내용이 아님")
                return False
        else:
            print_test_result("ReDoc UI 접근", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("ReDoc UI 접근", False, str(e))
        return False

def test_stats():
    print_test_header("통계 조회")
    try:
        r = requests.get(f"{BASE_URL}/stats")
        if r.status_code == 200:
            data = r.json()
            stats = data.get('data', {})
            print_test_result("통계 조회", True, 
                            f"엔드포인트: {stats.get('endpoint_count', 0)}개, "
                            f"파일: {stats.get('file_count', 0)}개")
            
            # 태그별 통계 출력
            tag_stats = stats.get('tag_stats', {})
            if tag_stats:
                print("  태그별 엔드포인트:")
                for tag, count in tag_stats.items():
                    print(f"    {tag}: {count}개")
            
            return True
        else:
            print_test_result("통계 조회", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("통계 조회", False, str(e))
        return False

def test_config():
    print_test_header("설정 조회")
    try:
        r = requests.get(f"{BASE_URL}/config")
        if r.status_code == 200:
            data = r.json()
            config = data.get('data', {})
            print_test_result("설정 조회", True, 
                            f"제목: {config.get('title', 'N/A')}, "
                            f"버전: {config.get('version', 'N/A')}")
            
            # 활성화된 기능 출력
            enabled_features = []
            if config.get('enable_swagger_ui'):
                enabled_features.append("Swagger UI")
            if config.get('enable_redoc'):
                enabled_features.append("ReDoc")
            if config.get('enable_postman'):
                enabled_features.append("Postman")
            if config.get('enable_insomnia'):
                enabled_features.append("Insomnia")
            
            print(f"  활성화된 기능: {', '.join(enabled_features)}")
            
            return True
        else:
            print_test_result("설정 조회", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("설정 조회", False, str(e))
        return False

def test_download_file():
    print_test_header("파일 다운로드")
    try:
        # 먼저 파일 목록 조회
        r = requests.get(f"{BASE_URL}/files")
        if r.status_code == 200:
            data = r.json()
            files = data.get('data', {}).get('files', [])
            
            if not files:
                print_test_result("파일 다운로드", False, "다운로드할 파일이 없습니다")
                return False
            
            # 첫 번째 파일 다운로드 시도
            first_file = files[0]
            filename = first_file.get('name')
            
            r = requests.get(f"{BASE_URL}/files/{filename}")
            if r.status_code == 200:
                print_test_result("파일 다운로드", True, f"파일: {filename}")
                return True
            else:
                print_test_result("파일 다운로드", False, f"HTTP {r.status_code}")
                return False
        else:
            print_test_result("파일 다운로드", False, "파일 목록 조회 실패")
            return False
    except Exception as e:
        print_test_result("파일 다운로드", False, str(e))
        return False

def test_update_config():
    print_test_header("설정 업데이트")
    try:
        # 현재 설정 조회
        r = requests.get(f"{BASE_URL}/config")
        if r.status_code != 200:
            print_test_result("설정 업데이트", False, "현재 설정 조회 실패")
            return False
        
        current_config = r.json().get('data', {})
        
        # 설정 업데이트
        update_data = {
            "title": f"{current_config.get('title', 'API')} (테스트)",
            "version": "1.0.1"
        }
        
        r = requests.put(f"{BASE_URL}/config", json=update_data)
        if r.status_code == 200:
            print_test_result("설정 업데이트", True, "설정이 업데이트되었습니다")
            
            # 원래 설정으로 복원
            restore_data = {
                "title": current_config.get('title', 'API'),
                "version": current_config.get('version', '1.0.0')
            }
            requests.put(f"{BASE_URL}/config", json=restore_data)
            
            return True
        else:
            print_test_result("설정 업데이트", False, f"HTTP {r.status_code}")
            return False
    except Exception as e:
        print_test_result("설정 업데이트", False, str(e))
        return False

def run_all_tests():
    print("🚀 API 문서 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    results.append(test_health())
    results.append(test_generate_docs())
    results.append(test_list_files())
    results.append(test_openapi_spec())
    results.append(test_swagger_ui())
    results.append(test_redoc_ui())
    results.append(test_stats())
    results.append(test_config())
    results.append(test_download_file())
    results.append(test_update_config())
    
    print("\n테스트 결과:")
    print(f"✅ 성공: {results.count(True)} / {len(results)}")
    print(f"❌ 실패: {results.count(False)} / {len(results)}")
    print(f"📅 테스트 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if all(results):
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        print("\n📖 생성된 문서 확인:")
        print("- Swagger UI: http://localhost:5000/api/docs/swagger")
        print("- ReDoc: http://localhost:5000/api/docs/redoc")
        print("- OpenAPI JSON: http://localhost:5000/api/docs/openapi")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")

if __name__ == "__main__":
    run_all_tests() 