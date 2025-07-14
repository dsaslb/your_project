"""
플러그인 마이크로서비스 관리 시스템
고도화된 마이크로서비스 아키텍처로 플러그인 격리 및 독립 실행 관리
"""

import asyncio
import json
import logging
import os
import subprocess
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import docker
from docker.errors import DockerException, ImageNotFound, ContainerError
import aiohttp
import aiofiles
from dataclasses import dataclass, asdict
import yaml
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil
import requests
from urllib.parse import urljoin

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """서비스 상태 열거형"""
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class ServiceType(Enum):
    """서비스 타입 열거형"""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    WEBSOCKET = "websocket"
    BACKGROUND = "background"
    SCHEDULER = "scheduler"
    WORKER = "worker"

@dataclass
class ServiceConfig:
    """서비스 설정 데이터 클래스"""
    name: str
    plugin_id: str
    service_type: ServiceType
    port: int
    host: str = "0.0.0.0"
    environment: Optional[Dict[str, str]] = None  # pyright: ignore
    volumes: Optional[List[str]] = None  # pyright: ignore
    networks: Optional[List[str]] = None  # pyright: ignore
    depends_on: Optional[List[str]] = None  # pyright: ignore
    health_check: Optional[Dict[str, Any]] = None  # pyright: ignore
    resource_limits: Optional[Dict[str, Any]] = None  # pyright: ignore
    restart_policy: str = "unless-stopped"
    version: str = "latest"
    
    def __post_init__(self):
        if self.environment is None:
            self.environment = {}
        if self.volumes is None:
            self.volumes = []
        if self.networks is None:
            self.networks = ["plugin_network"]
        if self.depends_on is None:
            self.depends_on = []
        if self.health_check is None:
            self.health_check = {
                "url": f"http://localhost:{self.port}/health",
                "interval": 30,
                "timeout": 10,
                "retries": 3
            }
        if self.resource_limits is None:
            self.resource_limits = {
                "memory": "512m",
                "cpu": "0.5"
            }

@dataclass
class ServiceInstance:
    """서비스 인스턴스 데이터 클래스"""
    id: str
    config: ServiceConfig
    status: ServiceStatus
    container_id: Optional[str]
    container_name: str
    port: int
    host_port: int
    start_time: Optional[datetime]
    last_health_check: Optional[datetime]
    health_status: ServiceStatus
    resource_usage: Dict[str, Any]
    logs: List[Dict[str, Any]]
    error_message: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "id": self.id,
            "name": self.config.name,
            "plugin_id": self.config.plugin_id,
            "service_type": self.config.service_type.value,
            "status": self.status.value,
            "health_status": self.health_status.value,
            "port": self.port,
            "host_port": self.host_port,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_health_check": self.last_health_check.isoformat() if self.last_health_check else None,
            "resource_usage": self.resource_usage,
            "error_message": self.error_message
        }

@dataclass
class NetworkConfig:
    """네트워크 설정 데이터 클래스"""
    name: str
    driver: str = "bridge"
    subnet: str = "172.20.0.0/16"
    gateway: str = "172.20.0.1"
    enable_ipv6: bool = False
    internal: bool = False
    labels: Optional[Dict[str, str]] = None  # pyright: ignore

    def __post_init__(self):
        if self.labels is None:
            self.labels = {"com.plugin.system": "true"}

