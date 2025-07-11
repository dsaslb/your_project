#!/usr/bin/env python3
"""
플러그인 배포 테스트 스크립트
플러그인 시스템의 배포 과정을 테스트하고 검증합니다.
"""

import os
import sys
import json
import time
import requests
import subprocess
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

class PluginDeploymentTester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": []
            }
        }
    
    def log_test(self, test_name, status, details=None, error=None):
        """테스트 결과 로깅"""
        test_result = {
            "name": test_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "details": details
        }
        
        if error:
            test_result["error"] = str(error)
        
        self.test_results["tests"].append(test_result)
        self.test_results["summary"]["total"] += 1
        
        if status == "PASSED":
            self.test_results["summary"]["passed"] += 1
        else:
            self.test_results["summary"]["failed"] += 1
            if error:
                self.test_results["summary"]["errors"].append(f"{test_name}: {error}")
        
        print(f"[{status}] {test_name}")
        if details:
            print(f"  Details: {details}")
        if error:
            print(f"  Error: {error}")
    
    def test_application_startup(self):
        """애플리케이션 시작 테스트"""
        try:
            # 애플리케이션 시작
            process = subprocess.Popen(
                ["python", "app.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # 시작 대기
            time.sleep(10)
            
            # 헬스체크
            response = requests.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                self.log_test("Application Startup", "PASSED", "Application started successfully")
                return process
            else:
                self.log_test("Application Startup", "FAILED", f"Health check failed: {response.status_code}")
                process.terminate()
                return None
                
        except Exception as e:
            self.log_test("Application Startup", "FAILED", error=str(e))
            return None
    
    def test_plugin_system_initialization(self):
        """플러그인 시스템 초기화 테스트"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                if "plugins" in status:
                    self.log_test("Plugin System Initialization", "PASSED", f"Found {len(status['plugins'])} plugins")
                    return True
                else:
                    self.log_test("Plugin System Initialization", "FAILED", "No plugins found in status")
                    return False
            else:
                self.log_test("Plugin System Initialization", "FAILED", f"Status API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin System Initialization", "FAILED", error=str(e))
            return False
    
    def test_plugin_loading(self):
        """플러그인 로딩 테스트"""
        try:
            # 플러그인 디렉토리 확인
            plugin_dir = Path("plugins")
            if not plugin_dir.exists():
                self.log_test("Plugin Loading", "FAILED", "Plugin directory not found")
                return False
            
            # 플러그인 파일 확인
            plugin_files = list(plugin_dir.glob("**/*.py"))
            if not plugin_files:
                self.log_test("Plugin Loading", "FAILED", "No plugin files found")
                return False
            
            # 플러그인 로딩 상태 확인
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            
            if response.status_code == 200:
                status = response.json()
                loaded_plugins = status.get("plugins", [])
                
                if loaded_plugins:
                    self.log_test("Plugin Loading", "PASSED", f"Loaded {len(loaded_plugins)} plugins")
                    return True
                else:
                    self.log_test("Plugin Loading", "FAILED", "No plugins loaded")
                    return False
            else:
                self.log_test("Plugin Loading", "FAILED", f"Status API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Loading", "FAILED", error=str(e))
            return False
    
    def test_plugin_monitoring_start(self):
        """플러그인 모니터링 시작 테스트"""
        try:
            response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/start", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "started":
                    self.log_test("Plugin Monitoring Start", "PASSED", "Monitoring started successfully")
                    return True
                else:
                    self.log_test("Plugin Monitoring Start", "FAILED", f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Plugin Monitoring Start", "FAILED", f"Start API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Monitoring Start", "FAILED", error=str(e))
            return False
    
    def test_plugin_metrics_collection(self):
        """플러그인 메트릭 수집 테스트"""
        try:
            # 메트릭 수집 대기
            time.sleep(5)
            
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics = response.json()
                if "plugins" in metrics and metrics["plugins"]:
                    self.log_test("Plugin Metrics Collection", "PASSED", f"Collected metrics for {len(metrics['plugins'])} plugins")
                    return True
                else:
                    self.log_test("Plugin Metrics Collection", "FAILED", "No metrics collected")
                    return False
            else:
                self.log_test("Plugin Metrics Collection", "FAILED", f"Metrics API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Metrics Collection", "FAILED", error=str(e))
            return False
    
    def test_plugin_backup_system(self):
        """플러그인 백업 시스템 테스트"""
        try:
            response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/backup", timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "success":
                    self.log_test("Plugin Backup System", "PASSED", f"Backup created: {result.get('backup_path', 'N/A')}")
                    return True
                else:
                    self.log_test("Plugin Backup System", "FAILED", f"Backup failed: {result}")
                    return False
            else:
                self.log_test("Plugin Backup System", "FAILED", f"Backup API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Backup System", "FAILED", error=str(e))
            return False
    
    def test_plugin_restart_functionality(self):
        """플러그인 재시작 기능 테스트"""
        try:
            # 플러그인 목록 가져오기
            status_response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            
            if status_response.status_code == 200:
                status = status_response.json()
                plugins = status.get("plugins", [])
                
                if plugins:
                    # 첫 번째 플러그인 재시작
                    plugin_name = plugins[0]["name"]
                    restart_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/restart/{plugin_name}", timeout=30)
                    
                    if restart_response.status_code == 200:
                        result = restart_response.json()
                        if result.get("status") == "success":
                            self.log_test("Plugin Restart Functionality", "PASSED", f"Plugin {plugin_name} restarted successfully")
                            return True
                        else:
                            self.log_test("Plugin Restart Functionality", "FAILED", f"Restart failed: {result}")
                            return False
                    else:
                        self.log_test("Plugin Restart Functionality", "FAILED", f"Restart API failed: {restart_response.status_code}")
                        return False
                else:
                    self.log_test("Plugin Restart Functionality", "FAILED", "No plugins available for restart")
                    return False
            else:
                self.log_test("Plugin Restart Functionality", "FAILED", f"Status API failed: {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Restart Functionality", "FAILED", error=str(e))
            return False
    
    def test_plugin_monitoring_stop(self):
        """플러그인 모니터링 중지 테스트"""
        try:
            response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/stop", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "stopped":
                    self.log_test("Plugin Monitoring Stop", "PASSED", "Monitoring stopped successfully")
                    return True
                else:
                    self.log_test("Plugin Monitoring Stop", "FAILED", f"Unexpected response: {result}")
                    return False
            else:
                self.log_test("Plugin Monitoring Stop", "FAILED", f"Stop API failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Monitoring Stop", "FAILED", error=str(e))
            return False
    
    def test_application_shutdown(self, process):
        """애플리케이션 종료 테스트"""
        try:
            if process:
                process.terminate()
                process.wait(timeout=10)
                self.log_test("Application Shutdown", "PASSED", "Application shutdown successfully")
                return True
            else:
                self.log_test("Application Shutdown", "FAILED", "No process to shutdown")
                return False
                
        except Exception as e:
            self.log_test("Application Shutdown", "FAILED", error=str(e))
            return False
    
    def generate_report(self):
        """테스트 리포트 생성"""
        summary = self.test_results["summary"]
        
        report = {
            "test_info": {
                "timestamp": self.test_results["timestamp"],
                "total_tests": summary["total"],
                "passed": summary["passed"],
                "failed": summary["failed"],
                "success_rate": (summary["passed"] / summary["total"] * 100) if summary["total"] > 0 else 0
            },
            "test_results": self.test_results["tests"],
            "errors": summary["errors"],
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self):
        """개선 권장사항 생성"""
        recommendations = []
        summary = self.test_results["summary"]
        
        if summary["failed"] > 0:
            recommendations.append("일부 테스트가 실패했습니다. 실패한 테스트를 확인하고 수정하세요.")
        
        if summary["success_rate"] < 80:
            recommendations.append("테스트 성공률이 낮습니다. 시스템 안정성을 개선하세요.")
        
        if not recommendations:
            recommendations.append("모든 테스트가 통과했습니다. 시스템이 정상적으로 작동합니다.")
        
        return recommendations
    
    def save_results(self, filename="plugin-deployment-test-results.json"):
        """결과를 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        report = self.generate_report()
        with open("plugin-deployment-test-report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=== 플러그인 배포 테스트 시작 ===")
        
        # 애플리케이션 시작
        process = self.test_application_startup()
        if not process:
            return False
        
        try:
            # 플러그인 시스템 테스트
            self.test_plugin_system_initialization()
            self.test_plugin_loading()
            
            # 모니터링 테스트
            self.test_plugin_monitoring_start()
            self.test_plugin_metrics_collection()
            
            # 기능 테스트
            self.test_plugin_backup_system()
            self.test_plugin_restart_functionality()
            
            # 모니터링 중지
            self.test_plugin_monitoring_stop()
            
        finally:
            # 애플리케이션 종료
            self.test_application_shutdown(process)
        
        # 결과 저장
        self.save_results()
        
        # 리포트 출력
        report = self.generate_report()
        print("\n=== 플러그인 배포 테스트 결과 ===")
        print(f"총 테스트: {report['test_info']['total_tests']}")
        print(f"성공: {report['test_info']['passed']}")
        print(f"실패: {report['test_info']['failed']}")
        print(f"성공률: {report['test_info']['success_rate']:.1f}%")
        
        if report['errors']:
            print("\n오류:")
            for error in report['errors']:
                print(f"- {error}")
        
        print("\n권장사항:")
        for rec in report['recommendations']:
            print(f"- {rec}")
        
        return report['test_info']['success_rate'] >= 80

def main():
    """메인 함수"""
    tester = PluginDeploymentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 플러그인 배포 테스트가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 플러그인 배포 테스트에서 문제가 발견되었습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 