"""
서비스 분해 및 모듈화 시스템
도메인 기반 서비스 분해, 바운디드 컨텍스트, 서비스 간 통신을 포함한 완전한 마이크로서비스 아키텍처
"""

import logging
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import queue
import asyncio
import aiohttp
from aiohttp import web
import websockets
import sqlite3
from pathlib import Path
import pickle
import hashlib
import hmac
import base64
import secrets
import struct
import socket
import ssl
import paho.mqtt.client as mqtt
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import schedule
import yaml
import docker
from docker.errors import DockerException
import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceType(Enum):
    """서비스 타입"""
    API_GATEWAY = "api_gateway"
    USER_SERVICE = "user_service"
    AUTH_SERVICE = "auth_service"
    PAYMENT_SERVICE = "payment_service"
    NOTIFICATION_SERVICE = "notification_service"
    ANALYTICS_SERVICE = "analytics_service"
    STORAGE_SERVICE = "storage_service"
    WORKFLOW_SERVICE = "workflow_service"
    INTEGRATION_SERVICE = "integration_service"
    MONITORING_SERVICE = "monitoring_service"

class ServiceStatus(Enum):
    """서비스 상태"""
    RUNNING = "running"
    STOPPED = "stopped"
    STARTING = "starting"
    STOPPING = "stopping"
    ERROR = "error"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"

class CommunicationType(Enum):
    """통신 타입"""
    HTTP_REST = "http_rest"
    GRPC = "grpc"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAM = "event_stream"
    WEBSOCKET = "websocket"

@dataclass
class ServiceDefinition:
    """서비스 정의"""
    service_id: str
    name: str
    service_type: ServiceType
    version: str
    description: str
    domain: str
    bounded_context: str
    dependencies: List[str]
    endpoints: List[Dict[str, Any]]
    configuration: Dict[str, Any]
    health_check: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ServiceInstance:
    """서비스 인스턴스"""
    instance_id: str
    service_id: str
    host: str
    port: int
    status: ServiceStatus
    health_score: float
    load_balancer_weight: int
    metadata: Dict[str, Any]
    started_at: datetime
    last_heartbeat: datetime

@dataclass
class ServiceCommunication:
    """서비스 간 통신"""
    communication_id: str
    source_service: str
    target_service: str
    communication_type: CommunicationType
    protocol: str
    endpoint: str
    timeout: int
    retry_policy: Dict[str, Any]
    circuit_breaker: Dict[str, Any]
    created_at: datetime

@dataclass
class ServiceDependency:
    """서비스 의존성"""
    dependency_id: str
    service_id: str
    dependent_service: str
    dependency_type: str
    required: bool
    health_check: bool
    timeout: int
    created_at: datetime

