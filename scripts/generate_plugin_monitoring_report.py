#!/usr/bin/env python3
"""
플러그인 모니터링 리포트 생성 스크립트
플러그인 성능 모니터링 시스템의 상태와 성능을 분석하여 리포트를 생성합니다.
"""

import os
import sys
import json
import time
import requests
import psutil
from pathlib import Path
from datetime import datetime, timedelta

class PluginMonitoringReportGenerator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "system_info": {},
            "plugin_status": {},
            "performance_metrics": {},
            "alerts": {},
            "recommendations": [],
            "summary": {}
        }
    
    def collect_system_info(self):
        """시스템 정보 수집"""
        try:
            # 시스템 리소스 정보
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            self.report["system_info"] = {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "memory_used_gb": memory.used / 1024 / 1024 / 1024,
                "memory_available_gb": memory.available / 1024 / 1024 / 1024,
                "disk_usage_percent": disk.percent,
                "disk_used_gb": disk.used / 1024 / 1024 / 1024,
                "disk_free_gb": disk.free / 1024 / 1024 / 1024,
                "timestamp": datetime.now().isoformat()
            }
            
            print("✅ 시스템 정보 수집 완료")
            return True
            
        except Exception as e:
            print(f"❌ 시스템 정보 수집 실패: {e}")
            return False
    
    def collect_plugin_status(self):
        """플러그인 상태 정보 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/status", timeout=10)
            
            if response.status_code == 200:
                status_data = response.json()
                self.report["plugin_status"] = {
                    "total_plugins": len(status_data.get("plugins", [])),
                    "active_plugins": len([p for p in status_data.get("plugins", []) if p.get("status") == "active"]),
                    "inactive_plugins": len([p for p in status_data.get("plugins", []) if p.get("status") == "inactive"]),
                    "error_plugins": len([p for p in status_data.get("plugins", []) if p.get("status") == "error"]),
                    "plugins": status_data.get("plugins", []),
                    "timestamp": datetime.now().isoformat()
                }
                
                print("✅ 플러그인 상태 정보 수집 완료")
                return True
            else:
                print(f"❌ 플러그인 상태 API 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 플러그인 상태 수집 실패: {e}")
            return False
    
    def collect_performance_metrics(self):
        """성능 메트릭 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics_data = response.json()
                self.report["performance_metrics"] = {
                    "plugins_metrics": metrics_data.get("plugins", []),
                    "system_metrics": metrics_data.get("system", {}),
                    "performance_trends": metrics_data.get("trends", {}),
                    "timestamp": datetime.now().isoformat()
                }
                
                print("✅ 성능 메트릭 수집 완료")
                return True
            else:
                print(f"❌ 성능 메트릭 API 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 성능 메트릭 수집 실패: {e}")
            return False
    
    def collect_alerts(self):
        """알림 정보 수집"""
        try:
            response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/alerts", timeout=10)
            
            if response.status_code == 200:
                alerts_data = response.json()
                self.report["alerts"] = {
                    "total_alerts": len(alerts_data.get("alerts", [])),
                    "critical_alerts": len([a for a in alerts_data.get("alerts", []) if a.get("level") == "critical"]),
                    "warning_alerts": len([a for a in alerts_data.get("alerts", []) if a.get("level") == "warning"]),
                    "info_alerts": len([a for a in alerts_data.get("alerts", []) if a.get("level") == "info"]),
                    "alerts": alerts_data.get("alerts", []),
                    "timestamp": datetime.now().isoformat()
                }
                
                print("✅ 알림 정보 수집 완료")
                return True
            else:
                print(f"❌ 알림 API 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 알림 정보 수집 실패: {e}")
            return False
    
    def analyze_performance(self):
        """성능 분석"""
        recommendations = []
        
        # CPU 사용량 분석
        cpu_usage = self.report["system_info"].get("cpu_usage_percent", 0)
        if cpu_usage > 80:
            recommendations.append("CPU 사용량이 높습니다 ({}%). 플러그인 최적화가 필요합니다.".format(cpu_usage))
        elif cpu_usage > 60:
            recommendations.append("CPU 사용량이 중간 수준입니다 ({}%). 모니터링을 지속하세요.".format(cpu_usage))
        
        # 메모리 사용량 분석
        memory_usage = self.report["system_info"].get("memory_usage_percent", 0)
        if memory_usage > 85:
            recommendations.append("메모리 사용량이 높습니다 ({}%). 메모리 누수 검사가 필요합니다.".format(memory_usage))
        elif memory_usage > 70:
            recommendations.append("메모리 사용량이 중간 수준입니다 ({}%). 모니터링을 지속하세요.".format(memory_usage))
        
        # 디스크 사용량 분석
        disk_usage = self.report["system_info"].get("disk_usage_percent", 0)
        if disk_usage > 90:
            recommendations.append("디스크 사용량이 높습니다 ({}%). 정리가 필요합니다.".format(disk_usage))
        elif disk_usage > 80:
            recommendations.append("디스크 사용량이 중간 수준입니다 ({}%). 모니터링을 지속하세요.".format(disk_usage))
        
        # 플러그인 상태 분석
        plugin_status = self.report["plugin_status"]
        error_plugins = plugin_status.get("error_plugins", 0)
        if error_plugins > 0:
            recommendations.append("오류 상태의 플러그인이 {}개 있습니다. 확인이 필요합니다.".format(error_plugins))
        
        inactive_plugins = plugin_status.get("inactive_plugins", 0)
        if inactive_plugins > 0:
            recommendations.append("비활성 플러그인이 {}개 있습니다. 활성화를 고려하세요.".format(inactive_plugins))
        
        # 알림 분석
        alerts = self.report["alerts"]
        critical_alerts = alerts.get("critical_alerts", 0)
        if critical_alerts > 0:
            recommendations.append("중요한 알림이 {}개 있습니다. 즉시 확인이 필요합니다.".format(critical_alerts))
        
        warning_alerts = alerts.get("warning_alerts", 0)
        if warning_alerts > 0:
            recommendations.append("경고 알림이 {}개 있습니다. 주의가 필요합니다.".format(warning_alerts))
        
        # 성능 메트릭 분석
        plugins_metrics = self.report["performance_metrics"].get("plugins_metrics", [])
        for plugin in plugins_metrics:
            plugin_name = plugin.get("name", "Unknown")
            
            # CPU 사용량 체크
            cpu_usage = plugin.get("cpu_usage", 0)
            if cpu_usage > 80:
                recommendations.append("플러그인 '{}'의 CPU 사용량이 높습니다 ({}%)".format(plugin_name, cpu_usage))
            
            # 메모리 사용량 체크
            memory_usage = plugin.get("memory_usage", 0)
            if memory_usage > 85:
                recommendations.append("플러그인 '{}'의 메모리 사용량이 높습니다 ({}%)".format(plugin_name, memory_usage))
            
            # 응답 시간 체크
            response_time = plugin.get("response_time", 0)
            if response_time > 2000:
                recommendations.append("플러그인 '{}'의 응답 시간이 느립니다 ({}ms)".format(plugin_name, response_time))
        
        if not recommendations:
            recommendations.append("시스템 성능이 양호합니다. 현재 상태를 유지하세요.")
        
        self.report["recommendations"] = recommendations
    
    def generate_summary(self):
        """요약 정보 생성"""
        system_info = self.report["system_info"]
        plugin_status = self.report["plugin_status"]
        alerts = self.report["alerts"]
        
        # 전체 상태 평가
        overall_status = "GOOD"
        if (system_info.get("cpu_usage_percent", 0) > 80 or 
            system_info.get("memory_usage_percent", 0) > 85 or
            plugin_status.get("error_plugins", 0) > 0 or
            alerts.get("critical_alerts", 0) > 0):
            overall_status = "CRITICAL"
        elif (system_info.get("cpu_usage_percent", 0) > 60 or 
              system_info.get("memory_usage_percent", 0) > 70 or
              alerts.get("warning_alerts", 0) > 0):
            overall_status = "WARNING"
        
        self.report["summary"] = {
            "overall_status": overall_status,
            "system_health": {
                "cpu_usage": system_info.get("cpu_usage_percent", 0),
                "memory_usage": system_info.get("memory_usage_percent", 0),
                "disk_usage": system_info.get("disk_usage_percent", 0)
            },
            "plugin_health": {
                "total_plugins": plugin_status.get("total_plugins", 0),
                "active_plugins": plugin_status.get("active_plugins", 0),
                "error_plugins": plugin_status.get("error_plugins", 0)
            },
            "alert_summary": {
                "total_alerts": alerts.get("total_alerts", 0),
                "critical_alerts": alerts.get("critical_alerts", 0),
                "warning_alerts": alerts.get("warning_alerts", 0)
            },
            "timestamp": datetime.now().isoformat()
        }
    
    def save_report(self, filename="plugin-monitoring-report.json"):
        """리포트를 파일로 저장"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.report, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 리포트가 {filename}에 저장되었습니다.")
            return True
            
        except Exception as e:
            print(f"❌ 리포트 저장 실패: {e}")
            return False
    
    def print_summary(self):
        """요약 정보 출력"""
        summary = self.report["summary"]
        
        print("\n" + "="*60)
        print("플러그인 모니터링 시스템 리포트")
        print("="*60)
        print(f"생성 시간: {self.report['timestamp']}")
        print(f"전체 상태: {summary['overall_status']}")
        
        print("\n시스템 상태:")
        system_health = summary["system_health"]
        print(f"  CPU 사용량: {system_health['cpu_usage']:.1f}%")
        print(f"  메모리 사용량: {system_health['memory_usage']:.1f}%")
        print(f"  디스크 사용량: {system_health['disk_usage']:.1f}%")
        
        print("\n플러그인 상태:")
        plugin_health = summary["plugin_health"]
        print(f"  총 플러그인: {plugin_health['total_plugins']}")
        print(f"  활성 플러그인: {plugin_health['active_plugins']}")
        print(f"  오류 플러그인: {plugin_health['error_plugins']}")
        
        print("\n알림 요약:")
        alert_summary = summary["alert_summary"]
        print(f"  총 알림: {alert_summary['total_alerts']}")
        print(f"  중요 알림: {alert_summary['critical_alerts']}")
        print(f"  경고 알림: {alert_summary['warning_alerts']}")
        
        print("\n권장사항:")
        for i, rec in enumerate(self.report["recommendations"], 1):
            print(f"  {i}. {rec}")
        
        print("="*60)
    
    def generate_all(self):
        """전체 리포트 생성"""
        print("플러그인 모니터링 리포트 생성 시작...")
        
        # 데이터 수집
        self.collect_system_info()
        self.collect_plugin_status()
        self.collect_performance_metrics()
        self.collect_alerts()
        
        # 분석 및 요약
        self.analyze_performance()
        self.generate_summary()
        
        # 저장 및 출력
        self.save_report()
        self.print_summary()
        
        return self.report

def main():
    """메인 함수"""
    generator = PluginMonitoringReportGenerator()
    report = generator.generate_all()
    
    if report["summary"]["overall_status"] == "CRITICAL":
        print("\n⚠️  시스템에 중요한 문제가 발견되었습니다. 즉시 확인하세요!")
        sys.exit(1)
    elif report["summary"]["overall_status"] == "WARNING":
        print("\n⚠️  시스템에 주의가 필요한 문제가 있습니다.")
        sys.exit(0)
    else:
        print("\n✅ 시스템이 정상적으로 작동하고 있습니다.")
        sys.exit(0)

if __name__ == "__main__":
    main() 