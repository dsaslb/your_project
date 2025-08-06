#!/usr/bin/env python3
"""
시스템 설정 관리 테스트 스크립트
"""

import requests
import json
import time
from datetime import datetime

# 테스트 설정
BASE_URL = "http://localhost:5000"

class SettingsSystemTester:
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
        """설정 시스템 상태 확인 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/health")
            if response.status_code == 200:
                data = response.json()
                self.print_test_result(
                    "설정 시스템 상태 확인",
                    True,
                    f"총 설정: {data.get('data', {}).get('total_settings', 0)}개"
                )
                return True
            else:
                self.print_test_result("설정 시스템 상태 확인", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 시스템 상태 확인", False, f"오류: {str(e)}")
            return False
    
    def test_get_stats(self):
        """설정 통계 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data.get('data', {})
                self.print_test_result(
                    "설정 통계 조회",
                    True,
                    f"총 설정: {stats.get('total_settings', 0)}개, 카테고리: {stats.get('categories', 0)}개"
                )
                return True
            else:
                self.print_test_result("설정 통계 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 통계 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_settings(self):
        """설정 목록 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/settings")
            if response.status_code == 200:
                data = response.json()
                settings = data.get('data', [])
                self.print_test_result(
                    "설정 목록 조회",
                    True,
                    f"총 {len(settings)}개의 설정"
                )
                return True
            else:
                self.print_test_result("설정 목록 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 목록 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_setting_by_key(self):
        """특정 설정 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/settings/app_name")
            if response.status_code == 200:
                data = response.json()
                setting = data.get('data', {})
                self.print_test_result(
                    "특정 설정 조회",
                    True,
                    f"설정 키: {setting.get('key')}, 값: {setting.get('value')}"
                )
                return True
            else:
                self.print_test_result("특정 설정 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("특정 설정 조회", False, f"오류: {str(e)}")
            return False
    
    def test_update_setting(self):
        """설정 값 변경 테스트"""
        try:
            # 테스트용 임시 값
            test_value = f"테스트 값 {datetime.now().strftime('%H:%M:%S')}"
            
            response = self.session.put(f"{BASE_URL}/api/settings/settings/app_name", json={
                "value": test_value,
                "changed_by": "test_user",
                "change_reason": "테스트를 위한 설정 변경"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.print_test_result(
                    "설정 값 변경",
                    True,
                    f"변경된 값: {test_value}"
                )
                return True
            else:
                self.print_test_result("설정 값 변경", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 값 변경", False, f"오류: {str(e)}")
            return False
    
    def test_validate_setting(self):
        """설정 값 검증 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/settings/settings/app_name/validate", json={
                "value": "유효한 앱 이름"
            })
            
            if response.status_code == 200:
                data = response.json()
                validation_result = data.get('data', {})
                self.print_test_result(
                    "설정 값 검증",
                    True,
                    f"검증 결과: {validation_result.get('message', '알 수 없음')}"
                )
                return True
            else:
                self.print_test_result("설정 값 검증", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 값 검증", False, f"오류: {str(e)}")
            return False
    
    def test_create_setting(self):
        """새 설정 생성 테스트"""
        try:
            test_setting = {
                "key": f"test_setting_{int(time.time())}",
                "value": "테스트 설정 값",
                "category": "system",
                "description": "테스트를 위한 임시 설정",
                "data_type": "string",
                "is_sensitive": False,
                "is_required": False,
                "default_value": "기본값"
            }
            
            response = self.session.post(f"{BASE_URL}/api/settings/settings", json=test_setting)
            
            if response.status_code == 201:
                data = response.json()
                self.print_test_result(
                    "새 설정 생성",
                    True,
                    f"생성된 설정 키: {test_setting['key']}"
                )
                return True
            else:
                self.print_test_result("새 설정 생성", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("새 설정 생성", False, f"오류: {str(e)}")
            return False
    
    def test_get_categories(self):
        """설정 카테고리 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/categories")
            if response.status_code == 200:
                data = response.json()
                categories = data.get('data', [])
                self.print_test_result(
                    "설정 카테고리 조회",
                    True,
                    f"총 {len(categories)}개의 카테고리"
                )
                return True
            else:
                self.print_test_result("설정 카테고리 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 카테고리 조회", False, f"오류: {str(e)}")
            return False
    
    def test_get_changes(self):
        """설정 변경 이력 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/changes?limit=10")
            if response.status_code == 200:
                data = response.json()
                changes = data.get('data', [])
                self.print_test_result(
                    "설정 변경 이력 조회",
                    True,
                    f"최근 {len(changes)}개의 변경 이력"
                )
                return True
            else:
                self.print_test_result("설정 변경 이력 조회", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 변경 이력 조회", False, f"오류: {str(e)}")
            return False
    
    def test_export_settings(self):
        """설정 내보내기 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/export?format=json")
            if response.status_code == 200:
                data = response.json()
                export_data = data.get('data', {})
                self.print_test_result(
                    "설정 내보내기",
                    True,
                    f"형식: {export_data.get('format')}, 내보내기 시간: {export_data.get('exported_at')}"
                )
                return True
            else:
                self.print_test_result("설정 내보내기", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 내보내기", False, f"오류: {str(e)}")
            return False
    
    def test_import_settings(self):
        """설정 가져오기 테스트"""
        try:
            # 테스트용 설정 데이터
            test_settings = {
                "import_test_setting": "가져오기 테스트 값",
                "import_test_setting_2": "가져오기 테스트 값 2"
            }
            
            response = self.session.post(f"{BASE_URL}/api/settings/import", json={
                "content": json.dumps(test_settings),
                "format": "json",
                "changed_by": "test_user"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.print_test_result(
                    "설정 가져오기",
                    True,
                    f"가져오기 시간: {data.get('data', {}).get('imported_at')}"
                )
                return True
            else:
                self.print_test_result("설정 가져오기", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 가져오기", False, f"오류: {str(e)}")
            return False
    
    def test_generate_env_file(self):
        """환경 변수 파일 생성 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/env-file")
            if response.status_code == 200:
                data = response.json()
                env_data = data.get('data', {})
                self.print_test_result(
                    "환경 변수 파일 생성",
                    True,
                    f"생성 시간: {env_data.get('generated_at')}"
                )
                return True
            else:
                self.print_test_result("환경 변수 파일 생성", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("환경 변수 파일 생성", False, f"오류: {str(e)}")
            return False
    
    def test_create_backup(self):
        """설정 백업 생성 테스트"""
        try:
            response = self.session.post(f"{BASE_URL}/api/settings/backup", json={
                "name": f"테스트 백업 {datetime.now().strftime('%H:%M:%S')}",
                "description": "테스트를 위한 설정 백업",
                "created_by": "test_user"
            })
            
            if response.status_code == 201:
                data = response.json()
                backup_data = data.get('data', {})
                self.print_test_result(
                    "설정 백업 생성",
                    True,
                    f"백업 ID: {backup_data.get('backup_id')}, 이름: {backup_data.get('name')}"
                )
                return backup_data.get('backup_id')
            else:
                self.print_test_result("설정 백업 생성", False, f"상태 코드: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("설정 백업 생성", False, f"오류: {str(e)}")
            return None
    
    def test_get_backups(self):
        """백업 목록 조회 테스트"""
        try:
            response = self.session.get(f"{BASE_URL}/api/settings/backup")
            if response.status_code == 200:
                data = response.json()
                backups = data.get('data', [])
                self.print_test_result(
                    "백업 목록 조회",
                    True,
                    f"총 {len(backups)}개의 백업"
                )
                return backups[0].get('backup_id') if backups else None
            else:
                self.print_test_result("백업 목록 조회", False, f"상태 코드: {response.status_code}")
                return None
        except Exception as e:
            self.print_test_result("백업 목록 조회", False, f"오류: {str(e)}")
            return None
    
    def test_restore_backup(self, backup_id):
        """설정 백업 복원 테스트"""
        if not backup_id:
            self.print_test_result("설정 백업 복원", False, "백업 ID가 없습니다")
            return False
        
        try:
            response = self.session.post(f"{BASE_URL}/api/settings/backup/{backup_id}/restore", json={
                "restore_sensitive": False
            })
            
            if response.status_code == 200:
                data = response.json()
                restore_data = data.get('data', {})
                self.print_test_result(
                    "설정 백업 복원",
                    True,
                    f"복원 시간: {restore_data.get('restored_at')}"
                )
                return True
            else:
                self.print_test_result("설정 백업 복원", False, f"상태 코드: {response.status_code}")
                return False
        except Exception as e:
            self.print_test_result("설정 백업 복원", False, f"오류: {str(e)}")
            return False
    
    def test_invalid_requests(self):
        """잘못된 요청 테스트"""
        try:
            # 존재하지 않는 설정 조회
            response = self.session.get(f"{BASE_URL}/api/settings/settings/nonexistent_setting")
            if response.status_code == 404:
                self.print_test_result("잘못된 설정 조회", True, "예상대로 404 오류 발생")
            else:
                self.print_test_result("잘못된 설정 조회", False, f"예상 404, 실제: {response.status_code}")
            
            # 잘못된 형식으로 설정 변경
            response = self.session.put(f"{BASE_URL}/api/settings/settings/app_name", json={
                "invalid_field": "잘못된 필드"
            })
            if response.status_code == 400:
                self.print_test_result("잘못된 설정 변경", True, "예상대로 400 오류 발생")
            else:
                self.print_test_result("잘못된 설정 변경", False, f"예상 400, 실제: {response.status_code}")
            
            return True
        except Exception as e:
            self.print_test_result("잘못된 요청 테스트", False, f"오류: {str(e)}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("⚙️ 시스템 설정 관리 테스트 시작")
        print("=" * 50)
        
        tests = [
            ("시스템 상태 확인", self.test_health_check),
            ("설정 통계 조회", self.test_get_stats),
            ("설정 목록 조회", self.test_get_settings),
            ("특정 설정 조회", self.test_get_setting_by_key),
            ("설정 값 검증", self.test_validate_setting),
            ("설정 값 변경", self.test_update_setting),
            ("새 설정 생성", self.test_create_setting),
            ("설정 카테고리 조회", self.test_get_categories),
            ("설정 변경 이력 조회", self.test_get_changes),
            ("설정 내보내기", self.test_export_settings),
            ("설정 가져오기", self.test_import_settings),
            ("환경 변수 파일 생성", self.test_generate_env_file),
            ("백업 생성", self.test_create_backup),
            ("백업 목록 조회", self.test_get_backups),
            ("잘못된 요청 테스트", self.test_invalid_requests),
        ]
        
        passed = 0
        total = len(tests)
        backup_id = None
        
        for test_name, test_func in tests:
            try:
                if test_name == "백업 생성":
                    backup_id = test_func()
                    if backup_id:
                        passed += 1
                elif test_name == "백업 목록 조회":
                    result = test_func()
                    if result:
                        backup_id = result
                        passed += 1
                elif test_name == "설정 백업 복원":
                    if backup_id:
                        if test_func(backup_id):
                            passed += 1
                    else:
                        self.print_test_result(test_name, False, "백업 ID가 없습니다")
                else:
                    if test_func():
                        passed += 1
                time.sleep(0.5)  # API 호출 간격
            except Exception as e:
                self.print_test_result(test_name, False, f"테스트 실행 오류: {str(e)}")
        
        # 백업 복원 테스트 (백업 ID가 있는 경우)
        if backup_id:
            try:
                if self.test_restore_backup(backup_id):
                    passed += 1
            except Exception as e:
                self.print_test_result("설정 백업 복원", False, f"테스트 실행 오류: {str(e)}")
        
        print("=" * 50)
        print(f"📊 테스트 결과: {passed}/{total + 1} 통과")  # +1 for backup restore
        
        if passed == total + 1:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️ 일부 테스트가 실패했습니다.")
        
        return passed == total + 1

def main():
    """메인 함수"""
    print("시스템 설정 관리 테스트를 시작합니다...")
    print(f"테스트 대상 URL: {BASE_URL}")
    print()
    
    tester = SettingsSystemTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 설정 시스템이 정상적으로 작동합니다!")
    else:
        print("\n❌ 설정 시스템에 문제가 있습니다. 로그를 확인해주세요.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main()) 