class ServiceDecompositionSystem:
    """서비스 분해 및 모듈화 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.services: Dict[str, ServiceDefinition] = {}
        self.instances: Dict[str, ServiceInstance] = {}
        self.communications: Dict[str, ServiceCommunication] = {}
        self.dependencies: Dict[str, List[ServiceDependency]] = defaultdict(list)
        
        # 서비스 레지스트리
        self.service_registry: Dict[str, List[ServiceInstance]] = defaultdict(list)
        
        # 헬스 체크
        self.health_checkers: Dict[str, Callable] = {}
        
        # Docker 클라이언트
        self.docker_client = None
        self._init_docker()
        
        # Kubernetes 클라이언트
        self.k8s_client = None
        self._init_kubernetes()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './microservices.db'))
        self._init_database()
        
        # 기본 서비스 정의 로드
        self._load_default_services()
        
        # 헬스 체크 스레드
        self.health_check_thread = None
        self.is_running = False
        
        logger.info("서비스 분해 및 모듈화 시스템 초기화 완료")
    
    def _init_docker(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            logger.info("Docker 클라이언트 초기화 완료")
        except DockerException as e:
            logger.warning(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _init_kubernetes(self):
        """Kubernetes 클라이언트 초기화"""
        try:
            config.load_kube_config()
            self.k8s_client = client.CoreV1Api()
            logger.info("Kubernetes 클라이언트 초기화 완료")
        except Exception as e:
            logger.warning(f"Kubernetes 클라이언트 초기화 실패: {e}")
            self.k8s_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 서비스 정의 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_definitions (
                    service_id TEXT PRIMARY KEY,
                    name TEXT,
                    service_type TEXT,
                    version TEXT,
                    description TEXT,
                    domain TEXT,
                    bounded_context TEXT,
                    dependencies TEXT,
                    endpoints TEXT,
                    configuration TEXT,
                    health_check TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # 서비스 인스턴스 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_instances (
                    instance_id TEXT PRIMARY KEY,
                    service_id TEXT,
                    host TEXT,
                    port INTEGER,
                    status TEXT,
                    health_score REAL,
                    load_balancer_weight INTEGER,
                    metadata TEXT,
                    started_at TEXT,
                    last_heartbeat TEXT,
                    FOREIGN KEY (service_id) REFERENCES service_definitions (service_id)
                )
            ''')
            
            # 서비스 통신 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_communications (
                    communication_id TEXT PRIMARY KEY,
                    source_service TEXT,
                    target_service TEXT,
                    communication_type TEXT,
                    protocol TEXT,
                    endpoint TEXT,
                    timeout INTEGER,
                    retry_policy TEXT,
                    circuit_breaker TEXT,
                    created_at TEXT
                )
            ''')
            
            # 서비스 의존성 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_dependencies (
                    dependency_id TEXT PRIMARY KEY,
                    service_id TEXT,
                    dependent_service TEXT,
                    dependency_type TEXT,
                    required INTEGER,
                    health_check INTEGER,
                    timeout INTEGER,
                    created_at TEXT,
                    FOREIGN KEY (service_id) REFERENCES service_definitions (service_id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("마이크로서비스 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _load_default_services(self):
        """기본 서비스 정의 로드"""
        try:
            default_services = [
                {
                    'name': 'API Gateway',
                    'service_type': ServiceType.API_GATEWAY,
                    'version': '1.0.0',
                    'description': 'API 게이트웨이 서비스',
                    'domain': 'Infrastructure',
                    'bounded_context': 'Gateway',
                    'dependencies': [],
                    'endpoints': [
                        {'path': '/api/v1', 'method': 'GET', 'description': 'API 정보'},
                        {'path': '/health', 'method': 'GET', 'description': '헬스 체크'}
                    ],
                    'configuration': {
                        'port': 8080,
                        'timeout': 30,
                        'rate_limit': 1000
                    },
                    'health_check': {
                        'endpoint': '/health',
                        'interval': 30,
                        'timeout': 5
                    }
                },
                {
                    'name': 'User Service',
                    'service_type': ServiceType.USER_SERVICE,
                    'version': '1.0.0',
                    'description': '사용자 관리 서비스',
                    'domain': 'User Management',
                    'bounded_context': 'User',
                    'dependencies': ['auth_service'],
                    'endpoints': [
                        {'path': '/users', 'method': 'GET', 'description': '사용자 목록'},
                        {'path': '/users/{id}', 'method': 'GET', 'description': '사용자 조회'},
                        {'path': '/users', 'method': 'POST', 'description': '사용자 생성'}
                    ],
                    'configuration': {
                        'port': 8081,
                        'database': 'user_db',
                        'cache_ttl': 300
                    },
                    'health_check': {
                        'endpoint': '/health',
                        'interval': 30,
                        'timeout': 5
                    }
                },
                {
                    'name': 'Auth Service',
                    'service_type': ServiceType.AUTH_SERVICE,
                    'version': '1.0.0',
                    'description': '인증 및 권한 관리 서비스',
                    'domain': 'Security',
                    'bounded_context': 'Authentication',
                    'dependencies': [],
                    'endpoints': [
                        {'path': '/auth/login', 'method': 'POST', 'description': '로그인'},
                        {'path': '/auth/register', 'method': 'POST', 'description': '회원가입'},
                        {'path': '/auth/verify', 'method': 'POST', 'description': '토큰 검증'}
                    ],
                    'configuration': {
                        'port': 8082,
                        'jwt_secret': 'your-secret-key',
                        'token_expiry': 3600
                    },
                    'health_check': {
                        'endpoint': '/health',
                        'interval': 30,
                        'timeout': 5
                    }
                },
                {
                    'name': 'Payment Service',
                    'service_type': ServiceType.PAYMENT_SERVICE,
                    'version': '1.0.0',
                    'description': '결제 처리 서비스',
                    'domain': 'Payment',
                    'bounded_context': 'Payment',
                    'dependencies': ['notification_service'],
                    'endpoints': [
                        {'path': '/payments', 'method': 'POST', 'description': '결제 생성'},
                        {'path': '/payments/{id}', 'method': 'GET', 'description': '결제 조회'},
                        {'path': '/payments/{id}/refund', 'method': 'POST', 'description': '환불'}
                    ],
                    'configuration': {
                        'port': 8083,
                        'payment_gateway': 'stripe',
                        'webhook_secret': 'webhook-secret'
                    },
                    'health_check': {
                        'endpoint': '/health',
                        'interval': 30,
                        'timeout': 5
                    }
                },
                {
                    'name': 'Notification Service',
                    'service_type': ServiceType.NOTIFICATION_SERVICE,
                    'version': '1.0.0',
                    'description': '알림 서비스',
                    'domain': 'Communication',
                    'bounded_context': 'Notification',
                    'dependencies': [],
                    'endpoints': [
                        {'path': '/notifications', 'method': 'POST', 'description': '알림 전송'},
                        {'path': '/notifications/{id}', 'method': 'GET', 'description': '알림 조회'},
                        {'path': '/notifications/batch', 'method': 'POST', 'description': '배치 알림'}
                    ],
                    'configuration': {
                        'port': 8084,
                        'email_provider': 'smtp',
                        'sms_provider': 'twilio'
                    },
                    'health_check': {
                        'endpoint': '/health',
                        'interval': 30,
                        'timeout': 5
                    }
                }
            ]
            
            for service_info in default_services:
                self.register_service(service_info)
            
            logger.info(f"{len(default_services)}개 기본 서비스 정의 로드 완료")
            
        except Exception as e:
            logger.error(f"기본 서비스 로드 오류: {e}")
    
    def register_service(self, service_info: Dict[str, Any]) -> str:
        """서비스 등록"""
        try:
            service_id = str(uuid.uuid4())
            
            service = ServiceDefinition(
                service_id=service_id,
                name=service_info['name'],
                service_type=ServiceType(service_info['service_type']),
                version=service_info['version'],
                description=service_info['description'],
                domain=service_info['domain'],
                bounded_context=service_info['bounded_context'],
                dependencies=service_info.get('dependencies', []),
                endpoints=service_info.get('endpoints', []),
                configuration=service_info.get('configuration', {}),
                health_check=service_info.get('health_check', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.services[service_id] = service
            
            # 의존성 등록
            for dep_service in service.dependencies:
                dependency = ServiceDependency(
                    dependency_id=str(uuid.uuid4()),
                    service_id=service_id,
                    dependent_service=dep_service,
                    dependency_type='required',
                    required=True,
                    health_check=True,
                    timeout=30,
                    created_at=datetime.now()
                )
                self.dependencies[service_id].append(dependency)
            
            # 데이터베이스에 저장
            self._save_service_to_db(service)
            
            logger.info(f"서비스 등록 완료: {service_id}")
            return service_id
            
        except Exception as e:
            logger.error(f"서비스 등록 오류: {e}")
            raise
    
    def deploy_service(self, service_id: str, deployment_config: Dict[str, Any]) -> str:
        """서비스 배포"""
        try:
            if service_id not in self.services:
                raise ValueError(f"서비스를 찾을 수 없습니다: {service_id}")
            
            service = self.services[service_id]
            
            # Docker 컨테이너 배포
            if self.docker_client:
                instance_id = self._deploy_docker_service(service, deployment_config)
            # Kubernetes 배포
            elif self.k8s_client:
                instance_id = self._deploy_kubernetes_service(service, deployment_config)
            else:
                # 로컬 프로세스 배포
                instance_id = self._deploy_local_service(service, deployment_config)
            
            logger.info(f"서비스 배포 완료: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"서비스 배포 오류: {e}")
            raise
    
    def _deploy_docker_service(self, service: ServiceDefinition, config: Dict[str, Any]) -> str:
        """Docker 서비스 배포"""
        try:
            instance_id = str(uuid.uuid4())
            
            # Docker 이미지 빌드 또는 가져오기
            image_name = config.get('image', f"{service.name.lower()}:{service.version}")
            
            # 컨테이너 실행
            container = self.docker_client.containers.run(
                image=image_name,
                name=f"{service.name.lower()}-{instance_id[:8]}",
                ports={f"{service.configuration.get('port', 8080)}/tcp": None},
                environment=config.get('environment', {}),
                detach=True,
                restart_policy={"Name": "always"}
            )
            
            # 포트 매핑 가져오기
            port_bindings = container.attrs['NetworkSettings']['Ports']
            host_port = None
            for container_port, bindings in port_bindings.items():
                if bindings:
                    host_port = int(bindings[0]['HostPort'])
                    break
            
            # 서비스 인스턴스 생성
            instance = ServiceInstance(
                instance_id=instance_id,
                service_id=service.service_id,
                host='localhost',
                port=host_port or service.configuration.get('port', 8080),
                status=ServiceStatus.STARTING,
                health_score=1.0,
                load_balancer_weight=1,
                metadata={
                    'container_id': container.id,
                    'image': image_name,
                    'deployment_type': 'docker'
                },
                started_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
            
            self.instances[instance_id] = instance
            self.service_registry[service.service_id].append(instance)
            
            # 데이터베이스에 저장
            self._save_instance_to_db(instance)
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Docker 서비스 배포 오류: {e}")
            raise
    
    def _deploy_kubernetes_service(self, service: ServiceDefinition, config: Dict[str, Any]) -> str:
        """Kubernetes 서비스 배포"""
        try:
            instance_id = str(uuid.uuid4())
            
            # Kubernetes Deployment 생성
            deployment = client.V1Deployment(
                metadata=client.V1ObjectMeta(
                    name=f"{service.name.lower()}-{instance_id[:8]}",
                    labels={"app": service.name.lower()}
                ),
                spec=client.V1DeploymentSpec(
                    replicas=1,
                    selector=client.V1LabelSelector(
                        match_labels={"app": service.name.lower()}
                    ),
                    template=client.V1PodTemplateSpec(
                        metadata=client.V1ObjectMeta(
                            labels={"app": service.name.lower()}
                        ),
                        spec=client.V1PodSpec(
                            containers=[
                                client.V1Container(
                                    name=service.name.lower(),
                                    image=config.get('image', f"{service.name.lower()}:{service.version}"),
                                    ports=[client.V1ContainerPort(container_port=service.configuration.get('port', 8080))],
                                    env=[client.V1EnvVar(name=k, value=str(v)) for k, v in config.get('environment', {}).items()]
                                )
                            ]
                        )
                    )
                )
            )
            
            # Deployment 생성
            apps_v1 = client.AppsV1Api()
            apps_v1.create_namespaced_deployment(
                namespace="default",
                body=deployment
            )
            
            # Service 생성
            k8s_service = client.V1Service(
                metadata=client.V1ObjectMeta(
                    name=f"{service.name.lower()}-service-{instance_id[:8]}"
                ),
                spec=client.V1ServiceSpec(
                    selector={"app": service.name.lower()},
                    ports=[client.V1ServicePort(port=service.configuration.get('port', 8080))]
                )
            )
            
            self.k8s_client.create_namespaced_service(
                namespace="default",
                body=k8s_service
            )
            
            # 서비스 인스턴스 생성
            instance = ServiceInstance(
                instance_id=instance_id,
                service_id=service.service_id,
                host=f"{service.name.lower()}-service-{instance_id[:8]}.default.svc.cluster.local",
                port=service.configuration.get('port', 8080),
                status=ServiceStatus.STARTING,
                health_score=1.0,
                load_balancer_weight=1,
                metadata={
                    'deployment_name': f"{service.name.lower()}-{instance_id[:8]}",
                    'service_name': f"{service.name.lower()}-service-{instance_id[:8]}",
                    'deployment_type': 'kubernetes'
                },
                started_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
            
            self.instances[instance_id] = instance
            self.service_registry[service.service_id].append(instance)
            
            # 데이터베이스에 저장
            self._save_instance_to_db(instance)
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Kubernetes 서비스 배포 오류: {e}")
            raise
    
    def _deploy_local_service(self, service: ServiceDefinition, config: Dict[str, Any]) -> str:
        """로컬 서비스 배포"""
        try:
            instance_id = str(uuid.uuid4())
            
            # 서비스 인스턴스 생성
            instance = ServiceInstance(
                instance_id=instance_id,
                service_id=service.service_id,
                host='localhost',
                port=service.configuration.get('port', 8080),
                status=ServiceStatus.RUNNING,
                health_score=1.0,
                load_balancer_weight=1,
                metadata={
                    'deployment_type': 'local',
                    'process_id': None
                },
                started_at=datetime.now(),
                last_heartbeat=datetime.now()
            )
            
            self.instances[instance_id] = instance
            self.service_registry[service.service_id].append(instance)
            
            # 데이터베이스에 저장
            self._save_instance_to_db(instance)
            
            return instance_id
            
        except Exception as e:
            logger.error(f"로컬 서비스 배포 오류: {e}")
            raise
    
    def create_service_communication(self, source_service: str, target_service: str,
                                   communication_config: Dict[str, Any]) -> str:
        """서비스 간 통신 설정"""
        try:
            communication_id = str(uuid.uuid4())
            
            communication = ServiceCommunication(
                communication_id=communication_id,
                source_service=source_service,
                target_service=target_service,
                communication_type=CommunicationType(communication_config.get('type', 'http_rest')),
                protocol=communication_config.get('protocol', 'http'),
                endpoint=communication_config.get('endpoint', ''),
                timeout=communication_config.get('timeout', 30),
                retry_policy=communication_config.get('retry_policy', {
                    'max_retries': 3,
                    'backoff_factor': 2
                }),
                circuit_breaker=communication_config.get('circuit_breaker', {
                    'failure_threshold': 5,
                    'recovery_timeout': 60
                }),
                created_at=datetime.now()
            )
            
            self.communications[communication_id] = communication
            
            # 데이터베이스에 저장
            self._save_communication_to_db(communication)
            
            logger.info(f"서비스 통신 설정 완료: {communication_id}")
            return communication_id
            
        except Exception as e:
            logger.error(f"서비스 통신 설정 오류: {e}")
            raise
    
    def get_service_instances(self, service_id: str) -> List[ServiceInstance]:
        """서비스 인스턴스 조회"""
        try:
            return self.service_registry.get(service_id, [])
        except Exception as e:
            logger.error(f"서비스 인스턴스 조회 오류: {e}")
            return []
    
    def get_healthy_instances(self, service_id: str) -> List[ServiceInstance]:
        """정상 인스턴스 조회"""
        try:
            instances = self.service_registry.get(service_id, [])
            return [instance for instance in instances if instance.status == ServiceStatus.HEALTHY]
        except Exception as e:
            logger.error(f"정상 인스턴스 조회 오류: {e}")
            return []
    
    def get_service_dependencies(self, service_id: str) -> List[ServiceDependency]:
        """서비스 의존성 조회"""
        try:
            return self.dependencies.get(service_id, [])
        except Exception as e:
            logger.error(f"서비스 의존성 조회 오류: {e}")
            return []
    
    def check_service_health(self, service_id: str) -> Dict[str, Any]:
        """서비스 헬스 체크"""
        try:
            instances = self.service_registry.get(service_id, [])
            
            if not instances:
                return {
                    'service_id': service_id,
                    'status': 'no_instances',
                    'healthy_count': 0,
                    'total_count': 0,
                    'health_score': 0.0
                }
            
            healthy_count = sum(1 for instance in instances if instance.status == ServiceStatus.HEALTHY)
            total_count = len(instances)
            health_score = healthy_count / total_count if total_count > 0 else 0.0
            
            return {
                'service_id': service_id,
                'status': 'healthy' if health_score > 0.5 else 'unhealthy',
                'healthy_count': healthy_count,
                'total_count': total_count,
                'health_score': health_score,
                'instances': [
                    {
                        'instance_id': instance.instance_id,
                        'host': instance.host,
                        'port': instance.port,
                        'status': instance.status.value,
                        'health_score': instance.health_score
                    }
                    for instance in instances
                ]
            }
            
        except Exception as e:
            logger.error(f"서비스 헬스 체크 오류: {e}")
            return {
                'service_id': service_id,
                'status': 'error',
                'error': str(e)
            }
    
    def _save_service_to_db(self, service: ServiceDefinition):
        """서비스를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO service_definitions 
                (service_id, name, service_type, version, description, domain, bounded_context,
                 dependencies, endpoints, configuration, health_check, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service.service_id,
                service.name,
                service.service_type.value,
                service.version,
                service.description,
                service.domain,
                service.bounded_context,
                json.dumps(service.dependencies),
                json.dumps(service.endpoints),
                json.dumps(service.configuration),
                json.dumps(service.health_check),
                service.created_at.isoformat(),
                service.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"서비스 데이터베이스 저장 오류: {e}")
    
    def _save_instance_to_db(self, instance: ServiceInstance):
        """인스턴스를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO service_instances 
                (instance_id, service_id, host, port, status, health_score, load_balancer_weight,
                 metadata, started_at, last_heartbeat)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                instance.instance_id,
                instance.service_id,
                instance.host,
                instance.port,
                instance.status.value,
                instance.health_score,
                instance.load_balancer_weight,
                json.dumps(instance.metadata),
                instance.started_at.isoformat(),
                instance.last_heartbeat.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"인스턴스 데이터베이스 저장 오류: {e}")
    
    def _save_communication_to_db(self, communication: ServiceCommunication):
        """통신을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO service_communications 
                (communication_id, source_service, target_service, communication_type, protocol,
                 endpoint, timeout, retry_policy, circuit_breaker, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                communication.communication_id,
                communication.source_service,
                communication.target_service,
                communication.communication_type.value,
                communication.protocol,
                communication.endpoint,
                communication.timeout,
                json.dumps(communication.retry_policy),
                json.dumps(communication.circuit_breaker),
                communication.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"통신 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            # Docker 컨테이너 정리
            if self.docker_client:
                for instance in self.instances.values():
                    if instance.metadata.get('deployment_type') == 'docker':
                        container_id = instance.metadata.get('container_id')
                        if container_id:
                            try:
                                container = self.docker_client.containers.get(container_id)
                                container.stop()
                                container.remove()
                            except:
                                pass
            
            logger.info("서비스 분해 및 모듈화 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './microservices.db'
    }
    
    # 서비스 분해 시스템 생성
    decomposition_system = ServiceDecompositionSystem(config)
    
    # 사용자 정의 서비스 등록
    custom_service = {
        'name': 'Custom Analytics Service',
        'service_type': 'analytics_service',
        'version': '1.0.0',
        'description': '사용자 정의 분석 서비스',
        'domain': 'Analytics',
        'bounded_context': 'CustomAnalytics',
        'dependencies': ['user_service'],
        'endpoints': [
            {'path': '/analytics/custom', 'method': 'POST', 'description': '커스텀 분석'}
        ],
        'configuration': {
            'port': 8085,
            'database': 'analytics_db'
        },
        'health_check': {
            'endpoint': '/health',
            'interval': 30,
            'timeout': 5
        }
    }
    
    service_id = decomposition_system.register_service(custom_service)
    print(f"서비스 등록 완료: {service_id}")
    
    # 서비스 배포
    deployment_config = {
        'image': 'custom-analytics:1.0.0',
        'environment': {
            'DATABASE_URL': 'postgresql://localhost/analytics_db',
            'LOG_LEVEL': 'INFO'
        }
    }
    
    instance_id = decomposition_system.deploy_service(service_id, deployment_config)
    print(f"서비스 배포 완료: {instance_id}")
    
    # 서비스 통신 설정
    communication_config = {
        'type': 'http_rest',
        'protocol': 'http',
        'endpoint': '/api/v1',
        'timeout': 30,
        'retry_policy': {
            'max_retries': 3,
            'backoff_factor': 2
        }
    }
    
    comm_id = decomposition_system.create_service_communication(
        'user_service', 'custom_analytics_service', communication_config
    )
    print(f"서비스 통신 설정 완료: {comm_id}")
    
    # 서비스 헬스 체크
    health_status = decomposition_system.check_service_health(service_id)
    print(f"서비스 헬스 상태: {health_status}") 