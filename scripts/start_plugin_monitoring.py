#!/usr/bin/env python3
"""
플러그인 모니터링 시스템 시작 스크립트
Docker 컨테이너에서 플러그인 모니터링을 백그라운드로 시작합니다.
"""

import os
import sys
import time
import signal
import threading
import requests
from datetime import datetime

class PluginMonitoringStarter:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.monitoring_enabled = os.getenv("PLUGIN_MONITORING_ENABLED", "true").lower() == "true"
        self.backup_enabled = os.getenv("PLUGIN_BACKUP_ENABLED", "true").lower() == "true"
        self.alert_enabled = os.getenv("PLUGIN_ALERT_ENABLED", "true").lower() == "true"
        self.running = True
        
        # 시그널 핸들러 설정
        signal.signal(signal.SIGTERM, self.signal_handler)
        signal.signal(signal.SIGINT, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """시그널 핸들러"""
        print(f"Received signal {signum}, shutting down plugin monitoring...")
        self.running = False
    
    def wait_for_application(self, max_wait=60):
        """애플리케이션 시작 대기"""
        print("Waiting for main application to start...")
        
        for i in range(max_wait):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print("Main application is ready!")
                    return True
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(1)
            if i % 10 == 0:
                print(f"Still waiting... ({i}/{max_wait})")
        
        print("Warning: Main application may not be ready")
        return False
    
    def start_plugin_monitoring(self):
        """플러그인 모니터링 시작"""
        if not self.monitoring_enabled:
            print("Plugin monitoring is disabled")
            return
        
        try:
            print("Starting plugin monitoring...")
            response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/start", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("status") == "started":
                    print("✅ Plugin monitoring started successfully")
                else:
                    print(f"⚠️  Plugin monitoring start response: {result}")
            else:
                print(f"❌ Failed to start plugin monitoring: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error starting plugin monitoring: {e}")
    
    def start_automatic_backup(self):
        """자동 백업 시작"""
        if not self.backup_enabled:
            print("Automatic backup is disabled")
            return
        
        def backup_worker():
            while self.running:
                try:
                    time.sleep(3600)  # 1시간마다 백업
                    if not self.running:
                        break
                    
                    print("Running automatic plugin backup...")
                    response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/backup", timeout=60)
                    
                    if response.status_code == 200:
                        result = response.json()
                        if result.get("status") == "success":
                            print("✅ Automatic backup completed")
                        else:
                            print(f"⚠️  Automatic backup failed: {result}")
                    else:
                        print(f"❌ Automatic backup API failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"❌ Error in automatic backup: {e}")
        
        backup_thread = threading.Thread(target=backup_worker, daemon=True)
        backup_thread.start()
        print("✅ Automatic backup worker started")
    
    def start_performance_monitoring(self):
        """성능 모니터링 시작"""
        def performance_worker():
            while self.running:
                try:
                    time.sleep(300)  # 5분마다 성능 체크
                    if not self.running:
                        break
                    
                    # 성능 메트릭 수집
                    response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/metrics", timeout=10)
                    
                    if response.status_code == 200:
                        metrics = response.json()
                        plugins = metrics.get("plugins", [])
                        
                        # 성능 임계값 체크
                        for plugin in plugins:
                            plugin_name = plugin.get("name", "Unknown")
                            cpu_usage = plugin.get("cpu_usage", 0)
                            memory_usage = plugin.get("memory_usage", 0)
                            
                            if cpu_usage > 80 or memory_usage > 85:
                                print(f"⚠️  High resource usage detected for plugin '{plugin_name}': CPU={cpu_usage}%, Memory={memory_usage}%")
                    
                except Exception as e:
                    print(f"❌ Error in performance monitoring: {e}")
        
        performance_thread = threading.Thread(target=performance_worker, daemon=True)
        performance_thread.start()
        print("✅ Performance monitoring worker started")
    
    def start_health_check(self):
        """헬스 체크 시작"""
        def health_worker():
            while self.running:
                try:
                    time.sleep(60)  # 1분마다 헬스 체크
                    if not self.running:
                        break
                    
                    response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/health", timeout=10)
                    
                    if response.status_code != 200:
                        print(f"⚠️  Plugin monitoring health check failed: {response.status_code}")
                    
                except Exception as e:
                    print(f"❌ Error in health check: {e}")
        
        health_thread = threading.Thread(target=health_worker, daemon=True)
        health_thread.start()
        print("✅ Health check worker started")
    
    def start_alert_monitoring(self):
        """알림 모니터링 시작"""
        if not self.alert_enabled:
            print("Alert monitoring is disabled")
            return
        
        def alert_worker():
            while self.running:
                try:
                    time.sleep(30)  # 30초마다 알림 체크
                    if not self.running:
                        break
                    
                    response = requests.get(f"{self.base_url}/api/admin/plugin-monitoring/alerts", timeout=10)
                    
                    if response.status_code == 200:
                        alerts = response.json()
                        critical_alerts = [a for a in alerts.get("alerts", []) if a.get("level") == "critical"]
                        warning_alerts = [a for a in alerts.get("alerts", []) if a.get("level") == "warning"]
                        
                        if critical_alerts:
                            print(f"🚨 Critical alerts detected: {len(critical_alerts)}")
                            for alert in critical_alerts:
                                print(f"  - {alert.get('message', 'Unknown alert')}")
                        
                        if warning_alerts:
                            print(f"⚠️  Warning alerts detected: {len(warning_alerts)}")
                    
                except Exception as e:
                    print(f"❌ Error in alert monitoring: {e}")
        
        alert_thread = threading.Thread(target=alert_worker, daemon=True)
        alert_thread.start()
        print("✅ Alert monitoring worker started")
    
    def run(self):
        """메인 실행 함수"""
        print("="*60)
        print("Plugin Monitoring System Starter")
        print("="*60)
        print(f"Monitoring enabled: {self.monitoring_enabled}")
        print(f"Backup enabled: {self.backup_enabled}")
        print(f"Alert enabled: {self.alert_enabled}")
        print("="*60)
        
        # 애플리케이션 시작 대기
        if not self.wait_for_application():
            print("Warning: Proceeding without confirming application readiness")
        
        # 플러그인 모니터링 시작
        self.start_plugin_monitoring()
        
        # 백그라운드 워커들 시작
        self.start_automatic_backup()
        self.start_performance_monitoring()
        self.start_health_check()
        self.start_alert_monitoring()
        
        print("✅ All plugin monitoring workers started")
        print("Plugin monitoring system is running in background...")
        
        # 메인 루프
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived keyboard interrupt, shutting down...")
        
        # 정리
        self.cleanup()
    
    def cleanup(self):
        """정리 작업"""
        print("Cleaning up plugin monitoring...")
        
        try:
            # 플러그인 모니터링 중지
            response = requests.post(f"{self.base_url}/api/admin/plugin-monitoring/stop", timeout=10)
            if response.status_code == 200:
                print("✅ Plugin monitoring stopped successfully")
            else:
                print(f"⚠️  Failed to stop plugin monitoring: {response.status_code}")
        except Exception as e:
            print(f"❌ Error stopping plugin monitoring: {e}")
        
        print("Plugin monitoring system shutdown complete")

def main():
    """메인 함수"""
    starter = PluginMonitoringStarter()
    starter.run()

if __name__ == "__main__":
    main() 