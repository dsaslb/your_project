#!/usr/bin/env python3
"""
백업 시스템 테스트 스크립트
"""

import requests
import json
import time
import os
import tempfile
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"

def print_test_result(test_name, success, message=""):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    print(f"{test_name}: {status}")
    if message:
        print(f"  {message}")
    print()

def test_health_check():
    """백업 시스템 상태 확인 테스트"""
    print("=== 백업 시스템 상태 확인 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/backup/health")
        success = response.status_code == 200
        data = response.json() if success else {}
        
        print_test_result(
            "상태 확인",
            success,
            f"상태: {data.get('status', 'unknown')}" if success else f"HTTP {response.status_code}"
        )
        return success
    except Exception as e:
        print_test_result("상태 확인", False, str(e))
        return False

def test_create_backup_job():
    """백업 작업 생성 테스트"""
    print("=== 백업 작업 생성 테스트 ===")
    
    try:
        # 테스트용 임시 디렉토리 생성
        temp_dir = tempfile.mkdtemp()
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("테스트 데이터")
        
        job_data = {
            "name": "테스트 백업",
            "source_paths": [temp_dir],
            "destination": "./test_backups",
            "schedule": "daily"
        }
        
        response = requests.post(f"{BASE_URL}/api/backup/jobs", json=job_data)
        
        if response.status_code == 201:
            data = response.json()
            job_id = data.get('job_id')
            
            print_test_result(
                "백업 작업 생성",
                True,
                f"작업 ID: {job_id}"
            )
            return job_id
        else:
            print_test_result("백업 작업 생성", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("백업 작업 생성", False, str(e))
        return None

def test_get_backup_jobs():
    """백업 작업 목록 조회 테스트"""
    print("=== 백업 작업 목록 조회 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/backup/jobs")
        
        if response.status_code == 200:
            data = response.json()
            jobs = data.get('jobs', [])
            
            print_test_result(
                "백업 작업 조회",
                True,
                f"작업 수: {len(jobs)}"
            )
            
            # 작업 상세 정보 출력
            for job in jobs:
                print(f"  - {job.get('name')}: {job.get('schedule')}")
                
            return True
        else:
            print_test_result("백업 작업 조회", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("백업 작업 조회", False, str(e))
        return False

def test_run_backup(job_id):
    """백업 실행 테스트"""
    print("=== 백업 실행 테스트 ===")
    
    if not job_id:
        print_test_result("백업 실행", False, "작업 ID가 없습니다")
        return None
    
    try:
        response = requests.post(f"{BASE_URL}/api/backup/jobs/{job_id}/run", json={
            "backup_type": "full"
        })
        
        if response.status_code == 200:
            data = response.json()
            backup_id = data.get('backup_id')
            
            print_test_result(
                "백업 실행",
                True,
                f"백업 ID: {backup_id}"
            )
            return backup_id
        else:
            print_test_result("백업 실행", False, f"HTTP {response.status_code}")
            return None
            
    except Exception as e:
        print_test_result("백업 실행", False, str(e))
        return None

def test_backup_stats():
    """백업 통계 조회 테스트"""
    print("=== 백업 통계 조회 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/backup/stats")
        
        if response.status_code == 200:
            data = response.json()
            
            print_test_result(
                "백업 통계 조회",
                True,
                f"총 백업: {data.get('total_backups', 0)}, "
                f"성공률: {data.get('success_rate', 0)}%, "
                f"총 크기: {data.get('total_size_mb', 0):.2f} MB"
            )
            return True
        else:
            print_test_result("백업 통계 조회", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("백업 통계 조회", False, str(e))
        return False

def test_backup_records():
    """백업 기록 조회 테스트"""
    print("=== 백업 기록 조회 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/backup/records")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print_test_result(
                "백업 기록 조회",
                True,
                f"기록 수: {len(records)}"
            )
            
            # 최근 기록 출력
            if records:
                print("  최근 백업 기록:")
                for record in records[:3]:  # 최근 3개만
                    print(f"    - {record.get('name')}: {record.get('status')} ({record.get('backup_type')})")
                    
            return records
        else:
            print_test_result("백업 기록 조회", False, f"HTTP {response.status_code}")
            return []
            
    except Exception as e:
        print_test_result("백업 기록 조회", False, str(e))
        return []

def test_scheduler_status():
    """스케줄러 상태 조회 테스트"""
    print("=== 스케줄러 상태 조회 테스트 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/backup/scheduler/status")
        
        if response.status_code == 200:
            data = response.json()
            
            print_test_result(
                "스케줄러 상태 조회",
                True,
                f"실행 중: {data.get('is_running', False)}, "
                f"스케줄: {data.get('backup_schedule', 'unknown')}"
            )
            return True
        else:
            print_test_result("스케줄러 상태 조회", False, f"HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print_test_result("스케줄러 상태 조회", False, str(e))
        return False

def test_scheduler_control():
    """스케줄러 제어 테스트"""
    print("=== 스케줄러 제어 테스트 ===")
    
    try:
        # 스케줄러 중지
        response = requests.post(f"{BASE_URL}/api/backup/scheduler/stop")
        success = response.status_code == 200
        print_test_result("스케줄러 중지", success, f"HTTP {response.status_code}")
        
        time.sleep(1)
        
        # 스케줄러 시작
        response = requests.post(f"{BASE_URL}/api/backup/scheduler/start")
        success = response.status_code == 200
        print_test_result("스케줄러 시작", success, f"HTTP {response.status_code}")
        
        return True
        
    except Exception as e:
        print_test_result("스케줄러 제어", False, str(e))
        return False

def test_backup_test(job_id):
    """백업 테스트 실행"""
    print("=== 백업 테스트 실행 ===")
    
    if not job_id:
        print_test_result("백업 테스트", False, "작업 ID가 없습니다")
        return False
    
    try:
        response = requests.post(f"{BASE_URL}/api/backup/jobs/{job_id}/test")
        
        success = response.status_code == 200
        print_test_result("백업 테스트", success, f"HTTP {response.status_code}")
        
        return success
        
    except Exception as e:
        print_test_result("백업 테스트", False, str(e))
        return False

def test_cleanup():
    """백업 정리 테스트"""
    print("=== 백업 정리 테스트 ===")
    
    try:
        response = requests.post(f"{BASE_URL}/api/backup/cleanup")
        
        success = response.status_code == 200
        print_test_result("백업 정리", success, f"HTTP {response.status_code}")
        
        return success
        
    except Exception as e:
        print_test_result("백업 정리", False, str(e))
        return False

def test_restore_backup(records):
    """백업 복구 테스트"""
    print("=== 백업 복구 테스트 ===")
    
    if not records:
        print_test_result("백업 복구", False, "복구할 백업이 없습니다")
        return False
    
    # 성공한 백업 중 첫 번째 것 선택
    success_record = None
    for record in records:
        if record.get('status') == 'success':
            success_record = record
            break
    
    if not success_record:
        print_test_result("백업 복구", False, "성공한 백업이 없습니다")
        return False
    
    try:
        # 임시 복구 디렉토리 생성
        restore_dir = tempfile.mkdtemp()
        
        response = requests.post(
            f"{BASE_URL}/api/backup/records/{success_record['backup_id']}/restore",
            json={"destination": restore_dir}
        )
        
        success = response.status_code == 200
        print_test_result(
            "백업 복구",
            success,
            f"복구 대상: {success_record.get('name')}, HTTP {response.status_code}"
        )
        
        return success
        
    except Exception as e:
        print_test_result("백업 복구", False, str(e))
        return False

def main():
    """메인 테스트 함수"""
    print("💾 백업 시스템 테스트 시작")
    print(f"테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"테스트 서버: {BASE_URL}")
    print("=" * 50)
    
    # 1. 상태 확인
    if not test_health_check():
        print("❌ 백업 시스템이 실행되지 않고 있습니다.")
        print("서버를 시작한 후 다시 시도해주세요.")
        return
    
    # 2. 백업 작업 생성
    job_id = test_create_backup_job()
    
    # 3. 백업 작업 조회
    test_get_backup_jobs()
    
    # 4. 백업 실행
    backup_id = test_run_backup(job_id)
    
    # 5. 백업 통계 조회
    test_backup_stats()
    
    # 6. 백업 기록 조회
    records = test_backup_records()
    
    # 7. 스케줄러 상태 조회
    test_scheduler_status()
    
    # 8. 스케줄러 제어
    test_scheduler_control()
    
    # 9. 백업 테스트
    test_backup_test(job_id)
    
    # 10. 백업 복구 (성공한 백업이 있는 경우)
    test_restore_backup(records)
    
    # 11. 백업 정리
    test_cleanup()
    
    print("=" * 50)
    print("💾 백업 시스템 테스트 완료")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main() 