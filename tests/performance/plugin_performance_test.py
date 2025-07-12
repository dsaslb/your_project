# 성능 테스트를 위한 Locust 라이브러리
# 설치 필요: pip install locust
from locust import HttpUser, task, between  # type: ignore
import random

class PluginPerformanceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """사용자 시작 시 로그인"""
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = self.client.post("/login", json=login_data)
        if response.status_code == 200:
            self.client.headers.update({"Authorization": f"Bearer {response.json().get('token', '')}"})
    
    @task(3)
    def test_plugin_monitoring_dashboard(self):
        """플러그인 모니터링 대시보드 접근 테스트"""
        self.client.get("/api/admin/plugin-monitoring/dashboard")
    
    @task(2)
    def test_plugin_status_api(self):
        """플러그인 상태 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/status")
    
    @task(2)
    def test_plugin_metrics_api(self):
        """플러그인 메트릭 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/metrics")
    
    @task(1)
    def test_plugin_performance_api(self):
        """플러그인 성능 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/performance")
    
    @task(1)
    def test_plugin_alerts_api(self):
        """플러그인 알림 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/alerts")
    
    @task(1)
    def test_start_monitoring(self):
        """모니터링 시작 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/start")
    
    @task(1)
    def test_stop_monitoring(self):
        """모니터링 중지 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/stop")
    
    @task(1)
    def test_plugin_restart(self):
        """플러그인 재시작 API 테스트"""
        plugin_name = random.choice(["your_program_management", "analytics", "automation"])
        self.client.post(f"/api/admin/plugin-monitoring/restart/{plugin_name}")
    
    @task(1)
    def test_plugin_health_check(self):
        """플러그인 헬스체크 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/health")
    
    @task(1)
    def test_plugin_logs(self):
        """플러그인 로그 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/logs")
    
    @task(1)
    def test_plugin_backup(self):
        """플러그인 백업 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/backup")
    
    @task(1)
    def test_plugin_restore(self):
        """플러그인 복원 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/restore")
    
    @task(1)
    def test_plugin_update(self):
        """플러그인 업데이트 API 테스트"""
        plugin_name = random.choice(["your_program_management", "analytics", "automation"])
        self.client.post(f"/api/admin/plugin-monitoring/update/{plugin_name}")
    
    @task(1)
    def test_plugin_install(self):
        """플러그인 설치 API 테스트"""
        plugin_data = {
            "name": "test_plugin",
            "version": "1.0.0",
            "description": "Test plugin for performance testing"
        }
        self.client.post("/api/admin/plugin-monitoring/install", json=plugin_data)
    
    @task(1)
    def test_plugin_uninstall(self):
        """플러그인 제거 API 테스트"""
        plugin_name = random.choice(["test_plugin", "temp_plugin"])
        self.client.delete(f"/api/admin/plugin-monitoring/uninstall/{plugin_name}")
    
    @task(1)
    def test_plugin_configuration(self):
        """플러그인 설정 API 테스트"""
        config_data = {
            "monitoring_enabled": True,
            "alert_thresholds": {
                "cpu": 80,
                "memory": 85,
                "response_time": 2000
            }
        }
        self.client.put("/api/admin/plugin-monitoring/config", json=config_data)
    
    @task(1)
    def test_plugin_dependencies(self):
        """플러그인 의존성 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/dependencies")
    
    @task(1)
    def test_plugin_events(self):
        """플러그인 이벤트 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/events")
    
    @task(1)
    def test_plugin_statistics(self):
        """플러그인 통계 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/statistics")
    
    @task(1)
    def test_plugin_optimization(self):
        """플러그인 최적화 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/optimize")
    
    @task(1)
    def test_plugin_diagnostics(self):
        """플러그인 진단 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/diagnostics")
    
    @task(1)
    def test_plugin_maintenance(self):
        """플러그인 유지보수 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/maintenance")
    
    @task(1)
    def test_plugin_cleanup(self):
        """플러그인 정리 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/cleanup")
    
    @task(1)
    def test_plugin_validation(self):
        """플러그인 검증 API 테스트"""
        self.client.post("/api/admin/plugin-monitoring/validate")
    
    @task(1)
    def test_plugin_export(self):
        """플러그인 내보내기 API 테스트"""
        self.client.get("/api/admin/plugin-monitoring/export")
    
    @task(1)
    def test_plugin_import(self):
        """플러그인 가져오기 API 테스트"""
        import_data = {
            "plugin_data": "base64_encoded_plugin_data",
            "overwrite": False
        }
        self.client.post("/api/admin/plugin-monitoring/import", json=import_data) 
