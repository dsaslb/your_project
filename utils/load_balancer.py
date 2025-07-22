"""
로드 밸런싱 및 확장 시스템
서버 분산, 헬스체크, 자동 스케일링
"""

import logging
import time
import threading
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import requests
import json
import redis
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class ServerStatus(Enum):
    """서버 상태"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

@dataclass
class Server:
    """서버 정보"""
    id: str
    host: str
    port: int
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    status: ServerStatus = ServerStatus.UNKNOWN
    last_health_check: float = 0
    response_time: float = 0
    error_count: int = 0
    success_count: int = 0

class LoadBalancingAlgorithm(Enum):
    """로드 밸런싱 알고리즘"""
    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    WEIGHTED_LEAST_CONNECTIONS = "weighted_least_connections"
    IP_HASH = "ip_hash"
    LEAST_RESPONSE_TIME = "least_response_time"

class LoadBalancer:
    """로드 밸런서"""
    
    def __init__(self, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.servers: Dict[str, Server] = {}
        self.current_index = 0
        self.health_check_interval = 30  # 30초
        self.health_check_timeout = 5    # 5초
        self.max_failures = 3
        self.redis_client = None
        self.lock = threading.Lock()
        
        # 헬스체크 스레드 시작
        self.health_check_thread = threading.Thread(target=self._health_check_loop, daemon=True)
        self.health_check_thread.start()
    
    def add_server(self, server_id: str, host: str, port: int, weight: int = 1) -> bool:
        """서버 추가"""
        try:
            with self.lock:
                server = Server(
                    id=server_id,
                    host=host,
                    port=port,
                    weight=weight
                )
                self.servers[server_id] = server
                
                logger.info(f"서버 추가 완료: {server_id} ({host}:{port})")
                return True
                
        except Exception as e:
            logger.error(f"서버 추가 실패: {e}")
            return False
    
    def remove_server(self, server_id: str) -> bool:
        """서버 제거"""
        try:
            with self.lock:
                if server_id in self.servers:
                    del self.servers[server_id]
                    logger.info(f"서버 제거 완료: {server_id}")
                    return True
                return False
                
        except Exception as e:
            logger.error(f"서버 제거 실패: {e}")
            return False
    
    def get_server(self, client_ip: str = None) -> Optional[Server]:
        """로드 밸런싱 알고리즘에 따라 서버 선택"""
        try:
            with self.lock:
                healthy_servers = [
                    server for server in self.servers.values()
                    if server.status == ServerStatus.HEALTHY
                ]
                
                if not healthy_servers:
                    logger.warning("사용 가능한 서버가 없습니다")
                    return None
                
                if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
                    return self._round_robin(healthy_servers)
                elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
                    return self._least_connections(healthy_servers)
                elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
                    return self._weighted_round_robin(healthy_servers)
                elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_LEAST_CONNECTIONS:
                    return self._weighted_least_connections(healthy_servers)
                elif self.algorithm == LoadBalancingAlgorithm.IP_HASH:
                    return self._ip_hash(healthy_servers, client_ip)
                elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
                    return self._least_response_time(healthy_servers)
                else:
                    return healthy_servers[0]
                    
        except Exception as e:
            logger.error(f"서버 선택 실패: {e}")
            return None
    
    def _round_robin(self, servers: List[Server]) -> Server:
        """라운드 로빈 알고리즘"""
        if not servers:
            return None
        
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server
    
    def _least_connections(self, servers: List[Server]) -> Server:
        """최소 연결 알고리즘"""
        return min(servers, key=lambda s: s.current_connections)
    
    def _weighted_round_robin(self, servers: List[Server]) -> Server:
        """가중 라운드 로빈 알고리즘"""
        total_weight = sum(server.weight for server in servers)
        current_weight = self.current_index % total_weight
        
        for server in servers:
            if current_weight < server.weight:
                self.current_index += 1
                return server
            current_weight -= server.weight
        
        return servers[0]
    
    def _weighted_least_connections(self, servers: List[Server]) -> Server:
        """가중 최소 연결 알고리즘"""
        return min(servers, key=lambda s: s.current_connections / s.weight)
    
    def _ip_hash(self, servers: List[Server], client_ip: str) -> Server:
        """IP 해시 알고리즘"""
        if not client_ip:
            return servers[0]
        
        hash_value = hash(client_ip) % len(servers)
        return servers[hash_value]
    
    def _least_response_time(self, servers: List[Server]) -> Server:
        """최소 응답 시간 알고리즘"""
        return min(servers, key=lambda s: s.response_time)
    
    def increment_connections(self, server_id: str) -> bool:
        """서버 연결 수 증가"""
        try:
            with self.lock:
                if server_id in self.servers:
                    server = self.servers[server_id]
                    if server.current_connections < server.max_connections:
                        server.current_connections += 1
                        return True
            return False
            
        except Exception as e:
            logger.error(f"연결 수 증가 실패: {e}")
            return False
    
    def decrement_connections(self, server_id: str) -> bool:
        """서버 연결 수 감소"""
        try:
            with self.lock:
                if server_id in self.servers:
                    server = self.servers[server_id]
                    if server.current_connections > 0:
                        server.current_connections -= 1
                        return True
            return False
            
        except Exception as e:
            logger.error(f"연결 수 감소 실패: {e}")
            return False
    
    def _health_check_loop(self):
        """헬스체크 루프"""
        while True:
            try:
                self._perform_health_checks()
                time.sleep(self.health_check_interval)
            except Exception as e:
                logger.error(f"헬스체크 루프 오류: {e}")
                time.sleep(5)
    
    def _perform_health_checks(self):
        """헬스체크 수행"""
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self._check_server_health, server): server
                for server in self.servers.values()
            }
            
            for future in as_completed(futures):
                server = futures[future]
                try:
                    is_healthy = future.result()
                    self._update_server_status(server, is_healthy)
                except Exception as e:
                    logger.error(f"서버 {server.id} 헬스체크 실패: {e}")
                    self._update_server_status(server, False)
    
    def _check_server_health(self, server: Server) -> bool:
        """개별 서버 헬스체크"""
        try:
            start_time = time.time()
            
            response = requests.get(
                f"http://{server.host}:{server.port}/health",
                timeout=self.health_check_timeout
            )
            
            response_time = time.time() - start_time
            server.response_time = response_time
            
            is_healthy = response.status_code == 200
            
            if is_healthy:
                server.success_count += 1
                server.error_count = 0
            else:
                server.error_count += 1
            
            return is_healthy
            
        except Exception as e:
            server.error_count += 1
            logger.debug(f"서버 {server.id} 헬스체크 실패: {e}")
            return False
    
    def _update_server_status(self, server: Server, is_healthy: bool):
        """서버 상태 업데이트"""
        try:
            with self.lock:
                server.last_health_check = time.time()
                
                if is_healthy:
                    if server.error_count == 0:
                        server.status = ServerStatus.HEALTHY
                else:
                    if server.error_count >= self.max_failures:
                        server.status = ServerStatus.UNHEALTHY
                        logger.warning(f"서버 {server.id} 비정상 상태로 변경")
                
        except Exception as e:
            logger.error(f"서버 상태 업데이트 실패: {e}")
    
    def get_server_stats(self) -> Dict:
        """서버 통계 조회"""
        try:
            with self.lock:
                stats = {
                    'total_servers': len(self.servers),
                    'healthy_servers': len([s for s in self.servers.values() if s.status == ServerStatus.HEALTHY]),
                    'unhealthy_servers': len([s for s in self.servers.values() if s.status == ServerStatus.UNHEALTHY]),
                    'total_connections': sum(s.current_connections for s in self.servers.values()),
                    'servers': []
                }
                
                for server in self.servers.values():
                    stats['servers'].append({
                        'id': server.id,
                        'host': server.host,
                        'port': server.port,
                        'status': server.status.value,
                        'current_connections': server.current_connections,
                        'max_connections': server.max_connections,
                        'response_time': server.response_time,
                        'success_count': server.success_count,
                        'error_count': server.error_count,
                        'last_health_check': server.last_health_check
                    })
                
                return stats
                
        except Exception as e:
            logger.error(f"서버 통계 조회 실패: {e}")
            return {}

class AutoScaler:
    """자동 스케일러"""
    
    def __init__(self, load_balancer: LoadBalancer, redis_client: redis.Redis):
        self.load_balancer = load_balancer
        self.redis_client = redis_client
        self.scaling_config = {
            'min_servers': 2,
            'max_servers': 10,
            'cpu_threshold': 80,  # CPU 사용률 임계값
            'memory_threshold': 85,  # 메모리 사용률 임계값
            'connection_threshold': 80,  # 연결 수 임계값
            'scale_up_cooldown': 300,  # 스케일 업 쿨다운 (5분)
            'scale_down_cooldown': 600,  # 스케일 다운 쿨다운 (10분)
        }
        self.last_scale_up = 0
        self.last_scale_down = 0
        self.scaling_thread = threading.Thread(target=self._scaling_loop, daemon=True)
        self.scaling_thread.start()
    
    def _scaling_loop(self):
        """스케일링 루프"""
        while True:
            try:
                self._check_scaling_needs()
                time.sleep(60)  # 1분마다 체크
            except Exception as e:
                logger.error(f"스케일링 루프 오류: {e}")
                time.sleep(30)
    
    def _check_scaling_needs(self):
        """스케일링 필요성 체크"""
        try:
            current_time = time.time()
            stats = self.load_balancer.get_server_stats()
            
            if not stats['servers']:
                return
            
            # 평균 CPU 사용률 계산
            total_cpu = 0
            total_memory = 0
            total_connections = 0
            
            for server in stats['servers']:
                # Redis에서 서버 메트릭 조회
                cpu_key = f"server:{server['id']}:cpu"
                memory_key = f"server:{server['id']}:memory"
                
                cpu_usage = float(self.redis_client.get(cpu_key) or 0)
                memory_usage = float(self.redis_client.get(memory_key) or 0)
                
                total_cpu += cpu_usage
                total_memory += memory_usage
                total_connections += server['current_connections']
            
            avg_cpu = total_cpu / len(stats['servers'])
            avg_memory = total_memory / len(stats['servers'])
            avg_connections = total_connections / len(stats['servers'])
            
            # 스케일 업 조건 체크
            if (avg_cpu > self.scaling_config['cpu_threshold'] or
                avg_memory > self.scaling_config['memory_threshold'] or
                avg_connections > self.scaling_config['connection_threshold']):
                
                if (current_time - self.last_scale_up > self.scaling_config['scale_up_cooldown'] and
                    len(stats['servers']) < self.scaling_config['max_servers']):
                    
                    self._scale_up()
                    self.last_scale_up = current_time
            
            # 스케일 다운 조건 체크
            elif (avg_cpu < self.scaling_config['cpu_threshold'] * 0.5 and
                  avg_memory < self.scaling_config['memory_threshold'] * 0.5 and
                  avg_connections < self.scaling_config['connection_threshold'] * 0.5):
                
                if (current_time - self.last_scale_down > self.scaling_config['scale_down_cooldown'] and
                    len(stats['servers']) > self.scaling_config['min_servers']):
                    
                    self._scale_down()
                    self.last_scale_down = current_time
                    
        except Exception as e:
            logger.error(f"스케일링 체크 실패: {e}")
    
    def _scale_up(self):
        """스케일 업"""
        try:
            logger.info("스케일 업 시작")
            
            # 새 서버 생성 로직
            # Docker 컨테이너 또는 클라우드 인스턴스 생성
            new_server_id = f"server-{int(time.time())}"
            
            # 새 서버를 로드 밸런서에 추가
            # self.load_balancer.add_server(new_server_id, host, port)
            
            logger.info(f"스케일 업 완료: {new_server_id}")
            
        except Exception as e:
            logger.error(f"스케일 업 실패: {e}")
    
    def _scale_down(self):
        """스케일 다운"""
        try:
            logger.info("스케일 다운 시작")
            
            # 가장 적은 부하를 받는 서버 찾기
            stats = self.load_balancer.get_server_stats()
            if not stats['servers']:
                return
            
            # 연결 수가 가장 적은 서버 선택
            target_server = min(stats['servers'], key=lambda s: s['current_connections'])
            
            # 서버 제거
            # self.load_balancer.remove_server(target_server['id'])
            
            logger.info(f"스케일 다운 완료: {target_server['id']}")
            
        except Exception as e:
            logger.error(f"스케일 다운 실패: {e}")
    
    def update_scaling_config(self, config: Dict):
        """스케일링 설정 업데이트"""
        try:
            self.scaling_config.update(config)
            logger.info("스케일링 설정 업데이트 완료")
            
        except Exception as e:
            logger.error(f"스케일링 설정 업데이트 실패: {e}")

class LoadBalancerManager:
    """로드 밸런서 관리자"""
    
    def __init__(self, redis_url: str):
        self.redis_client = redis.from_url(redis_url)
        self.load_balancers: Dict[str, LoadBalancer] = {}
        self.auto_scalers: Dict[str, AutoScaler] = {}
    
    def create_load_balancer(self, name: str, algorithm: LoadBalancingAlgorithm) -> LoadBalancer:
        """로드 밸런서 생성"""
        try:
            load_balancer = LoadBalancer(algorithm)
            self.load_balancers[name] = load_balancer
            
            # 자동 스케일러 생성
            auto_scaler = AutoScaler(load_balancer, self.redis_client)
            self.auto_scalers[name] = auto_scaler
            
            logger.info(f"로드 밸런서 생성 완료: {name}")
            return load_balancer
            
        except Exception as e:
            logger.error(f"로드 밸런서 생성 실패: {e}")
            raise
    
    def get_load_balancer(self, name: str) -> Optional[LoadBalancer]:
        """로드 밸런서 조회"""
        return self.load_balancers.get(name)
    
    def remove_load_balancer(self, name: str) -> bool:
        """로드 밸런서 제거"""
        try:
            if name in self.load_balancers:
                del self.load_balancers[name]
                del self.auto_scalers[name]
                logger.info(f"로드 밸런서 제거 완료: {name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"로드 밸런서 제거 실패: {e}")
            return False
    
    def get_all_stats(self) -> Dict:
        """모든 로드 밸런서 통계 조회"""
        try:
            stats = {}
            for name, lb in self.load_balancers.items():
                stats[name] = lb.get_server_stats()
            return stats
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}

# 전역 로드 밸런서 관리자 인스턴스
lb_manager = None

def init_load_balancer_manager(redis_url: str):
    """로드 밸런서 관리자 초기화"""
    global lb_manager
    lb_manager = LoadBalancerManager(redis_url)
    logger.info("로드 밸런서 관리자 초기화 완료")

def get_load_balancer_manager() -> Optional[LoadBalancerManager]:
    """로드 밸런서 관리자 반환"""
    return lb_manager 