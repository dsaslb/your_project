#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
플러그인 설정 관리 시스템 테스트 스크립트
설정 생성, 수정, 백업, 복원, 내보내기, 가져오기 등의 기능을 테스트합니다.
"""

import requests
import json
import time
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# 테스트 설정
BASE_URL = "http://localhost:5000"
TEST_PLUGIN = "test_plugin_settings"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "admin123"
}

class PluginSettingsTester:
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """테스트 결과 로깅"""
        status = "✅ PASS" if success else "❌ FAIL"
        timestamp = datetime.now().strftime("%H:%M:%S")
        result = f"[{timestamp}] {status} - {test_name}"
        if message:
            result += f": {message}"
        print(result)
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "message": message,
            "timestamp": timestamp
        })
        
    def login(self) -> bool:
        """관리자 로그인"""
        try:
            login_data = {
                "username": ADMIN_CREDENTIALS["username"],
                "password": ADMIN_CREDENTIALS["password"]
            }
            
            response = self.session.post(f"{self.base_url}/auth/login", data=login_data)
            
            if response.status_code == 200:
                self.log_test("관리자 로그인", True)
                return True
            else:
                self.log_test("관리자 로그인", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("관리자 로그인", False, str(e))
            return False
    
    def test_create_settings_template(self) -> bool:
        """설정 템플릿 생성 테스트"""
        try:
            template = {
                "name": "테스트 플러그인 설정 템플릿",
                "description": "플러그인 설정 관리 테스트를 위한 템플릿",
                "schema": {
                    "type": "object",
                    "properties": {
                        "enabled": {"type": "boolean"},
                        "debug_mode": {"type": "boolean"},
                        "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR"]},
                        "auto_reload": {"type": "boolean"},
                        "permissions": {"type": "array", "items": {"type": "string"}},
                        "config": {
                            "type": "object",
                            "properties": {
                                "max_connections": {"type": "integer", "minimum": 1, "maximum": 1000},
                                "timeout": {"type": "integer", "minimum": 1, "maximum": 300},
                                "cache_size": {"type": "integer", "minimum": 1, "maximum": 10000}
                            }
                        }
                    },
                    "required": ["enabled", "log_level"]
                },
                "default_settings": {
                    "enabled": True,
                    "debug_mode": False,
                    "log_level": "INFO",
                    "auto_reload": False,
                    "permissions": ["read", "write"],
                    "config": {
                        "max_connections": 100,
                        "timeout": 30,
                        "cache_size": 1000
                    }
                },
                "migrations": {
                    "1.0.0_to_2.0.0": {
                        "description": "버전 2.0.0으로 마이그레이션",
                        "changes": [
                            "새로운 설정 필드 추가",
                            "기존 설정 구조 변경"
                        ]
                    }
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/template",
                json={"template": template}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("설정 템플릿 생성", True)
                    return True
                else:
                    self.log_test("설정 템플릿 생성", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 템플릿 생성", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 템플릿 생성", False, str(e))
            return False
    
    def test_get_settings_template(self) -> bool:
        """설정 템플릿 조회 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/template")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    template = data.get("data", {})
                    if template.get("name"):
                        self.log_test("설정 템플릿 조회", True)
                        return True
                    else:
                        self.log_test("설정 템플릿 조회", False, "템플릿 데이터 없음")
                        return False
                else:
                    self.log_test("설정 템플릿 조회", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 템플릿 조회", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 템플릿 조회", False, str(e))
            return False
    
    def test_create_initial_settings(self) -> bool:
        """초기 설정 생성 테스트"""
        try:
            initial_settings = {
                "enabled": True,
                "debug_mode": False,
                "log_level": "INFO",
                "auto_reload": False,
                "permissions": ["read", "write"],
                "config": {
                    "max_connections": 100,
                    "timeout": 30,
                    "cache_size": 1000
                },
                "version": "1.0.0"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}",
                json={"settings": initial_settings}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("초기 설정 생성", True)
                    return True
                else:
                    self.log_test("초기 설정 생성", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("초기 설정 생성", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("초기 설정 생성", False, str(e))
            return False
    
    def test_get_settings(self) -> bool:
        """설정 조회 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    settings = data.get("data", {}).get("settings", {})
                    metadata = data.get("data", {}).get("metadata", {})
                    
                    if settings and metadata:
                        self.log_test("설정 조회", True)
                        return True
                    else:
                        self.log_test("설정 조회", False, "설정 또는 메타데이터 없음")
                        return False
                else:
                    self.log_test("설정 조회", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 조회", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 조회", False, str(e))
            return False
    
    def test_update_settings(self) -> bool:
        """설정 업데이트 테스트"""
        try:
            updated_settings = {
                "enabled": True,
                "debug_mode": True,
                "log_level": "DEBUG",
                "auto_reload": True,
                "permissions": ["read", "write", "admin"],
                "config": {
                    "max_connections": 200,
                    "timeout": 60,
                    "cache_size": 2000
                },
                "version": "1.1.0"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}",
                json={"settings": updated_settings}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("설정 업데이트", True)
                    return True
                else:
                    self.log_test("설정 업데이트", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 업데이트", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 업데이트", False, str(e))
            return False
    
    def test_validate_settings(self) -> bool:
        """설정 검증 테스트"""
        try:
            # 유효한 설정
            valid_settings = {
                "enabled": True,
                "debug_mode": False,
                "log_level": "INFO",
                "auto_reload": False,
                "permissions": ["read", "write"],
                "config": {
                    "max_connections": 100,
                    "timeout": 30,
                    "cache_size": 1000
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/validate",
                json={"settings": valid_settings}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("data", {}).get("is_valid"):
                    self.log_test("설정 검증 (유효한 설정)", True)
                else:
                    self.log_test("설정 검증 (유효한 설정)", False, "설정이 유효하지 않음")
                    return False
            else:
                self.log_test("설정 검증 (유효한 설정)", False, f"Status: {response.status_code}")
                return False
            
            # 유효하지 않은 설정
            invalid_settings = {
                "enabled": "invalid_boolean",  # boolean이어야 함
                "log_level": "INVALID_LEVEL",  # 허용되지 않은 값
                "config": {
                    "max_connections": -1  # 최소값 위반
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/validate",
                json={"settings": invalid_settings}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and not data.get("data", {}).get("is_valid"):
                    self.log_test("설정 검증 (유효하지 않은 설정)", True)
                    return True
                else:
                    self.log_test("설정 검증 (유효하지 않은 설정)", False, "유효하지 않은 설정이 유효하다고 판단됨")
                    return False
            else:
                self.log_test("설정 검증 (유효하지 않은 설정)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 검증", False, str(e))
            return False
    
    def test_create_backup(self) -> bool:
        """백업 생성 테스트"""
        try:
            response = self.session.post(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/backup")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("백업 생성", True)
                    return True
                else:
                    self.log_test("백업 생성", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("백업 생성", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("백업 생성", False, str(e))
            return False
    
    def test_get_backup_list(self) -> bool:
        """백업 목록 조회 테스트"""
        try:
            response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/backup")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    backups = data.get("data", [])
                    if len(backups) > 0:
                        self.log_test("백업 목록 조회", True, f"{len(backups)}개 백업 발견")
                        return True
                    else:
                        self.log_test("백업 목록 조회", False, "백업이 없음")
                        return False
                else:
                    self.log_test("백업 목록 조회", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("백업 목록 조회", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("백업 목록 조회", False, str(e))
            return False
    
    def test_export_settings(self) -> bool:
        """설정 내보내기 테스트"""
        try:
            # JSON 형식으로 내보내기
            response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/export?format=json")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("data"):
                    self.log_test("설정 내보내기 (JSON)", True)
                else:
                    self.log_test("설정 내보내기 (JSON)", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 내보내기 (JSON)", False, f"Status: {response.status_code}")
                return False
            
            # YAML 형식으로 내보내기
            response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/export?format=yaml")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success" and data.get("data"):
                    self.log_test("설정 내보내기 (YAML)", True)
                    return True
                else:
                    self.log_test("설정 내보내기 (YAML)", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 내보내기 (YAML)", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 내보내기", False, str(e))
            return False
    
    def test_import_settings(self) -> bool:
        """설정 가져오기 테스트"""
        try:
            # 내보낸 설정 데이터 가져오기
            export_response = self.session.get(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/export?format=json")
            
            if export_response.status_code != 200:
                self.log_test("설정 가져오기", False, "내보내기 데이터를 가져올 수 없음")
                return False
            
            export_data = export_response.json()
            if not export_data.get("data"):
                self.log_test("설정 가져오기", False, "내보내기 데이터가 없음")
                return False
            
            # 설정 가져오기
            import_data = {
                "import_data": export_data["data"],
                "format": "json"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/import",
                json=import_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("설정 가져오기", True)
                    return True
                else:
                    self.log_test("설정 가져오기", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 가져오기", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 가져오기", False, str(e))
            return False
    
    def test_migrate_settings(self) -> bool:
        """설정 마이그레이션 테스트"""
        try:
            migration_data = {
                "from_version": "1.0.0",
                "to_version": "2.0.0"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/migrate",
                json=migration_data
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("설정 마이그레이션", True)
                    return True
                else:
                    self.log_test("설정 마이그레이션", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 마이그레이션", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 마이그레이션", False, str(e))
            return False
    
    def test_reset_settings(self) -> bool:
        """설정 초기화 테스트"""
        try:
            response = self.session.post(f"{self.base_url}/api/plugin-settings/{TEST_PLUGIN}/reset")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "success":
                    self.log_test("설정 초기화", True)
                    return True
                else:
                    self.log_test("설정 초기화", False, data.get("error", "Unknown error"))
                    return False
            else:
                self.log_test("설정 초기화", False, f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("설정 초기화", False, str(e))
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 플러그인 설정 관리 시스템 테스트 시작")
        print("=" * 60)
        
        # 로그인
        if not self.login():
            print("❌ 로그인 실패로 테스트를 중단합니다.")
            return
        
        print()
        
        # 테스트 실행
        tests = [
            ("설정 템플릿 생성", self.test_create_settings_template),
            ("설정 템플릿 조회", self.test_get_settings_template),
            ("초기 설정 생성", self.test_create_initial_settings),
            ("설정 조회", self.test_get_settings),
            ("설정 업데이트", self.test_update_settings),
            ("설정 검증", self.test_validate_settings),
            ("백업 생성", self.test_create_backup),
            ("백업 목록 조회", self.test_get_backup_list),
            ("설정 내보내기", self.test_export_settings),
            ("설정 가져오기", self.test_import_settings),
            ("설정 마이그레이션", self.test_migrate_settings),
            ("설정 초기화", self.test_reset_settings),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, False, f"예외 발생: {str(e)}")
            
            time.sleep(0.5)  # API 호출 간격
        
        print()
        print("=" * 60)
        print(f"📊 테스트 결과: {passed}/{total} 통과")
        
        if passed == total:
            print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        else:
            print("⚠️  일부 테스트가 실패했습니다.")
        
        # 상세 결과 출력
        print("\n📋 상세 결과:")
        for result in self.test_results:
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {result['test']} - {result['message'] if result['message'] else '성공'}")
        
        return passed == total

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        base_url = BASE_URL
    
    print(f"🔗 테스트 대상 URL: {base_url}")
    print(f"🧪 테스트 플러그인: {TEST_PLUGIN}")
    print()
    
    tester = PluginSettingsTester(base_url)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 