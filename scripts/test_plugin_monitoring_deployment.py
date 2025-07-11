#!/usr/bin/env python3
"""
플러그인 모니터링 시스템 배포 테스트 스크립트
플러그인 성능 모니터링 시스템의 배포 과정을 테스트하고 검증합니다.
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

class PluginMonitoringDeploymentTester:
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
    
    def test_monitoring_api_endpoints(self):
        """모니터링 API 엔드포인트 테스트"""
        endpoints = [
            "/api/admin/plugin-monitoring/health",
            "/api/admin/plugin-monitoring/status",
            "/api/admin/plugin-monitoring/metrics",
            "/api/admin/plugin-monitoring/performance",
            "/api/admin/plugin-monitoring/alerts",
            "/api/admin/plugin-monitoring/dashboard"
        ]
        
        all_passed = True
        
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    self.log_test(f"API Endpoint: {endpoint}", "PASSED", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API Endpoint: {endpoint}", "FAILED", f"Status: {response.status_code}")
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"API Endpoint: {endpoint}", "FAILED", error=str(e))
                all_passed = False
        
        return all_passed
    
    def test_monitoring_start_stop(self):
        """모니터링 시작/중지 테스트"""
        try:
            # 모니터링 시작
            start_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/start", timeout=10)
            
            if start_response.status_code == 200:
                start_result = start_response.json()
                if start_result.get("status") == "started":
                    self.log_test("Monitoring Start", "PASSED", "Monitoring started successfully")
                    
                    # 잠시 대기
                    time.sleep(3)
                    
                    # 모니터링 중지
                    stop_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/stop", timeout=10)
                    
                    if stop_response.status_code == 200:
                        stop_result = stop_response.json()
                        if stop_result.get("status") == "stopped":
                            self.log_test("Monitoring Stop", "PASSED", "Monitoring stopped successfully")
                            return True
                        else:
                            self.log_test("Monitoring Stop", "FAILED", f"Unexpected response: {stop_result}")
                            return False
                    else:
                        self.log_test("Monitoring Stop", "FAILED", f"Stop API failed: {stop_response.status_code}")
                        return False
                else:
                    self.log_test("Monitoring Start", "FAILED", f"Unexpected response: {start_result}")
                    return False
            else:
                self.log_test("Monitoring Start", "FAILED", f"Start API failed: {start_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Monitoring Start/Stop", "FAILED", error=str(e))
            return False
    
    def test_real_time_monitoring(self):
        """실시간 모니터링 테스트"""
        try:
            # 모니터링 시작
            start_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/start", timeout=10)
            
            if start_response.status_code != 200:
                self.log_test("Real-time Monitoring", "FAILED", "Failed to start monitoring")
                return False
            
            # 실시간 데이터 수집 테스트
            time.sleep(5)
            
            metrics_response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/metrics", timeout=10)
            
            if metrics_response.status_code == 200:
                metrics = metrics_response.json()
                
                if "plugins" in metrics and metrics["plugins"]:
                    # 실시간 데이터가 있는지 확인
                    has_real_time_data = False
                    for plugin in metrics["plugins"]:
                        if "cpu_usage" in plugin or "memory_usage" in plugin or "response_time" in plugin:
                            has_real_time_data = True
                            break
                    
                    if has_real_time_data:
                        self.log_test("Real-time Monitoring", "PASSED", "Real-time data collected successfully")
                    else:
                        self.log_test("Real-time Monitoring", "FAILED", "No real-time data found")
                        return False
                else:
                    self.log_test("Real-time Monitoring", "FAILED", "No metrics data available")
                    return False
            else:
                self.log_test("Real-time Monitoring", "FAILED", f"Metrics API failed: {metrics_response.status_code}")
                return False
            
            # 모니터링 중지
            stop_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/stop", timeout=10)
            
            return True
                
        except Exception as e:
            self.log_test("Real-time Monitoring", "FAILED", error=str(e))
            return False
    
    def test_alert_system(self):
        """알림 시스템 테스트"""
        try:
            # 알림 설정 확인
            alerts_response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/alerts", timeout=10)
            
            if alerts_response.status_code == 200:
                alerts = alerts_response.json()
                
                if "alerts" in alerts:
                    self.log_test("Alert System", "PASSED", f"Alert system active with {len(alerts['alerts'])} alerts")
                    return True
                else:
                    self.log_test("Alert System", "PASSED", "Alert system available")
                    return True
            else:
                self.log_test("Alert System", "FAILED", f"Alerts API failed: {alerts_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Alert System", "FAILED", error=str(e))
            return False
    
    def test_performance_dashboard(self):
        """성능 대시보드 테스트"""
        try:
            # 대시보드 데이터 확인
            dashboard_response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/dashboard", timeout=10)
            
            if dashboard_response.status_code == 200:
                dashboard = dashboard_response.json()
                
                required_fields = ["plugins", "system_metrics", "performance_trends"]
                missing_fields = [field for field in required_fields if field not in dashboard]
                
                if not missing_fields:
                    self.log_test("Performance Dashboard", "PASSED", "Dashboard data available")
                    return True
                else:
                    self.log_test("Performance Dashboard", "FAILED", f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("Performance Dashboard", "FAILED", f"Dashboard API failed: {dashboard_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Performance Dashboard", "FAILED", error=str(e))
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
                            self.log_test("Plugin Restart", "PASSED", f"Plugin {plugin_name} restarted successfully")
                            return True
                        else:
                            self.log_test("Plugin Restart", "FAILED", f"Restart failed: {result}")
                            return False
                    else:
                        self.log_test("Plugin Restart", "FAILED", f"Restart API failed: {restart_response.status_code}")
                        return False
                else:
                    self.log_test("Plugin Restart", "FAILED", "No plugins available for restart")
                    return False
            else:
                self.log_test("Plugin Restart", "FAILED", f"Status API failed: {status_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Plugin Restart", "FAILED", error=str(e))
            return False
    
    def test_backup_restore_system(self):
        """백업/복원 시스템 테스트"""
        try:
            # 백업 생성
            backup_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/backup", timeout=30)
            
            if backup_response.status_code == 200:
                backup_result = backup_response.json()
                if backup_result.get("status") == "success":
                    backup_path = backup_result.get("backup_path", "")
                    self.log_test("Backup System", "PASSED", f"Backup created: {backup_path}")
                    
                    # 백업 파일 존재 확인
                    if backup_path and os.path.exists(backup_path):
                        self.log_test("Backup File Verification", "PASSED", "Backup file exists")
                        
                        # 복원 테스트 (선택적)
                        restore_response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/restore", timeout=30)
                        
                        if restore_response.status_code == 200:
                            restore_result = restore_response.json()
                            if restore_result.get("status") == "success":
                                self.log_test("Restore System", "PASSED", "Restore completed successfully")
                                return True
                            else:
                                self.log_test("Restore System", "FAILED", f"Restore failed: {restore_result}")
                                return False
                        else:
                            self.log_test("Restore System", "FAILED", f"Restore API failed: {restore_response.status_code}")
                            return False
                    else:
                        self.log_test("Backup File Verification", "FAILED", "Backup file not found")
                        return False
                else:
                    self.log_test("Backup System", "FAILED", f"Backup failed: {backup_result}")
                    return False
            else:
                self.log_test("Backup System", "FAILED", f"Backup API failed: {backup_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Backup/Restore System", "FAILED", error=str(e))
            return False
    
    def test_frontend_integration(self):
        """프론트엔드 통합 테스트"""
        try:
            # 프론트엔드 빌드 확인
            frontend_dir = Path("your_program_frontend")
            if not frontend_dir.exists():
                self.log_test("Frontend Integration", "FAILED", "Frontend directory not found")
                return False
            
            # 빌드 파일 확인
            build_dir = frontend_dir / ".next"
            if build_dir.exists():
                self.log_test("Frontend Integration", "PASSED", "Frontend build files found")
                return True
            else:
                self.log_test("Frontend Integration", "FAILED", "Frontend build files not found")
                return False
                
        except Exception as e:
            self.log_test("Frontend Integration", "FAILED", error=str(e))
            return False
    
    def test_monitoring_configuration(self):
        """모니터링 설정 테스트"""
        try:
            # 설정 API 확인
            config_response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/config", timeout=10)
            
            if config_response.status_code == 200:
                config = config_response.json()
                
                if "monitoring_enabled" in config:
                    self.log_test("Monitoring Configuration", "PASSED", "Configuration available")
                    return True
                else:
                    self.log_test("Monitoring Configuration", "FAILED", "Configuration incomplete")
                    return False
            else:
                self.log_test("Monitoring Configuration", "FAILED", f"Config API failed: {config_response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Monitoring Configuration", "FAILED", error=str(e))
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
            recommendations.append("일부 모니터링 테스트가 실패했습니다. 실패한 테스트를 확인하고 수정하세요.")
        
        if summary["success_rate"] < 80:
            recommendations.append("모니터링 시스템 성공률이 낮습니다. 시스템 안정성을 개선하세요.")
        
        if not recommendations:
            recommendations.append("모든 모니터링 테스트가 통과했습니다. 시스템이 정상적으로 작동합니다.")
        
        return recommendations
    
    def save_results(self, filename="plugin-monitoring-deployment-test-results.json"):
        """결과를 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)
        
        report = self.generate_report()
        with open("plugin-monitoring-deployment-test-report.json", 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("=== 플러그인 모니터링 배포 테스트 시작 ===")
        
        # API 엔드포인트 테스트
        self.test_monitoring_api_endpoints()
        
        # 모니터링 기능 테스트
        self.test_monitoring_start_stop()
        self.test_real_time_monitoring()
        self.test_alert_system()
        self.test_performance_dashboard()
        
        # 플러그인 관리 기능 테스트
        self.test_plugin_restart_functionality()
        self.test_backup_restore_system()
        
        # 통합 테스트
        self.test_frontend_integration()
        self.test_monitoring_configuration()
        
        # 결과 저장
        self.save_results()
        
        # 리포트 출력
        report = self.generate_report()
        print("\n=== 플러그인 모니터링 배포 테스트 결과 ===")
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
    tester = PluginMonitoringDeploymentTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ 플러그인 모니터링 배포 테스트가 성공적으로 완료되었습니다!")
        sys.exit(0)
    else:
        print("\n❌ 플러그인 모니터링 배포 테스트에서 문제가 발견되었습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main() 