#!/usr/bin/env python3
"""
테스트 실행 스크립트
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path

def run_command(command, description):
    """명령어 실행"""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"실행 명령어: {command}")
    print("-" * 60)
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"실행 시간: {execution_time:.2f}초")
        print(f"종료 코드: {result.returncode}")
        
        if result.stdout:
            print("\n📤 표준 출력:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️ 표준 오류:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ {description} 성공!")
        else:
            print(f"\n❌ {description} 실패!")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n❌ 명령어 실행 중 오류 발생: {e}")
        return False

def run_python_tests():
    """Python 테스트 실행"""
    tests = [
        ("tests/test_api.py", "API 단위 테스트"),
        ("tests/test_integration.py", "통합 테스트")
    ]
    
    all_passed = True
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            success = run_command(
                f"python -m pytest {test_file} -v --tb=short",
                description
            )
            if not success:
                all_passed = False
        else:
            print(f"\n⚠️ 테스트 파일을 찾을 수 없습니다: {test_file}")
    
    return all_passed

def run_frontend_tests():
    """프론트엔드 테스트 실행"""
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("\n⚠️ frontend 디렉토리를 찾을 수 없습니다.")
        return False
    
    # package.json 확인
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("\n⚠️ frontend/package.json을 찾을 수 없습니다.")
        return False
    
    # npm 테스트 실행
    success = run_command(
        "cd frontend && npm test -- --watchAll=false",
        "프론트엔드 테스트"
    )
    
    return success

def run_linting():
    """코드 린팅 실행"""
    linting_tests = [
        ("python -m flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics", "Python 문법 검사"),
        ("python -m black . --check", "Python 코드 포맷 검사"),
        ("python -m isort . --check-only", "Python import 정렬 검사")
    ]
    
    all_passed = True
    
    for command, description in linting_tests:
        success = run_command(command, description)
        if not success:
            all_passed = False
    
    return all_passed

def run_security_checks():
    """보안 검사 실행"""
    security_tests = [
        ("python -c \"import ast; ast.parse(open('swagger_docs.py').read())\"", "Python 구문 검사"),
        ("python -c \"import json; json.loads(open('config/address_search_config.json').read())\"", "JSON 구문 검사")
    ]
    
    all_passed = True
    
    for command, description in security_tests:
        success = run_command(command, description)
        if not success:
            all_passed = False
    
    return all_passed

def run_performance_tests():
    """성능 테스트 실행"""
    print(f"\n{'='*60}")
    print("🚀 성능 테스트")
    print(f"{'='*60}")
    
    # 간단한 성능 테스트
    performance_tests = [
        ("python -c \"import time; start=time.time(); import swagger_docs; print(f'모듈 로드 시간: {time.time()-start:.3f}초')\"", "모듈 로드 성능"),
        ("python -c \"import time; start=time.time(); from swagger_docs import DataStore; ds=DataStore(); print(f'데이터 저장소 초기화: {time.time()-start:.3f}초')\"", "데이터 저장소 성능")
    ]
    
    all_passed = True
    
    for command, description in performance_tests:
        success = run_command(command, description)
        if not success:
            all_passed = False
    
    return all_passed

def generate_test_report(results):
    """테스트 리포트 생성"""
    report = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_tests": len(results),
            "passed": sum(1 for r in results.values() if r),
            "failed": sum(1 for r in results.values() if not r)
        },
        "results": results
    }
    
    # 리포트 파일 저장
    with open("test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*60}")
    print("📊 테스트 리포트")
    print(f"{'='*60}")
    print(f"생성 시간: {report['timestamp']}")
    print(f"총 테스트: {report['summary']['total_tests']}")
    print(f"성공: {report['summary']['passed']}")
    print(f"실패: {report['summary']['failed']}")
    print(f"성공률: {(report['summary']['passed']/report['summary']['total_tests']*100):.1f}%")
    
    if report['summary']['failed'] > 0:
        print("\n❌ 실패한 테스트:")
        for test_name, passed in results.items():
            if not passed:
                print(f"  - {test_name}")
    
    print(f"\n📄 상세 리포트: test_report.json")

def main():
    """메인 함수"""
    print("🧪 멀티테넌시 관리 시스템 테스트 실행")
    print("=" * 60)
    
    results = {}
    
    # 1. Python 테스트
    results["Python 테스트"] = run_python_tests()
    
    # 2. 프론트엔드 테스트
    results["프론트엔드 테스트"] = run_frontend_tests()
    
    # 3. 린팅 검사
    results["코드 린팅"] = run_linting()
    
    # 4. 보안 검사
    results["보안 검사"] = run_security_checks()
    
    # 5. 성능 테스트
    results["성능 테스트"] = run_performance_tests()
    
    # 6. 리포트 생성
    generate_test_report(results)
    
    # 7. 최종 결과
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    print(f"\n{'='*60}")
    print("🎯 최종 결과")
    print(f"{'='*60}")
    
    if passed_tests == total_tests:
        print("🎉 모든 테스트가 통과했습니다!")
        return 0
    else:
        print(f"⚠️ {total_tests - passed_tests}개 테스트가 실패했습니다.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 