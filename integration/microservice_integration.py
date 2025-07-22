"""
마이크로서비스 통합 시스템
서비스 디스커버리, 로드 밸런싱, 서킷 브레이커, 서비스 메시 기능
"""

import json
import logging
import time
import threading
import requests
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import uuid
from pathlib import Path
from collections import defaultdict, deque
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# 로깅 설정
logger = logging.getLogger(__name__)

class ServiceStatus(Enum):
    """서비스 상태"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

class CircuitBreakerState(Enum):
    """서킷 브레이커 상태"""
    CLOSED = "closed"      # 정상 상태
    OPEN = "open"          # 차단 상태
    HALF_OPEN = "half_open"  # 반열림 상태

@dataclass
class ServiceInstance:
    """서비스 인스턴스"""
    id: str
    service_name: str
    host: str
    port: int
    protocol: str
    health_check_url: str
    status: ServiceStatus
    last_health_check: datetime
    response_time: float
    error_count: int
    success_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

@dataclass
class ServiceDefinition:
    """서비스 정의"""
    id: str
    name: str
    version: str
    description: str
    endpoints: List[Dict[str, Any]]
    health_check_interval: int
    timeout: int
    retry_count: int
    circuit_breaker_config: Dict[str, Any]
    load_balancer_config: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    is_active: bool

@dataclass
class CircuitBreaker:
    """서킷 브레이커"""
    service_name: str
    state: CircuitBreakerState
    failure_threshold: int
    success_threshold: int
    timeout_seconds: int
    failure_count: int
    success_count: int
    last_failure_time: Optional[datetime]
    last_state_change: datetime

class LoadBalancer:
    """로드 밸런서"""
    
    def __init__(self, strategy: str = "round_robin"):
        self.strategy = strategy
        self.current_index = 0
        self.lock = threading.Lock()
    
    def select_instance(self, instances: List[ServiceInstance]) -> Optional[ServiceInstance]:
        """인스턴스 선택"""
        if not instances:
            return None
        
        healthy_instances = [inst for inst in instances if inst.status == ServiceStatus.HEALTHY]
        if not healthy_instances:
            return None
        
        with self.lock:
            if self.strategy == "round_robin":
                instance = healthy_instances[self.current_index % len(healthy_instances)]
                self.current_index += 1
                return instance
            
            elif self.strategy == "random":
                return random.choice(healthy_instances)
            
            elif self.strategy == "least_connections":
                return min(healthy_instances, key=lambda x: x.metadata.get('active_connections', 0))
            
            elif self.strategy == "weighted":
                # 가중치 기반 선택
                total_weight = sum(inst.metadata.get('weight', 1) for inst in healthy_instances)
                rand = random.uniform(0, total_weight)
                current_weight = 0
                
                for instance in healthy_instances:
                    current_weight += instance.metadata.get('weight', 1)
                    if rand <= current_weight:
                        return instance
                
                return healthy_instances[0]
            
            else:
                return healthy_instances[0]

class MicroserviceIntegration:
    """마이크로서비스 통합 시스템"""
    
    def __init__(self, db_path: str = "data/integration/microservices.db"):
        self.db_path = db_path
        self.services: Dict[str, ServiceDefinition] = {}
        self.instances: Dict[str, List[ServiceInstance]] = defaultdict(list)
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.health_check_threads: Dict[str, threading.Thread] = {}
        self.service_mesh: Dict[str, Any] = {}
        
        # 비동기 HTTP 클라이언트
        self.session = None
        
        # 디렉토리 생성
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # 데이터베이스 초기화
        self.initialize_database()
        
        # 기본 서비스 등록
        self.register_default_services()
        
        # 헬스 체크 시작
        self.start_health_checks()
    
    def initialize_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 서비스 정의 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS service_definitions (
                        id TEXT PRIMARY KEY,
                        name TEXT NOT NULL,
                        version TEXT NOT NULL,
                        description TEXT,
                        endpoints TEXT NOT NULL,
                        health_check_interval INTEGER NOT NULL,
                        timeout INTEGER NOT NULL,
                        retry_count INTEGER NOT NULL,
                        circuit_breaker_config TEXT NOT NULL,
                        load_balancer_config TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL,
                        is_active INTEGER NOT NULL
                    )
                """)
                
                # 서비스 인스턴스 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS service_instances (
                        id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        host TEXT NOT NULL,
                        port INTEGER NOT NULL,
                        protocol TEXT NOT NULL,
                        health_check_url TEXT NOT NULL,
                        status TEXT NOT NULL,
                        last_health_check TEXT NOT NULL,
                        response_time REAL NOT NULL,
                        error_count INTEGER NOT NULL,
                        success_count INTEGER NOT NULL,
                        metadata TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # 서킷 브레이커 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS circuit_breakers (
                        service_name TEXT PRIMARY KEY,
                        state TEXT NOT NULL,
                        failure_threshold INTEGER NOT NULL,
                        success_threshold INTEGER NOT NULL,
                        timeout_seconds INTEGER NOT NULL,
                        failure_count INTEGER NOT NULL,
                        success_count INTEGER NOT NULL,
                        last_failure_time TEXT,
                        last_state_change TEXT NOT NULL
                    )
                """)
                
                # 서비스 메시 테이블
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS service_mesh (
                        id TEXT PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        mesh_config TEXT NOT NULL,
                        routing_rules TEXT NOT NULL,
                        security_policies TEXT NOT NULL,
                        created_at TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                """)
                
                # 인덱스 생성
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_instances_service ON service_instances(service_name)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_instances_status ON service_instances(status)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_breakers_service ON circuit_breakers(service_name)")
                
                conn.commit()
                logger.info("마이크로서비스 통합 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 오류: {str(e)}")
            raise
    
    def register_default_services(self):
        """기본 서비스 등록"""
        # 사용자 관리 서비스
        self.register_service(
            name="user-service",
            version="1.0.0",
            description="사용자 관리 서비스",
            endpoints=[
                {"path": "/users", "method": "GET", "description": "사용자 목록 조회"},
                {"path": "/users/{id}", "method": "GET", "description": "사용자 상세 조회"},
                {"path": "/users", "method": "POST", "description": "사용자 생성"},
                {"path": "/users/{id}", "method": "PUT", "description": "사용자 수정"},
                {"path": "/users/{id}", "method": "DELETE", "description": "사용자 삭제"}
            ],
            health_check_interval=30,
            timeout=10,
            retry_count=3,
            circuit_breaker_config={
                "failure_threshold": 5,
                "success_threshold": 2,
                "timeout_seconds": 60
            },
            load_balancer_config={
                "strategy": "round_robin",
                "health_check_enabled": True
            }
        )
        
        # 주문 관리 서비스
        self.register_service(
            name="order-service",
            version="1.0.0",
            description="주문 관리 서비스",
            endpoints=[
                {"path": "/orders", "method": "GET", "description": "주문 목록 조회"},
                {"path": "/orders/{id}", "method": "GET", "description": "주문 상세 조회"},
                {"path": "/orders", "method": "POST", "description": "주문 생성"},
                {"path": "/orders/{id}/status", "method": "PUT", "description": "주문 상태 변경"}
            ],
            health_check_interval=30,
            timeout=15,
            retry_count=3,
            circuit_breaker_config={
                "failure_threshold": 3,
                "success_threshold": 2,
                "timeout_seconds": 120
            },
            load_balancer_config={
                "strategy": "least_connections",
                "health_check_enabled": True
            }
        )
        
        # 결제 서비스
        self.register_service(
            name="payment-service",
            version="1.0.0",
            description="결제 처리 서비스",
            endpoints=[
                {"path": "/payments", "method": "POST", "description": "결제 처리"},
                {"path": "/payments/{id}", "method": "GET", "description": "결제 상태 조회"},
                {"path": "/payments/{id}/refund", "method": "POST", "description": "환불 처리"}
            ],
            health_check_interval=60,
            timeout=30,
            retry_count=2,
            circuit_breaker_config={
                "failure_threshold": 2,
                "success_threshold": 3,
                "timeout_seconds": 300
            },
            load_balancer_config={
                "strategy": "weighted",
                "health_check_enabled": True
            }
        )
    
    def register_service(self, name: str, version: str, description: str, endpoints: List[Dict],
                        health_check_interval: int = 30, timeout: int = 10, retry_count: int = 3,
                        circuit_breaker_config: Dict = None, load_balancer_config: Dict = None) -> str:
        """서비스 등록"""
        try:
            service_id = str(uuid.uuid4())
            now = datetime.now()
            
            service = ServiceDefinition(
                id=service_id,
                name=name,
                version=version,
                description=description,
                endpoints=endpoints,
                health_check_interval=health_check_interval,
                timeout=timeout,
                retry_count=retry_count,
                circuit_breaker_config=circuit_breaker_config or {},
                load_balancer_config=load_balancer_config or {},
                created_at=now,
                updated_at=now,
                is_active=True
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO service_definitions 
                    (id, name, version, description, endpoints, health_check_interval, timeout, retry_count, circuit_breaker_config, load_balancer_config, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    service.id, service.name, service.version, service.description,
                    json.dumps(service.endpoints), service.health_check_interval,
                    service.timeout, service.retry_count, json.dumps(service.circuit_breaker_config),
                    json.dumps(service.load_balancer_config), service.created_at.isoformat(),
                    service.updated_at.isoformat(), 1 if service.is_active else 0
                ))
                conn.commit()
            
            self.services[service_id] = service
            
            # 서킷 브레이커 초기화
            self._initialize_circuit_breaker(name, circuit_breaker_config or {})
            
            # 로드 밸런서 초기화
            strategy = load_balancer_config.get('strategy', 'round_robin') if load_balancer_config else 'round_robin'
            self.load_balancers[name] = LoadBalancer(strategy)
            
            logger.info(f"서비스 등록: {name} v{version}")
            return service_id
            
        except Exception as e:
            logger.error(f"서비스 등록 오류: {str(e)}")
            raise
    
    def register_instance(self, service_name: str, host: str, port: int, protocol: str = "http",
                         health_check_url: str = None, metadata: Dict[str, Any] = None) -> str:
        """서비스 인스턴스 등록"""
        try:
            instance_id = str(uuid.uuid4())
            now = datetime.now()
            
            if not health_check_url:
                health_check_url = f"{protocol}://{host}:{port}/health"
            
            instance = ServiceInstance(
                id=instance_id,
                service_name=service_name,
                host=host,
                port=port,
                protocol=protocol,
                health_check_url=health_check_url,
                status=ServiceStatus.UNKNOWN,
                last_health_check=now,
                response_time=0.0,
                error_count=0,
                success_count=0,
                metadata=metadata or {},
                created_at=now,
                updated_at=now
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO service_instances 
                    (id, service_name, host, port, protocol, health_check_url, status, last_health_check, response_time, error_count, success_count, metadata, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    instance.id, instance.service_name, instance.host, instance.port,
                    instance.protocol, instance.health_check_url, instance.status.value,
                    instance.last_health_check.isoformat(), instance.response_time,
                    instance.error_count, instance.success_count, json.dumps(instance.metadata),
                    instance.created_at.isoformat(), instance.updated_at.isoformat()
                ))
                conn.commit()
            
            self.instances[service_name].append(instance)
            
            logger.info(f"서비스 인스턴스 등록: {service_name} at {host}:{port}")
            return instance_id
            
        except Exception as e:
            logger.error(f"서비스 인스턴스 등록 오류: {str(e)}")
            raise
    
    def _initialize_circuit_breaker(self, service_name: str, config: Dict[str, Any]):
        """서킷 브레이커 초기화"""
        try:
            circuit_breaker = CircuitBreaker(
                service_name=service_name,
                state=CircuitBreakerState.CLOSED,
                failure_threshold=config.get('failure_threshold', 5),
                success_threshold=config.get('success_threshold', 2),
                timeout_seconds=config.get('timeout_seconds', 60),
                failure_count=0,
                success_count=0,
                last_failure_time=None,
                last_state_change=datetime.now()
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO circuit_breakers 
                    (service_name, state, failure_threshold, success_threshold, timeout_seconds, failure_count, success_count, last_failure_time, last_state_change)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    circuit_breaker.service_name, circuit_breaker.state.value,
                    circuit_breaker.failure_threshold, circuit_breaker.success_threshold,
                    circuit_breaker.timeout_seconds, circuit_breaker.failure_count,
                    circuit_breaker.success_count,
                    circuit_breaker.last_failure_time.isoformat() if circuit_breaker.last_failure_time else None,
                    circuit_breaker.last_state_change.isoformat()
                ))
                conn.commit()
            
            self.circuit_breakers[service_name] = circuit_breaker
            
        except Exception as e:
            logger.error(f"서킷 브레이커 초기화 오류: {str(e)}")
    
    def start_health_checks(self):
        """헬스 체크 시작"""
        for service_name in self.services:
            self._start_health_check_thread(service_name)
    
    def _start_health_check_thread(self, service_name: str):
        """헬스 체크 스레드 시작"""
        def health_check_worker():
            while True:
                try:
                    self._perform_health_checks(service_name)
                    
                    # 헬스 체크 간격만큼 대기
                    service = self._get_service_by_name(service_name)
                    if service:
                        time.sleep(service.health_check_interval)
                    else:
                        time.sleep(60)
                        
                except Exception as e:
                    logger.error(f"헬스 체크 워커 오류: {str(e)}")
                    time.sleep(60)
        
        thread = threading.Thread(target=health_check_worker, daemon=True)
        thread.start()
        self.health_check_threads[service_name] = thread
        logger.info(f"헬스 체크 스레드 시작: {service_name}")
    
    def _perform_health_checks(self, service_name: str):
        """헬스 체크 수행"""
        instances = self.instances.get(service_name, [])
        
        for instance in instances:
            try:
                start_time = time.time()
                
                # 헬스 체크 요청
                response = requests.get(
                    instance.health_check_url,
                    timeout=5,
                    headers={'User-Agent': 'MicroserviceIntegration/1.0'}
                )
                
                response_time = time.time() - start_time
                
                # 응답 분석
                if response.status_code == 200:
                    instance.status = ServiceStatus.HEALTHY
                    instance.success_count += 1
                    instance.response_time = response_time
                else:
                    instance.status = ServiceStatus.UNHEALTHY
                    instance.error_count += 1
                
                instance.last_health_check = datetime.now()
                instance.updated_at = datetime.now()
                
                # 데이터베이스 업데이트
                self._update_instance_status(instance)
                
            except Exception as e:
                instance.status = ServiceStatus.UNHEALTHY
                instance.error_count += 1
                instance.last_health_check = datetime.now()
                instance.updated_at = datetime.now()
                
                self._update_instance_status(instance)
                logger.warning(f"헬스 체크 실패: {instance.host}:{instance.port} - {str(e)}")
    
    def _update_instance_status(self, instance: ServiceInstance):
        """인스턴스 상태 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE service_instances 
                    SET status = ?, last_health_check = ?, response_time = ?, error_count = ?, success_count = ?, updated_at = ?
                    WHERE id = ?
                """, (
                    instance.status.value, instance.last_health_check.isoformat(),
                    instance.response_time, instance.error_count, instance.success_count,
                    instance.updated_at.isoformat(), instance.id
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"인스턴스 상태 업데이트 오류: {str(e)}")
    
    def call_service(self, service_name: str, endpoint: str, method: str = "GET",
                    data: Dict = None, headers: Dict = None, timeout: int = None) -> Dict[str, Any]:
        """서비스 호출"""
        try:
            # 서킷 브레이커 확인
            if not self._is_circuit_breaker_closed(service_name):
                raise Exception(f"서킷 브레이커가 열려있습니다: {service_name}")
            
            # 인스턴스 선택
            instance = self._select_instance(service_name)
            if not instance:
                raise Exception(f"사용 가능한 인스턴스가 없습니다: {service_name}")
            
            # 요청 URL 구성
            url = f"{instance.protocol}://{instance.host}:{instance.port}{endpoint}"
            
            # 타임아웃 설정
            service = self._get_service_by_name(service_name)
            request_timeout = timeout or (service.timeout if service else 30)
            
            # 요청 전송
            start_time = time.time()
            
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers or {},
                timeout=request_timeout
            )
            
            response_time = time.time() - start_time
            
            # 성공 처리
            self._handle_success(service_name)
            
            return {
                'status_code': response.status_code,
                'headers': dict(response.headers),
                'body': response.text,
                'response_time': response_time,
                'instance': {
                    'host': instance.host,
                    'port': instance.port,
                    'id': instance.id
                }
            }
            
        except Exception as e:
            # 실패 처리
            self._handle_failure(service_name)
            raise Exception(f"서비스 호출 실패: {str(e)}")
    
    def _is_circuit_breaker_closed(self, service_name: str) -> bool:
        """서킷 브레이커가 닫혀있는지 확인"""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if not circuit_breaker:
            return True
        
        # OPEN 상태에서 타임아웃 확인
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if circuit_breaker.last_failure_time:
                timeout_time = circuit_breaker.last_failure_time + timedelta(seconds=circuit_breaker.timeout_seconds)
                if datetime.now() > timeout_time:
                    # HALF-OPEN으로 변경
                    circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                    circuit_breaker.last_state_change = datetime.now()
                    self._update_circuit_breaker(circuit_breaker)
        
        return circuit_breaker.state != CircuitBreakerState.OPEN
    
    def _select_instance(self, service_name: str) -> Optional[ServiceInstance]:
        """인스턴스 선택"""
        instances = self.instances.get(service_name, [])
        healthy_instances = [inst for inst in instances if inst.status == ServiceStatus.HEALTHY]
        
        if not healthy_instances:
            return None
        
        load_balancer = self.load_balancers.get(service_name)
        if load_balancer:
            return load_balancer.select_instance(healthy_instances)
        else:
            return random.choice(healthy_instances)
    
    def _handle_success(self, service_name: str):
        """성공 처리"""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker:
            circuit_breaker.success_count += 1
            circuit_breaker.failure_count = 0
            
            # HALF-OPEN에서 CLOSED로 변경
            if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                if circuit_breaker.success_count >= circuit_breaker.success_threshold:
                    circuit_breaker.state = CircuitBreakerState.CLOSED
                    circuit_breaker.last_state_change = datetime.now()
                    self._update_circuit_breaker(circuit_breaker)
    
    def _handle_failure(self, service_name: str):
        """실패 처리"""
        circuit_breaker = self.circuit_breakers.get(service_name)
        if circuit_breaker:
            circuit_breaker.failure_count += 1
            circuit_breaker.last_failure_time = datetime.now()
            
            # CLOSED에서 OPEN으로 변경
            if circuit_breaker.state == CircuitBreakerState.CLOSED:
                if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
                    circuit_breaker.state = CircuitBreakerState.OPEN
                    circuit_breaker.last_state_change = datetime.now()
                    self._update_circuit_breaker(circuit_breaker)
            
            # HALF-OPEN에서 OPEN으로 변경
            elif circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
                circuit_breaker.state = CircuitBreakerState.OPEN
                circuit_breaker.last_state_change = datetime.now()
                self._update_circuit_breaker(circuit_breaker)
    
    def _update_circuit_breaker(self, circuit_breaker: CircuitBreaker):
        """서킷 브레이커 업데이트"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE circuit_breakers 
                    SET state = ?, failure_count = ?, success_count = ?, last_failure_time = ?, last_state_change = ?
                    WHERE service_name = ?
                """, (
                    circuit_breaker.state.value, circuit_breaker.failure_count,
                    circuit_breaker.success_count,
                    circuit_breaker.last_failure_time.isoformat() if circuit_breaker.last_failure_time else None,
                    circuit_breaker.last_state_change.isoformat(),
                    circuit_breaker.service_name
                ))
                conn.commit()
        except Exception as e:
            logger.error(f"서킷 브레이커 업데이트 오류: {str(e)}")
    
    def _get_service_by_name(self, service_name: str) -> Optional[ServiceDefinition]:
        """이름으로 서비스 조회"""
        for service in self.services.values():
            if service.name == service_name:
                return service
        return None
    
    def get_service_status(self, service_name: str) -> Dict[str, Any]:
        """서비스 상태 조회"""
        try:
            instances = self.instances.get(service_name, [])
            circuit_breaker = self.circuit_breakers.get(service_name)
            
            healthy_count = len([inst for inst in instances if inst.status == ServiceStatus.HEALTHY])
            total_count = len(instances)
            
            return {
                'service_name': service_name,
                'total_instances': total_count,
                'healthy_instances': healthy_count,
                'unhealthy_instances': total_count - healthy_count,
                'availability': (healthy_count / total_count * 100) if total_count > 0 else 0,
                'circuit_breaker_state': circuit_breaker.state.value if circuit_breaker else 'unknown',
                'last_health_check': max([inst.last_health_check for inst in instances]) if instances else None
            }
            
        except Exception as e:
            logger.error(f"서비스 상태 조회 오류: {str(e)}")
            return {}
    
    def get_all_services_status(self) -> Dict[str, Any]:
        """모든 서비스 상태 조회"""
        try:
            services_status = {}
            total_instances = 0
            total_healthy = 0
            
            for service_name in self.services:
                status = self.get_service_status(service_name)
                services_status[service_name] = status
                total_instances += status.get('total_instances', 0)
                total_healthy += status.get('healthy_instances', 0)
            
            return {
                'services': services_status,
                'summary': {
                    'total_services': len(self.services),
                    'total_instances': total_instances,
                    'total_healthy_instances': total_healthy,
                    'overall_availability': (total_healthy / total_instances * 100) if total_instances > 0 else 0
                }
            }
            
        except Exception as e:
            logger.error(f"전체 서비스 상태 조회 오류: {str(e)}")
            return {}
    
    def add_service_mesh_config(self, service_name: str, mesh_config: Dict[str, Any],
                               routing_rules: List[Dict], security_policies: List[Dict]):
        """서비스 메시 설정 추가"""
        try:
            mesh_id = str(uuid.uuid4())
            now = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO service_mesh 
                    (id, service_name, mesh_config, routing_rules, security_policies, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    mesh_id, service_name, json.dumps(mesh_config),
                    json.dumps(routing_rules), json.dumps(security_policies),
                    now.isoformat(), now.isoformat()
                ))
                conn.commit()
            
            self.service_mesh[service_name] = {
                'mesh_config': mesh_config,
                'routing_rules': routing_rules,
                'security_policies': security_policies
            }
            
            logger.info(f"서비스 메시 설정 추가: {service_name}")
            
        except Exception as e:
            logger.error(f"서비스 메시 설정 추가 오류: {str(e)}")
            raise
    
    def cleanup_old_instances(self, days: int = 7):
        """오래된 인스턴스 정리"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    DELETE FROM service_instances 
                    WHERE updated_at < datetime('now', '-{} days')
                """.format(days))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                logger.info(f"오래된 인스턴스 {deleted_count}개 정리 완료")
                return deleted_count
                
        except Exception as e:
            logger.error(f"인스턴스 정리 오류: {str(e)}")
            return 0 