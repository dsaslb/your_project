import os
import json
import time
import hashlib
import logging
import sqlite3
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import uuid
from collections import defaultdict, deque
from enum import Enum

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoadBalancingAlgorithm(Enum):
    """로드 밸런싱 알고리즘"""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    LEAST_CONNECTIONS = "least_connections"
    IP_HASH = "ip_hash"

class ServerStatus(Enum):
    """서버 상태"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

@dataclass
class LoadBalancerConfig:
    """로드 밸런서 설정 클래스"""
    data_dir: str
    health_check_interval: int = 30  # 초
    health_check_timeout: int = 5    # 초
    max_failures: int = 3
    enable_sticky_sessions: bool = True
    session_timeout: int = 1800      # 초 (30분)

@dataclass
class Server:
    """서버 정보"""
    server_id: str
    name: str
    host: str
    port: int
    protocol: str = "http"
    weight: int = 100
    max_connections: int = 1000
    is_active: bool = True
    status: ServerStatus = ServerStatus.HEALTHY
    health_check_url: str = "/health"
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class ServerGroup:
    """서버 그룹 정보"""
    group_id: str
    name: str
    algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN
    servers: List[Server] = None
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class LoadBalancerMetric:
    """로드 밸런서 메트릭 정보"""
    metric_id: str
    server_id: str
    group_id: str
    request_count: int
    response_time: float
    status_code: int
    timestamp: datetime = None

@dataclass
class HealthCheckResult:
    """헬스 체크 결과"""
    server_id: str
    status: ServerStatus
    response_time: float
    status_code: int
    last_check: datetime
    consecutive_failures: int = 0

class LoadBalancerManager:
    """로드 밸런서 관리자 클래스"""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.server_groups: Dict[str, ServerGroup] = {}
        self.servers: Dict[str, Server] = {}
        self.metrics: List[LoadBalancerMetric] = []
        self.health_check_results: Dict[str, HealthCheckResult] = {}
        self.connection_counts: Dict[str, int] = defaultdict(int)
        self.session_mapping: Dict[str, str] = {}  # session_id -> server_id
        
        # 설정 디렉토리 생성
        os.makedirs(config.data_dir, exist_ok=True)
        
        # 데이터베이스 초기화
        self.init_database()
        
        # 기본 서버 그룹 생성
        self.create_default_server_groups()
        
        # 기존 데이터 로드
        self.load_data()
        
        # 헬스 체크 스레드 시작
        self.health_check_thread = threading.Thread(target=self._health_check_worker, daemon=True)
        self.health_check_thread.start()
    
    def init_database(self):
        """로드 밸런서 데이터베이스 초기화"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        
        # 데이터베이스 잠금 문제 해결을 위한 설정
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        cursor = conn.cursor()
        
        # 서버 그룹 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS server_groups (
                group_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                algorithm TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        ''')
        
        # 서버 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS servers (
                server_id TEXT PRIMARY KEY,
                group_id TEXT NOT NULL,
                name TEXT NOT NULL,
                host TEXT NOT NULL,
                port INTEGER NOT NULL,
                protocol TEXT NOT NULL DEFAULT 'http',
                weight INTEGER NOT NULL DEFAULT 100,
                max_connections INTEGER NOT NULL DEFAULT 1000,
                is_active BOOLEAN NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'healthy',
                health_check_url TEXT NOT NULL DEFAULT '/health',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (group_id) REFERENCES server_groups (group_id)
            )
        ''')
        
        # 로드 밸런서 메트릭 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS load_balancer_metrics (
                metric_id TEXT PRIMARY KEY,
                server_id TEXT NOT NULL,
                group_id TEXT NOT NULL,
                request_count INTEGER NOT NULL,
                response_time REAL NOT NULL,
                status_code INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (server_id) REFERENCES servers (server_id),
                FOREIGN KEY (group_id) REFERENCES server_groups (group_id)
            )
        ''')
        
        # 헬스 체크 결과 테이블
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_check_results (
                server_id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                response_time REAL NOT NULL,
                status_code INTEGER NOT NULL,
                last_check TEXT NOT NULL,
                consecutive_failures INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (server_id) REFERENCES servers (server_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_default_server_groups(self):
        """기본 서버 그룹 생성"""
        # 기본 그룹 먼저 생성
        default_group_id = self.create_server_group(
            name="기본 그룹",
            algorithm=LoadBalancingAlgorithm.ROUND_ROBIN
        )
        
        default_groups = [
            {
                "name": "웹 서버 그룹",
                "algorithm": LoadBalancingAlgorithm.ROUND_ROBIN,
                "servers": [
                    {
                        "name": "웹 서버 1",
                        "host": "localhost",
                        "port": 5001,
                        "protocol": "http",
                        "weight": 100,
                        "health_check_url": "/health"
                    },
                    {
                        "name": "웹 서버 2",
                        "host": "localhost",
                        "port": 5002,
                        "protocol": "http",
                        "weight": 100,
                        "health_check_url": "/health"
                    }
                ]
            },
            {
                "name": "API 서버 그룹",
                "algorithm": LoadBalancingAlgorithm.LEAST_CONNECTIONS,
                "servers": [
                    {
                        "name": "API 서버 1",
                        "host": "localhost",
                        "port": 5003,
                        "protocol": "http",
                        "weight": 100,
                        "health_check_url": "/health"
                    }
                ]
            }
        ]
        
        for group_config in default_groups:
            group_id = self.create_server_group(
                name=group_config["name"],
                algorithm=group_config["algorithm"],
                servers=group_config["servers"]
            )
            
            logger.info(f"기본 서버 그룹 생성 완료: {group_config['name']} (ID: {group_id})")
    
    def create_server_group(self, name: str, algorithm: LoadBalancingAlgorithm,
                           servers: List[Dict] = None) -> str:
        """서버 그룹 생성"""
        group_id = str(uuid.uuid4())
        
        group = ServerGroup(
            group_id=group_id,
            name=name,
            algorithm=algorithm,
            servers=[],
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.server_groups[group_id] = group
        self._save_server_group(group)
        
        # 서버들 추가
        if servers:
            for server_data in servers:
                self.add_server_to_group(
                    group_id=group_id,
                    name=server_data["name"],
                    host=server_data["host"],
                    port=server_data["port"],
                    protocol=server_data.get("protocol", "http"),
                    weight=server_data.get("weight", 100),
                    health_check_url=server_data.get("health_check_url", "/health")
                )
        
        logger.info(f"서버 그룹 생성: {name} (알고리즘: {algorithm.value})")
        return group_id
    
    def add_server_to_group(self, group_id: str, name: str, host: str, port: int,
                           protocol: str = "http", weight: int = 100,
                           max_connections: int = 1000,
                           health_check_url: str = "/health") -> str:
        """서버 그룹에 서버 추가"""
        if group_id not in self.server_groups:
            raise ValueError(f"서버 그룹을 찾을 수 없습니다: {group_id}")
        
        server_id = str(uuid.uuid4())
        
        server = Server(
            server_id=server_id,
            name=name,
            host=host,
            port=port,
            protocol=protocol,
            weight=weight,
            max_connections=max_connections,
            is_active=True,
            status=ServerStatus.HEALTHY,
            health_check_url=health_check_url,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.servers[server_id] = server
        self.server_groups[group_id].servers.append(server)
        self._save_server(server, group_id)
        
        # 헬스 체크 결과 초기화
        self.health_check_results[server_id] = HealthCheckResult(
            server_id=server_id,
            status=ServerStatus.HEALTHY,
            response_time=0.0,
            status_code=200,
            last_check=datetime.utcnow(),
            consecutive_failures=0
        )
        
        logger.info(f"서버 추가: {name} ({host}:{port})")
        return server_id
    
    def select_server(self, group_id: str, client_ip: str = None,
                     session_id: str = None) -> Optional[Server]:
        """로드 밸런싱 알고리즘에 따라 서버 선택"""
        if group_id not in self.server_groups:
            return None
        
        group = self.server_groups[group_id]
        if not group.is_active:
            return None
        
        # 활성 서버만 필터링
        active_servers = [s for s in group.servers if s.is_active and s.status == ServerStatus.HEALTHY]
        
        if not active_servers:
            logger.warning(f"활성 서버가 없습니다: {group.name}")
            return None
        
        # 세션 고정 확인
        if self.config.enable_sticky_sessions and session_id:
            if session_id in self.session_mapping:
                server_id = self.session_mapping[session_id]
                server = next((s for s in active_servers if s.server_id == server_id), None)
                if server:
                    return server
        
        # 로드 밸런싱 알고리즘 적용
        selected_server = None
        
        if group.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            selected_server = self._round_robin_select(active_servers)
        elif group.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            selected_server = self._weighted_round_robin_select(active_servers)
        elif group.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            selected_server = self._least_connections_select(active_servers)
        elif group.algorithm == LoadBalancingAlgorithm.IP_HASH:
            selected_server = self._ip_hash_select(active_servers, client_ip)
        else:
            selected_server = active_servers[0]  # 기본값
        
        # 세션 매핑 저장
        if selected_server and session_id:
            self.session_mapping[session_id] = selected_server.server_id
        
        return selected_server
    
    def _round_robin_select(self, servers: List[Server]) -> Server:
        """라운드 로빈 선택"""
        index = int(time.time()) % len(servers)
        return servers[index]
    
    def _weighted_round_robin_select(self, servers: List[Server]) -> Server:
        """가중치 라운드 로빈 선택"""
        total_weight = sum(server.weight for server in servers)
        if total_weight == 0:
            return servers[0]
        
        index = int(time.time()) % total_weight
        
        current_weight = 0
        for server in servers:
            current_weight += server.weight
            if index < current_weight:
                return server
        
        return servers[0]
    
    def _least_connections_select(self, servers: List[Server]) -> Server:
        """최소 연결 수 선택"""
        return min(servers, key=lambda s: self.connection_counts.get(s.server_id, 0))
    
    def _ip_hash_select(self, servers: List[Server], client_ip: str) -> Server:
        """IP 해시 선택"""
        if not client_ip:
            return servers[0]
        
        hash_value = hash(client_ip)
        index = abs(hash_value) % len(servers)
        return servers[index]
    
    def record_request(self, server_id: str, group_id: str, response_time: float,
                      status_code: int):
        """요청 기록"""
        # 연결 수 증가
        self.connection_counts[server_id] += 1
        
        # 메트릭 저장
        metric = LoadBalancerMetric(
            metric_id=str(uuid.uuid4()),
            server_id=server_id,
            group_id=group_id,
            request_count=1,
            response_time=response_time,
            status_code=status_code,
            timestamp=datetime.utcnow()
        )
        
        self.metrics.append(metric)
        self._save_metric(metric)
    
    def record_response(self, server_id: str):
        """응답 완료 기록"""
        if server_id in self.connection_counts:
            self.connection_counts[server_id] = max(0, self.connection_counts[server_id] - 1)
    
    def _health_check_worker(self):
        """헬스 체크 워커 스레드"""
        while True:
            try:
                for server in self.servers.values():
                    if server.is_active:
                        try:
                            self._perform_health_check(server)
                        except Exception as e:
                            logger.warning(f"서버 {server.name} 헬스 체크 실패: {str(e)}")
                            continue
                
                time.sleep(self.config.health_check_interval)
                
            except Exception as e:
                logger.error(f"헬스 체크 워커 오류: {str(e)}")
                time.sleep(10)
    
    def _perform_health_check(self, server: Server):
        """개별 서버 헬스 체크 수행"""
        try:
            url = f"{server.protocol}://{server.host}:{server.port}{server.health_check_url}"
            
            start_time = time.time()
            response = requests.get(
                url,
                timeout=self.config.health_check_timeout,
                headers={'User-Agent': 'LoadBalancer/1.0'}
            )
            response_time = time.time() - start_time
            
            # 헬스 체크 결과 업데이트
            if response.status_code == 200:
                self._update_server_status(server.server_id, ServerStatus.HEALTHY, response_time, response.status_code)
            else:
                self._update_server_status(server.server_id, ServerStatus.UNHEALTHY, response_time, response.status_code)
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"서버 {server.name} 헬스 체크 실패: {str(e)}")
            self._update_server_status(server.server_id, ServerStatus.UNHEALTHY, 0.0, 0)
    
    def _update_server_status(self, server_id: str, status: ServerStatus, response_time: float, status_code: int):
        """서버 상태 업데이트"""
        if server_id not in self.health_check_results:
            self.health_check_results[server_id] = HealthCheckResult(
                server_id=server_id,
                status=status,
                response_time=response_time,
                status_code=status_code,
                last_check=datetime.utcnow(),
                consecutive_failures=0
            )
        else:
            result = self.health_check_results[server_id]
            
            if status == ServerStatus.HEALTHY:
                result.consecutive_failures = 0
            else:
                result.consecutive_failures += 1
            
            result.status = status
            result.response_time = response_time
            result.status_code = status_code
            result.last_check = datetime.utcnow()
        
        # 서버 상태 업데이트
        if server_id in self.servers:
            server = self.servers[server_id]
            
            # 연속 실패 횟수에 따른 상태 결정
            if result.consecutive_failures >= self.config.max_failures:
                server.status = ServerStatus.UNHEALTHY
            else:
                server.status = status
            
            server.updated_at = datetime.utcnow()
            self._save_server(server, None)
        
        # 헬스 체크 결과 저장
        self._save_health_check_result(self.health_check_results[server_id])
    
    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """로드 밸런서 통계 조회"""
        try:
            stats = {
                'total_groups': len(self.server_groups),
                'active_groups': len([g for g in self.server_groups.values() if g.is_active]),
                'total_servers': len(self.servers),
                'healthy_servers': len([s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]),
                'unhealthy_servers': len([s for s in self.servers.values() if s.status == ServerStatus.UNHEALTHY]),
                'total_connections': sum(self.connection_counts.values()),
                'total_metrics': len(self.metrics),
                'active_sessions': len(self.session_mapping)
            }
            
            # 그룹별 통계
            group_stats = []
            for group in self.server_groups.values():
                healthy_count = len([s for s in group.servers if s.status == ServerStatus.HEALTHY])
                total_count = len(group.servers)
                
                group_stats.append({
                    'group_id': group.group_id,
                    'name': group.name,
                    'algorithm': group.algorithm.value,
                    'healthy_servers': healthy_count,
                    'total_servers': total_count,
                    'health_rate': (healthy_count / total_count * 100) if total_count > 0 else 0
                })
            
            stats['group_stats'] = group_stats
            
            # 최근 메트릭 분석
            recent_metrics = [m for m in self.metrics if m.timestamp > datetime.utcnow() - timedelta(hours=1)]
            
            if recent_metrics:
                stats.update({
                    'requests_last_hour': len(recent_metrics),
                    'avg_response_time': sum(m.response_time for m in recent_metrics) / len(recent_metrics),
                    'success_rate': len([m for m in recent_metrics if 200 <= m.status_code < 400]) / len(recent_metrics) * 100
                })
            
            return stats
            
        except Exception as e:
            logger.error(f"통계 조회 오류: {str(e)}")
            return {}
    
    def load_data(self):
        """데이터 로드"""
        try:
            self._load_server_groups()
            self._load_servers()
            self._load_metrics()
            self._load_health_check_results()
            
            logger.info(f"로드 밸런서 데이터 로드 완료: {len(self.server_groups)}개 그룹, {len(self.servers)}개 서버")
            
        except Exception as e:
            logger.error(f"로드 밸런서 데이터 로드 오류: {str(e)}")
    
    # 데이터베이스 저장 메서드들
    def _save_server_group(self, group: ServerGroup):
        """서버 그룹을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO server_groups 
            (group_id, name, algorithm, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            group.group_id,
            group.name,
            group.algorithm.value,
            group.is_active,
            group.created_at.isoformat(),
            group.updated_at.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_server(self, server: Server, group_id: str):
        """서버를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        
        # 데이터베이스 잠금 문제 해결을 위한 설정
        conn = sqlite3.connect(db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        cursor = conn.cursor()
        
        # group_id가 None이면 기본값 사용
        actual_group_id = group_id if group_id is not None else "default_group"
        
        cursor.execute('''
            INSERT OR REPLACE INTO servers 
            (server_id, group_id, name, host, port, protocol, weight, max_connections, 
             is_active, status, health_check_url, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            server.server_id,
            actual_group_id,
            server.name,
            server.host,
            server.port,
            server.protocol,
            server.weight,
            server.max_connections,
            server.is_active,
            server.status.value,
            server.health_check_url,
            server.created_at.isoformat() if server.created_at else datetime.utcnow().isoformat(),
            server.updated_at.isoformat() if server.updated_at else datetime.utcnow().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_metric(self, metric: LoadBalancerMetric):
        """메트릭을 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO load_balancer_metrics 
            (metric_id, server_id, group_id, request_count, response_time, status_code, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            metric.metric_id,
            metric.server_id,
            metric.group_id,
            metric.request_count,
            metric.response_time,
            metric.status_code,
            metric.timestamp.isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def _save_health_check_result(self, result: HealthCheckResult):
        """헬스 체크 결과를 데이터베이스에 저장"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO health_check_results 
            (server_id, status, response_time, status_code, last_check, consecutive_failures)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            result.server_id,
            result.status.value,
            result.response_time,
            result.status_code,
            result.last_check.isoformat(),
            result.consecutive_failures
        ))
        
        conn.commit()
        conn.close()
    
    def _load_server_groups(self):
        """데이터베이스에서 서버 그룹 로드"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM server_groups')
        rows = cursor.fetchall()
        
        for row in rows:
            group = ServerGroup(
                group_id=row[0],
                name=row[1],
                algorithm=LoadBalancingAlgorithm(row[2]),
                servers=[],
                is_active=bool(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5])
            )
            self.server_groups[group.group_id] = group
        
        conn.close()
    
    def _load_servers(self):
        """데이터베이스에서 서버 로드"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM servers')
        rows = cursor.fetchall()
        
        for row in rows:
            server = Server(
                server_id=row[0],
                name=row[2],
                host=row[3],
                port=row[4],
                protocol=row[5],
                weight=row[6],
                max_connections=row[7],
                is_active=bool(row[8]),
                status=ServerStatus(row[9]),
                health_check_url=row[10],
                created_at=datetime.fromisoformat(row[11]),
                updated_at=datetime.fromisoformat(row[12])
            )
            self.servers[server.server_id] = server
            
            # 서버 그룹에 추가
            group_id = row[1]
            if group_id in self.server_groups:
                self.server_groups[group_id].servers.append(server)
        
        conn.close()
    
    def _load_metrics(self):
        """데이터베이스에서 메트릭 로드"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM load_balancer_metrics ORDER BY timestamp DESC LIMIT 1000')
        rows = cursor.fetchall()
        
        for row in rows:
            metric = LoadBalancerMetric(
                metric_id=row[0],
                server_id=row[1],
                group_id=row[2],
                request_count=row[3],
                response_time=row[4],
                status_code=row[5],
                timestamp=datetime.fromisoformat(row[6])
            )
            self.metrics.append(metric)
        
        conn.close()
    
    def _load_health_check_results(self):
        """데이터베이스에서 헬스 체크 결과 로드"""
        db_path = os.path.join(self.config.data_dir, 'load_balancer.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM health_check_results')
        rows = cursor.fetchall()
        
        for row in rows:
            result = HealthCheckResult(
                server_id=row[0],
                status=ServerStatus(row[1]),
                response_time=row[2],
                status_code=row[3],
                last_check=datetime.fromisoformat(row[4]),
                consecutive_failures=row[5]
            )
            self.health_check_results[result.server_id] = result
        
        conn.close() 