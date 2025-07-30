"""
컨테이너 오케스트레이션 시스템 (Kubernetes)
컨테이너 배포, 스케일링, 로드 밸런싱, 서비스 디스커버리를 포함한 완전한 오케스트레이션 플랫폼
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
from aiohttp import web, ClientSession, ClientTimeout
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
import redis
from redis.exceptions import RedisError
import yaml
import subprocess
import docker
from kubernetes import client, config, watch
from kubernetes.client.rest import ApiException
import requests
from collections import defaultdict, deque

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PodStatus(Enum):
    """Pod 상태"""
    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"

class ServiceType(Enum):
    """서비스 타입"""
    CLUSTER_IP = "ClusterIP"
    NODE_PORT = "NodePort"
    LOAD_BALANCER = "LoadBalancer"
    EXTERNAL_NAME = "ExternalName"

class DeploymentStrategy(Enum):
    """배포 전략"""
    ROLLING_UPDATE = "RollingUpdate"
    RECREATE = "Recreate"
    BLUE_GREEN = "BlueGreen"
    CANARY = "Canary"

@dataclass
class Pod:
    """Pod 정보"""
    pod_id: str
    name: str
    namespace: str
    status: PodStatus
    node_name: str
    ip_address: str
    containers: List[Dict[str, Any]]
    labels: Dict[str, str]
    annotations: Dict[str, str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Service:
    """서비스 정보"""
    service_id: str
    name: str
    namespace: str
    service_type: ServiceType
    cluster_ip: str
    external_ip: str
    ports: List[Dict[str, Any]]
    selector: Dict[str, str]
    endpoints: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class Deployment:
    """배포 정보"""
    deployment_id: str
    name: str
    namespace: str
    replicas: int
    available_replicas: int
    strategy: DeploymentStrategy
    image: str
    labels: Dict[str, str]
    env_vars: Dict[str, str]
    resources: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class Node:
    """노드 정보"""
    node_id: str
    name: str
    status: str
    ip_address: str
    capacity: Dict[str, str]
    allocatable: Dict[str, str]
    conditions: List[Dict[str, Any]]
    labels: Dict[str, str]
    created_at: datetime
    updated_at: datetime

class KubernetesOrchestrator:
    """컨테이너 오케스트레이션 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.pods: Dict[str, Pod] = {}
        self.services: Dict[str, Service] = {}
        self.deployments: Dict[str, Deployment] = {}
        self.nodes: Dict[str, Node] = {}
        
        # Kubernetes 클라이언트
        self.k8s_client = None
        self._init_kubernetes_client()
        
        # Docker 클라이언트
        self.docker_client = None
        self._init_docker_client()
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './kubernetes.db'))
        self._init_database()
        
        # 모니터링 스레드
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # 스케일링 스레드
        self.scaling_thread = None
        self.is_scaling = False
        
        # 로드 밸런서
        self.load_balancer = None
        self._init_load_balancer()
        
        logger.info("Kubernetes 오케스트레이터 초기화 완료")
    
    def _init_kubernetes_client(self):
        """Kubernetes 클라이언트 초기화"""
        try:
            # kubeconfig 로드
            config.load_kube_config()
            
            # API 클라이언트 생성
            self.k8s_client = client.CoreV1Api()
            
            logger.info("Kubernetes 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.warning(f"Kubernetes 클라이언트 초기화 실패: {e}")
            self.k8s_client = None
    
    def _init_docker_client(self):
        """Docker 클라이언트 초기화"""
        try:
            self.docker_client = docker.from_env()
            
            # Docker 연결 테스트
            self.docker_client.ping()
            logger.info("Docker 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.warning(f"Docker 클라이언트 초기화 실패: {e}")
            self.docker_client = None
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 5),
                decode_responses=True
            )
            
            # Redis 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 클라이언트 초기화 완료")
            
        except RedisError as e:
            logger.warning(f"Redis 클라이언트 초기화 실패: {e}")
            self.redis_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Pod 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pods (
                    pod_id TEXT PRIMARY KEY,
                    name TEXT,
                    namespace TEXT,
                    status TEXT,
                    node_name TEXT,
                    ip_address TEXT,
                    containers TEXT,
                    labels TEXT,
                    annotations TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Service 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS services (
                    service_id TEXT PRIMARY KEY,
                    name TEXT,
                    namespace TEXT,
                    service_type TEXT,
                    cluster_ip TEXT,
                    external_ip TEXT,
                    ports TEXT,
                    selector TEXT,
                    endpoints TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Deployment 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS deployments (
                    deployment_id TEXT PRIMARY KEY,
                    name TEXT,
                    namespace TEXT,
                    replicas INTEGER,
                    available_replicas INTEGER,
                    strategy TEXT,
                    image TEXT,
                    labels TEXT,
                    env_vars TEXT,
                    resources TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            # Node 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS nodes (
                    node_id TEXT PRIMARY KEY,
                    name TEXT,
                    status TEXT,
                    ip_address TEXT,
                    capacity TEXT,
                    allocatable TEXT,
                    conditions TEXT,
                    labels TEXT,
                    created_at TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Kubernetes 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def _init_load_balancer(self):
        """로드 밸런서 초기화"""
        try:
            # 간단한 로드 밸런서 구현
            self.load_balancer = {
                'services': {},
                'health_checks': {},
                'round_robin_indexes': defaultdict(int)
            }
            
            logger.info("로드 밸런서 초기화 완료")
            
        except Exception as e:
            logger.error(f"로드 밸런서 초기화 오류: {e}")
    
    def create_deployment(self, deployment_info: Dict[str, Any]) -> str:
        """배포 생성"""
        try:
            deployment_id = str(uuid.uuid4())
            
            # Kubernetes Deployment 생성
            if self.k8s_client:
                deployment = client.V1Deployment(
                    metadata=client.V1ObjectMeta(
                        name=deployment_info['name'],
                        namespace=deployment_info.get('namespace', 'default'),
                        labels=deployment_info.get('labels', {})
                    ),
                    spec=client.V1DeploymentSpec(
                        replicas=deployment_info.get('replicas', 1),
                        selector=client.V1LabelSelector(
                            match_labels=deployment_info.get('selector', {})
                        ),
                        template=client.V1PodTemplateSpec(
                            metadata=client.V1ObjectMeta(
                                labels=deployment_info.get('labels', {})
                            ),
                            spec=client.V1PodSpec(
                                containers=[
                                    client.V1Container(
                                        name=deployment_info['name'],
                                        image=deployment_info['image'],
                                        ports=deployment_info.get('ports', []),
                                        env=[
                                            client.V1EnvVar(
                                                name=key,
                                                value=value
                                            )
                                            for key, value in deployment_info.get('env_vars', {}).items()
                                        ],
                                        resources=client.V1ResourceRequirements(
                                            requests=deployment_info.get('resources', {}).get('requests', {}),
                                            limits=deployment_info.get('resources', {}).get('limits', {})
                                        )
                                    )
                                ]
                            )
                        )
                    )
                )
                
                # Kubernetes API 호출
                apps_v1 = client.AppsV1Api()
                result = apps_v1.create_namespaced_deployment(
                    namespace=deployment_info.get('namespace', 'default'),
                    body=deployment
                )
                
                logger.info(f"Kubernetes 배포 생성 완료: {result.metadata.name}")
            
            # 내부 배포 정보 생성
            deployment_obj = Deployment(
                deployment_id=deployment_id,
                name=deployment_info['name'],
                namespace=deployment_info.get('namespace', 'default'),
                replicas=deployment_info.get('replicas', 1),
                available_replicas=0,
                strategy=DeploymentStrategy(deployment_info.get('strategy', 'RollingUpdate')),
                image=deployment_info['image'],
                labels=deployment_info.get('labels', {}),
                env_vars=deployment_info.get('env_vars', {}),
                resources=deployment_info.get('resources', {}),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.deployments[deployment_id] = deployment_obj
            
            # 데이터베이스에 저장
            self._save_deployment_to_db(deployment_obj)
            
            logger.info(f"배포 생성 완료: {deployment_id}")
            return deployment_id
            
        except Exception as e:
            logger.error(f"배포 생성 오류: {e}")
            raise
    
    def create_service(self, service_info: Dict[str, Any]) -> str:
        """서비스 생성"""
        try:
            service_id = str(uuid.uuid4())
            
            # Kubernetes Service 생성
            if self.k8s_client:
                service = client.V1Service(
                    metadata=client.V1ObjectMeta(
                        name=service_info['name'],
                        namespace=service_info.get('namespace', 'default'),
                        labels=service_info.get('labels', {})
                    ),
                    spec=client.V1ServiceSpec(
                        type=service_info.get('service_type', 'ClusterIP'),
                        selector=service_info.get('selector', {}),
                        ports=[
                            client.V1ServicePort(
                                port=port['port'],
                                target_port=port.get('target_port', port['port']),
                                protocol=port.get('protocol', 'TCP')
                            )
                            for port in service_info.get('ports', [])
                        ]
                    )
                )
                
                # Kubernetes API 호출
                result = self.k8s_client.create_namespaced_service(
                    namespace=service_info.get('namespace', 'default'),
                    body=service
                )
                
                logger.info(f"Kubernetes 서비스 생성 완료: {result.metadata.name}")
            
            # 내부 서비스 정보 생성
            service_obj = Service(
                service_id=service_id,
                name=service_info['name'],
                namespace=service_info.get('namespace', 'default'),
                service_type=ServiceType(service_info.get('service_type', 'ClusterIP')),
                cluster_ip='',
                external_ip='',
                ports=service_info.get('ports', []),
                selector=service_info.get('selector', {}),
                endpoints=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            self.services[service_id] = service_obj
            
            # 데이터베이스에 저장
            self._save_service_to_db(service_obj)
            
            logger.info(f"서비스 생성 완료: {service_id}")
            return service_id
            
        except Exception as e:
            logger.error(f"서비스 생성 오류: {e}")
            raise
    
    def scale_deployment(self, deployment_name: str, namespace: str, replicas: int):
        """배포 스케일링"""
        try:
            if self.k8s_client:
                # Kubernetes API를 통한 스케일링
                apps_v1 = client.AppsV1Api()
                apps_v1.patch_namespaced_deployment_scale(
                    name=deployment_name,
                    namespace=namespace,
                    body={'spec': {'replicas': replicas}}
                )
                
                logger.info(f"배포 스케일링 완료: {deployment_name} -> {replicas} replicas")
            
            # 내부 배포 정보 업데이트
            for deployment in self.deployments.values():
                if deployment.name == deployment_name and deployment.namespace == namespace:
                    deployment.replicas = replicas
                    deployment.updated_at = datetime.now()
                    self._save_deployment_to_db(deployment)
                    break
                    
        except Exception as e:
            logger.error(f"배포 스케일링 오류: {e}")
    
    def start_monitoring(self):
        """모니터링 시작"""
        try:
            if self.is_monitoring:
                logger.warning("모니터링이 이미 실행 중입니다")
                return
            
            self.is_monitoring = True
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True
            )
            self.monitoring_thread.start()
            
            logger.info("Kubernetes 모니터링 시작")
            
        except Exception as e:
            logger.error(f"모니터링 시작 오류: {e}")
    
    def _monitoring_loop(self):
        """모니터링 루프"""
        try:
            while self.is_monitoring:
                # Pod 상태 모니터링
                self._monitor_pods()
                
                # Service 상태 모니터링
                self._monitor_services()
                
                # Deployment 상태 모니터링
                self._monitor_deployments()
                
                # Node 상태 모니터링
                self._monitor_nodes()
                
                # 30초 대기
                time.sleep(30)
                
        except Exception as e:
            logger.error(f"모니터링 루프 오류: {e}")
        finally:
            self.is_monitoring = False
    
    def _monitor_pods(self):
        """Pod 상태 모니터링"""
        try:
            if not self.k8s_client:
                return
            
            # 모든 Pod 조회
            pods = self.k8s_client.list_pod_for_all_namespaces()
            
            for pod in pods.items:
                pod_id = pod.metadata.uid
                
                # Pod 정보 생성
                pod_obj = Pod(
                    pod_id=pod_id,
                    name=pod.metadata.name,
                    namespace=pod.metadata.namespace,
                    status=PodStatus(pod.status.phase),
                    node_name=pod.spec.node_name if pod.spec.node_name else '',
                    ip_address=pod.status.pod_ip if pod.status.pod_ip else '',
                    containers=[
                        {
                            'name': container.name,
                            'image': container.image,
                            'ready': container.ready,
                            'restart_count': container.restart_count
                        }
                        for container in pod.status.container_statuses or []
                    ],
                    labels=pod.metadata.labels or {},
                    annotations=pod.metadata.annotations or {},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.pods[pod_id] = pod_obj
                self._save_pod_to_db(pod_obj)
                
        except Exception as e:
            logger.error(f"Pod 모니터링 오류: {e}")
    
    def _monitor_services(self):
        """Service 상태 모니터링"""
        try:
            if not self.k8s_client:
                return
            
            # 모든 Service 조회
            services = self.k8s_client.list_service_for_all_namespaces()
            
            for service in services.items:
                service_id = service.metadata.uid
                
                # Service 정보 생성
                service_obj = Service(
                    service_id=service_id,
                    name=service.metadata.name,
                    namespace=service.metadata.namespace,
                    service_type=ServiceType(service.spec.type),
                    cluster_ip=service.spec.cluster_ip,
                    external_ip=service.status.load_balancer.ingress[0].ip if service.status.load_balancer.ingress else '',
                    ports=[
                        {
                            'port': port.port,
                            'target_port': port.target_port,
                            'protocol': port.protocol
                        }
                        for port in service.spec.ports
                    ],
                    selector=service.spec.selector or {},
                    endpoints=[],
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.services[service_id] = service_obj
                self._save_service_to_db(service_obj)
                
        except Exception as e:
            logger.error(f"Service 모니터링 오류: {e}")
    
    def _monitor_deployments(self):
        """Deployment 상태 모니터링"""
        try:
            if not self.k8s_client:
                return
            
            # 모든 Deployment 조회
            apps_v1 = client.AppsV1Api()
            deployments = apps_v1.list_deployment_for_all_namespaces()
            
            for deployment in deployments.items:
                deployment_id = deployment.metadata.uid
                
                # Deployment 정보 생성
                deployment_obj = Deployment(
                    deployment_id=deployment_id,
                    name=deployment.metadata.name,
                    namespace=deployment.metadata.namespace,
                    replicas=deployment.spec.replicas,
                    available_replicas=deployment.status.available_replicas or 0,
                    strategy=DeploymentStrategy(deployment.spec.strategy.type),
                    image=deployment.spec.template.spec.containers[0].image,
                    labels=deployment.metadata.labels or {},
                    env_vars={},
                    resources={},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.deployments[deployment_id] = deployment_obj
                self._save_deployment_to_db(deployment_obj)
                
        except Exception as e:
            logger.error(f"Deployment 모니터링 오류: {e}")
    
    def _monitor_nodes(self):
        """Node 상태 모니터링"""
        try:
            if not self.k8s_client:
                return
            
            # 모든 Node 조회
            nodes = self.k8s_client.list_node()
            
            for node in nodes.items:
                node_id = node.metadata.uid
                
                # Node 정보 생성
                node_obj = Node(
                    node_id=node_id,
                    name=node.metadata.name,
                    status=node.status.conditions[-1].type if node.status.conditions else 'Unknown',
                    ip_address=node.status.addresses[0].address if node.status.addresses else '',
                    capacity=node.status.capacity,
                    allocatable=node.status.allocatable,
                    conditions=[
                        {
                            'type': condition.type,
                            'status': condition.status,
                            'message': condition.message
                        }
                        for condition in node.status.conditions
                    ],
                    labels=node.metadata.labels or {},
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                self.nodes[node_id] = node_obj
                self._save_node_to_db(node_obj)
                
        except Exception as e:
            logger.error(f"Node 모니터링 오류: {e}")
    
    def get_pod_status(self, pod_name: str, namespace: str = 'default') -> Optional[Pod]:
        """Pod 상태 조회"""
        try:
            for pod in self.pods.values():
                if pod.name == pod_name and pod.namespace == namespace:
                    return pod
            return None
        except Exception as e:
            logger.error(f"Pod 상태 조회 오류: {e}")
            return None
    
    def get_service_endpoints(self, service_name: str, namespace: str = 'default') -> List[str]:
        """서비스 엔드포인트 조회"""
        try:
            if not self.k8s_client:
                return []
            
            # Endpoints 조회
            endpoints = self.k8s_client.read_namespaced_endpoints(
                name=service_name,
                namespace=namespace
            )
            
            endpoint_ips = []
            for subset in endpoints.subsets or []:
                for address in subset.addresses or []:
                    endpoint_ips.append(address.ip)
            
            return endpoint_ips
            
        except Exception as e:
            logger.error(f"서비스 엔드포인트 조회 오류: {e}")
            return []
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """클러스터 상태 조회"""
        try:
            status = {
                'total_pods': len(self.pods),
                'running_pods': len([p for p in self.pods.values() if p.status == PodStatus.RUNNING]),
                'total_services': len(self.services),
                'total_deployments': len(self.deployments),
                'total_nodes': len(self.nodes),
                'healthy_nodes': len([n for n in self.nodes.values() if n.status == 'Ready']),
                'pods_by_namespace': defaultdict(int),
                'services_by_type': defaultdict(int)
            }
            
            # 네임스페이스별 Pod 수
            for pod in self.pods.values():
                status['pods_by_namespace'][pod.namespace] += 1
            
            # 서비스 타입별 수
            for service in self.services.values():
                status['services_by_type'][service.service_type.value] += 1
            
            return status
            
        except Exception as e:
            logger.error(f"클러스터 상태 조회 오류: {e}")
            return {}
    
    def apply_yaml_config(self, yaml_content: str) -> Dict[str, str]:
        """YAML 설정 적용"""
        try:
            results = {}
            
            # YAML 파싱
            configs = yaml.safe_load_all(yaml_content)
            
            for config in configs:
                kind = config.get('kind', '')
                name = config.get('metadata', {}).get('name', '')
                namespace = config.get('metadata', {}).get('namespace', 'default')
                
                if kind == 'Deployment':
                    deployment_id = self.create_deployment(config)
                    results[f"{kind}:{name}"] = deployment_id
                    
                elif kind == 'Service':
                    service_id = self.create_service(config)
                    results[f"{kind}:{name}"] = service_id
                    
                elif kind == 'ConfigMap':
                    # ConfigMap 생성
                    if self.k8s_client:
                        config_map = client.V1ConfigMap(
                            metadata=client.V1ObjectMeta(
                                name=name,
                                namespace=namespace
                            ),
                            data=config.get('data', {})
                        )
                        
                        self.k8s_client.create_namespaced_config_map(
                            namespace=namespace,
                            body=config_map
                        )
                        results[f"{kind}:{name}"] = "created"
                        
                elif kind == 'Secret':
                    # Secret 생성
                    if self.k8s_client:
                        secret = client.V1Secret(
                            metadata=client.V1ObjectMeta(
                                name=name,
                                namespace=namespace
                            ),
                            data=config.get('data', {}),
                            type=config.get('type', 'Opaque')
                        )
                        
                        self.k8s_client.create_namespaced_secret(
                            namespace=namespace,
                            body=secret
                        )
                        results[f"{kind}:{name}"] = "created"
            
            return results
            
        except Exception as e:
            logger.error(f"YAML 설정 적용 오류: {e}")
            raise
    
    def _save_pod_to_db(self, pod: Pod):
        """Pod를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO pods 
                (pod_id, name, namespace, status, node_name, ip_address,
                 containers, labels, annotations, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pod.pod_id,
                pod.name,
                pod.namespace,
                pod.status.value,
                pod.node_name,
                pod.ip_address,
                json.dumps(pod.containers),
                json.dumps(pod.labels),
                json.dumps(pod.annotations),
                pod.created_at.isoformat(),
                pod.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Pod 데이터베이스 저장 오류: {e}")
    
    def _save_service_to_db(self, service: Service):
        """Service를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO services 
                (service_id, name, namespace, service_type, cluster_ip,
                 external_ip, ports, selector, endpoints, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                service.service_id,
                service.name,
                service.namespace,
                service.service_type.value,
                service.cluster_ip,
                service.external_ip,
                json.dumps(service.ports),
                json.dumps(service.selector),
                json.dumps(service.endpoints),
                service.created_at.isoformat(),
                service.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Service 데이터베이스 저장 오류: {e}")
    
    def _save_deployment_to_db(self, deployment: Deployment):
        """Deployment를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO deployments 
                (deployment_id, name, namespace, replicas, available_replicas,
                 strategy, image, labels, env_vars, resources, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                deployment.deployment_id,
                deployment.name,
                deployment.namespace,
                deployment.replicas,
                deployment.available_replicas,
                deployment.strategy.value,
                deployment.image,
                json.dumps(deployment.labels),
                json.dumps(deployment.env_vars),
                json.dumps(deployment.resources),
                deployment.created_at.isoformat(),
                deployment.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Deployment 데이터베이스 저장 오류: {e}")
    
    def _save_node_to_db(self, node: Node):
        """Node를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO nodes 
                (node_id, name, status, ip_address, capacity, allocatable,
                 conditions, labels, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                node.node_id,
                node.name,
                node.status,
                node.ip_address,
                json.dumps(node.capacity),
                json.dumps(node.allocatable),
                json.dumps(node.conditions),
                json.dumps(node.labels),
                node.created_at.isoformat(),
                node.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Node 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            self.is_monitoring = False
            self.is_scaling = False
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("Kubernetes 오케스트레이터 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './kubernetes.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 5
        }
    }
    
    # Kubernetes 오케스트레이터 생성
    k8s_orchestrator = KubernetesOrchestrator(config)
    
    # 배포 생성
    deployment_info = {
        'name': 'web-app',
        'namespace': 'default',
        'replicas': 3,
        'image': 'nginx:latest',
        'ports': [{'containerPort': 80}],
        'env_vars': {
            'NODE_ENV': 'production',
            'PORT': '80'
        },
        'resources': {
            'requests': {'cpu': '100m', 'memory': '128Mi'},
            'limits': {'cpu': '500m', 'memory': '512Mi'}
        },
        'labels': {'app': 'web-app', 'tier': 'frontend'}
    }
    
    deployment_id = k8s_orchestrator.create_deployment(deployment_info)
    print(f"배포 생성 완료: {deployment_id}")
    
    # 서비스 생성
    service_info = {
        'name': 'web-app-service',
        'namespace': 'default',
        'service_type': 'LoadBalancer',
        'ports': [{'port': 80, 'target_port': 80}],
        'selector': {'app': 'web-app'},
        'labels': {'app': 'web-app'}
    }
    
    service_id = k8s_orchestrator.create_service(service_info)
    print(f"서비스 생성 완료: {service_id}")
    
    # 모니터링 시작
    k8s_orchestrator.start_monitoring()
    
    # 클러스터 상태 조회
    status = k8s_orchestrator.get_cluster_status()
    print(f"클러스터 상태: {status}")
    
    # 배포 스케일링
    k8s_orchestrator.scale_deployment('web-app', 'default', 5)
    print("배포 스케일링 완료") 