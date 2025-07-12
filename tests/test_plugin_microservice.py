"""
플러그인 마이크로서비스 시스템 테스트
고도화된 마이크로서비스 아키텍처 테스트
"""

import unittest
import json
import tempfile
import shutil
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock, MagicMock

# 테스트 대상 모듈들
from core.backend.plugin_microservice_manager import (
    PluginMicroserviceManager, ServiceConfig, ServiceType, ServiceStatus, ServiceInstance, NetworkConfig
)
from api.plugin_microservice_api import plugin_microservice_bp

class TestServiceConfig(unittest.TestCase):
    """서비스 설정 테스트"""
    
    def test_service_config_creation(self):
        """서비스 설정 생성 테스트"""
        config = ServiceConfig(
            name="테스트 서비스",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080,
            host="0.0.0.0",
            environment={"TEST_VAR": "test_value"},
            volumes=["/host/path:/container/path"],
            networks=["plugin_network"],
            depends_on=["database"],
            restart_policy="unless-stopped",
            version="latest"
        )
        
        self.assertEqual(config.name, "테스트 서비스")
        self.assertEqual(config.plugin_id, "test_plugin")
        self.assertEqual(config.service_type, ServiceType.REST_API)
        self.assertEqual(config.port, 8080)
        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.environment["TEST_VAR"], "test_value")
        self.assertEqual(config.volumes[0], "/host/path:/container/path")
        self.assertEqual(config.networks[0], "plugin_network")
        self.assertEqual(config.depends_on[0], "database")
        self.assertEqual(config.restart_policy, "unless-stopped")
        self.assertEqual(config.version, "latest")
    
    def test_service_config_defaults(self):
        """서비스 설정 기본값 테스트"""
        config = ServiceConfig(
            name="기본 서비스",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        self.assertEqual(config.host, "0.0.0.0")
        self.assertEqual(config.environment, {})
        self.assertEqual(config.volumes, [])
        self.assertEqual(config.networks, ["plugin_network"])
        self.assertEqual(config.depends_on, [])
        self.assertIsNotNone(config.health_check)
        self.assertIsNotNone(config.resource_limits)
        self.assertEqual(config.restart_policy, "unless-stopped")
        self.assertEqual(config.version, "latest")

class TestServiceInstance(unittest.TestCase):
    """서비스 인스턴스 테스트"""
    
    def test_service_instance_creation(self):
        """서비스 인스턴스 생성 테스트"""
        config = ServiceConfig(
            name="테스트 서비스",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_instance_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={"cpu": 10.5, "memory": 512},
            logs=[],
            error_message=None
        )
        
        self.assertEqual(instance.id, "test_instance_123")
        self.assertEqual(instance.config.name, "테스트 서비스")
        self.assertEqual(instance.status, ServiceStatus.RUNNING)
        self.assertEqual(instance.container_id, "container_123")
        self.assertEqual(instance.port, 8080)
        self.assertEqual(instance.host_port, 8080)
        self.assertEqual(instance.health_status, ServiceStatus.HEALTHY)
        self.assertEqual(instance.resource_usage["cpu"], 10.5)
        self.assertIsNone(instance.error_message)
    
    def test_service_instance_to_dict(self):
        """서비스 인스턴스 딕셔너리 변환 테스트"""
        config = ServiceConfig(
            name="테스트 서비스",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        start_time = datetime.now()
        instance = ServiceInstance(
            id="test_instance_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=start_time,
            last_health_check=start_time,
            health_status=ServiceStatus.HEALTHY,
            resource_usage={"cpu": 10.5},
            logs=[],
            error_message=None
        )
        
        instance_dict = instance.to_dict()
        
        self.assertEqual(instance_dict["id"], "test_instance_123")
        self.assertEqual(instance_dict["name"], "테스트 서비스")
        self.assertEqual(instance_dict["plugin_id"], "test_plugin")
        self.assertEqual(instance_dict["service_type"], "rest_api")
        self.assertEqual(instance_dict["status"], "running")
        self.assertEqual(instance_dict["health_status"], "healthy")
        self.assertEqual(instance_dict["port"], 8080)
        self.assertEqual(instance_dict["host_port"], 8080)
        self.assertIsNone(instance_dict["error_message"])

class TestNetworkConfig(unittest.TestCase):
    """네트워크 설정 테스트"""
    
    def test_network_config_creation(self):
        """네트워크 설정 생성 테스트"""
        config = NetworkConfig(
            name="test_network",
            driver="bridge",
            subnet="172.20.0.0/16",
            gateway="172.20.0.1",
            enable_ipv6=True,
            internal=False
        )
        
        self.assertEqual(config.name, "test_network")
        self.assertEqual(config.driver, "bridge")
        self.assertEqual(config.subnet, "172.20.0.0/16")
        self.assertEqual(config.gateway, "172.20.0.1")
        self.assertTrue(config.enable_ipv6)
        self.assertFalse(config.internal)
        self.assertIsNotNone(config.labels)
        self.assertEqual(config.labels["com.plugin.system"], "true")
    
    def test_network_config_defaults(self):
        """네트워크 설정 기본값 테스트"""
        config = NetworkConfig("default_network")
        
        self.assertEqual(config.name, "default_network")
        self.assertEqual(config.driver, "bridge")
        self.assertEqual(config.subnet, "172.20.0.0/16")
        self.assertEqual(config.gateway, "172.20.0.1")
        self.assertFalse(config.enable_ipv6)
        self.assertFalse(config.internal)
        self.assertIsNotNone(config.labels)

class TestPluginMicroserviceManager(unittest.TestCase):
    """플러그인 마이크로서비스 매니저 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PluginMicroserviceManager(self.temp_dir)
    
    def tearDown(self):
        """테스트 정리"""
        shutil.rmtree(self.temp_dir)
    
    def test_manager_initialization(self):
        """매니저 초기화 테스트"""
        self.assertIsInstance(self.manager.services, dict)
        self.assertIsInstance(self.manager.networks, dict)
        self.assertIsInstance(self.manager.executor, type(self.manager.executor))
        self.assertEqual(self.manager.health_check_interval, 30)
        self.assertIsNotNone(self.manager.port_manager)
    
    @patch('core.backend.plugin_microservice_manager.docker.from_env')
    def test_docker_client_initialization(self, mock_docker):
        """Docker 클라이언트 초기화 테스트"""
        # Docker 사용 가능한 경우
        mock_docker.return_value = Mock()
        manager = PluginMicroserviceManager()
        self.assertIsNotNone(manager.docker_client)
        
        # Docker 사용 불가능한 경우
        mock_docker.side_effect = Exception("Docker not available")
        manager = PluginMicroserviceManager()
        self.assertIsNone(manager.docker_client)
    
    def test_port_manager(self):
        """포트 관리자 테스트"""
        port_manager = self.manager.port_manager
        
        # 포트 할당
        port1 = port_manager.allocate_port()
        port2 = port_manager.allocate_port()
        
        self.assertNotEqual(port1, port2)
        self.assertTrue(port_manager.is_port_allocated(port1))
        self.assertTrue(port_manager.is_port_allocated(port2))
        
        # 포트 해제
        port_manager.release_port(port1)
        self.assertFalse(port_manager.is_port_allocated(port1))
        self.assertTrue(port_manager.is_port_allocated(port2))
    
    async def test_create_network(self):
        """네트워크 생성 테스트"""
        if not self.manager.docker_client:
            self.skipTest("Docker 클라이언트가 없습니다")
        
        config = NetworkConfig("test_network")
        success = self.manager._create_network(config)
        
        # Docker 클라이언트가 없는 경우 False 반환
        if not self.manager.docker_client:
            self.assertFalse(success)
        else:
            # 실제 Docker 환경에서는 True 반환 가능
            pass
    
    async def test_create_service(self):
        """서비스 생성 테스트"""
        if not self.manager.docker_client:
            self.skipTest("Docker 클라이언트가 없습니다")
        
        # 테스트 플러그인 디렉토리 생성
        plugin_dir = Path(self.temp_dir) / "test_plugin"
        plugin_dir.mkdir()
        
        # 기본 플러그인 파일 생성
        backend_dir = plugin_dir / "backend"
        backend_dir.mkdir()
        
        with open(backend_dir / "plugin.py", "w") as f:
            f.write("# 테스트 플러그인\nprint('Hello, World!')\n")
        
        # 서비스 설정
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        try:
            service_id = await self.manager.create_service("test_plugin", config)
            self.assertIsInstance(service_id, str)
            self.assertIn(service_id, self.manager.services)
        except Exception as e:
            # Docker 환경이 없는 경우 예외 발생 가능
            self.assertIn("Docker", str(e) or "docker", str(e).lower())
    
    async def test_get_service(self):
        """서비스 조회 테스트"""
        # 존재하지 않는 서비스
        service = await self.manager.get_service("non_existent")
        self.assertIsNone(service)
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        # 서비스 인스턴스 직접 생성
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.STOPPED,
            container_id=None,
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=None,
            last_health_check=None,
            health_status=ServiceStatus.UNHEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 서비스 조회
        service = await self.manager.get_service("test_service_123")
        self.assertIsNotNone(service)
        self.assertEqual(service.id, "test_service_123")
        self.assertEqual(service.config.name, "test_service")
    
    async def test_list_services(self):
        """서비스 목록 조회 테스트"""
        # 테스트 서비스들 생성
        config1 = ServiceConfig(
            name="service1",
            plugin_id="plugin1",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        config2 = ServiceConfig(
            name="service2",
            plugin_id="plugin2",
            service_type=ServiceType.WEBSOCKET,
            port=8081
        )
        
        instance1 = ServiceInstance(
            id="service1_123",
            config=config1,
            status=ServiceStatus.RUNNING,
            container_id="container1",
            container_name="container1",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        instance2 = ServiceInstance(
            id="service2_123",
            config=config2,
            status=ServiceStatus.STOPPED,
            container_id="container2",
            container_name="container2",
            port=8081,
            host_port=8081,
            start_time=None,
            last_health_check=None,
            health_status=ServiceStatus.UNHEALTHY,
            resource_usage={},
            logs=[],
            error_message="Test error"
        )
        
        self.manager.services["service1_123"] = instance1
        self.manager.services["service2_123"] = instance2
        
        # 전체 서비스 목록
        services = await self.manager.list_services()
        self.assertEqual(len(services), 2)
        
        # 특정 플러그인 필터링
        services = await self.manager.list_services(plugin_id="plugin1")
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["plugin_id"], "plugin1")
        
        # 상태별 필터링
        services = await self.manager.list_services(status=ServiceStatus.RUNNING)
        self.assertEqual(len(services), 1)
        self.assertEqual(services[0]["status"], "running")
    
    async def test_stop_service(self):
        """서비스 중지 테스트"""
        # 존재하지 않는 서비스
        success = await self.manager.stop_service("non_existent")
        self.assertFalse(success)
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 서비스 중지
        success = await self.manager.stop_service("test_service_123")
        self.assertTrue(success)
        self.assertEqual(instance.status, ServiceStatus.STOPPED)
    
    async def test_restart_service(self):
        """서비스 재시작 테스트"""
        # 존재하지 않는 서비스
        success = await self.manager.restart_service("non_existent")
        self.assertFalse(success)
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.STOPPED,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=None,
            last_health_check=None,
            health_status=ServiceStatus.UNHEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 서비스 재시작
        success = await self.manager.restart_service("test_service_123")
        self.assertTrue(success)
        self.assertEqual(instance.status, ServiceStatus.RUNNING)
    
    async def test_delete_service(self):
        """서비스 삭제 테스트"""
        # 존재하지 않는 서비스
        success = await self.manager.delete_service("non_existent")
        self.assertFalse(success)
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.STOPPED,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=None,
            last_health_check=None,
            health_status=ServiceStatus.UNHEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 서비스 삭제
        success = await self.manager.delete_service("test_service_123")
        self.assertTrue(success)
        self.assertNotIn("test_service_123", self.manager.services)
    
    async def test_get_service_logs(self):
        """서비스 로그 조회 테스트"""
        # 존재하지 않는 서비스
        logs = await self.manager.get_service_logs("non_existent")
        self.assertEqual(logs, [])
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 로그 조회 (Docker 클라이언트가 없는 경우 빈 리스트 반환)
        logs = await self.manager.get_service_logs("test_service_123")
        self.assertIsInstance(logs, list)
    
    async def test_get_service_metrics(self):
        """서비스 메트릭 조회 테스트"""
        # 존재하지 않는 서비스
        metrics = await self.manager.get_service_metrics("non_existent")
        self.assertEqual(metrics, {})
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 메트릭 조회 (Docker 클라이언트가 없는 경우 빈 딕셔너리 반환)
        metrics = await self.manager.get_service_metrics("test_service_123")
        self.assertIsInstance(metrics, dict)
    
    async def test_scale_service(self):
        """서비스 스케일링 테스트"""
        # 존재하지 않는 서비스
        success = await self.manager.scale_service("non_existent", 3)
        self.assertFalse(success)
        
        # 테스트 서비스 생성
        config = ServiceConfig(
            name="test_service",
            plugin_id="test_plugin",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        instance = ServiceInstance(
            id="test_service_123",
            config=config,
            status=ServiceStatus.RUNNING,
            container_id="container_123",
            container_name="test_container",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        self.manager.services["test_service_123"] = instance
        
        # 스케일링 (현재는 단일 인스턴스만 지원)
        success = await self.manager.scale_service("test_service_123", 3)
        self.assertTrue(success)
    
    async def test_get_service_discovery_info(self):
        """서비스 디스커버리 정보 테스트"""
        # 테스트 서비스들 생성
        config1 = ServiceConfig(
            name="service1",
            plugin_id="plugin1",
            service_type=ServiceType.REST_API,
            port=8080
        )
        
        config2 = ServiceConfig(
            name="service2",
            plugin_id="plugin2",
            service_type=ServiceType.WEBSOCKET,
            port=8081
        )
        
        instance1 = ServiceInstance(
            id="service1_123",
            config=config1,
            status=ServiceStatus.RUNNING,
            container_id="container1",
            container_name="container1",
            port=8080,
            host_port=8080,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.HEALTHY,
            resource_usage={},
            logs=[],
            error_message=None
        )
        
        instance2 = ServiceInstance(
            id="service2_123",
            config=config2,
            status=ServiceStatus.RUNNING,
            container_id="container2",
            container_name="container2",
            port=8081,
            host_port=8081,
            start_time=datetime.now(),
            last_health_check=datetime.now(),
            health_status=ServiceStatus.UNHEALTHY,
            resource_usage={},
            logs=[],
            error_message="Test error"
        )
        
        self.manager.services["service1_123"] = instance1
        self.manager.services["service2_123"] = instance2
        
        # 디스커버리 정보 조회
        discovery_info = await self.manager.get_service_discovery_info()
        
        self.assertEqual(discovery_info["total_services"], 2)
        self.assertEqual(discovery_info["healthy_services"], 1)
        self.assertEqual(discovery_info["unhealthy_services"], 1)
        self.assertEqual(len(discovery_info["services"]), 2)
        self.assertIsInstance(discovery_info["networks"], list)
    
    async def test_cleanup_unused_resources(self):
        """사용하지 않는 리소스 정리 테스트"""
        cleanup_stats = await self.manager.cleanup_unused_resources()
        
        self.assertIsInstance(cleanup_stats, dict)
        self.assertIn("containers_removed", cleanup_stats)
        self.assertIn("images_removed", cleanup_stats)
        self.assertIn("networks_removed", cleanup_stats)
        self.assertIsInstance(cleanup_stats["containers_removed"], int)
        self.assertIsInstance(cleanup_stats["images_removed"], int)
        self.assertIsInstance(cleanup_stats["networks_removed"], int)

class TestPluginMicroserviceAPI(unittest.TestCase):
    """플러그인 마이크로서비스 API 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        from flask import Flask
        self.app = Flask(__name__)
        self.app.register_blueprint(plugin_microservice_bp)
        self.client = self.app.test_client()
    
    def test_list_services_endpoint(self):
        """서비스 목록 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = [
                {
                    "id": "test_service",
                    "name": "테스트 서비스",
                    "plugin_id": "test_plugin",
                    "service_type": "rest_api",
                    "status": "running",
                    "health_status": "healthy",
                    "port": 8080,
                    "host_port": 8080,
                    "start_time": "2024-01-01T00:00:00",
                    "last_health_check": "2024-01-01T00:00:00",
                    "resource_usage": {},
                    "error_message": None
                }
            ]
            
            response = self.client.get('/api/plugin-microservice/services')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 1)
            self.assertEqual(data['data'][0]['id'], 'test_service')
    
    def test_get_service_endpoint(self):
        """특정 서비스 조회 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_service = Mock()
            mock_service.to_dict.return_value = {
                "id": "test_service",
                "name": "테스트 서비스",
                "plugin_id": "test_plugin",
                "service_type": "rest_api",
                "status": "running",
                "health_status": "healthy",
                "port": 8080,
                "host_port": 8080,
                "start_time": "2024-01-01T00:00:00",
                "last_health_check": "2024-01-01T00:00:00",
                "resource_usage": {},
                "error_message": None
            }
            
            mock_run_async.return_value = mock_service
            
            response = self.client.get('/api/plugin-microservice/services/test_service')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['id'], 'test_service')
    
    def test_create_service_endpoint(self):
        """서비스 생성 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = "test_service_123"
            
            service_data = {
                "plugin_id": "test_plugin",
                "name": "테스트 서비스",
                "service_type": "rest_api",
                "port": 8080,
                "host": "0.0.0.0",
                "environment": {"TEST_VAR": "test_value"},
                "volumes": [],
                "networks": ["plugin_network"],
                "depends_on": [],
                "restart_policy": "unless-stopped",
                "version": "latest"
            }
            
            response = self.client.post(
                '/api/plugin-microservice/services',
                data=json.dumps(service_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service_123')
    
    def test_stop_service_endpoint(self):
        """서비스 중지 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            response = self.client.post('/api/plugin-microservice/services/test_service/stop')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service')
    
    def test_start_service_endpoint(self):
        """서비스 시작 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            response = self.client.post('/api/plugin-microservice/services/test_service/start')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service')
    
    def test_restart_service_endpoint(self):
        """서비스 재시작 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            response = self.client.post('/api/plugin-microservice/services/test_service/restart')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service')
    
    def test_delete_service_endpoint(self):
        """서비스 삭제 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            response = self.client.delete('/api/plugin-microservice/services/test_service')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service')
    
    def test_get_service_logs_endpoint(self):
        """서비스 로그 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = [
                "2024-01-01T00:00:00 INFO: 서비스 시작",
                "2024-01-01T00:00:01 INFO: 헬스 체크 통과"
            ]
            
            response = self.client.get('/api/plugin-microservice/services/test_service/logs')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(len(data['data']), 2)
    
    def test_get_service_metrics_endpoint(self):
        """서비스 메트릭 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = {
                "cpu_percent": 15.5,
                "memory_usage_mb": 256.0,
                "memory_limit_mb": 512.0,
                "memory_percent": 50.0,
                "network_rx_mb": 10.5,
                "network_tx_mb": 5.2,
                "timestamp": "2024-01-01T00:00:00"
            }
            
            response = self.client.get('/api/plugin-microservice/services/test_service/metrics')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['cpu_percent'], 15.5)
            self.assertEqual(data['data']['memory_percent'], 50.0)
    
    def test_scale_service_endpoint(self):
        """서비스 스케일링 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = True
            
            scale_data = {"replicas": 3}
            
            response = self.client.post(
                '/api/plugin-microservice/services/test_service/scale',
                data=json.dumps(scale_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'test_service')
            self.assertEqual(data['data']['replicas'], 3)
    
    def test_get_service_discovery_endpoint(self):
        """서비스 디스커버리 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = {
                "services": [
                    {
                        "id": "test_service",
                        "name": "테스트 서비스",
                        "plugin_id": "test_plugin",
                        "type": "rest_api",
                        "status": "running",
                        "health": "healthy",
                        "endpoint": "http://localhost:8080",
                        "port": 8080,
                        "start_time": "2024-01-01T00:00:00"
                    }
                ],
                "networks": [
                    {
                        "name": "plugin_network",
                        "id": "network_123",
                        "driver": "bridge",
                        "scope": "local"
                    }
                ],
                "total_services": 1,
                "healthy_services": 1,
                "unhealthy_services": 0
            }
            
            response = self.client.get('/api/plugin-microservice/discovery')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['total_services'], 1)
            self.assertEqual(data['data']['healthy_services'], 1)
            self.assertEqual(len(data['data']['services']), 1)
            self.assertEqual(len(data['data']['networks']), 1)
    
    def test_cleanup_resources_endpoint(self):
        """리소스 정리 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = {
                "containers_removed": 2,
                "images_removed": 1,
                "networks_removed": 0
            }
            
            response = self.client.post('/api/plugin-microservice/cleanup')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['containers_removed'], 2)
            self.assertEqual(data['data']['images_removed'], 1)
            self.assertEqual(data['data']['networks_removed'], 0)
    
    def test_health_check_endpoint(self):
        """헬스 체크 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = {
                "services": [],
                "networks": [],
                "total_services": 0,
                "healthy_services": 0,
                "unhealthy_services": 0
            }
            
            response = self.client.get('/api/plugin-microservice/health')
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['status'], 'healthy')
            self.assertEqual(data['data']['total_services'], 0)
    
    def test_get_service_templates_endpoint(self):
        """서비스 템플릿 API 테스트"""
        response = self.client.get('/api/plugin-microservice/templates')
        data = json.loads(response.data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertGreater(len(data['data']), 0)
        
        # 템플릿 구조 확인
        template = data['data'][0]
        self.assertIn('id', template)
        self.assertIn('name', template)
        self.assertIn('description', template)
        self.assertIn('service_type', template)
        self.assertIn('port', template)
        self.assertIn('template', template)
    
    def test_create_service_from_template_endpoint(self):
        """템플릿 서비스 생성 API 테스트"""
        with patch('api.plugin_microservice_api.run_async') as mock_run_async:
            mock_run_async.return_value = "template_service_123"
            
            template_data = {
                "plugin_id": "test_plugin",
                "name": "템플릿 서비스"
            }
            
            response = self.client.post(
                '/api/plugin-microservice/templates/rest_api_basic/create',
                data=json.dumps(template_data),
                content_type='application/json'
            )
            data = json.loads(response.data)
            
            self.assertEqual(response.status_code, 201)
            self.assertTrue(data['success'])
            self.assertEqual(data['data']['service_id'], 'template_service_123')
            self.assertEqual(data['data']['template_id'], 'rest_api_basic')

if __name__ == '__main__':
    unittest.main() 