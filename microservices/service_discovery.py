"""
서비스 디스커버리 시스템
서비스 등록, 서비스 발견, 헬스 체크, 로드 밸런싱을 포함한 완전한 서비스 디스커버리 플랫폼
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
import redis
from redis.exceptions import RedisError
import consul
import etcd3
from etcd3.exceptions import Etcd3Exception
import random
import statistics
from collections import defaultdict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """서비스 상태"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"

class LoadBalancingStrategy(Enum):
    """로드 밸런싱 전략"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    RANDOM = "random"

class HealthCheckType(Enum):
    """헬스 체크 타입"""
    HTTP = "http"
    TCP = "tcp"
    GRPC = "grpc"
    COMMAND = "command"
    SCRIPT = "script"

@dataclass
class ServiceInstance:
    """서비스 인스턴스"""
    instance_id: str
    service_name: str
    service_id: str
    host: str
    port: int
    protocol: str
    status: ServiceStatus
    health_score: float
    load_balancer_weight: int
    metadata: Dict[str, Any]
    tags: List[str]
    version: str
    region: str
    zone: str
    registered_at: datetime
    last_heartbeat: datetime
    last_health_check: datetime

@dataclass
class ServiceRegistration:
    """서비스 등록"""
    registration_id: str
    service_name: str
    service_id: str
    host: str
    port: int
    protocol: str
    health_check_config: Dict[str, Any]
    load_balancer_config: Dict[str, Any]
    metadata: Dict[str, Any]
    tags: List[str]
    version: str
    region: str
    zone: str
    ttl: int
    created_at: datetime

@dataclass
class HealthCheck:
    """헬스 체크"""
    check_id: str
    service_id: str
    check_type: HealthCheckType
    endpoint: str
    interval: int
    timeout: int
    retries: int
    success_threshold: int
    failure_threshold: int
    enabled: bool
    created_at: datetime

@dataclass
class LoadBalancer:
    """로드 밸런서"""
    lb_id: str
    service_name: str
    strategy: LoadBalancingStrategy
    instances: List[ServiceInstance]
    weights: Dict[str, int]
    connection_counts: Dict[str, int]
    last_used: Dict[str, datetime]
    created_at: datetime

class ServiceDiscoverySystem:
    """서비스 디스커버리 시스템"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.instances: Dict[str, ServiceInstance] = {}
        self.registrations: Dict[str, ServiceRegistration] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        
        # 서비스 레지스트리 (서비스명 -> 인스턴스 목록)
        self.service_registry: Dict[str, List[ServiceInstance]] = defaultdict(list)
        
        # Redis 클라이언트
        self.redis_client = None
        self._init_redis()
        
        # Consul 클라이언트
        self.consul_client = None
        self._init_consul()
        
        # Etcd 클라이언트
        self.etcd_client = None
        self._init_etcd()
        
        # HTTP 클라이언트 세션
        self.http_session = None
        
        # 데이터베이스
        self.db_path = Path(config.get('db_path', './service_discovery.db'))
        self._init_database()
        
        # 헬스 체크 스레드
        self.health_check_thread = None
        self.is_running = False
        
        # 로드 밸런싱 인덱스
        self.round_robin_indexes: Dict[str, int] = defaultdict(int)
        
        logger.info("서비스 디스커버리 시스템 초기화 완료")
    
    def _init_redis(self):
        """Redis 클라이언트 초기화"""
        try:
            redis_config = self.config.get('redis', {})
            self.redis_client = redis.Redis(
                host=redis_config.get('host', 'localhost'),
                port=redis_config.get('port', 6379),
                db=redis_config.get('db', 1),
                decode_responses=True
            )
            
            # Redis 연결 테스트
            self.redis_client.ping()
            logger.info("Redis 클라이언트 초기화 완료")
            
        except RedisError as e:
            logger.warning(f"Redis 클라이언트 초기화 실패: {e}")
            self.redis_client = None
    
    def _init_consul(self):
        """Consul 클라이언트 초기화"""
        try:
            consul_config = self.config.get('consul', {})
            self.consul_client = consul.Consul(
                host=consul_config.get('host', 'localhost'),
                port=consul_config.get('port', 8500),
                token=consul_config.get('token')
            )
            
            logger.info("Consul 클라이언트 초기화 완료")
            
        except Exception as e:
            logger.warning(f"Consul 클라이언트 초기화 실패: {e}")
            self.consul_client = None
    
    def _init_etcd(self):
        """Etcd 클라이언트 초기화"""
        try:
            etcd_config = self.config.get('etcd', {})
            self.etcd_client = etcd3.client(
                host=etcd_config.get('host', 'localhost'),
                port=etcd_config.get('port', 2379)
            )
            
            logger.info("Etcd 클라이언트 초기화 완료")
            
        except Etcd3Exception as e:
            logger.warning(f"Etcd 클라이언트 초기화 실패: {e}")
            self.etcd_client = None
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 서비스 인스턴스 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_instances (
                    instance_id TEXT PRIMARY KEY,
                    service_name TEXT,
                    service_id TEXT,
                    host TEXT,
                    port INTEGER,
                    protocol TEXT,
                    status TEXT,
                    health_score REAL,
                    load_balancer_weight INTEGER,
                    metadata TEXT,
                    tags TEXT,
                    version TEXT,
                    region TEXT,
                    zone TEXT,
                    registered_at TEXT,
                    last_heartbeat TEXT,
                    last_health_check TEXT
                )
            ''')
            
            # 서비스 등록 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS service_registrations (
                    registration_id TEXT PRIMARY KEY,
                    service_name TEXT,
                    service_id TEXT,
                    host TEXT,
                    port INTEGER,
                    protocol TEXT,
                    health_check_config TEXT,
                    load_balancer_config TEXT,
                    metadata TEXT,
                    tags TEXT,
                    version TEXT,
                    region TEXT,
                    zone TEXT,
                    ttl INTEGER,
                    created_at TEXT
                )
            ''')
            
            # 헬스 체크 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS health_checks (
                    check_id TEXT PRIMARY KEY,
                    service_id TEXT,
                    check_type TEXT,
                    endpoint TEXT,
                    interval INTEGER,
                    timeout INTEGER,
                    retries INTEGER,
                    success_threshold INTEGER,
                    failure_threshold INTEGER,
                    enabled INTEGER,
                    created_at TEXT
                )
            ''')
            
            # 로드 밸런서 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS load_balancers (
                    lb_id TEXT PRIMARY KEY,
                    service_name TEXT,
                    strategy TEXT,
                    instances TEXT,
                    weights TEXT,
                    connection_counts TEXT,
                    last_used TEXT,
                    created_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("서비스 디스커버리 데이터베이스 초기화 완료")
            
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {e}")
            raise
    
    def register_service(self, registration_info: Dict[str, Any]) -> str:
        """서비스 등록"""
        try:
            registration_id = str(uuid.uuid4())
            instance_id = str(uuid.uuid4())
            
            # 서비스 등록 생성
            registration = ServiceRegistration(
                registration_id=registration_id,
                service_name=registration_info['service_name'],
                service_id=registration_info['service_id'],
                host=registration_info['host'],
                port=registration_info['port'],
                protocol=registration_info.get('protocol', 'http'),
                health_check_config=registration_info.get('health_check', {}),
                load_balancer_config=registration_info.get('load_balancer', {}),
                metadata=registration_info.get('metadata', {}),
                tags=registration_info.get('tags', []),
                version=registration_info.get('version', '1.0.0'),
                region=registration_info.get('region', 'default'),
                zone=registration_info.get('zone', 'default'),
                ttl=registration_info.get('ttl', 300),
                created_at=datetime.now()
            )
            
            # 서비스 인스턴스 생성
            instance = ServiceInstance(
                instance_id=instance_id,
                service_name=registration.service_name,
                service_id=registration.service_id,
                host=registration.host,
                port=registration.port,
                protocol=registration.protocol,
                status=ServiceStatus.STARTING,
                health_score=1.0,
                load_balancer_weight=registration.load_balancer_config.get('weight', 1),
                metadata=registration.metadata,
                tags=registration.tags,
                version=registration.version,
                region=registration.region,
                zone=registration.zone,
                registered_at=datetime.now(),
                last_heartbeat=datetime.now(),
                last_health_check=datetime.now()
            )
            
            self.registrations[registration_id] = registration
            self.instances[instance_id] = instance
            self.service_registry[registration.service_name].append(instance)
            
            # 헬스 체크 설정
            if registration.health_check_config:
                health_check = self._create_health_check(instance_id, registration.health_check_config)
                self.health_checks[health_check.check_id] = health_check
            
            # 로드 밸런서 생성
            if registration.service_name not in self.load_balancers:
                load_balancer = self._create_load_balancer(registration.service_name, registration.load_balancer_config)
                self.load_balancers[registration.service_name] = load_balancer
            
            # 외부 레지스트리에 등록
            self._register_to_external_registry(registration, instance)
            
            # 데이터베이스에 저장
            self._save_registration_to_db(registration)
            self._save_instance_to_db(instance)
            
            logger.info(f"서비스 등록 완료: {registration_id}")
            return registration_id
            
        except Exception as e:
            logger.error(f"서비스 등록 오류: {e}")
            raise
    
    def _create_health_check(self, service_id: str, health_check_config: Dict[str, Any]) -> HealthCheck:
        """헬스 체크 생성"""
        try:
            check_id = str(uuid.uuid4())
            
            health_check = HealthCheck(
                check_id=check_id,
                service_id=service_id,
                check_type=HealthCheckType(health_check_config.get('type', 'http')),
                endpoint=health_check_config.get('endpoint', '/health'),
                interval=health_check_config.get('interval', 30),
                timeout=health_check_config.get('timeout', 5),
                retries=health_check_config.get('retries', 3),
                success_threshold=health_check_config.get('success_threshold', 1),
                failure_threshold=health_check_config.get('failure_threshold', 3),
                enabled=health_check_config.get('enabled', True),
                created_at=datetime.now()
            )
            
            return health_check
            
        except Exception as e:
            logger.error(f"헬스 체크 생성 오류: {e}")
            raise
    
    def _create_load_balancer(self, service_name: str, lb_config: Dict[str, Any]) -> LoadBalancer:
        """로드 밸런서 생성"""
        try:
            lb_id = str(uuid.uuid4())
            
            load_balancer = LoadBalancer(
                lb_id=lb_id,
                service_name=service_name,
                strategy=LoadBalancingStrategy(lb_config.get('strategy', 'round_robin')),
                instances=[],
                weights={},
                connection_counts={},
                last_used={},
                created_at=datetime.now()
            )
            
            return load_balancer
            
        except Exception as e:
            logger.error(f"로드 밸런서 생성 오류: {e}")
            raise
    
    def _register_to_external_registry(self, registration: ServiceRegistration, instance: ServiceInstance):
        """외부 레지스트리에 등록"""
        try:
            # Redis에 등록
            if self.redis_client:
                service_key = f"service:{registration.service_name}"
                instance_data = {
                    'instance_id': instance.instance_id,
                    'host': instance.host,
                    'port': instance.port,
                    'protocol': instance.protocol,
                    'status': instance.status.value,
                    'health_score': instance.health_score,
                    'metadata': instance.metadata,
                    'tags': instance.tags,
                    'version': instance.version,
                    'region': instance.region,
                    'zone': instance.zone,
                    'registered_at': instance.registered_at.isoformat()
                }
                
                self.redis_client.hset(service_key, instance.instance_id, json.dumps(instance_data))
                self.redis_client.expire(service_key, registration.ttl)
            
            # Consul에 등록
            if self.consul_client:
                service_id = f"{registration.service_name}-{instance.instance_id[:8]}"
                
                self.consul_client.agent.service.register(
                    name=registration.service_name,
                    service_id=service_id,
                    address=instance.host,
                    port=instance.port,
                    tags=instance.tags,
                    meta=instance.metadata,
                    check={
                        'http': f"{instance.protocol}://{instance.host}:{instance.port}{registration.health_check_config.get('endpoint', '/health')}",
                        'interval': f"{registration.health_check_config.get('interval', 30)}s",
                        'timeout': f"{registration.health_check_config.get('timeout', 5)}s"
                    }
                )
            
            # Etcd에 등록
            if self.etcd_client:
                service_key = f"/services/{registration.service_name}/{instance.instance_id}"
                service_value = json.dumps({
                    'host': instance.host,
                    'port': instance.port,
                    'protocol': instance.protocol,
                    'status': instance.status.value,
                    'metadata': instance.metadata,
                    'registered_at': instance.registered_at.isoformat()
                })
                
                self.etcd_client.put(service_key, service_value.encode())
            
        except Exception as e:
            logger.error(f"외부 레지스트리 등록 오류: {e}")
    
    def discover_service(self, service_name: str, strategy: LoadBalancingStrategy = None) -> Optional[ServiceInstance]:
        """서비스 발견"""
        try:
            instances = self.service_registry.get(service_name, [])
            
            if not instances:
                return None
            
            # 정상 인스턴스만 필터링
            healthy_instances = [instance for instance in instances if instance.status == ServiceStatus.HEALTHY]
            
            if not healthy_instances:
                return None
            
            # 로드 밸런서 가져오기
            load_balancer = self.load_balancers.get(service_name)
            
            if not load_balancer:
                # 기본 로드 밸런서 생성
                load_balancer = LoadBalancer(
                    lb_id=str(uuid.uuid4()),
                    service_name=service_name,
                    strategy=LoadBalancingStrategy.ROUND_ROBIN,
                    instances=healthy_instances,
                    weights={},
                    connection_counts={},
                    last_used={},
                    created_at=datetime.now()
                )
                self.load_balancers[service_name] = load_balancer
            
            # 로드 밸런싱 전략에 따라 인스턴스 선택
            selected_instance = self._select_instance(load_balancer, healthy_instances, strategy)
            
            if selected_instance:
                # 연결 수 증가
                load_balancer.connection_counts[selected_instance.instance_id] = \
                    load_balancer.connection_counts.get(selected_instance.instance_id, 0) + 1
                load_balancer.last_used[selected_instance.instance_id] = datetime.now()
            
            return selected_instance
            
        except Exception as e:
            logger.error(f"서비스 발견 오류: {e}")
            return None
    
    def _select_instance(self, load_balancer: LoadBalancer, instances: List[ServiceInstance], 
                        strategy: LoadBalancingStrategy = None) -> Optional[ServiceInstance]:
        """인스턴스 선택"""
        try:
            if not instances:
                return None
            
            strategy = strategy or load_balancer.strategy
            
            if strategy == LoadBalancingStrategy.ROUND_ROBIN:
                return self._round_robin_selection(load_balancer, instances)
            
            elif strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
                return self._least_connections_selection(load_balancer, instances)
            
            elif strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin_selection(load_balancer, instances)
            
            elif strategy == LoadBalancingStrategy.IP_HASH:
                return self._ip_hash_selection(instances)
            
            elif strategy == LoadBalancingStrategy.RANDOM:
                return self._random_selection(instances)
            
            else:
                return instances[0]
                
        except Exception as e:
            logger.error(f"인스턴스 선택 오류: {e}")
            return instances[0] if instances else None
    
    def _round_robin_selection(self, load_balancer: LoadBalancer, instances: List[ServiceInstance]) -> ServiceInstance:
        """라운드 로빈 선택"""
        try:
            index = self.round_robin_indexes[load_balancer.service_name] % len(instances)
            selected_instance = instances[index]
            self.round_robin_indexes[load_balancer.service_name] += 1
            return selected_instance
        except Exception as e:
            logger.error(f"라운드 로빈 선택 오류: {e}")
            return instances[0] if instances else None
    
    def _least_connections_selection(self, load_balancer: LoadBalancer, instances: List[ServiceInstance]) -> ServiceInstance:
        """최소 연결 선택"""
        try:
            min_connections = float('inf')
            selected_instance = None
            
            for instance in instances:
                connections = load_balancer.connection_counts.get(instance.instance_id, 0)
                if connections < min_connections:
                    min_connections = connections
                    selected_instance = instance
            
            return selected_instance
        except Exception as e:
            logger.error(f"최소 연결 선택 오류: {e}")
            return instances[0] if instances else None
    
    def _weighted_round_robin_selection(self, load_balancer: LoadBalancer, instances: List[ServiceInstance]) -> ServiceInstance:
        """가중 라운드 로빈 선택"""
        try:
            total_weight = sum(instance.load_balancer_weight for instance in instances)
            
            if total_weight == 0:
                return instances[0] if instances else None
            
            # 가중치 기반 선택
            random_value = random.uniform(0, total_weight)
            current_weight = 0
            
            for instance in instances:
                current_weight += instance.load_balancer_weight
                if random_value <= current_weight:
                    return instance
            
            return instances[0] if instances else None
        except Exception as e:
            logger.error(f"가중 라운드 로빈 선택 오류: {e}")
            return instances[0] if instances else None
    
    def _ip_hash_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """IP 해시 선택"""
        try:
            # 클라이언트 IP 기반 해시 (실제로는 요청 컨텍스트에서 가져옴)
            client_ip = "127.0.0.1"  # 실제로는 요청에서 추출
            hash_value = hash(client_ip)
            index = hash_value % len(instances)
            return instances[index]
        except Exception as e:
            logger.error(f"IP 해시 선택 오류: {e}")
            return instances[0] if instances else None
    
    def _random_selection(self, instances: List[ServiceInstance]) -> ServiceInstance:
        """랜덤 선택"""
        try:
            return random.choice(instances)
        except Exception as e:
            logger.error(f"랜덤 선택 오류: {e}")
            return instances[0] if instances else None
    
    async def perform_health_check(self, instance: ServiceInstance) -> bool:
        """헬스 체크 수행"""
        try:
            health_check = None
            for check in self.health_checks.values():
                if check.service_id == instance.instance_id:
                    health_check = check
                    break
            
            if not health_check or not health_check.enabled:
                return True
            
            # HTTP 헬스 체크
            if health_check.check_type == HealthCheckType.HTTP:
                return await self._http_health_check(instance, health_check)
            
            # TCP 헬스 체크
            elif health_check.check_type == HealthCheckType.TCP:
                return self._tcp_health_check(instance, health_check)
            
            # gRPC 헬스 체크
            elif health_check.check_type == HealthCheckType.GRPC:
                return await self._grpc_health_check(instance, health_check)
            
            else:
                return True
                
        except Exception as e:
            logger.error(f"헬스 체크 수행 오류: {e}")
            return False
    
    async def _http_health_check(self, instance: ServiceInstance, health_check: HealthCheck) -> bool:
        """HTTP 헬스 체크"""
        try:
            if not self.http_session:
                timeout = ClientTimeout(total=health_check.timeout)
                self.http_session = ClientSession(timeout=timeout)
            
            url = f"{instance.protocol}://{instance.host}:{instance.port}{health_check.endpoint}"
            
            async with self.http_session.get(url) as response:
                is_healthy = response.status == 200
                
                # 헬스 점수 업데이트
                instance.health_score = 1.0 if is_healthy else 0.0
                instance.status = ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY
                instance.last_health_check = datetime.now()
                
                return is_healthy
                
        except Exception as e:
            logger.error(f"HTTP 헬스 체크 오류: {e}")
            instance.health_score = 0.0
            instance.status = ServiceStatus.UNHEALTHY
            instance.last_health_check = datetime.now()
            return False
    
    def _tcp_health_check(self, instance: ServiceInstance, health_check: HealthCheck) -> bool:
        """TCP 헬스 체크"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(health_check.timeout)
            
            result = sock.connect_ex((instance.host, instance.port))
            sock.close()
            
            is_healthy = result == 0
            
            # 헬스 점수 업데이트
            instance.health_score = 1.0 if is_healthy else 0.0
            instance.status = ServiceStatus.HEALTHY if is_healthy else ServiceStatus.UNHEALTHY
            instance.last_health_check = datetime.now()
            
            return is_healthy
            
        except Exception as e:
            logger.error(f"TCP 헬스 체크 오류: {e}")
            instance.health_score = 0.0
            instance.status = ServiceStatus.UNHEALTHY
            instance.last_health_check = datetime.now()
            return False
    
    async def _grpc_health_check(self, instance: ServiceInstance, health_check: HealthCheck) -> bool:
        """gRPC 헬스 체크"""
        try:
            # gRPC 헬스 체크 구현 (실제로는 grpcio 라이브러리 사용)
            # 여기서는 간단한 HTTP 체크로 대체
            return await self._http_health_check(instance, health_check)
            
        except Exception as e:
            logger.error(f"gRPC 헬스 체크 오류: {e}")
            return False
    
    def get_service_instances(self, service_name: str) -> List[ServiceInstance]:
        """서비스 인스턴스 조회"""
        try:
            return self.service_registry.get(service_name, [])
        except Exception as e:
            logger.error(f"서비스 인스턴스 조회 오류: {e}")
            return []
    
    def get_healthy_instances(self, service_name: str) -> List[ServiceInstance]:
        """정상 인스턴스 조회"""
        try:
            instances = self.service_registry.get(service_name, [])
            return [instance for instance in instances if instance.status == ServiceStatus.HEALTHY]
        except Exception as e:
            logger.error(f"정상 인스턴스 조회 오류: {e}")
            return []
    
    def get_service_health(self, service_name: str) -> Dict[str, Any]:
        """서비스 헬스 상태 조회"""
        try:
            instances = self.service_registry.get(service_name, [])
            
            if not instances:
                return {
                    'service_name': service_name,
                    'status': 'no_instances',
                    'healthy_count': 0,
                    'total_count': 0,
                    'health_score': 0.0
                }
            
            healthy_count = sum(1 for instance in instances if instance.status == ServiceStatus.HEALTHY)
            total_count = len(instances)
            health_score = healthy_count / total_count if total_count > 0 else 0.0
            
            return {
                'service_name': service_name,
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
                        'health_score': instance.health_score,
                        'last_health_check': instance.last_health_check.isoformat()
                    }
                    for instance in instances
                ]
            }
            
        except Exception as e:
            logger.error(f"서비스 헬스 상태 조회 오류: {e}")
            return {
                'service_name': service_name,
                'status': 'error',
                'error': str(e)
            }
    
    def _save_registration_to_db(self, registration: ServiceRegistration):
        """등록을 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO service_registrations 
                (registration_id, service_name, service_id, host, port, protocol,
                 health_check_config, load_balancer_config, metadata, tags, version,
                 region, zone, ttl, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                registration.registration_id,
                registration.service_name,
                registration.service_id,
                registration.host,
                registration.port,
                registration.protocol,
                json.dumps(registration.health_check_config),
                json.dumps(registration.load_balancer_config),
                json.dumps(registration.metadata),
                json.dumps(registration.tags),
                registration.version,
                registration.region,
                registration.zone,
                registration.ttl,
                registration.created_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"등록 데이터베이스 저장 오류: {e}")
    
    def _save_instance_to_db(self, instance: ServiceInstance):
        """인스턴스를 데이터베이스에 저장"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO service_instances 
                (instance_id, service_name, service_id, host, port, protocol, status,
                 health_score, load_balancer_weight, metadata, tags, version, region,
                 zone, registered_at, last_heartbeat, last_health_check)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                instance.instance_id,
                instance.service_name,
                instance.service_id,
                instance.host,
                instance.port,
                instance.protocol,
                instance.status.value,
                instance.health_score,
                instance.load_balancer_weight,
                json.dumps(instance.metadata),
                json.dumps(instance.tags),
                instance.version,
                instance.region,
                instance.zone,
                instance.registered_at.isoformat(),
                instance.last_heartbeat.isoformat(),
                instance.last_health_check.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"인스턴스 데이터베이스 저장 오류: {e}")
    
    def destroy(self):
        """서비스 정리"""
        try:
            if self.http_session:
                asyncio.create_task(self.http_session.close())
            
            if self.redis_client:
                self.redis_client.close()
            
            logger.info("서비스 디스커버리 시스템 정리 완료")
        except Exception as e:
            logger.error(f"서비스 정리 오류: {e}")

# 사용 예시
if __name__ == "__main__":
    # 설정
    config = {
        'db_path': './service_discovery.db',
        'redis': {
            'host': 'localhost',
            'port': 6379,
            'db': 1
        },
        'consul': {
            'host': 'localhost',
            'port': 8500
        },
        'etcd': {
            'host': 'localhost',
            'port': 2379
        }
    }
    
    # 서비스 디스커버리 시스템 생성
    discovery_system = ServiceDiscoverySystem(config)
    
    # 서비스 등록
    service_info = {
        'service_name': 'user-service',
        'service_id': 'user-service-v1',
        'host': 'localhost',
        'port': 8081,
        'protocol': 'http',
        'health_check': {
            'type': 'http',
            'endpoint': '/health',
            'interval': 30,
            'timeout': 5
        },
        'load_balancer': {
            'strategy': 'round_robin',
            'weight': 1
        },
        'metadata': {
            'version': '1.0.0',
            'environment': 'production'
        },
        'tags': ['api', 'user'],
        'version': '1.0.0',
        'region': 'us-west',
        'zone': 'us-west-1',
        'ttl': 300
    }
    
    registration_id = discovery_system.register_service(service_info)
    print(f"서비스 등록 완료: {registration_id}")
    
    # 서비스 발견
    instance = discovery_system.discover_service('user-service')
    if instance:
        print(f"서비스 발견: {instance.host}:{instance.port}")
    
    # 서비스 헬스 상태 조회
    health_status = discovery_system.get_service_health('user-service')
    print(f"서비스 헬스 상태: {health_status}")
    
    # 서비스 인스턴스 조회
    instances = discovery_system.get_service_instances('user-service')
    print(f"서비스 인스턴스: {len(instances)}개") 