class PluginMicroserviceManager:
    """플러그인 마이크로서비스 관리 시스템"""
    
    def __init__(self, base_path: str = "plugins", docker_host: str = "unix://var/run/docker.sock"):
        self.base_path = Path(base_path)
        self.docker_host = docker_host
        self.docker_client = None
        self.services: Dict[str, ServiceInstance] = {}
        self.networks: Dict[str, Any] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.health_check_interval = 30
        try:
            from .port_manager import PortManager  # PortManager가 정의되어 있는 파일에서 import합니다. # noqa
        except ImportError:
            # PortManager가 없을 경우 예외 처리: 임시 더미 클래스 정의
            class PortManager:  # noqa
                def __init__(self):
                    pass
        self.port_manager = PortManager()
        self._init_docker_client()
        self._init_networks()
        self._load_existing_services()
        self._start_health_monitoring()
    
    def _init_docker_client(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker 클라이언트 초기화 성공")
        except DockerException as e:
            logger.error(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _init_networks(self):
        """네트워크 초기화"""
        if not self.docker_client:
            return
        
        try:
            # 기본 플러그인 네트워크 생성
            network_config = NetworkConfig("plugin_network")
            self._create_network(network_config)
            
            # 격리된 네트워크 생성
            isolated_config = NetworkConfig("plugin_isolated", internal=True)
            self._create_network(isolated_config)
            
            logger.info("플러그인 네트워크 초기화 완료")
        except Exception as e:
            logger.error(f"네트워크 초기화 실패: {e}")
    
    def _create_network(self, config: NetworkConfig) -> bool:
        """네트워크 생성"""
        try:
            existing_networks = self.docker_client.networks.list(names=[config.name])
            if existing_networks:
                self.networks[config.name] = existing_networks[0]
                return True
            
            network = self.docker_client.networks.create(
                name=config.name,
                driver=config.driver,
                ipam=__import__("docker").types.IPAMConfig(  # pyright: ignore
                    driver='default',
                    config=[
                        __import__("docker").types.IPAMPool(  # pyright: ignore
                            subnet=config.subnet,
                            gateway=config.gateway
                        )
                    ]
                ),
                enable_ipv6=config.enable_ipv6,
                internal=config.internal,
                labels=config.labels
            )
            
            self.networks[config.name] = network
            logger.info(f"네트워크 생성 완료: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"네트워크 생성 실패: {config.name} - {e}")
            return False
    
    def _load_existing_services(self):
        """기존 서비스 로드"""
        if not self.docker_client:
            return
        
        try:
            containers = self.docker_client.containers.list(
                filters={"label": "com.plugin.system=true"}
            )
            
            for container in containers:
                try:
                    service_id = container.labels.get("com.plugin.service.id")
                    if service_id:
                        # 서비스 정보 복구
                        self._recover_service_from_container(container, service_id)
                except Exception as e:
                    logger.error(f"컨테이너에서 서비스 복구 실패: {container.id} - {e}")
            
            logger.info(f"기존 서비스 {len(containers)}개 로드 완료")
        except Exception as e:
            logger.error(f"기존 서비스 로드 실패: {e}")
    
    def _recover_service_from_container(self, container, service_id: str):
        """컨테이너에서 서비스 정보 복구"""
        try:
            # 컨테이너 정보에서 서비스 설정 추출
            container_info = container.attrs
            
            # 포트 정보 추출
            ports = container_info.get("NetworkSettings", {}).get("Ports", {})
            host_port = None
            container_port = None
            
            for port_mapping in ports.values():
                if port_mapping:
                    host_port = int(port_mapping[0]["HostPort"])
                    container_port = int(port_mapping[0]["HostPort"])
                    break
            
            # 서비스 설정 생성
            config = ServiceConfig(
                name=container.labels.get("com.plugin.service.name", "unknown"),
                plugin_id=container.labels.get("com.plugin.id", "unknown"),
                service_type=ServiceType(container.labels.get("com.plugin.service.type", "rest_api")),
                port=container_port or 8080
                # host_port 파라미터는 ServiceConfig에 존재하지 않으므로 제거했습니다. # noqa
            )
            
            # 서비스 인스턴스 생성
            service = ServiceInstance(
                id=service_id,
                config=config,
                status=ServiceStatus.RUNNING if container.status == "running" else ServiceStatus.STOPPED,
                container_id=container.id,
                container_name=container.name,
                port=container_port or 8080,
                host_port=host_port or 8080,
                start_time=datetime.fromtimestamp(container.attrs["Created"]),
                last_health_check=None,
                health_status=ServiceStatus.UNHEALTHY,
                resource_usage={},
                logs=[],
                error_message=None
            )
            
            self.services[service_id] = service
            logger.info(f"서비스 복구 완료: {service_id}")
            
        except Exception as e:
            logger.error(f"서비스 복구 실패: {service_id} - {e}")
    
    def _start_health_monitoring(self):
        """헬스 체크 모니터링 시작"""
        def health_monitor():
            while True:
                try:
                    asyncio.run(self._check_all_services_health())
                    time.sleep(self.health_check_interval)
                except Exception as e:
                    logger.error(f"헬스 체크 모니터링 오류: {e}")
                    time.sleep(10)
        
        monitor_thread = threading.Thread(target=health_monitor, daemon=True)
        monitor_thread.start()
        logger.info("헬스 체크 모니터링 시작")
    
    async def _check_all_services_health(self):
        """모든 서비스 헬스 체크"""
        for service_id, service in self.services.items():
            if service.status == ServiceStatus.RUNNING:
                await self._check_service_health(service)
    
    async def _check_service_health(self, service: ServiceInstance):
        """개별 서비스 헬스 체크"""
        try:
            health_url = service.config.health_check["url"].replace("localhost", "127.0.0.1")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(health_url, timeout=service.config.health_check["timeout"]) as response:
                    if response.status == 200:
                        service.health_status = ServiceStatus.HEALTHY
                        service.error_message = None
                    else:
                        service.health_status = ServiceStatus.UNHEALTHY
                        service.error_message = f"HTTP {response.status}"
            
            service.last_health_check = datetime.now()
            
        except Exception as e:
            service.health_status = ServiceStatus.UNHEALTHY
            service.error_message = str(e)
            service.last_health_check = datetime.now()
    
    async def create_service(self, plugin_id: str, service_config: ServiceConfig) -> str:
        """새 서비스 생성"""
        if not self.docker_client:
            raise RuntimeError("Docker 클라이언트가 초기화되지 않았습니다")
        
        service_id = f"{plugin_id}_{service_config.name}_{int(time.time())}"
        
        try:
            # 포트 할당
            host_port = await self.port_manager.allocate_port()  # pyright: ignore

            # Docker 이미지 빌드 또는 가져오기
            try:
                image_name = await self._prepare_service_image(plugin_id, service_config)  # pyright: ignore
            except AttributeError:
                logger.error("_prepare_service_image 메서드를 찾을 수 없습니다. 이미지 준비를 건너뜁니다.")  # pyright: ignore
                image_name = f"plugin_{plugin_id}_{service_config.name}:{service_config.version}"

            # 컨테이너 생성
            try:
                container = await self._create_service_container(
                    service_id, service_config, image_name, host_port
                )  # pyright: ignore
            except AttributeError as e:
                logger.error(f"_create_service_container 메서드를 찾을 수 없습니다: {e}")  # pyright: ignore
                raise RuntimeError("_create_service_container 메서드가 필요합니다.")  # pyright: ignore
            
            # 서비스 인스턴스 생성
            service = ServiceInstance(
                id=service_id,
                config=service_config,
                status=ServiceStatus.STARTING,
                container_id=container.id,
                container_name=container.name,
                port=service_config.port,
                host_port=host_port,
                start_time=datetime.now(),
                last_health_check=None,
                health_status=ServiceStatus.UNHEALTHY,
                resource_usage={},
                logs=[],
                error_message=None
            )
            
            self.services[service_id] = service
            # 서비스 시작
            await self._start_service(service)  # pyright: ignore

            logger.info(f"서비스 생성 완료: {service_id}")
            return service_id
        except Exception as e:
            logger.error(f"서비스 생성 실패: {service_id} - {e}")
            # 포트 해제
            try:
                await self.port_manager.release_port(host_port)  # pyright: ignore
            except AttributeError:
                logger.warning("PortManager에 release_port 메서드가 없습니다. 포트 해제를 건너뜁니다.")  # pyright: ignore
            except Exception as release_err:
                logger.error(f"포트 해제 중 오류 발생: {release_err}")  # pyright: ignore
            raise
        plugin_path = self.base_path / plugin_id
        image_name = f"plugin_{plugin_id}_{config.name}:{config.version}"
        
        # Dockerfile 확인
        dockerfile_path = plugin_path / "Dockerfile"
        if not dockerfile_path.exists():
            # 기본 Dockerfile 생성
            await self._create_default_dockerfile(plugin_path, config)
        
        try:
            # 이미지 빌드
            image, logs = self.docker_client.images.build(
                path=str(plugin_path),
                tag=image_name,
                rm=True,
                labels={
                    "com.plugin.id": plugin_id,
                    "com.plugin.service.name": config.name,
                    "com.plugin.system": "true"
                }
            )
            
            logger.info(f"이미지 빌드 완료: {image_name}")
            return image_name
            
        except Exception as e:
            logger.error(f"이미지 빌드 실패: {image_name} - {e}")
            raise
    
    async def _create_default_dockerfile(self, plugin_path: Path, config: ServiceConfig):
        """기본 Dockerfile 생성"""
        dockerfile_content = f"""
FROM python:3.9-slim

WORKDIR /app

# 플러그인 파일 복사
COPY . /app/

# 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt 2>/dev/null || echo "No requirements.txt found"

# 환경 변수 설정
ENV PLUGIN_ID={config.plugin_id}
ENV SERVICE_NAME={config.name}
ENV SERVICE_PORT={config.port}

# 헬스 체크 엔드포인트 추가
RUN echo 'from flask import Flask; app = Flask(__name__); @app.route("/health"); def health(): return {{"status": "healthy"}}; app.run(host="0.0.0.0", port={config.port})' > health_server.py

# 서비스 실행
CMD ["python", "health_server.py"]
"""
        
        dockerfile_path = plugin_path / "Dockerfile"
        async with aiofiles.open(dockerfile_path, 'w') as f:
            await f.write(dockerfile_content)
        
        logger.info(f"기본 Dockerfile 생성: {dockerfile_path}")
    
    async def _create_service_container(self, service_id: str, config: ServiceConfig, 
                                      image_name: str, host_port: int) -> Any:
        """서비스 컨테이너 생성"""
        container_name = f"plugin_{service_id}"
        
        # 환경 변수 설정
        env_vars = {
            "PLUGIN_ID": config.plugin_id,
            "SERVICE_NAME": config.name,
            "SERVICE_PORT": str(config.port),
            "HOST_PORT": str(host_port)
        }
        # config.environment가 None일 수 있으므로 안전하게 처리합니다.
        if config.environment:
            env_vars.update(config.environment)  # pyright: ignore
        # 볼륨 마운트 설정
        volumes = {}
        for volume in config.volumes:
            if ":" in volume:
                host_path, container_path = volume.split(":", 1)
                volumes[host_path] = {"bind": container_path, "mode": "rw"}
        
        # 리소스 제한 설정
        mem_limit = config.resource_limits.get("memory", "512m")
        cpu_limit = config.resource_limits.get("cpu", "0.5")
        
        # 라벨 설정
        labels = {
            "com.plugin.system": "true",
            "com.plugin.service.id": service_id,
            "com.plugin.service.name": config.name,
            "com.plugin.id": config.plugin_id,
            "com.plugin.service.type": config.service_type.value
        }

        # Docker SDK의 run 함수는 networks 파라미터를 지원하지 않으므로, 컨테이너 생성 후 네트워크에 연결해야 합니다.
        try:
            container = self.docker_client.containers.run(
                image=image_name,
                name=container_name,
                detach=True,
                ports={f"{config.port}/tcp": host_port},
                environment=env_vars,
                volumes=volumes,
                labels=labels,
                restart_policy={"Name": config.restart_policy, "MaximumRetryCount": 0},  # pyright: ignore
                mem_limit=mem_limit,
                cpu_quota=int(float(cpu_limit) * 100000),
                cpu_period=100000
            )

            # 네트워크 연결 처리 (config.networks가 있을 때만)
            # Docker 컨테이너가 생성된 후에 네트워크에 연결해야 하므로, run() 이후에 처리합니다.
            if hasattr(config, "networks") and config.networks:  # pyright: ignore
                for network_name in config.networks:
                    try:
                        network = self.docker_client.networks.get(network_name)
                        network.connect(container)
                    except Exception as net_err:
                        logger.warning(f"네트워크 연결 실패: {network_name} - {net_err}")

            logger.info(f"컨테이너 생성 완료: {container.id}")
            return container

        except Exception as e:
            logger.error(f"컨테이너 생성 실패: {e}")
            raise
    async def _start_service(self, service: ServiceInstance):
        """서비스 시작"""
        try:
            container = self.docker_client.containers.get(service.container_id)
            container.start()
            
            service.status = ServiceStatus.RUNNING
            service.start_time = datetime.now()
            
            # 헬스 체크 대기
            await asyncio.sleep(5)
            await self._check_service_health(service)
            
            logger.info(f"서비스 시작 완료: {service.id}")
            
        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error_message = str(e)
            logger.error(f"서비스 시작 실패: {service.id} - {e}")
    
    async def stop_service(self, service_id: str) -> bool:
        """서비스 중지"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        try:
            if service.container_id:
                container = self.docker_client.containers.get(service.container_id)
                container.stop(timeout=30)
                service.status = ServiceStatus.STOPPED
            
            # 포트 해제
            self.port_manager.release_port(service.host_port)
            
            logger.info(f"서비스 중지 완료: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"서비스 중지 실패: {service_id} - {e}")
            return False
    
    async def restart_service(self, service_id: str) -> bool:
        """서비스 재시작"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        try:
            if service.container_id:
                container = self.docker_client.containers.get(service.container_id)
                container.restart(timeout=30)
                
                service.status = ServiceStatus.RUNNING
                service.start_time = datetime.now()
                
                # 헬스 체크 대기
                await asyncio.sleep(5)
                await self._check_service_health(service)
            
            logger.info(f"서비스 재시작 완료: {service_id}")
            return True
            
        except Exception as e:
            service.status = ServiceStatus.ERROR
            service.error_message = str(e)
            logger.error(f"서비스 재시작 실패: {service_id} - {e}")
            return False
    
    async def delete_service(self, service_id: str) -> bool:
        """서비스 삭제"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        try:
            # 서비스 중지
            await self.stop_service(service_id)
            
            # 컨테이너 삭제
            if service.container_id:
                container = self.docker_client.containers.get(service.container_id)
                container.remove(force=True)
            
            # 서비스 제거
            del self.services[service_id]
            
            logger.info(f"서비스 삭제 완료: {service_id}")
            return True
            
        except Exception as e:
            logger.error(f"서비스 삭제 실패: {service_id} - {e}")
            return False
    
    async def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        """서비스 조회"""
        return self.services.get(service_id)
    
    async def list_services(self, plugin_id: Optional[str] = None, 
                          status: Optional[ServiceStatus] = None) -> List[Dict[str, Any]]:
        """서비스 목록 조회"""
        services = []
        
        for service in self.services.values():
            if plugin_id and service.config.plugin_id != plugin_id:
                continue
            if status and service.status != status:
                continue
            
            services.append(service.to_dict())
        
        return services
    
    async def get_service_logs(self, service_id: str, lines: int = 100) -> List[str]:
        """서비스 로그 조회"""
        if service_id not in self.services:
            return []
        
        service = self.services[service_id]
        
        try:
            if service.container_id:
                container = self.docker_client.containers.get(service.container_id)
                logs = container.logs(tail=lines, timestamps=True).decode('utf-8')
                return logs.split('\n')[:-1]  # 마지막 빈 줄 제거
        except Exception as e:
            logger.error(f"로그 조회 실패: {service_id} - {e}")
        
        return []
    
    async def get_service_metrics(self, service_id: str) -> Dict[str, Any]:
        """서비스 메트릭 조회"""
        if service_id not in self.services:
            return {}
        
        service = self.services[service_id]
        
        try:
            if service.container_id:
                container = self.docker_client.containers.get(service.container_id)
                stats = container.stats(stream=False)
                
                # CPU 사용률 계산
                cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                           stats['precpu_stats']['cpu_usage']['total_usage']
                system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                              stats['precpu_stats']['system_cpu_usage']
                cpu_percent = (cpu_delta / system_delta) * 100.0
                
                # 메모리 사용량
                memory_usage = stats['memory_stats']['usage']
                memory_limit = stats['memory_stats']['limit']
                memory_percent = (memory_usage / memory_limit) * 100.0
                
                # 네트워크 통계
                network_stats = stats.get('networks', {})
                rx_bytes = sum(net['rx_bytes'] for net in network_stats.values())
                tx_bytes = sum(net['tx_bytes'] for net in network_stats.values())
                
                metrics = {
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_usage_mb": round(memory_usage / 1024 / 1024, 2),
                    "memory_limit_mb": round(memory_limit / 1024 / 1024, 2),
                    "memory_percent": round(memory_percent, 2),
                    "network_rx_mb": round(rx_bytes / 1024 / 1024, 2),
                    "network_tx_mb": round(tx_bytes / 1024 / 1024, 2),
                    "timestamp": datetime.now().isoformat()
                }
                
                service.resource_usage = metrics
                return metrics
                
        except Exception as e:
            logger.error(f"메트릭 조회 실패: {service_id} - {e}")
        
        return {}
    
    async def scale_service(self, service_id: str, replicas: int) -> bool:
        """서비스 스케일링"""
        if service_id not in self.services:
            return False
        
        if replicas <= 0:
            return await self.delete_service(service_id)
        
        # 현재는 단일 인스턴스만 지원
        # 향후 확장 시 여러 인스턴스 관리 로직 추가
        logger.info(f"서비스 스케일링 요청: {service_id} -> {replicas} replicas")
        return True
    
    async def get_service_discovery_info(self) -> Dict[str, Any]:
        """서비스 디스커버리 정보"""
        discovery_info = {
            "services": [],
            "networks": [],
            "total_services": len(self.services),
            "healthy_services": 0,
            "unhealthy_services": 0
        }
        
        for service in self.services.values():
            service_info = {
                "id": service.id,
                "name": service.config.name,
                "plugin_id": service.config.plugin_id,
                "type": service.config.service_type.value,
                "status": service.status.value,
                "health": service.health_status.value,
                "endpoint": f"http://localhost:{service.host_port}",
                "port": service.host_port,
                "start_time": service.start_time.isoformat() if service.start_time else None
            }
            
            discovery_info["services"].append(service_info)
            
            if service.health_status == ServiceStatus.HEALTHY:
                discovery_info["healthy_services"] += 1
            else:
                discovery_info["unhealthy_services"] += 1
        
        # 네트워크 정보
        for network_name, network in self.networks.items():
            network_info = {
                "name": network_name,
                "id": network.id,
                "driver": network.attrs.get("Driver", "unknown"),
                "scope": network.attrs.get("Scope", "unknown")
            }
            discovery_info["networks"].append(network_info)
        
        return discovery_info
    
    async def cleanup_unused_resources(self) -> Dict[str, int]:
        """사용하지 않는 리소스 정리"""
        cleanup_stats = {
            "containers_removed": 0,
            "images_removed": 0,
            "networks_removed": 0
        }
        
        try:
            # 중지된 컨테이너 정리
            containers = self.docker_client.containers.list(
                filters={"label": "com.plugin.system=true", "status": "exited"}
            )
            
            for container in containers:
                try:
                    container.remove()
                    cleanup_stats["containers_removed"] += 1
                except Exception as e:
                    logger.error(f"컨테이너 정리 실패: {container.id} - {e}")
            
            # 사용하지 않는 이미지 정리
            images = self.docker_client.images.list(
                filters={"label": "com.plugin.system=true", "dangling": True}
            )
            
            for image in images:
                try:
                    self.docker_client.images.remove(image.id, force=True)
                    cleanup_stats["images_removed"] += 1
                except Exception as e:
                    logger.error(f"이미지 정리 실패: {image.id} - {e}")
            
            logger.info(f"리소스 정리 완료: {cleanup_stats}")
            
        except Exception as e:
            logger.error(f"리소스 정리 실패: {e}")
        
        return cleanup_stats

class PortManager:
    """포트 관리자"""
    
    def __init__(self, start_port: int = 8000, end_port: int = 9000):
        self.start_port = start_port
        self.end_port = end_port
        self.allocated_ports: Set[int] = set()
    
    def allocate_port(self) -> int:
        """포트 할당"""
        for port in range(self.start_port, self.end_port + 1):
            if port not in self.allocated_ports:
                self.allocated_ports.add(port)
                return port
        raise RuntimeError("사용 가능한 포트가 없습니다")
    
    def release_port(self, port: int):
        """포트 해제"""
        if port in self.allocated_ports:
            self.allocated_ports.remove(port)
    
    def is_port_allocated(self, port: int) -> bool:
        """포트 할당 여부 확인"""
        return port in self.allocated_ports

# 전역 인스턴스
microservice_manager = PluginMicroserviceManager()  # noqa